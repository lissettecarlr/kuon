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

* paraformer方式语言转文本
* whisper的openai接口方式语言转文本
* chatgpt对话


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




## 语音输入

### 本地麦克风方式

依赖：

* pyaudio



### 云端语音输入
（未实现）

## 语音转文本

### paraformer方式

源码来自rapid的[RapidASR仓库](https://github.com/RapidAI/RapidASR/blob/main/README.md)

#### 依赖
* onnxruntime-gpu 或者 onnxruntime
* numpy
* librosa 用于音频分析和处理
* pyyaml
* typeguard==2.13.3



### whisper方式

#### 使用接口方式

使openai的接口进行转换，需要key，请求方式来自[这里](https://platform.openai.com/docs/api-reference/audio)

依赖:

* openai
* langid 检测语言的库（可选）

### 本地部署方式
（未实现）
来自openai的开源仓库[whisper](https://github.com/openai/whisper)


## 情感分析
（未实现）

## 思维

接收消息->处理消息->输出消息

消息格式传输格式示例
```
{"type": "auditory", "content": "你好"}
{"type":"speech","content":"不好"}
{"type":"cmd","content":"stop"}
```

### 灵魂
进行对话的基础，通过短句形式输出，方便转化为语音

#### chatgpt

* 通过http请求进行对话
* 代理
* 短期对话记忆
* 流式输出

## 文本转语言

### VITS

可以通过这个[仓库](https://github.com/Plachtaa/VITS-fast-fine-tuning/blob/main/README_ZH.md)进行训练，这里的部署代码来自[huggingface](https://huggingface.co/spaces/zomehwh/vits-uma-genshin-honkai)。

依赖：
* 需要安装[pytorch](https://pytorch.org/hub/)，先看看本机的cuda版本，然后安装对应的pytorch版本，我这里是11.6:
    ```
    conda install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.6 -c pytorch -c nvidia
    #或者
    pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116
    ```
* 其他去这儿安装text_to_sepeech\vits\requirements.txt

## 其他

查看环境有无cuda：
```
nvcc --version

nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2021 NVIDIA Corporation
Built on Fri_Dec_17_18:28:54_Pacific_Standard_Time_2021
Cuda compilation tools, release 11.6, V11.6.55
Build cuda_11.6.r11.6/compiler.30794723_0
```

