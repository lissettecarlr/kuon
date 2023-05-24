[首页](../README.md) |

# 语音输入

相关代码被保存在 : auditory_sense
通过本地麦克风或者网络连接网络麦克风进行语音输入.

## 目录结构
```
│   auditory_sense.py
│   local_microphone.py
│   network_input.py
```

## 本地麦克风方式

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

### 逻辑

多线程运行,会不间断进行录制,然后录制的段落语音本地缓存,将缓存文件地址存入队列中.


## 云端语音输入
（未实现）

## 测试

```
python test_auditory_sense.py
```