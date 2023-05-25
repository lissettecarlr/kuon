[首页](../README.md) |
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
