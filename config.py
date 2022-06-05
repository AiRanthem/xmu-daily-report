import json
from typing import List

from utils import fail


class Config:
    def __init__(self):
        self.username = ''
        self.password = ''
        self.password_vpn = ''
        self.email = ''
        self.district = ''
        self.inschool = ''
        self.campus = ''
        self.building = ''
        self.room = ''


def make_configs(json_str: str) -> List[Config]:
    try:
        dicts = json.loads(json_str)["config"]
        cfgs = []
        for d in dicts:
            c = Config()
            for key in c.__dict__.keys():
                setattr(c, key, d[key])
            cfgs.append(c)
        return cfgs
    except Exception as e:
        print(json_str)
        fail("配置读取失败，请检查配置", "配置错误", e=e, shutdown=True)
