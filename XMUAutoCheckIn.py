from selenium import webdriver
import os
import time
import logging

# from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--headless')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Login_URL = 'https://xmuxg.xmu.edu.cn/login'
Checkin_URL = 'https://xmuxg.xmu.edu.cn/app/214'

# VARIABLE NAME
USERNAME = "username"
PASSWD = "passwd"


def checkin(a, b):
    driver = webdriver.Chrome()
    run = True
    now = time.time()
    while run:
        try:
            logger.info("进入登录页面")
            driver.get(Login_URL)
            break
        except:
            logger.info(url, "获取失败，重试中")
            if (time.time() - now) > 10:
                run = False
                return '网页登陆失败'

    driver.maximize_window()
    logintab = driver.find_element_by_class_name('login-tab')
    login = driver.find_element_by_xpath("//*[@class='buttonBox']/button[2]")
    login.click()

    # 输入用户名密码
    time.sleep(2)
    c = driver.find_element_by_id('username')
    d = driver.find_element_by_id('password')
    c.send_keys(a)
    d.send_keys(b)

    # 点击登录
    login = driver.find_element_by_xpath("//*[@id='casLoginForm']/p[5]")
    login.click()

    # 重新跳转到打卡页面
    driver.get(Checkin_URL)

    now = time.time()
    while True:
        try:
            time.sleep(3)
            form = driver.find_element_by_xpath("//*[@class='gm-scroll-view']/div[2]")
            form.click()
            break
        except:
            time.sleep(1)
            logger.info("获取\"我的表单\"失败，重试中")
            if (time.time() - now) > 10:
                run = False
                return '获取\"我的表单\"失败'

    now = time.time()
    while True:
        try:
            time.sleep(3)
            text = driver.find_element_by_xpath("//*[@id='select_1582538939790']/div[1]/div[1]/span[1]").text
            break
        except:
            time.sleep(1)
            logger.info("查找框内文本失败，重试中")
            if (time.time() - now) > 10:
                run = False
                return '查找框内文本失败'

    if text == '请选择':
        now = time.time()
        while True:
            try:
                # 定位填“是”的页面
                yes = driver.find_element_by_xpath("//*[@id='select_1582538939790']/div[1]/div[1]")
                yes.click()
                break
            except:
                time.sleep(1)
                logger.info("点击\"是\"失败，重试中")
                if (time.time() - now) > 10:
                    run = False
                    return '点击\"是\"失败'

        now = time.time()
        while True:
            try:
                yes = driver.find_element_by_xpath("//*[@class='v-select-cover']/ul[1]/div[1]")
                yes.click()
                break
            except:
                time.sleep(1)
                logger.info("确认\"是\"失败，重试中")
                if (time.time() - now) > 10:
                    return '确认\"是\"失败'
        save = driver.find_element_by_xpath("//*[@class='preview-container']/div[1]/div[1]/span[1]/span[1]")
        save.click()

        time.sleep(1)
        # 保存确定
        driver.switch_to_alert().accept()
        time.sleep(3)
        output = '打卡成功'
    elif text == '是 Yes':
        output = '已打卡'
    else:
        output = '打卡失败！！！'
    driver.close()
    return output


def main():
    a = os.environ['USERNAME'].split('#')
    b = os.environ['PASSWD'].split('#')
    logger.info(checkin(a, b))

if __name__ == '__main__':
    main()
