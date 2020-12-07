# XMU每日打卡

此项目托管于``Github Action``进行XMU的每日健康打卡，仅供交流学习使用。

## Action执行打卡

1. Fork本项目；
2. 在`Settings->Secrets`下新建两个``Secrets`：
   + `USERNAME`：你的XMU用户名
   + `PASSWD`：统一身份认证的密码
3. 在`Action`下允许`workflow`运行；
4. 提交一次修改触发`workflow`，比如可以修改一下`README.md`。

## 邮件推送

出于某些考量，本项目添加了邮件推送服务。只需要另外再添加四个`Secrets`：

+ `FROM_ADDR`：发件人邮箱；
+ `MAIL_PASSWD`：邮箱授权密码，不是登录密码，需要注意；
+ `TO_ADDR`：收件人邮箱；
+ `SMTP_SERVER`：发件人邮箱的smtp服务器地址。

若不想开启邮件推送，请将`.github/workflows/XMU_Auto_Check_In.yml`中`env`下上述四条，以及`XMUAutoCheckIn.py`的第212行注释掉。

## Server酱推送

邮件推送可能比较麻烦，因此也添加了Server酱推送部分。前往http://sc.ftqq.com/ 获得个人的`SCKEY`，然后添加一条`Secrets`：

+ `SERVER_KEY`：将`SCKEY`复制进去。

若不想开启Server酱推送，请将`.github/workflows/XMU_Auto_Check_In.yml`中`env`下上述条，以及`XMUAutoCheckIn.py`的第213行注释掉。

## 免责声明

1. 本项目不会记录你的任何敏感信息，也不会上传到任何服务器上。（Secrets是连创建者本人也看不到现有的信息的）
2. 本工具执行过程中产生的日志，仅会在使用者自行配置推送渠道后进行推送。日志中不包含任何用户敏感信息。
3. 本项目仅用于学习交流，请不要用于盈利，由于某些特殊原因，也请不要肆意传播，导致的不良后果本人不承担任何责任。
4. 本项目遵守[MIT License](https://github.com/JunzhouLiu/BILIBILI-HELPER/blob/main/LICENSE) ，请各位知悉。
