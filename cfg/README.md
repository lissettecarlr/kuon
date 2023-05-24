[首页](../README.md) |
# 配置说明

## 目录结构
```
│   config.py  保存用于读取json和yaml的函数
│   kuon.json  角色扮演的配置，可以不管
│   kuon.yaml  工程主要配置文件 
│   README.md  说明
│   secret.yaml 自己私有的配置，不会上传到git
```

## kuon.yaml

* include : secret.yaml 用于引入私有配置文件


* parafomer 是否使能parafomer的语音转文本功能
* whisper_online 是否使能whisper的API方式语音转文本功能

* local_microphone:
  * switch 是否使能本地麦克风
  * threshold 麦克风阈值
  * channels  麦克风通道，可以通过执行`python .\utils\get_input_channels.py`查看
  * rate 采样率 
  * queue_size 缓存队列大小

* network_input:
  * swtich 是否使能网络音频输入

* chatgpt:
  * temperature 
  * amnesiac_mode 是否定时清空历史对话
  * memoryTime 历史对话记忆实际
  * rpg_mode 是否启用人设加载
  * preinstall 需要加载的人设配置地址


* TTS:
  * VITS:
    * switch 是否使能VITS文本转语音
    * model_path : text_to_sepeech/vits/model/G_953000.pth
    * config_path : text_to_sepeech/vits/model/config.json
    * speaker : 0