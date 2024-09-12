import selenium
import var
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import var


def replace_image_with_link(
    post_path, footer=var.FOOTER, image_base_uri=var.ONLINE_IMAGE_BASE_URI
):
    """
    用给定的图片链接替换markdown文件中路径，并在末尾添加页脚。

    :param post_path: 博客文章的路径。
    :param footer: 需要添加到文章末尾的页脚内容。
    :param image_base_uri: 图片的基础URL，用于替换图片路径中的相对路径。
    :return: 替换图片链接并添加页脚后的文章内容。
    """
    try:
        with open(post_path, "r", encoding="utf-8") as file:
            content = ""
            for line in file:
                content += re.sub(r"\(../images/", f"({image_base_uri}/", line)
            if footer:
                content += footer
            return content
    except FileNotFoundError:
        print(f"文件 {post_path} 不存在。")
        return ""
    except PermissionError:
        print(f"没有权限读取文件 {post_path}。")
        return ""


def fetch_attr(content, key):
    """
    从markdown文件中提取属性，支持多行属性
    """
    lines = content.split("\n")
    in_key = False
    result = []
    for line in lines:
        if line.startswith(key + ":"):
            in_key = True
            value = line.split(":", 1)[1].strip()
            if value:
                result.append(value)
        elif in_key and line.strip().startswith("-"):
            result.append(line.strip()[1:].strip())
        elif in_key:
            break
    return result if len(result) > 1 else (result[0] if result else "")


def get_driver():
    service = selenium.webdriver.chrome.service.Service(var.CHROME_DRIVER_PATH)
    options = selenium.webdriver.chrome.options.Options()
    options.page_load_strategy = "normal"
    options.add_argument(var.CHROME_USER_DATA)
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver


def wait_login(driver, element_type, element_value):
    print("等待用户登录")
    wait_login_time = 120
    try:
        wait = WebDriverWait(driver, wait_login_time)
        wait.until(EC.presence_of_element_located((element_type, element_value)))
    except Exception as e:
        print(e)
    print("等待登录结束")
