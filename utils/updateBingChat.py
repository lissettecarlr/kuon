# pip install gitpython

from git.repo import Repo
import os
import shutil

# 获取当前地址文件地址
base_dir = os.path.dirname(os.path.abspath(__file__))
# 根目录
base_dir = os.path.dirname(base_dir)
# chatGPT目录
chatGPT_dir = os.path.join(base_dir,'chatGPT')
# 缓存文件夹
cache_dir = os.path.join(base_dir,'cache')

import stat
def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

if __name__ == '__main__':
    # 判断目录是否存在
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    if not os.path.exists(chatGPT_dir):
        os.mkdir(chatGPT_dir)
    print('开始更新BingChat，缓存目录{}，chatGPT目录{}'.format(cache_dir,chatGPT_dir))

    # 更新 https://github.com/acheong08/EdgeGPT
    # 如果存在则删除
    acheong08ChatGPTPath = os.path.join(cache_dir,'bingchat')
    if os.path.exists(acheong08ChatGPTPath):
        shutil.rmtree(acheong08ChatGPTPath,onerror=readonly_handler)
    print("开始克隆仓库")
    Repo.clone_from('https://github.com/acheong08/EdgeGPT.git',to_path=acheong08ChatGPTPath,branch='master')
    # 将核心文件夹移动到chatGPT目录
    print("移动文件夹至 {}".format(os.path.join(chatGPT_dir,'bingchat')))
    os.rename(os.path.join(acheong08ChatGPTPath,'src'),os.path.join(chatGPT_dir,'bingchat'))
    #删除缓存文件夹及其内容
    print("删除缓存文件夹 {}".format(acheong08ChatGPTPath))
    shutil.rmtree(acheong08ChatGPTPath,onerror=readonly_handler)
    print('更新完成，该仓库消息请直接去 https://github.com/acheong08/EdgeGPT 查看')

