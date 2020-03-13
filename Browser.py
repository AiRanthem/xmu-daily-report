from app import *
from app.refresh_cookie import *


def main():
    load_cookie()

    if browser.current_url != APP_URL:
        login()

    # print(browser.page_source)
    # browser.find_element_by_xpath("//div[@title='我的表单']").click()
