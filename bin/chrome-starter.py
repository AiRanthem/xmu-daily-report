import os
from settings import CHROME_PATH

os.system("cd {} && .\chrome.exe --remote-debugging-port=9222".format(CHROME_PATH))