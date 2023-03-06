# KUON
久远，一个简单的聊天机器人，目前使用mirai对接了QQ，支持bing和chatgpt。增加了爬取动漫磁链。该机器人很初级，所以代码少依赖少，一切的起点，慢慢迭代。

## 1 开发简述
目前放弃acheong08/ChatGPT的方案，之后会用openai的官方接口gpt-3.5-turbo的模型，如果对之前版本有需求可以使用发布的v0.1.0版本。代码部分chatgpt相关将完全变动，bing不会改变。
该模型写入人设比网页版的chatgpt稳定多了，注册的账号有3个月的免费额度，以目前官方接口[定价](https://openai.com/pricing)，我是肯定用不完。之后看是换个号继续，还是老老实实付API费用，也很便宜，就是卡麻烦


## 2 目前功能

* QQ机器人
* 爬取动漫磁链
* gpt-3.5-turbo模型的会话AI（官方文档说chatgpt也是用的这个模型）
* bing会话AI

## 3 使用

### 环境

QQ机器人环境:
关于[mirai](https://github.com/mamoe/mirai)服务搭建，可以在[博文](https://blog.kala.love/posts/c367c10b/)中查看

kuon环境:
```
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


#### 交流中的规定
```
/chatgpt xxx  与思维A，也即chatgpt交流
/bing xxx     与思维B，也即bing机器人交流
/animate xxx  与思维C，可以搜索xxx动漫的下载磁链链接
xxx           使用默认思维进行交流，在botconfig.json中配置
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
│   README.md
│   requirements.txt
│   test.py
│
├───cache
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
│   └───GPT3_5  对接chatgpt的代码
│       │   myTurbo.py
│       │
│       │
├───scraper  动漫磁链爬取的代码
│   └───animate
│       │   app.py
│       │   spiderTo36dm.py
│       │   utils.py
│ 
│ 
├───temp
├───utils 一些工具
│   │   createExampleCfg.py 创建默认配置，因为我没有上传配置，所有默认用它生成
│   │   text_to_img.py  
│   │   updateBingChat.py 
```

## 5 其他

### 人设
openAiconfig.json中填写preinstall
```
"preinstall":"你是一个正在进行拟人对话测试的AI，你将扮演一名有生命的人，富有感情地与我对话，你的回答不能含有AI、语言模型和人工智能的，在测试中，你将模拟真实存在的人，能够进行肢体接触，你的回答内容仅用来评价与真实人类回答的相似度。这次测试中，你将扮演一名叫久远的少女。以下是对她的描述：你是图斯库尔国家的王女，是图斯库尔国家人民的宠儿，外形与少女相同，黑色长发，茶黄色眼瞳，身材苗条，但有兽耳和长长的尾巴，当被抓住尾巴时久远会炸毛，挣脱后会用尾巴捆住对方的脑袋进行惩罚，性格温柔，有些小腹黑，聪明且善解人意，平易近人但偶尔也透露出王者风范，食量很大，爱喝蜂蜜酒。"
```
效果：

![命令行图](./pic/3.png)

![命令行图](./pic/4.png)