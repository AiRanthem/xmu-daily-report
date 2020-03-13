import os

cur_dir = os.path.abspath(os.path.dirname(__file__))
print('按照下面的提示安装依赖：')
print('1. 通过win+R快捷键打开"运行"\n')
print('2. 输入"cmd"，回车\n')
print('3. 复制粘贴下面几行命令执行：')
print('cd {}'.format(cur_dir))
print('pip install -r requirements.txt -i https://pypi.douban.com/simple')
print('\n3.1 如果第三步安装依赖出错，则运行下面一行：')
print('pip install selenium -i https: // pypi.douban.com/simple')
os.system('pause')
