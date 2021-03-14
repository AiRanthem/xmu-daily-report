import os
from sys import argv

scripts = os.listdir("scripts")
scripts.remove("config.py")
scripts = list(map(lambda x: x[:-3], scripts))

if len(argv) != 2 or argv[1] not in scripts:
    print(f"usage: python run.py [script], available scripts are: {scripts}")
    exit(1)

os.system(f"python scripts/{argv[1]}.py")
