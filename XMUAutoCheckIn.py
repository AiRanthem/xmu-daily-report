import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.wait import WebDriverWait

import webdriver
from config import Config, get_configs
from job import click_given_xpath, click_mytable, dropdown_province, dropdown_city, dropdown_district, dropdown_confirm, \
    dropdown_inschool, dropdown_campus, dropdown_stay_in_school, dropdown_building, text_room, dropdown_indorm, \
    click_save
from log import logger
from utils import fail, send_mail, mask_stu_num, random_second, unix_timestamp, debug

# consts
VPN_LOGIN_URL = 'http://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/login'
VPN_CHECKIN_URL = 'http://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/app/214'
DIRECT_LOGIN_URL = 'http://xmuxg.xmu.edu.cn/login'
DIRECT_CHECKIN_URL = 'http://xmuxg.xmu.edu.cn/app/214'

class Checker:
    '''
    单账户打卡器
    '''
    def __init__(self, config: Config, use_vpn: bool):
        self.driver = webdriver.get_webdriver()
        self.use_vpn = use_vpn
        self.config = config

        self.masked_stu_num = mask_stu_num(self.config.username)
        self.login_url = VPN_LOGIN_URL if use_vpn else DIRECT_LOGIN_URL
        self.checkin_url = VPN_CHECKIN_URL if use_vpn else DIRECT_CHECKIN_URL
        self.children = []
    
        logger.info(f"账号【{self.masked_stu_num}】正在运行")
        logger.info("准备工作完成")
        self.driver.get(self.login_url)

    def login_vpn(self):
        logger.info("尝试使用VPN登录")
        login_tab = self.driver.find_element(By.CLASS_NAME, 'login-box')
        login_tab.find_element(By.XPATH, '//*[@id="user_name"]').send_keys(self.config.username)
        login_tab.find_element(By.XPATH, '//*[@id="form"]/div[3]/div/input').send_keys(self.config.password_vpn)
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element(By.XPATH, '//*[@id="login"]')).click()
        logger.info("VPN登录成功")

    def login_xmuxg(self):
        logger.info("进入XMUXG登录页面")
        click_given_xpath(self.driver, '//*[@id="loginLayout"]/div[3]/div[2]/div/button[3]', "统一身份认证")
        login_tab = self.driver.find_element(By.CLASS_NAME, 'auth_tab_content')
        login_tab.find_element(By.XPATH, '//*[@id="username"]').send_keys(self.config.username)
        login_tab.find_element(By.XPATH, '//*[@id="password"]').send_keys(self.config.password)
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element(By.XPATH, "//*[@id='casLoginForm']/p[4]/button")).click()
        logger.info("XMUXG登录成功")
    
    def checkin(self):
        self.driver.get(self.checkin_url)
        logger.info("进入打卡页面")
        click_given_xpath(self.driver, '//*[@id="mainM"]/div/div/div/div[1]/div[2]/div/div[3]/div[2]', "我的表单")
        job = click_mytable()
        job.add_child(
            dropdown_province("福建省"),
            dropdown_city("厦门市"),
            dropdown_district(self.config.district),
            dropdown_inschool(self.config.inschool).add_child(
                dropdown_campus(self.config.campus),
                dropdown_stay_in_school("住校内"),
                dropdown_indorm("住校内学生宿舍"),
                dropdown_building(self.config.building),
                text_room(self.config.room)
            ) if self.config.inschool.startswith("在校") else
            dropdown_inschool(self.config.inschool),
            dropdown_confirm(),
            click_save()
        )
        try:
            job.do()
        except NoAlertPresentException as e:
            fail("存在没有正确填写的部分，请向作者反馈", "打卡失败", self.config.email, e, shutdown=False, run_fail=True)
        except Exception as unknown_error:
            fail("未知错误", "打卡失败", self.config.email, unknown_error, shutdown=False, run_fail=True)
        else:
            logger.info("打卡成功")
            send_mail(f"账号【{self.masked_stu_num}】打卡成功", "打卡成功", self.config.email)
        finally:
            if not debug:
                self.driver.close()
    
    def workflow(self):
        if self.use_vpn:
            self.login_vpn()
        self.login_xmuxg()
        self.checkin()

def main():
    configs = get_configs()
    logger.info(f"已配置 {len(configs)} 个账号")
    for cfg in configs:
        success = False
        for i in range(1, 2 if debug else 11):
            logger.info(f'第{i}次尝试')
            try:
                checker = Checker(cfg, use_vpn=False)
                checker.workflow()
                success = True
                break
            except Exception as e:
                fail("直连打卡失败，尝试VPN", "打卡失败", "", e, shutdown=False)
                if debug:
                    break
                try:
                    checker = Checker(cfg, use_vpn=True)
                    checker.workflow()
                    success = True
                    break
                except Exception as e:
                    fail("尝试失败", "打卡失败", "", e, shutdown=False)
        if not success:
            fail(f"账号【{checker.masked_stu_num}】重试10次后依然打卡失败，请排查日志",
                 "打卡失败", cfg.email, shutdown=False)


if __name__ == '__main__':

    if not debug and time.localtime().tm_hour < 11:
        time_start: int = unix_timestamp()
        time_end: int = time_start + random_second()

        while True:
            if unix_timestamp() > time_end:
                break
    main()
