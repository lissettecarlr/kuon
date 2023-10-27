# 语音输入

通过本地麦克风或者网络连接网络麦克风进行语音输入.

## 1 目录结构
```
│   auditory_sense.py
│   local_microphone.py
│   network_input.py
```

## 2 本地麦克风方式

### 依赖

* pyaudio

### 相关参数

```
  switch : True
  threshold : 1500
  channels : 1
  rate : 48000 
  queue_size : 10
```

### 说明

* 创建一个线程用于接收麦克风输入
* 通过start开始接收
* 通过stop停止接收
* 接收文件会被临时缓存，通过audio_queue队列取出地址
* audio_processed_event事件将会在每次接收完成后被set


## 3 云端语音输入
（未实现）

