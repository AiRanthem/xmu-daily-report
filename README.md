# xmu-daily-form
厦大Daily Health Report 健康打卡自动填写脚本

## 缘由
昨天刚接触到selenium，觉得有趣，写一个简单的项目练练手
## 状态：ver 0.1
版本0.1，该脚本属于可用状态，我今天的表格就是用这个它填的（逃）

由于这个系统登陆方式错综复杂（可能只有我是用第二个按钮登陆的），暂时没有做自动登录功能。第一次使用需要手动登录。

最后需要用户确认提交，暂时没有做自动确认，后续版本会补上自动确认和自动登录功能。
## How to Use
```bash
git clone git@github.com:AiRanthem/xmu-daily-form.git
cd xmu-daily-form/tools
pip install -r requirements.txt
cd ..
# download your chromedriver executable to ./driver
python main.py
```
## 使用方法（手把手版）
### 注意，该安装文档提供的资源仅针对windows用户，mac用户请自行下载对应软件包。（如果你用Linux的话还要看安装方法？）
1. 点击右上角`Clone or download`下载压缩包并解压
2. 打开[tools](./tools)文件夹，安装python3.7
3. 双击[install-requirements.py](tools/install-requirements.py)，按照提示安装依赖
    >如果没有打开命令行而是打开了文本编辑器，请右键点击它选择 打开方式->python

4. 打开chrome，在地址栏输入`chrome://version`，查看第一行的版本，第一位就是版本号
    >比如我的chrome版本是80.0.3987.132，版本号就是80

5. 如果你的版本号不是80，请访问[这里](https://sites.google.com/a/chromium.org/chromedriver/downloads)下载对应版本的chromedriver，替换掉[driver](./driver)文件夹里的`chromedriver.exe`(没有后缀名的那个是Linux版，开发用的，可以删除)
5. 回到[xmu-daily-form](.)中，和第三步一样运行[how_to_use.py](./how_to_use.py)即可。
## update 0.1
1. 完成自动登录校验
2. 完成自动表格填写
3. todo：自动提交和手动提交的切换
4. todo：自动登录

## log
+ 2020/3/13：施工开始
+ 2020/3/13: 完成0.1版本
