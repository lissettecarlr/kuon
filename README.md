# Kuon

久远，一个开发中的大模型语音助手。之前代码太臃肿，于是重写，重点放在易用性上，使其成为一个实用的东西。

## 开发简述

简约代码则不再使用本地模型，即使要本地化也使用接口方式对接本程序。大模型只对接`openai`接口，其他厂商模型可以使用`oneapi`的方式匹配。目前取消了语音输入，原因在于实在不常用。后续再考虑是否加入。继续开发原因在于目前可以对接MCP，真正意义上能作为实用的助手了。

目前功能：
- [x] 大模型的记忆存储
- [x] 使用文本输入交流，输出文本和语音

后续计划：
1. 优化TTS,特殊符号处理
2. 优化记忆存储，提升记忆价值
3. 添加MCP，扩展技能
4. GUI交互

## 使用

### 环境

1. 克隆仓库
```bash
git clone https://github.com/yourusername/kuon.git
cd kuon
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置API密钥

windows
```bash
$env:OPENAI_API_KEY= ""
$env:OPENAI_BASE_URL= ""

# 如果使用阿里云的TTS则
$env:ALIYUN_ACCESS_KEY_ID = ""
```

linux
```bash
export OPENAI_API_KEY=""
export OPENAI_BASE_URL=""

# 如果使用阿里云的TTS则
export ALIYUN_ACCESS_KEY_ID=""
```

### 使用

运行主程序:
```bash
python kuon.py
```

程序启动后，直接输入文本与AI交互。输入"exit"或"quit"退出程序。
