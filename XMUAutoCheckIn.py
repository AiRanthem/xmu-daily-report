import logging
import os
import smtplib
import time
import traceback
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import requests
from selenium import webdriver
# chrome可选配置，部分功能经检测影响脚本运行所以关掉
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

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
# chrome_options.add_argument('--headless')
# 以最高权限运行
# chrome_options.add_argument('--no-sandbox')
# 禁用浏览器弹窗
# prefs = {
#     'profile.default_content_setting_values' :  {
#         'notifications' : 2
#      }
# }
# chrome_options.add_experimental_option('prefs',prefs)

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 登录url和打卡url
# Login_URL = 'https://xmuxg.xmu.edu.cn/login'
# Checkin_URL = 'https://xmuxg.xmu.edu.cn/app/214'
Login_URL = 'https://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/login'
Checkin_URL = 'https://webvpn.xmu.edu.cn/https/77726476706e69737468656265737421e8fa5484207e705d6b468ca88d1b203b/app/214'


def checkin():
    # XMU统一身份认证用户名密码(passwd_vpn是WebVPN登录密码，可能不一样，因此多设一个位置，若一样，secret里填写一样即可）
    username = os.environ['USERNAME'].split('#')
    passwd = os.environ['PASSWD'].split('#')
    passwd_vpn = os.environ['PASSWD'].split('#')

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    logger.info("准备工作完成")

    # 进入登录页面
    driver.get(Login_URL)

    logger.info("请求页面")

    # 首先登陆WebVPN，根据上面url在WebVPN登陆成功后会自动跳转打卡登录界面
    logintab = driver.find_element_by_class_name('login-box')
    login = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id('login'))
    user = logintab.find_element_by_id('user_name')
    pwd = logintab.find_element_by_xpath("//*[@id='form']/div[3]/div/input")
    user.send_keys(username)
    pwd.send_keys(passwd_vpn)
    login.click()
    time.sleep(1)

    # 选择统一身份认证登录跳转到真正的登录页面
    driver.get(Login_URL)
    login = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//button[contains(text(),'统一身份认证')]"))
    # login = driver.find_element_by_xpath("//button[contains(text(),'统一身份认证')]")
    login.click()

    # 查找页面元素，如果某些元素查找不到则返回错误
    while True:
        try:
            logger.info("进入登录页面")
            logintab = driver.find_element_by_class_name('auth_tab_content')
            login = WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//*[@id='casLoginForm']/p[4]/button"))
            user = logintab.find_element_by_id('username')
            pwd = logintab.find_element_by_id('password')
            logger.info("已定位到元素")
            break
        except:
            logger.info("未定位到元素!")
            driver.close()
            return '打卡失败'

    # 输入用户名密码并点击登录
    user.send_keys(username)
    pwd.send_keys(passwd)
    login.click()

    # 重新跳转到打卡页面
    driver.get(Checkin_URL)

    # 获取 “我的表单”
    while True:
        try:
            form = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath(
                "//*[@id='mainM']/div/div/div/div[1]/div[2]/div/div[3]/div[2]"))
            form.click()
            logger.info("获取\"我的表单\"成功")
            break
        except:
            logger.info("获取\"我的表单\"失败")
            driver.close()
            return '打卡失败'

    # 查找框内文本
    while True:
        try:
            text = WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//*[@id='select_1582538939790']/div/div/span[1]").text)
            logger.info("查找框内文本成功")
            break
        except:
            logger.info("查找框内文本失败")
            driver.close()
            return '打卡失败'

    # 定位填“是”的页面
    if text == '请选择':
        while True:
            try:
                yes = WebDriverWait(driver, 10).until(
                    lambda x: x.find_element_by_xpath("//*[@id='select_1582538939790']/div/div"))
                yes.click()
                logger.info("点击\"是\"成功")
                break
            except:
                logger.info("点击\"是\"失败")
                driver.close()
                return '打卡失败'

        now = time.time()
        while True:
            try:
                yes = WebDriverWait(driver, 10).until(
                    lambda x: x.find_element_by_xpath("/html/body/div[8]/ul/div/div[3]/li/label"))
                yes.click()
                logger.info("确认\"是\"成功")
                break
            except:
                logger.info("确认\"是\"失败")
                driver.close()
                return '打卡失败'

        # 点击保存按钮
        save = WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_xpath("//span[starts-with(text(),'保存')][1]"))
        save.click()

        time.sleep(1)
        # 保存确定
        driver.switch_to.alert().accept()
        time.sleep(3)
        output = '打卡成功'
    elif text == '是 Yes':
        output = '已打卡'
    driver.close()
    return output


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


# 通过邮件推送打卡情况
def sendMail(output):
    # 邮件设置信息，由于从secrets获取到的是list，这里进一步转string
    from_addr = ""
    from_addr = from_addr.join(os.environ['FROM_ADDR'].split('#'))
    mail_pwd = ""
    mail_pwd = mail_pwd.join(os.environ['MAIL_PWD'].split('#'))
    to_addr = ""
    to_addr = to_addr.join(os.environ['TO_ADDR'].split('#'))
    smtp_server = ""
    smtp_server = smtp_server.join(os.environ['SMTP_SERVER'].split('#'))

    msg = MIMEText(output, 'plain', 'utf-8')
    msg['From'] = _format_addr('XMU每日打卡 <%s>' % from_addr)
    msg['To'] = _format_addr('你可真是怠惰呢 <%s>' % to_addr)
    msg['Subject'] = Header(f'打卡结果 {output[:6]}', 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(from_addr, mail_pwd)
    logger.info("邮箱登录成功")
    server.sendmail(from_addr, [to_addr], msg.as_string())
    logger.info("邮件发送成功")
    server.quit()


# 通过Server酱推送打卡情况
def serverChan(output):
    # server酱的key
    server_key = ""
    server_key = server_key.join(os.environ['SERVER_KEY'].split('#'))

    api = "https://sc.ftqq.com/%s.send" % (server_key)
    title = u"XMU每日打卡"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    msg = {
        "text": title,
        "desp": output
    }
    requests.post(api, data=msg, headers=headers)


def main():

    # 10次重试
    for i in range(1, 11):
        logger.info(f'第{i}次尝试')
        try:
            output = checkin()
            logger.info(output)
            if output == '打卡失败':
                continue
            else:
                # 开启邮件推送
                sendMail(output)

                # 开启Server酱推送
                # serverChan(output)

                exit(0)
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
    sendMail('重试10次后依然打卡失败，请排查日志')


if __name__ == '__main__':
    main()
