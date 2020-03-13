from app import *
from app.refresh_cookie import *


def main():
    try:
        browser.delete_all_cookies()
        browser.get(LOGIN_URL)
        with open('cookies.txt', 'r', encoding='utf8') as f:
            list_cookies = json.loads(f.read())
            print('%%%%%%%%%%%%%%%%%', list_cookies)
            for cookie in list_cookies:
                browser.add_cookie(cookie)
        browser.get(APP_URL)
    except:
        browser.get(APP_URL)

    # if browser.current_url != APP_URL:
    #     login()

    print(browser.page_source)
    # browser.find_element_by_xpath("//div[@title='我的表单']").click()
