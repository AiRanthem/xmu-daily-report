import pickle

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from settings import *


class Browser:
    APP_URL = 'https://xmuxg.xmu.edu.cn/app/214'
    LOGIN_URL = 'http://xmuxg.xmu.edu.cn/xmu/app/214'
    chrome_option = Options()
    chrome_option.add_argument('--disable-extensions')
    chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path='driver/chromedriver.exe')

    def login(self):
        self.driver.get(self.LOGIN_URL)
        print('登陆过期，请登陆你的账号。')
        input('登录之后请在该窗口输入回车。')
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open('cookies.txt', 'wb'))

    def load_cookie(self):
        try:
            self.driver.get(self.APP_URL)
            cookies = pickle.load(open('cookies.txt', 'rb'))
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                self.driver.add_cookie(cookie)
            self.driver.get(self.APP_URL)
            print("cookie loaded")
        except Exception as e:
            print("ERROR:")
            print(e)
            print("---------")

    def wait_an_element_by_xpath(self, xpath):
        try:
            element = WebDriverWait(self.driver, LOAD_TIME).until(
                lambda driver: driver.find_element_by_xpath(xpath)
            )
            return element
        except Exception as e:
            print("连接超时。如要设置更长的等待时间，请打开 settings.py 文件，修改LOAD_TIME为更大值（单位：秒）")
            print("ERROR:")
            print(e)
            print("---------")
            exit(1)

    def fill(self):
        self.wait_an_element_by_xpath("//div[@title='我的表单']").click()
        if self.wait_an_element_by_xpath("//div[@data-name='select_1582538796361']//span[1]").text != '37.3以下 Below 37.3 degree celsius':
            self.wait_an_element_by_xpath("//div[@data-name='select_1582538796361']").click()
            self.wait_an_element_by_xpath("//label[@title='37.3以下 Below 37.3 degree celsius']").click()
        if self.wait_an_element_by_xpath("//div[@data-name='select_1582538846920']//span[1]").text != '否 No':
            self.wait_an_element_by_xpath("//div[@data-name='select_1582538846920']").click()
            self.wait_an_element_by_xpath("//label[@title='否 No']").click()
        if self.wait_an_element_by_xpath("//div[@data-name='select_1582538939790']//span[1]").text != '是 Yes':
            self.wait_an_element_by_xpath("//div[@data-name='select_1582538939790']").click()
            self.wait_an_element_by_xpath("//label[@title='是 Yes']").click()
        self.wait_an_element_by_xpath("//span[@class='form-save position-absolute']").click()

    def run(self):
        self.load_cookie()
        if self.driver.current_url != self.APP_URL:
            self.login()
        else:
            self.fill()

    # def __del__(self):
        # self.driver.close()
