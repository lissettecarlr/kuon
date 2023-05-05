# 配置说明


## brain_config

*   "secretKey": openai的key
*   "temperature": chatgpt回答随机性，越大越随机
*   "AmnesiacMode": 是否启用遗忘模式
*   "memoryTime": 遗忘模式的时间，单位秒
*   "isloadRPG": 是否添加预设
*   "preinstall": 预设文件的位置
*   "proxy": 访问chatgpt的代理地址
*   "model" : chatgpt的模型
*   "apiUrl" : 如果不是填写代理地址则使用此地址进行访问chatgpt


## speaking_config

*    "model": 文字转语音模型位置
*    "model_config": 文字转语音模型配置文件位置
*    "output_path": 转换后的语言存放位置

## hearing_config

*    "openaiKey": 使用whisper的openai接口方式则需要填写key，否则不填
*    "threshold": 接收声音的阈值, 
*    "channels":麦克风通道,
*    "rate":48000,
*    "recordAudioQueueSize":接收音频队列大小, 
*    "recordTextQueueSize":转化文字队列大小,


## barin_config


*    "secretKey": 使用api版本的chatgpt需要填写api,
*    "temperature": ,
*    "AmnesiacMode": 是否启用遗忘模式，也即超过设定时间清空历史记录，防止使用token过量,
*    "memoryTime": 超时时间
*    "isloadRPG": 是否添加预设
*    "preinstall": 预设地址
*    "proxy": 代理地址，由于chatgpt在国内无法访问，所以需要设置代理，方案见文档：[代理部署说明](../doc/proxy.md)
*    "model" : gpt的模型选择,
*    "apiUrl" : gpt直连的访问地址,
*    "cmdStop": 当解析输入发现属于该类，则输出停止信号
