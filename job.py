import time
from typing import Callable

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from log import logger
from utils import fail

NULL = '请选择'

DROPDOWN_PROVINCE = ['//*[@id="address_1582538163410"]/div/div[1]/div/div', '//label[@title="福建省"][1]', '省']
DROPDOWN_CITY = ['//*[@id="address_1582538163410"]/div/div[2]/div/div', '//label[@title="厦门市"][1]', '市']
DROPDOWN_DIGEST = ['//*[@id="address_1582538163410"]/div/div[3]/div/div', '//label[@title="翔安区"][1]', '区']
DROWDOWN_CONFIRM = ["//*[@id='select_1582538939790']/div/div/span[1]", "/html/body/div[8]/ul/div/div[3]/li/label",
                    '本人承诺']

TEXT_ROOM = []  # TODO


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


class Job:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.children = []

    def should_do(self) -> bool:
        ...

    def do(self):
        if self.should_do():
            self._do()
            for child in self.children:
                child.do()

    def _do(self):
        ...

    def add_child(self, *jobs):
        self.children.extend(jobs)


class DropdownJob(Job):
    def __init__(self, driver: WebDriver, dropdown_xpath: str, target_xpath: str, comment: str):
        super().__init__(driver)
        self.dropdown_xpath = dropdown_xpath
        self.target_xpath = target_xpath
        self.comment = comment

    def should_do(self) -> bool:
        try:
            return NULL in get_text(self.driver, self.dropdown_xpath, self.comment)
        except Exception:
            return False

    def _do(self):
        select_dropdown(self.driver, self.dropdown_xpath, self.target_xpath, self.comment)
        time.sleep(1)


class TextJob(Job):
    def __init__(self, driver: WebDriver, xpath: str, text: str):
        super().__init__(driver)
        self.xpath = xpath
        self.text = text

    def should_do(self) -> bool:
        return super().should_do()  # TODO Tomorrow

    def _do(self):
        super()._do()  # TODO Tomorrow


def create_jobs():
    pass  # TODO Tomorrow
