import json
from app import browser,APP_URL


def login():
    print('Please Login Your Account.')
    input('Press ENTER when you have logged in.')

    dict_cookies = browser.get_cookies()
    json_cookies = json.dumps(dict_cookies)
    with open('cookies.txt', 'w') as f:
        f.write(json_cookies)


def load():
    browser.delete_all_cookies()
    with open('cookies.txt', 'r', encoding='utf8') as f:
        list_cookies = json.loads(f.read())
        print('%%%%%%%%%%%%%%%%%', list_cookies)
        for cookie in list_cookies:
            browser.add_cookie(cookie)
        browser.get(APP_URL)
        # 读取完cookie刷新页面
        browser.refresh()



