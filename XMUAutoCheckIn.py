import json
import logging
import os
import time
import traceback
from typing import List

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

vpn_login_url = 'https://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/login'
vpn_checkin_url = 'https://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/app/214'
direct_login_url = 'https://xmuxg.xmu.edu.cn/login'
direct_checkin_url = 'https://xmuxg.xmu.edu.cn/app/214'
mail_server_url = 'http://120.77.39.85:8080/mail/daily_report'


def checkin(username, passwd, passwd_vpn, use_vpn=True):
    output = ""
    if debug:
        driver = webdriver.Edge()
    else:
        driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    login_url = vpn_login_url if use_vpn else direct_login_url
    checkin_url = vpn_checkin_url if use_vpn else direct_checkin_url

    logger.info("准备工作完成")

    # 进入登录页面
    driver.get(login_url)

    logger.info("请求页面")

    if use_vpn:
        # 首先登陆WebVPN，根据上面url在WebVPN登陆成功后会自动跳转打卡登录界面
        logintab = driver.find_element_by_class_name('login-box')
        login = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id('login'))
        user = logintab.find_element_by_id('user_name')
        pwd = logintab.find_element_by_xpath("//*[@id='form']/div[3]/div/input")
        user.send_keys(username)
        pwd.send_keys(passwd_vpn)
        login.click()
        time.sleep(1)

    # 选择统一身份认证登录跳转到真正的登录页面
    login = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//button[contains(text(),'统一身份认证')]"))
    login.click()

    # 查找页面元素，如果某些元素查找不到则返回错误
    while True:
        try:
            logger.info("进入登录页面")
            logintab = driver.find_element_by_class_name('auth_tab_content')
            login = WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//*[@id='casLoginForm']/p[4]/button"))
            user = logintab.find_element_by_id('username')
            pwd = logintab.find_element_by_id('password')
            logger.info("已定位到元素")
            break
        except Exception as e:
            logger.warning(e)
            logger.info("未定位到元素!")
            driver.close()
            return '打卡失败'

    # 输入用户名密码并点击登录
    user.send_keys(username)
    pwd.send_keys(passwd)
    login.click()

    # 重新跳转到打卡页面
    driver.get(checkin_url)

    # 获取 “我的表单”
    while True:
        try:
            form = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath(
                "//*[@id='mainM']/div/div/div/div[1]/div[2]/div/div[3]/div[2]"))
            form.click()
            logger.info("获取\"我的表单\"成功")
            break
        except Exception as e:
            logger.warning(e)
            traceback.print_exc()
            logger.info("获取\"我的表单\"失败")
            driver.close()
            return '打卡失败'

    # 查找框内文本
    while True:
        try:
            text = WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//*[@id='select_1582538939790']/div/div/span[1]").text)
            logger.info("查找框内文本成功")
            break
        except Exception as e:
            logger.warning(e)
            logger.info("查找框内文本失败")
            driver.close()
            return '打卡失败'

    # 定位填“是”的页面
    if text == '请选择':
        while True:
            try:
                yes = WebDriverWait(driver, 10).until(
                    lambda x: x.find_element_by_xpath("//*[@id='select_1582538939790']/div/div"))
                yes.click()
                logger.info("点击\"是\"成功")
                break
            except Exception as e:
                logger.warning(e)
                logger.info("点击\"是\"失败")
                driver.close()
                return '打卡失败'

        while True:
            try:
                yes = WebDriverWait(driver, 10).until(
                    lambda x: x.find_element_by_xpath("/html/body/div[8]/ul/div/div[3]/li/label"))
                yes.click()
                logger.info("确认\"是\"成功")
                break
            except Exception as e:
                logger.warning(e)
                logger.info("确认\"是\"失败")
                driver.close()
                return '打卡失败'

        # 点击保存按钮
        if not debug:
            save = WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//span[starts-with(text(),'保存')][1]"))
            save.click()

        time.sleep(1)
        # 保存确定
        try:
            if not debug:
                driver.switch_to.alert.accept()
            time.sleep(1)
            output = '打卡成功'
        except Exception as e:
            traceback.print_exc()
            output = '打卡失败'
    else:
        output = '今日已打卡'
    driver.close()
    return output


def send_mail(msg: str, title: str, to: str):
    if not debug:
        post = requests.post(mail_server_url, data=json.dumps({"title": title, "body": msg, "dest": to}))
        return post


CONFIG_KEYS = ["username", "password", "password_vpn", "email"]


def fail(msg: str, title: str, email: str = "", e: Exception = None, shutdown=True, run_fail=False):
    logger.warning(msg)
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
                    fail(f"第{i + 1}个配置的配置项{k}不是字符串，请加上双引号", "配置错误", run_fail=True)
        return configs
    except Exception as e:
        fail("配置读取失败，请检查配置", "配置错误", e=e, run_fail=True)


def main():
    # 10次重试
    configs = get_configs()
    for config in configs:
        success = False
        for i in range(1, 2 if debug else 11):
            logger.info(f'第{i}次尝试')
            try:
                output = checkin(
                    config["username"],
                    config["password"],
                    config["password_vpn"]
                )
                logger.info(output)
                if output != "打卡失败":
                    send_mail(f"账号【{config['username']}】{output}", "打卡成功", config["email"])
                    success = True
                    break
                logger.info("通过VPN打卡失败，尝试直接连接")
                output = checkin(
                    config["username"],
                    config["password"],
                    config["password_vpn"], False
                )
                if output != "打卡失败":
                    send_mail(f"账号【{config['username']}】{output}", "打卡成功", config["email"])
                    success = True
                    break
            except Exception as e:
                fail("尝试失败", "打卡失败", "", e, shutdown=False)
        if not success:
            fail(f"账号【{config['username']}】重试10次后依然打卡失败，请排查日志", "打卡失败", config["email"])


if __name__ == '__main__':
    main()
