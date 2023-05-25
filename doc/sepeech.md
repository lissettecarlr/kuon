[首页](../README.md) |
# 语音播放

## playsound

### 安装

* pip install playsound
* 需要修改playsound的源码，才能在windows中使用
   * Lib\site-packages\playsound.py，中移除使用utf-16进行解码的部分


## vlc

### 安装

* pip install python-vlc
* 需要安装vlc播放器，[下载](https://www.videolan.org/) 注意系统位数，否则之后可能会报错：[WinError 193]
* 将vlc的路径加入环境变量
* 在python中输入import vlc，如果没有报错，则安装成功



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