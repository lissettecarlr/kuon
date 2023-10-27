import os
import shutil
from git import Repo

# 将仓库克隆下来



repo_url = 'git@github.com:lissettecarlr/AutomaticSpeechRecognition.git'
Repo.clone_from(repo_url, "./AutomaticSpeechRecognition")

 
if os.path.exists("../kuonasr"):
    print("已存在，进行覆盖更新")
    shutil.copy2("../kuonasr/config.yaml","./AutomaticSpeechRecognition/kuonasr/config.yaml")
    shutil.rmtree("../kuonasr")
    shutil.copytree("./AutomaticSpeechRecognition/kuonasr","../kuonasr")
    print("更新完成")
else:
    shutil.copytree("./AutomaticSpeechRecognition/kuonasr","../kuonasr")
    shutil.copy2("../kuonasr/config.yaml.example","../kuonasr/config.yaml")
    print("添加完成，请在根据使用修改配置文件：kuonasr/config.yaml")