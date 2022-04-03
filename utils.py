import calendar
import json
import os
import random
import time

import requests

from log import get_log_string, logger

# 在开源项目中 暴露服务器ip可能是不明智的
MAIL_SERVER_URL = 'http://120.77.39.85:8080/mail/daily_report'

debug = os.getenv("ENV") == "debug"


def send_mail(msg: str, title: str, to: str):
    msg += '\n\n【运行日志】\n' + get_log_string()
    if not debug:
        post = requests.post(MAIL_SERVER_URL, data=json.dumps(
            {"title": title, "body": msg, "dest": to}))
        return post
    else:
        logger.info(msg)


def fail(msg: str, title: str, email: str = "", e: Exception = None, shutdown=True, run_fail=False):
    logger.error(msg)
    if e is not None:
        logger.error(e)
    if run_fail:
        raise RuntimeError(msg)
    if shutdown:
        send_mail(msg, title, email)
        exit(0)

def random_second() -> int:
    return random.randrange(start=0, stop=3600, step=1)

def unix_timestamp() -> int:
    gmt = time.gmtime()
    ts: int = calendar.timegm(gmt)
    return ts

def mask_stu_num(stu_num: str) -> str:
    # XMU学号为14位
    # mask仅应用于log信息
    return stu_num[0] + '*' * 9 + stu_num[10:]
