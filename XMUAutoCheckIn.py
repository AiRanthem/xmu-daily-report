import calendar
import os
import random
import time
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import webdriver
from config import Config, make_configs
from job import click_given_xpath, click_mytable, dropdown_province, dropdown_city, dropdown_district, dropdown_confirm, \
    dropdown_inschool, dropdown_campus, dropdown_stay_in_school, dropdown_building, text_room, dropdown_indorm, \
    click_save, dropdown_covid_test, click_vpn_login_tab
from log import logger
from utils import fail, send_mail, debug, mask_username
from webdriver import close

# consts
VPN_LOGIN_URL = 'http://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/login'
VPN_CHECKIN_URL = 'http://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/app/214'
DIRECT_LOGIN_URL = 'http://xmuxg.xmu.edu.cn/login'
DIRECT_CHECKIN_URL = 'http://xmuxg.xmu.edu.cn/app/214'


def random_second() -> int:
    return random.randrange(start=0, stop=3600, step=1)


def unix_timestamp() -> int:
    gmt = time.gmtime()
    ts: int = calendar.timegm(gmt)
    return ts


def checkin(cfg: Config, use_vpn=True) -> None:
    login_url = VPN_LOGIN_URL if use_vpn else DIRECT_LOGIN_URL
    checkin_url = VPN_CHECKIN_URL if use_vpn else DIRECT_CHECKIN_URL
    webdriver.refresh()
    driver = webdriver.get()
    logger.info("准备工作完成")

    # 进入登录页面
    logger.info("正在请求登录页面")
    driver.get(login_url)

    if use_vpn:
        # 首先登陆WebVPN，根据上面url在WebVPN登陆成功后会自动跳转打卡登录界面
        click_vpn_login_tab().do()
        logintab = driver.find_element(By.CLASS_NAME, 'login-box')
        login = WebDriverWait(driver, 10).until(
            lambda x: x.find_element(By.ID, 'login'))
        user = logintab.find_element(By.ID, 'user_name')
        pwd = logintab.find_element(
            By.XPATH,
            "//*[@id='form']/div[3]/div/input")
        user.send_keys(cfg.username)
        pwd.send_keys(cfg.password_vpn)
        login.click()
        logger.info("VPN登录完成")
        time.sleep(1)

    # 选择统一身份认证登录跳转到真正的登录页面
    click_given_xpath(driver, '//*[@id="loginLayout"]/div[3]/div[2]/div/button[3]', "统一身份认证")

    # 查找页面元素，如果某些元素查找不到则返回错误
    try:
        logger.info("进入XMUXG登录页面")
        logintab = WebDriverWait(driver, 100).until(lambda x: x.find_element(By.CLASS_NAME, 'auth_tab_content'))
        # logintab = driver.find_element(By.CLASS_NAME, 'auth_tab_content')
        login = WebDriverWait(driver, 100).until(
            lambda x: x.find_element(By.XPATH, "//*[@id='casLoginForm']/p[4]/button"))
        user = logintab.find_element(By.ID, 'username')
        pwd = logintab.find_element(By.ID, 'password')
    except Exception as e:
        logger.error(e)
        raise RuntimeError("XMUXG登录失败", e)

    # 输入用户名密码并点击登录
    user.send_keys(cfg.username)
    pwd.send_keys(cfg.password)
    login.click()

    # 重新跳转到打卡页面
    driver.get(checkin_url)

    # 开始工作
    job = click_mytable()
    job.add_child(
        dropdown_province("福建省"),
        dropdown_city("厦门市"),
        dropdown_district(cfg.district),
        dropdown_inschool(cfg.inschool).add_child(
            dropdown_campus(cfg.campus),
            dropdown_stay_in_school("住校内"),
            dropdown_indorm("住校内学生宿舍"),
            dropdown_building(cfg.building),
            text_room(cfg.room)
        ) if cfg.inschool.startswith("在校") else
        dropdown_inschool(cfg.inschool),
        dropdown_covid_test(),
        dropdown_confirm(),
        click_save()
    )
    job.do()

    try:
        if not debug:
            driver.switch_to.alert.accept()
        else:
            driver.switch_to.alert.dismiss()
    except Exception as e:
        fail("存在没有正确填写的部分，请向作者反馈", "打卡失败", cfg.email, e, shutdown=False, run_fail=True)
    time.sleep(1)
    logger.info("打卡成功")
    send_mail(f"账号【{cfg.username}】打卡成功", "打卡成功", cfg.email)


CONFIG_KEYS = ["username", "password", "password_vpn", "email"]


def get_configs() -> List[Config]:
    if debug:
        with open("config.json", encoding="utf8") as f:
            return make_configs(f.read())
    else:
        return make_configs(os.getenv("CONFIG"))


def main():
    configs = get_configs()
    logger.info(f"已配置 {len(configs)} 个账号")
    for cfg in configs:
        logger.info(f"账号【{mask_username(cfg.username)}】正在运行")
        success = False
        for i in range(1, 2 if debug else 11):
            logger.info(f'第{i}次尝试')
            try:
                checkin(cfg, False)
                success = True
                break
            except Exception as e:
                fail("直连打卡失败，尝试VPN", "打卡失败", "", e, shutdown=False)
                if debug:
                    break
                try:
                    checkin(cfg, True)
                    success = True
                    break
                except Exception as e:
                    fail("尝试失败", "打卡失败", "", e, shutdown=False)
        if not success:
            fail(f"账号【{cfg.username}】重试10次后依然打卡失败，请排查日志",
                 "打卡失败", cfg.email, shutdown=False, send=True)


if __name__ == '__main__':

    if not debug and time.localtime().tm_hour < 11:
        time_start: int = unix_timestamp()
        time_end: int = time_start + random_second()

        while True:
            if unix_timestamp() > time_end:
                break
    try:
        main()
    finally:
        if not debug:
            close()
