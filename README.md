此版本托管于``Github Action``进行自动打卡，只需要新建两个`Secrets`即可：
+ ``USERNAME``：你的XMU用户名
+ ``PASSWD``：统一身份认证的密码
添加邮件发送打卡结果功能，另外需要添加四个`Secrets`：
+ `FROM_ADDR`：发件人邮箱
+ `MAIL_PASSWD`：邮箱授权密码，不是登录密码，需要注意
+ `TO_ADDR`：收件人邮箱
+ `SMTP_SERVER`：smtp服务器地址
