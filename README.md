[首页](./README.md) | [历史的QQ_bot](./doc/README_QQ_BOT.md) | [语音输入](./doc/auditory_sense.md) | [语音转文本](./doc/sepeech_to_text.md)
<p align="center">
 <img src="./pic/logo.png" align="middle" width = "300"/>
<p align="center">
</p>

# KUON

久远，一个对接chatgpt的语音助手。使用筛选重组后的虚伪的假面字幕作为历史对话，形成久远的人设。

## 1 开发简述

历史版本文档可以由上方导航栏进行切换，或者切换到main分支，当前分支位real，目前旨在开发一个语音助手，最终目的还是做一个纸片人老婆。


## 2 目前功能

* paraformer方式语言转文本
* whisper的openai接口方式语言转文本
* chatgpt对话
* vits的文本转语音
* 语音播放
* 语音接收
* 传颂之物久远人设

## 3 使用

### 3.1 环境

```
Python 3.10
pip install -r requirements.txt
```

或者使用conda的配置
```
conda create --name kuon --file environment.yml
```
配置来自我这儿的环境，开发过程中可能安装了额外的包。
```
conda env export > environment.yml
```

### 3.2 配置

* 在cfg中添加secret.yaml文件，填入下列参数。key就是openai的key，proxy是代理地址，如何搞个代理可以参考[这里](./doc/proxy.md).
    ```
    OPENAI:
        key: 'sk-'
        proxy: 'https://api-openai/'

    ```

* 配置项的详细说明可见[文档](./cfg/README.md)


### 3.3 下载文字转语言的模型

* paraformer语音转文本[模型](https://pan.baidu.com/s/15qqCZt4xl9_8Xe-zsVCpKQ?pwd=1111):sepeech_to_text\Paraformer\resources\models
    * am.mvn
    * model.onnx
    * token_list.pkl

* VITS的文本转语音[模型](https://pan.baidu.com/s/1h0h6huYhiihpdAgFbT4DcQ?pwd=1111):text_to_sepeech\vits\model
    * G_953000.pth
    * config.json


### 3.4 运行

```
python kuon.py
```

## 4 其他

#### 无法输入声音

在配置文件中可以调整麦克风的输入通道，设备上由那些通道可以通过命令查看，默认是1
```
python .\utils\get_input_channels.py
输出
麦克风 ID 0 - Microsoft 声音映射器 - Input
麦克风 ID 1 - 麦克风 (WO Mic Device)
```
还能调节输入声音的阈值threshold，阈值越高，需要的声音越大才能触发输入。

#### VITS报错
```
RuntimeError: Error(s) in loading state_dict for SynthesizerTrn:
        size mismatch for enc_p.emb.weight: copying a param with shape torch.Size([52, 192]) from checkpoint, the shape in current model is torch.Size([43, 192]).
```
上列错误原因是 text_to_sepeech\vits\text\symbols.py中的symbols和训练模型的symbols不一致,改成一样就行了

#### 查看环境有无cuda：
```
nvcc --version

nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2021 NVIDIA Corporation
Built on Fri_Dec_17_18:28:54_Pacific_Standard_Time_2021
Cuda compilation tools, release 11.6, V11.6.55
Build cuda_11.6.r11.6/compiler.30794723_0
```

