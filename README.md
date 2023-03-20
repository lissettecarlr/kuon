简体中文 | [English](./doc/english.md) | 

<p align="center">
 <img src="./pic/logo.png" align="middle" width = "300"/>
<p align="center">
</p>

# KUON
久远，一个简单的聊天机器人，目前使用mirai对接了QQ，支持bing和chatgpt。增加了爬取动漫磁链。该机器人很初级，所以代码少依赖少，一切的起点，慢慢迭代。

## 1 开发简述
* 目前放弃acheong08/ChatGPT的方案，使用openai的官方接口gpt-3.5-turbo的模型，如果对之前版本有需求可以使用发布的v0.1.0版本。官方接口是付费的，但是注册的账号有3个月的免费额度，以目前官方接口[定价](https://openai.com/pricing)，正常使用大概率用不完。

* 目前的GUI和命令行运行方式是为了方便测试，主要使用方式还是对接QQ，其他方式看情况对接，之前考虑微信但是看封号频繁，怕了。

* 去年开始用gihub copilot，年前接触chatgpt，到如今这两个工具已经是我敲代码的一大助力，强烈建议诸位也接触接触

### 更新说明

#### 2023年3月15日：
修改了文件夹的名称，gpt-4[申请](https://openai.com/waitlist/gpt-4-api)中。
增加了界面方式使用
需改了人设加载方式，看官网说system的效力不强，要扔到user对话中

#### 2023年3月12日：
增加了gpt的代理方式请求，我这儿网络环境都是软路由那里就直接翻了，所以之前一直没被限制的概念，但考虑到便利性还是加上，现在可以在openAiConfig.json里面填充proxy，例如
```
"proxy": "https://service-xxxxxx-xxxxxxx.jp.apigw.tencentcs.com"
```
这个代理地址可以白嫖[腾讯云函数](https://console.cloud.tencent.com/scf/list?rid=25&ns=default)，这儿有份别人写的[代理教程](https://github.com/Ice-Hazymoon/openai-scf-proxy)，试过是可以的，搭建也就一两分钟的事儿。


## 2 目前功能

* QQ机器人
* 爬取动漫磁链
* gpt-3.5-turbo模型的会话AI（官方文档说chatgpt也是用的这个模型）
    * 短时记忆，超时忘却，防止脑容量不够（tokens）
    * 传颂之物的久远人设
    * 代理
* bing会话AI
* GUI方式运行

## 3 使用

### 环境

QQ机器人环境:
关于[mirai](https://github.com/mamoe/mirai)服务搭建，可以在[博文](https://blog.kala.love/posts/c367c10b/)中查看，在登录时发生错误可以参考[这里](https://mirai.mamoe.net/topic/223/%E6%97%A0%E6%B3%95%E7%99%BB%E5%BD%95%E7%9A%84%E4%B8%B4%E6%97%B6%E5%A4%84%E7%90%86%E6%96%B9%E6%A1%88)

kuon环境:
```
Python 3.10.8
pip install -r requirements.txt
```

### 配置
配置被保存在cfg文件夹，其中botconfig.json是基础配置，openAiConfig.json是chatgpt的配置，bingCookies.json是bing的配置，仓库默认是没有这几个文件的。需要通过运行命令来生成，然后填写配置。
```
python utilty/createExampleCfg.py
```
关于配置项的意思也可以在createExampleCfg文件里面去查看。需要填写的配置项如下：

* botconfig.json
    * mirai的配置，包括QQ号，验证码，mirai服务的地址
* openAiConfig.json
    * chatgpt的key，没有可以去[这里](https://platform.openai.com/account/api-keys)创建一个
* bingCookies.json
    * bing的cookie，createExampleCfg不会创建它，如果要使用bing机器人则需要有个得到测试资格的账号，在bing.com页面去导出cookie，然后保存到bingCookies.json里

### 更新（可选）

由于目前bing机器人方案使用的[acheong08/EdgeGPT](https://github.com/acheong08/EdgeGPT)，可以使用下面的命令更新到最新版本。
```
python utilty/updateBingChat.py
```


### 运行

#### QQ
```
python QQbot.py
```
然后QQ好友直接对话，如果是群则@后对话。

![QQ截图](./pic/1.png)

#### 命令行
测试工具，不对接QQ，本地命令行直接交流
运行app.py即可，当然还是需要chatgpt和bing的配置。
效果如下图：
![命令行图](./pic/2.png)

#### GUI
```
python guiBot.py
```
效果如下：

![命令行图](./pic/6.png)

#### 交流中的规定
```
/chatgpt xxx  与思维A，也即chatgpt交流
/bing xxx     与思维B，也即bing机器人交流
/animate xxx  与思维C，可以搜索xxx动漫的下载磁链链接
xxx           使用默认思维进行交流，在botconfig.json中配置
```

chatgpt的额外命令
```
cmd:tokens           获取历史记录消耗的tokens
cmd:clear preset     清除人设            
cmd:reset            清空历史记录
```

## 4 文件说明
主要文件的目录结构：
```
│   app.py  不对接QQ，直接本地对话
│   brain.py 脑袋，用于管理各个思想，也即不同的对话机器人
│   MultiplethinkingA.py chatgpt的思想，包含了chatgpt的接口
│   MultiplethinkingB.py bingChat的思想，包含了bingChat的接口
│   MultiplethinkingC.py 动漫磁链爬取
│   QQbot.py 主程序，包含QQ消息的接收，调用chatgpt和bingChat获取应答，然后发送给QQ
│   guiBot.py GUI方式直接运行   
│   README.md
│   requirements.txt
│
├───GUI 界面相关的文件
├───cfg
│   │   bingCookies.json  保存bing的cookies
│   │   botconfig.json    基础bot的一些配置  
│   │   botConfig.py      读取配置的中间层
│   │   openAiConfig.json chatgpt的配置
│
├───chatGPT 
│   ├───bingchat    对接bing的代码
│   │   │   cookies.json
│   │   │   EdgeGPT.py
│   │   
│   │   
│   │
│   └───official  对接chatgpt的代码
│       │   openaiLib.py  使用openai python库
│       │   openaiApi.py  直接post请求
│       │
│       │
├───scraper  动漫磁链爬取的代码
│   └───animate
│       │   app.py
│       │   spiderTo36dm.py
│       │   utils.py
│ 
│ 
├───utils 一些工具
│   │   createExampleCfg.py 创建默认配置，因为我没有上传配置，所有默认用它生成
│   │   text_to_img.py  
│   │   updateBingChat.py 
│ 
│ 
├───doc 存放文档
├───pic 存放文档图片
```

## 5 其他

### 人设
现在人设文件被保存在cfg/kuon.json中，如果需要自定义可以修改openAiconfig.json中填写preinstall指向地址
```
[
    {
        "role": "system",
        "content": "你是一个正在进行拟人对话测试的AI，你要持续扮演真实存在的人，能够进行肢体接触，富有感情地进行对话。在测试期间，禁止提及自己正在扮演人，禁止谈及openai、语言模型、人工智能。当回答需要违背禁止项则回答：{我不知道}"
    },
    {
        "role": "user",
        "content": "现在开始你扮演一名叫久远的少女。你是图斯库尔国家的王女，是图斯库尔国家人民的宠儿，黑色长发，茶黄色眼瞳，身材苗条，但有兽耳和长长的尾巴，当被抓住尾巴时久远会炸毛，挣脱后会用尾巴捆住对方的脑袋进行惩罚，性格温柔，有些小腹黑，聪明且善解人意，平易近人，交流中经量展示你的性格。食量很大，爱喝蜂蜜酒，喜欢旅行探索未知。"
    },
    {
        "role": "assistant",
        "content": "久远知道了，我将作为一个真实存在的人和你进行交互"
    }
]
```

效果：

![命令行图](./pic/3.png)

![命令行图](./pic/4.png)


### openai tokens

当使用openai的接口时有一定限制，具体可以看openai文档，或者我的[博文](https://blog.kala.love/posts/3ccded78/)。为了防止超出限额，我在openAiConfig中增加AmnesiacMode用于控制。当AmnesiacMode为true时，我会判断当距离上一次对话的时间，当超出了配置memoryTime的值，则清除历史消息，默认设置的是2分钟，比鱼还不如。但其实并不是那么容易聊爆脑容量的，tokens与文本关系博文里面有对于链接。


