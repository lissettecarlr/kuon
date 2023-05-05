# 声音转文字功能



## 说明

音频接收线程将会不断监听输入，将接收到的音频进行本地缓存，将缓存文件路径保存到队列中，并且发出通知。

语音转文本线程将监听是否有通知，如果有通知则从队列中取出所有缓存文件路径，将其转化为文本，然后将文本保存到输出队列。

输入队列由外部传入，该类别传输队列统一格式，例：{"type":"voice","content":"你好"}


## 接收音频

* 文件microphone_audio.py是使用sounddevice库来进行录音

* 文件microphone_audio_pa.py是使用pyaudio库来进行录音


## 处理音频

### whisper

文件audio_to_text_wsp.py 是使用whisper进行语音识别，分为[openAi的接口版本](https://platform.openai.com/docs/api-reference/audio)和[本地部署版](https://github.com/openai/whisper)

### vosk（未完成对接）

* [github地址](https://github.com/alphacep/vosk-api)
* [官网](https://alphacephei.com/vosk/index.zh)
* [模型](https://alphacephei.com/vosk/models)


