import os
import shutil
from git import Repo

# 将仓库克隆下来
if os.path.exists("./TextToSpeech"):
    print("清除本地缓存仓库")
    try:
        shutil.rmtree("./TextToSpeech")
    except:
        print("权限不够，请手动删除 TextToSpeech")
        exit()

print("开始克隆仓库")      
repo_url = 'git@github.com:lissettecarlr/TextToSpeech.git'
Repo.clone_from(repo_url, "./TextToSpeech")
print("克隆完成")


if os.path.exists("../kuontts"):
    print("已存在，进行覆盖更新")
    os.remove("./TextToSpeech/kuontts/config.yaml")
    shutil.copy2("../kuontts/config.yaml","./TextToSpeech/kuontts/config.yaml")
    shutil.rmtree("../kuontts")
    shutil.copytree("./TextToSpeech/kuontts","../kuontts")
    print("更新完成")
else:
    shutil.copytree("./TextToSpeech/kuontts","../kuontts")
    print("更新完成")