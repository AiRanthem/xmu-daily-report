import json
import os

import requests

from log import get_log_string, logger

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


def fail(msg: str, title: str, email: str = "", e: Exception = None, shutdown=True, run_fail=False, send=False):
    logger.error(msg)
    if e is not None:
        logger.error(e)
    if run_fail:
        raise RuntimeError(msg)
    if send:
        send_mail(msg, title, email)
    if shutdown:
        exit(0)


def mask_username(username: str) -> str:
    return f"{username[:3]} **** {username[-3:]}"
