import time
from typing import Callable

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import webdriver
from log import logger
from utils import fail

NULL = '请选择'


def must_operate_element(driver: WebDriver, by: str, target: str, do: Callable, comment: str):
    try:
        target = WebDriverWait(driver, 100).until(
            lambda x: x.find_element(by, target))
        result = do(target)
        logger.info(f"{comment} 成功")
        return result
    except Exception as e:
        fail(f"{comment} 失败", "", "", e, False, True)


def xpath_exists(driver: WebDriver, xpath: str, comment: str) -> bool:
    try:
        must_operate_element(driver, By.XPATH, xpath, lambda x: x, f"确认 {comment} 存在")
        return True
    except:
        return False


def click_given_xpath(driver: WebDriver, xpath: str, comment: str):
    must_operate_element(driver, By.XPATH, xpath, lambda x: x.click(), "点击 " + comment)


def get_text(driver: WebDriver, xpath: str, comment: str) -> str:
    return must_operate_element(driver, By.XPATH, xpath, lambda x: x.text, f"获取 {comment} 文本")


def set_text(driver: WebDriver, xpath: str, text: str, comment: str):
    must_operate_element(driver, By.XPATH, xpath, lambda x: x.send_keys(text), f"填写 {comment} 文本")


def select_dropdown(driver: WebDriver, dropdown_xpath: str, target_xpath: str, comment: str):
    click_given_xpath(driver, dropdown_xpath, f"{comment} 下拉框")
    time.sleep(1)
    click_given_xpath(driver, target_xpath, f"{comment} 选项")


class Job:
    def __init__(self, driver: WebDriver, comment: str):
        self.driver = driver
        self.comment = comment
        self.children = []

    def should_do(self) -> bool:
        ...

    def do(self):
        if self.should_do():
            logger.info(f"执行任务 {self.comment}")
            self._do()
            time.sleep(1)
            for child in self.children:
                child.do()
        else:
            logger.info(f"跳过任务 {self.comment}")

    def _do(self):
        ...

    def add_child(self, *jobs):
        self.children.extend(jobs)
        return self


class DropdownJob(Job):
    def __init__(self, driver: WebDriver, dropdown_xpath: str, target_xpath: str, comment: str):
        super().__init__(driver, comment)
        self.dropdown_xpath = dropdown_xpath
        self.target_xpath = target_xpath

    def should_do(self) -> bool:
        try:
            return NULL in get_text(self.driver, self.dropdown_xpath, self.comment)
        except Exception:
            return False

    def _do(self):
        select_dropdown(self.driver, self.dropdown_xpath, self.target_xpath, self.comment)
        time.sleep(1)


class TextJob(Job):
    def __init__(self, driver: WebDriver, xpath: str, text: str, comment: str):
        super().__init__(driver, comment)
        self.xpath = xpath
        self.text = text

    def should_do(self) -> bool:
        try:
            return xpath_exists(self.driver, self.xpath, self.comment)
        except Exception:
            return False

    def _do(self):
        set_text(self.driver, self.xpath, self.text, self.comment)


class ClickJob(Job):
    def __init__(self, driver: WebDriver, xpath: str, comment: str):
        super(ClickJob, self).__init__(driver, comment)
        self.xpath = xpath

    def should_do(self) -> bool:
        return xpath_exists(self.driver, self.xpath, self.comment)

    def _do(self):
        click_given_xpath(self.driver, self.xpath, self.comment)


def click_mytable() -> Job:
    return ClickJob(webdriver.get(), '//*[@id="mainM"]/div/div/div/div[1]/div[2]/div/div[3]/div[2]', "我的表单")


def dropdown_covid_test() -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="datetime_1660308822369"]/div',
                       '//div[@class="datepicker-dateRange"]/span[@class="datepicker-dateRange-item-active"]',
                       "核酸时间")


def dropdown_province(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="address_1582538163410"]/div/div[1]/div/div',
                       f'//label[@title="{data}"][1]', '省')


def dropdown_city(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="address_1582538163410"]/div/div[2]/div/div',
                       f'//label[@title="{data}"][1]',
                       '市')


def dropdown_district(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="address_1582538163410"]/div/div[3]/div/div',
                       f'//label[@title="{data}"][1]',
                       '区')


def dropdown_confirm() -> Job:
    return DropdownJob(webdriver.get(), "//*[@id='select_1582538939790']/div/div/span[1]",
                       "/html/body/div[8]/ul/div/div["
                       "3]/li/label", '本人承诺')


def dropdown_inschool(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="select_1611108284522"]/div/div', f'//label[@title="{data}"][1]',
                       "是否在校")


def dropdown_campus(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="select_1582538643070"]/div/div/span[1]',
                       f'//label[starts-with(@title, "{data}")][1]',
                       "校区")


def dropdown_stay_in_school(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="select_1611110401193"]/div/div',
                       f'//label[starts-with(@title, "{data}")][1]',
                       "是否住在校内")


def dropdown_indorm(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="select_1611108377024"]/div/div',
                       f'//label[starts-with(@title, "{data}")][1]',
                       "是否住在校内学生宿舍")


def dropdown_building(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="select_1611108445364"]/div/div',
                       f'//label[starts-with(@title, "{data}")][1]',
                       "楼栋")


def text_room(data: str) -> Job:
    return TextJob(webdriver.get(), '//*[@id="input_1611108449736"]/input', data, "房间号")


def drowdown_live_in_xiamen(data: str) -> Job:
    return DropdownJob(webdriver.get(), '//*[@id="radio_1611108503484"]/div/div',
                       f'//label[starts-with(@title, "{data}")][1]',
                       "是否家在厦门")


def text_address(data: str) -> Job:
    return TextJob(webdriver.get(), '//*[@id="input_1611108489669"]/input', data, "校外住址")


def click_save() -> Job:
    return ClickJob(webdriver.get(), "//span[starts-with(text(),'保存')][1]", "保存")


def click_vpn_login_tab() -> Job:
    return ClickJob(webdriver.get(), '//*[@id="local"]', "VPN选择账号登录")
