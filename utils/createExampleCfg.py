#用于生成示例配置文件

import os
import json

if __name__ == '__main__':
    # 获取当前地址文件地址
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 根目录
    base_dir = os.path.dirname(base_dir)
    # cfg目录
    cfg_dir = os.path.join(base_dir,'cfg')
    # botconfig.json
    botconfig_json = os.path.join(cfg_dir,'botconfig.json')
    # openAiConfig.json
    openAiConfig_json = os.path.join(cfg_dir,'openAiConfig.json')
    # 判断目录是否存在
    if not os.path.exists(cfg_dir):
        os.mkdir(cfg_dir)
    if not os.path.exists(botconfig_json):
        with open(botconfig_json,'w',encoding='utf-8') as f:
            json.dump({
                        "mirai": {
                            "qq" : 1234,
                            "verifyKey" : "1111",
                            "http"  : "http://172,0,0,1:1111",
                            "ws"  : "ws://172,0,0,1:1111"
                        },
                        "responseTimeout": 30.0,   #应答超时
                        "responseQuoteTextFlag": "False", #是否在回复的时候提示是回复的哪一句
                        "responseText":{
                            "timeout":"反应慢，稍等", #超时是发送
                            "nullText":"你啥也没说", #接收消息为空时
                            "tooFast":"请等会再发"  #发送消息过快
                        },
                        "mention" : "at", # QQ群中被AT才触发
                        "prefix":[""], # 命令前缀
                        "acceptFriendRequest":"True", #是否接收好友请求
                        "acceptGroupRequest":"False", #是否接收群请求
                        "defaultThinking":"A", #默认激活思维
            },f,indent=2)
            
    if not os.path.exists(openAiConfig_json):
        with open(openAiConfig_json,'w',encoding='utf-8') as f:
            json.dump({
                "secretKey":"sk-xxx",
                "temperature":0.7,
                "isloadRPG":"False", #是否加载预设角色扮演
                "preinstall":[]
            },f,indent=2)

