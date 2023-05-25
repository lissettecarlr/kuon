[首页](../README.md) |
# 语音播放

## playsound

### 安装

* pip install playsound
* 需要修改playsound的源码，才能在windows中使用
   * Lib\site-packages\playsound.py，中移除使用utf-16进行解码的部分


## vlc（存在问题）

### 安装

* pip install python-vlc
* 需要安装vlc播放器，[下载](https://www.videolan.org/) 注意系统位数，否则之后可能会报错：[WinError 193]
* 将vlc的路径加入环境变量
* 在python中输入import vlc，如果没有报错，则安装成功

### 问题

在播放模型输出的音频是报错：
```
[000001ed5f9df650] wasapi generic error: cannot negotiate audio format (error 0x88890008)
```
原因是音频文件的采样率或位深度不兼容，音频的参数可在模型配置文件见到，虽然可以对输出文件进行一次转换，但是多个步骤，算了换一种。

## pydub

### 安装
详细可见[github](https://github.com/jiaaro/pydub)

* pip install pydub
* pip install pyaudio

### 示例
```
from pydub import AudioSegment
from pydub.playback import play

# 读取音频文件
audio_file = AudioSegment.from_wav(r"J:\code\kuon\text_to_sepeech\temp\0.wav")
# 播放音频文件
play(audio_file)
```