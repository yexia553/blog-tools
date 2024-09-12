"""
此脚本用于把本地的markdown博客通过chrome发布到CSDN
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from itertools import chain
from functools import partial
import pyperclip
import var
from csdn.utils import fetch_attr, get_content_main_body, replace_image_with_link, wait_login, get_driver
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


def csdn_publisher(driver, blog_content):
    """
    发布博客内容到CSDN
    """
    csdn_config = {
        "site": "https://editor.csdn.net/md/",
        "visibility": "全部可见",
    }
    driver.switch_to.new_window("tab")
    driver.get(csdn_config["site"])
    time.sleep(1)

    wait_login(
        driver,
        By.XPATH,
        '//div[contains(@class,"article-bar")]//input[contains(@placeholder,"请输入文章标题")]',
    )
    title = driver.find_element(
        By.XPATH,
        '//div[contains(@class,"article-bar")]//input[contains(@placeholder,"请输入文章标题")]',
    )
    title.clear()
    blog_title = fetch_attr(blog_content, "title")
    if blog_title:
        title.send_keys(blog_title)
    else:
        logging.error("markdown博客没有title属性或者title属性没有值")
    time.sleep(1)

    # 文章内容
    content_main_body = get_content_main_body(blog_content)
    cmd_ctrl = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
    pyperclip.copy(content_main_body)
    action_chains = webdriver.ActionChains(driver)
    content = driver.find_element(
        By.XPATH, '//div[@class="editor"]//div[@class="cledit-section"]'
    )
    content.click()
    time.sleep(1)
    action_chains.key_down(cmd_ctrl).send_keys("v").key_up(cmd_ctrl).perform()
    time.sleep(1)

    # 发布文章
    driver.find_element(
        By.XPATH,
        '//button[contains(@class, "btn-publish") and contains(text(),"发布文章")]',
    ).click()
    time.sleep(1)

    # 文章标签
    tags = fetch_attr(blog_content, "tags")
    if tags:
        driver.find_element(
            By.XPATH,
            '//div[@class="mark_selection"]//button[@class="tag__btn-tag" and contains(text(),"添加文章标签")]',
        ).click()
        time.sleep(1)
        tag_input = driver.find_element(
            By.XPATH,
            '//div[@class="mark_selection_box"]//input[contains(@placeholder,"请输入文字搜索")]',
        )
        for tag in tags:
            tag_input.send_keys(tag)
            time.sleep(1)
            tag_input.send_keys(Keys.ENTER)
            time.sleep(1)
        driver.find_element(
            By.XPATH, '//div[@class="mark_selection_box"]//button[@title="关闭"]'
        ).click()
        time.sleep(1)
    else:
        logging.error("markdown博客没有tags属性或者tags属性没有值")

    # 文章封面
    image = fetch_attr(blog_content, "image")
    if image:
        driver.find_element(
            By.XPATH, "//input[@class='el-upload__input' and @type='file']"
        ).send_keys(image)
        time.sleep(1)

    # 摘要
    summary = fetch_attr(blog_content, "description")
    if summary:
        driver.find_element(
            By.XPATH,
            '//div[@class="desc-box"]//textarea[contains(@placeholder,"摘要：会在推荐、列表等场景外露")]',
        ).send_keys(summary)
        time.sleep(1)

    # 可见范围
    visibility = csdn_config["visibility"]
    if visibility:
        visibility_input = driver.find_element(
            By.XPATH,
            f'//div[@class="switch-box"]//label[contains(text(),"{visibility}")]',
        )
        visibility_input.find_element(By.XPATH, "..").click()

    # 发布
    driver.find_element(
        By.XPATH,
        '//div[@class="modal__button-bar"]//button[contains(text(),"发布文章")]',
    ).click()


def process_blogs(start_date, end_date):
    driver = get_driver()
    date_range = [
        start_date + timedelta(n) for n in range((end_date - start_date).days)
    ]

    def is_blog_in_date_range(path, dates):
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        blog_date = fetch_attr(content, "date").strip()
        return any(date.strftime("%Y-%m-%d") in blog_date for date in dates)

    all_markdown_files = chain.from_iterable(
        Path(item).glob("**/*.md") for item in var.MARKDOWN_PATH
    )
    filtered_files = filter(
        partial(is_blog_in_date_range, dates=date_range), all_markdown_files
    )

    for path in filtered_files:
        logging.info(str(path))
        markdown_content = replace_image_with_link(str(path))
        markdown_content += var.FOOTER
        csdn_publisher(driver, markdown_content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start", help="Start date as days before current date", type=int, default=1
    )
    parser.add_argument(
        "--end", help="End date as days before current date", type=int, default=-1
    )
    args = parser.parse_args()

    current_date = datetime.now()
    start_date = current_date - timedelta(days=args.start)
    end_date = current_date - timedelta(days=args.end)

    start_time = time.time()
    process_blogs(start_date, end_date)
    logging.info("程序耗时%.2f秒.", time.time() - start_time)


if __name__ == "__main__":
    main()
