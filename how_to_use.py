import os

cur_dir = os.path.abspath(os.path.dirname(__file__))
print('按照下面的提示运行脚本：\n')
print('注意：如果要求登陆，请在登陆后去命令行中按一下回车！')
print('1. 通过win+R快捷键打开"运行"\n')
print('2. 输入"cmd"，回车\n')
print('3. 复制粘贴下面几行命令执行：')
print('cd {}'.format(cur_dir))
print('python main.py')
os.system('pause')
