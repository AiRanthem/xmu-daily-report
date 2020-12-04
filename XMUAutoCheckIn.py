from selenium import webdriver
import os
import time
import logging

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
# 添加UA
# chrome_options.add_argument('user-agent="MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"')
# 指定浏览器分辨率
# chrome_options.add_argument('window-size=1920x3000') 
# 谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--disable-gpu') 
 # 隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('--hide-scrollbars')
# 不加载图片, 提升速度
chrome_options.add_argument('blink-settings=imagesEnabled=false') 
# 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
chrome_options.add_argument('--headless') 
# 以最高权限运行
chrome_options.add_argument('--no-sandbox')
# 禁用浏览器弹窗
prefs = {  
    'profile.default_content_setting_values' :  {  
        'notifications' : 2  
     }  
}  
chrome_options.add_experimental_option('prefs',prefs)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Login_URL = 'https://xmuxg.xmu.edu.cn/login'
# Login_URL = 'https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu'
Checkin_URL = 'https://xmuxg.xmu.edu.cn/app/214'


def checkin(username, passwd):
    driver = webdriver.Chrome(chrome_options=chrome_options)
    
    driver.get(Login_URL)
    driver.maximize_window()

    # 这里直接定位到登录页面了，所以下面步骤不需要
    logintab = driver.find_element_by_class_name('login-tab')
    login = driver.find_element_by_xpath("//*[@class='buttonBox']/button[2]")
    login.click()

    # 输入用户名密码
    time.sleep(1)
    logger.info("进入登录页面")
    a = driver.find_element_by_id('username')
    b = driver.find_element_by_id('password')
    a.send_keys(username)
    b.send_keys(passwd)

    # 点击登录，相当玄学，有可能提示找不到该元素，那时候就手动打卡吧
    run = True
    now = time.time()
    while run:
        try:
            time.sleep(1)
            login = driver.find_element_by_xpath("//*[@id='casLoginForm']/p[5]")
            login.click()
            logger.info("已定位到元素")
            break
        except:
            logger.info("还未定位到元素!")
            if (time.time() - now) > 10:
                run = False
                return '运气不好，遇上了玄学问题'

    # 重新跳转到打卡页面
    driver.get(Checkin_URL)
    
    sleep(2)
    now = time.time()
    while True:
        try:
            form = driver.find_element_by_xpath("//*[@class='gm-scroll-view']/div[2]")
            form.click()
            break
        except:
            time.sleep(1)
            logger.info("获取\"我的表单\"失败，重试中")
            if (time.time() - now) > 10:
                run = False
                return '获取\"我的表单\"失败'

    sleep(2)
    now = time.time()
    while True:
        try:
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


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendMail(from_addr, mail_pwd, to_addr, smtp_server, output):
    msg = MIMEText(output, 'plain', 'utf-8')
    msg['From'] = _format_addr('XMU每日打卡 <%s>' % from_addr)
    msg['To'] = _format_addr('你可真是怠惰呢 <%s>' % to_addr)
    msg['Subject'] = Header('每日打卡结果反馈', 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(from_addr, mail_pwd)
    logger.info("邮箱登录成功")
    server.sendmail(from_addr, [to_addr], msg.as_string())
    logger.info("邮件发送成功")
    server.quit()

def main():
    # XMU统一身份认证用户名密码
    username = os.environ['USERNAME'].split('#')
    passwd = os.environ['PASSWD'].split('#')

    # 邮件设置信息，由于从secrets获取到的是list，这里进一步转string
    from_addr = ""
    from_addr = from_addr.join(os.environ['FROM_ADDR'].split('#'))
    mail_pwd = ""
    mail_pwd = mail_pwd.join(os.environ['MAIL_PWD'].split('#'))
    to_addr = ""
    to_addr = to_addr.join(os.environ['TO_ADDR'].split('#'))
    smtp_server = ""
    smtp_server = smtp_server.join(os.environ['SMTP_SERVER'].split('#'))

    output = checkin(username, passwd)
    logger.info(output)
    sendMail(from_addr, mail_pwd, to_addr, smtp_server, output)


if __name__ == '__main__':
    main()
