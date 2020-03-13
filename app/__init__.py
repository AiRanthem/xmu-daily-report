from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_option = Options()
chrome_option.add_argument('--disable-extensions')
chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# browser = webdriver.Chrome(executable_path='driver/chromedriver', options=chrome_option)
browser = webdriver.Chrome(executable_path='driver/chromedriver')

LOGIN_URL = 'http://xmuxg.xmu.edu.cn/xmu/app/214'
APP_URL = 'https://xmuxg.xmu.edu.cn/app/214'
