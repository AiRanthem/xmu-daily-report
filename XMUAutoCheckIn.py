from selenium import webdriver
import time

# from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--headless')

logfile = 'XMUAutoCheckIn.log'
userfile = 'users'
url = 'https://xmuxg.xmu.edu.cn/login'
# url = 'https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu'
# chromedriver = '/usr/bin/chromedriver'


def checkin(a, b):
    driver = webdriver.Chrome()
    run = True
    now = time.time()
    while run:
        try:
            driver.get(url)
            break
        except:
            print(url, "获取失败，重试中")
            if (time.time() - now) > 10:
                run = False
                return '网页登陆失败'

    driver.maximize_window()
    logintab = driver.find_element_by_class_name('login-tab')
    login = driver.find_element_by_xpath("//*[@class='buttonBox']/button[2]")
    login.click()

    time.sleep(0.2)
    c = driver.find_element_by_id('username')
    d = driver.find_element_by_id('password')
    c.send_keys(a)
    d.send_keys(b)

    # 登录
#     while 1:
#         start = time.clock()
#         try:
#             driver.find_element_by_xpath("//*[@id='casLoginForm']/p[5]").click()
#             print("已定位到元素")
#             end=time.clock()
#             break
#         except:
#             print("还未定位到元素!")
    login = driver.find_element_by_xpath("//*[@id='casLoginForm']/p[5]")
    login.click()
    

    driver.get('https://xmuxg.xmu.edu.cn/app/214')

    now = time.time()
    while True:
        try:
            time.sleep(3)
            form = driver.find_element_by_xpath("//*[@class='gm-scroll-view']/div[2]")
            form.click()
            break
        except:
            time.sleep(1)
            print("获取\"我的表单\"失败，重试中")
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
            print("查找框内文本失败，重试中")
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
                print("点击\"是\"失败，重试中")
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
                print("确认\"是\"失败，重试中")
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


with open(userfile, 'r') as users:
    lines = users.readlines()
    for line in lines:
        line = line.strip()
        if line[0] == '#':
            continue
        a, b = line.split(' ')
        output = checkin(a, b)

        cur_time = (time.strftime('%Y_%m_%d_%r', time.localtime(time.time())))
        with open(logfile, 'a') as log:
            log.write(cur_time + ' ' + a + ' ' + output + '\n')

        print('End\n')
