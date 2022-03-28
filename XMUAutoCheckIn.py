import io
import json
import logging
import os
import time
import traceback
from typing import List, Callable

import random
import calendar

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

debug = os.getenv("ENV") == "debug"

chrome_options = Options()
# 谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--disable-gpu')
# 隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('--hide-scrollbars')
# 不加载图片, 提升速度
chrome_options.add_argument('blink-settings=imagesEnabled=false')

# 日志配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# consts
VPN_LOGIN_URL = 'http://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/login'
VPN_CHECKIN_URL = 'http://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/app/214'
DIRECT_LOGIN_URL = 'http://xmuxg.xmu.edu.cn/login'
DIRECT_CHECKIN_URL = 'http://xmuxg.xmu.edu.cn/app/214'
MAIL_SERVER_URL = 'http://120.77.39.85:8080/mail/daily_report'

NULL = '请选择'


def random_second() -> int:
    return random.randrange(start=0, stop=3600, step=1)


def unix_timestamp() -> int:
    gmt = time.gmtime()
    ts: int = calendar.timegm(gmt)
    return ts


def must_operate_element_by_xpath(driver: WebDriver, xpath: str, do: Callable, comment: str):
    try:
        target = WebDriverWait(driver, 10).until(
            lambda x: x.find_element(By.XPATH, xpath))
        result = do(target)
        logger.info(f"{comment} 成功")
        return result
    except Exception as e:
        driver.close()
        fail(f"{comment} 失败", "", "", e, False, True)


def click_given_xpath(driver: WebDriver, xpath: str, comment: str):
    must_operate_element_by_xpath(driver, xpath, lambda x: x.click(), "点击 " + comment)


def get_text(driver: WebDriver, xpath: str, comment: str) -> str:
    return must_operate_element_by_xpath(driver, xpath, lambda x: x.text, f"获取 {comment} 文本")


def select_dropdown(driver: WebDriver, dropdown_xpath: str, target_xpath: str, comment: str):
    click_given_xpath(driver, dropdown_xpath, f"{comment} 下拉框")
    time.sleep(1)
    click_given_xpath(driver, target_xpath, f"{comment} 选项")


def checkin(username, passwd, passwd_vpn, email, use_vpn=True) -> None:
    if debug:
        driver = webdriver.Edge()
    else:
        driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    login_url = VPN_LOGIN_URL if use_vpn else DIRECT_LOGIN_URL
    checkin_url = VPN_CHECKIN_URL if use_vpn else DIRECT_CHECKIN_URL
    logger.info("准备工作完成")

    # 进入登录页面
    logger.info("正在请求登录页面")
    driver.get(login_url)

    if use_vpn:
        # 首先登陆WebVPN，根据上面url在WebVPN登陆成功后会自动跳转打卡登录界面
        logintab = driver.find_element(By.CLASS_NAME, 'login-box')
        login = WebDriverWait(driver, 10).until(
            lambda x: x.find_element(By.ID, 'login'))
        user = logintab.find_element(By.ID, 'user_name')
        pwd = logintab.find_element(
            By.XPATH,
            "//*[@id='form']/div[3]/div/input")
        user.send_keys(username)
        pwd.send_keys(passwd_vpn)
        login.click()
        logger.info("VPN登录完成")
        time.sleep(1)

    # 选择统一身份认证登录跳转到真正的登录页面
    click_given_xpath(driver, '//*[@id="loginLayout"]/div[3]/div[2]/div/button[3]', "统一身份认证")

    # 查找页面元素，如果某些元素查找不到则返回错误
    try:
        logger.info("进入XMUXG登录页面")
        logintab = driver.find_element(By.CLASS_NAME, 'auth_tab_content')
        login = WebDriverWait(driver, 10).until(
            lambda x: x.find_element(By.XPATH, "//*[@id='casLoginForm']/p[4]/button"))
        user = logintab.find_element(By.ID, 'username')
        pwd = logintab.find_element(By.ID, 'password')
    except Exception as e:
        logger.error(e)
        driver.close()
        raise RuntimeError("XMUXG登录失败", e)

    # 输入用户名密码并点击登录
    user.send_keys(username)
    pwd.send_keys(passwd)
    login.click()

    # 重新跳转到打卡页面
    driver.get(checkin_url)

    # 开始工作
    click_given_xpath(driver, '//*[@id="mainM"]/div/div/div/div[1]/div[2]/div/div[3]/div[2]', "我的表单")

    """
    开发者注意：如果发现新的下拉框可能需要填写，请在为dropdowns列表按照
    下拉框XPATH     选项XPATH    下拉框描述
    的顺序添加项并提交PR
    """
    dropdowns = [
        ['//*[@id="address_1582538163410"]/div/div[1]/div/div', '//label[@title="福建省"][1]', '省'],
        ['//*[@id="address_1582538163410"]/div/div[2]/div/div', '//label[@title="厦门市"][1]', '市'],
        ['//*[@id="address_1582538163410"]/div/div[3]/div/div', '//label[@title="思明区"][1]', '区'],
        ["//*[@id='select_1582538939790']/div/div/span[1]", "/html/body/div[8]/ul/div/div[3]/li/label", '本人承诺']
    ]
    for dropdown in dropdowns:
        if NULL in get_text(driver, dropdown[0], dropdown[2]):
            select_dropdown(driver, *dropdown)
            time.sleep(1)
        else:
            logger.info(f'{dropdown[2]} 已填写')

    # 点击保存按钮
    click_given_xpath(driver, "//span[starts-with(text(),'保存')][1]", "保存")

    time.sleep(1)
    # 保存确定
    if not debug:
        driver.switch_to.alert.accept()
    else:
        driver.switch_to.alert.dismiss()
    time.sleep(1)
    driver.close()
    logger.info("打卡成功")
    send_mail(f"账号【{username}】打卡成功", "打卡成功", email)


def send_mail(msg: str, title: str, to: str):
    msg += '\n\n【运行日志】\n' + log_stream.getvalue()
    if not debug:
        post = requests.post(MAIL_SERVER_URL, data=json.dumps(
            {"title": title, "body": msg, "dest": to}))
        return post
    else:
        logger.info(msg)


CONFIG_KEYS = ["username", "password", "password_vpn", "email"]


def fail(msg: str, title: str, email: str = "", e: Exception = None, shutdown=True, run_fail=False):
    logger.error(msg)
    if e is not None:
        logger.error(e)
        traceback.print_exc()
    if run_fail:
        raise RuntimeError(msg)
    if shutdown:
        send_mail(msg, title, email)
        exit(0)


def get_configs() -> List[dict]:
    try:
        if debug:
            with open("config.json") as f:
                configs = json.load(f)["config"]
        else:
            configs = json.loads(os.getenv("CONFIG"))["config"]
        for i, config in enumerate(configs):
            for k in CONFIG_KEYS:
                if k not in config.keys():
                    fail(f"第{i + 1}个配置缺少配置项{k}", "配置错误", run_fail=True)
                if not isinstance(config[k], str):
                    fail(f"第{i + 1}个配置的配置项{k}不是字符串，请加上双引号",
                         "配置错误", run_fail=True)
        return configs
    except Exception as e:
        fail("配置读取失败，请检查配置", "配置错误", e=e, run_fail=True)


def main():
    configs = get_configs()
    logger.info(f"已配置 {len(configs)} 个账号")
    for config in configs:
        logger.info(f"账号【{config['username']}】正在运行")
        success = False
        for i in range(1, 2 if debug else 11):
            logger.info(f'第{i}次尝试')
            try:
                checkin(
                    config["username"],
                    config["password"],
                    config["password_vpn"],
                    config['email'], False
                )
                success = True
                break
            except RuntimeError:
                logger.info("直连打卡失败，尝试VPN")
                try:
                    checkin(
                        config["username"],
                        config["password"],
                        config["password_vpn"],
                        config['email'], True
                    )
                    success = True
                    break
                except Exception as e:
                    fail("尝试失败", "打卡失败", "", e, shutdown=False)
        if not success:
            fail(f"账号【{config['username']}】重试10次后依然打卡失败，请排查日志",
                 "打卡失败", config["email"])


if __name__ == '__main__':

    if not debug and time.localtime().tm_hour < 11:
        time_start: int = unix_timestamp()
        time_end: int = time_start + random_second()

        while True:
            if unix_timestamp() > time_end:
                break

    main()
