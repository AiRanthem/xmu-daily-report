# xmu-daily-report
厦大Daily Health Report 健康打卡自动填写脚本

如果以后厦大有类似异常烦人的需要每天完成的机械任务，我会在这个仓库中同步更新相应脚本，维护到我研究生毕业。也希望大家自信编写脚本并提PR。

**声明：使用该项目请遵循MIT协议**

## Version 1.0
使用 [playwright-python](https://github.com/microsoft/playwright-python) 替代selenium重写，实现一键安装和部署，简化使用

## 使用准备

### requirements
+ 需要python3.7以上的版本，若没有请自行登录[python.org](python.org)下载。Windows用户可以在Microsoft Store中搜索 python 直接安装。

### installation
在终端中执行以下命令：

```shell
pip install playwright -i https://pypi.douban.com/simple
python -m playwright install chromium
```

## 使用方法

### 本地运行
首先请按照提示编辑[script目录中的config.py文件](./scripts/config.py)

```shell
python run.py 脚本名
# example: python run.py daily-report
```
目前支持的脚本有
+ daily-report（每日健康打卡）

## log
+ 2020/3/13: 项目开始
+ 2020/3/13: 完成使用selenium的0.1版本
+ 2020/3/14: version 0.2 update, bug fix
+ 2021/3/14: 一周年，version 1.0，使用playwright重写，大幅简化安装流程和使用方法。
