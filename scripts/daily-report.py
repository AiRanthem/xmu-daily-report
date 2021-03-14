from playwright.sync_api import sync_playwright

from config import STUDENT_ID, STUDENT_PASSWD

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to https://xmuxg.xmu.edu.cn/xmu/login?app=214
    page.goto("https://xmuxg.xmu.edu.cn/xmu/login?app=214")

    # Click button:has-text("统一身份认证")
    page.click("button:has-text(\"统一身份认证\")")
    # assert page.url == "https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu"

    # Go to https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu
    page.goto("https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu")

    # Click [placeholder="用户名"]
    page.click("[placeholder=\"用户名\"]")

    # Fill [placeholder="用户名"]
    page.fill("[placeholder=\"用户名\"]", STUDENT_ID)

    # Click [placeholder="密码"]
    page.click("[placeholder=\"密码\"]")

    # Fill [placeholder="密码"]
    page.fill("[placeholder=\"密码\"]", STUDENT_PASSWD)

    # Click button:has-text("登录")
    page.click("button:has-text(\"登录\")")
    # assert page.url == "https://xmuxg.xmu.edu.cn/platform"

    # Click text=Daily Health Report 健康打卡
    with page.expect_popup() as popup_info:
        page.click("text=Daily Health Report 健康打卡")
    page1 = popup_info.value

    # Click text=我的表单
    page1.click("text=我的表单")

    # Click #select_1582538939790 >> text=请选择
    page1.click("#select_1582538939790 >> text=请选择")

    # Click text=是 Yes
    page1.click("text=是 Yes")

    # Click text=保存
    page1.once("dialog", lambda dialog: dialog.dismiss())
    page1.click("text=保存")

    # Close page
    page1.close()

    # Close page
    page.close()

    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)