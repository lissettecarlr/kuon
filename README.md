[首页](./README.md) | [历史的QQ_bot](./doc/README_QQ_BOT.md) | [配置文档](./cfg/README.md) | [听-文档](./hearing/README.md) | [说-文档](./speaking/README.md) | [思-文档](./brain/README.md)

<p align="center">
 <img src="./pic/logo.png" align="middle" width = "300"/>
<p align="center">
</p>

# KUON

久远，一个对接chatgpt的语音助手

## 1 开发简述

历史版本文档可以由上方导航栏进行切换，或者切换到main分支，当前分支位real，目前旨在开发一个语音助手，最终目的还是做一个纸片人老婆。

## 2 目前功能

* 语音输入
* chatgpt对输入对话生成应答
* 语音输出（可控声线）

## 3 使用

### 环境
```
Python 3.10
pip install -r requirements.txt
```

### 配置

* 修改 cfg/hearing_config_temp.json文件名，删除_temp，然后填写私有的配置项

* 修改 cfg/brain_config_temp.json文件名，删除_temp，然后填写私有的配置项

* 配置项的详细说明可见[文档](./cfg/README.md)


### 下载文字转语言的模型

* 可以去[这里](https://huggingface.co/spaces/zomehwh/vits-uma-genshin-honkai/tree/main/model)，下载G_953000.pth和config.json两个文件，然后放到./speaking/vits/model文件夹下

* 也可以通过[BD云](https://pan.baidu.com/s/1h0h6huYhiihpdAgFbT4DcQ?pwd=1111)下载

### 可能出现的问题

#### 无法输入声音

在配置文件hearing_config.json中可以调整麦克风的输入通道，设备上由那些通道可以通过命令查看，默认是1
```
python .\utils\get_input_channels.py
输出
麦克风 ID 0 - Microsoft 声音映射器 - Input
麦克风 ID 1 - 麦克风 (WO Mic Device)
```
还能调节输入声音的阈值threshold，阈值越高，需要的声音越大才能触发输入。



### 运行

```
python kuon.py
```

然后对着麦克风说话吧~


## 4 文件说明
