# Kuon

<p align="center">
  <img src="./images/logo.jpg" alt="Kuon Logo" width="200">
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991)](https://openai.com/)
[![TTS](https://img.shields.io/badge/TTS-Aliyun-FF6A00)](https://www.aliyun.com/)
[![MCP](https://img.shields.io/badge/MCP-Enabled-brightgreen)](https://openai-agents.readthedocs.io/)

久远，一个开发中的大模型语音助手。之前代码太臃肿，于是新分支重写，重点放在易用性上，使其成为一个实用的东西。

## 开发简述

简约代码则不再使用本地模型，即使要本地化也使用接口方式对接本程序。大模型只对接`openai`接口，其他厂商模型可以使用`oneapi`的方式匹配。目前取消了语音输入，原因在于实在不常用。后续再考虑是否加入。使用`MCP`来扩展助手能力。

目前功能：
- [x] 大模型的记忆存储
- [x] 使用文本输入交流，输出文本和语音
- [x] MCP功能

后续计划：
- [ ] 优化TTS
- [ ] 优化记忆存储，提升记忆价值
- [ ] GUI交互

## 安装与使用

### 环境准备

1. 创建并激活conda环境（可选）
```bash
conda create -n kuon python=3.10
conda activate kuon
```

2. 克隆仓库
```bash
git clone https://github.com/yourusername/kuon.git
cd kuon
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

### 配置

#### 1. API密钥配置

**对话密钥（必需）**
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY = "您的OpenAI API密钥"
$env:OPENAI_BASE_URL = "API基础URL"

# Linux/macOS
export OPENAI_API_KEY="您的OpenAI API密钥"
export OPENAI_BASE_URL="API基础URL"
```

* TTS密钥（可选，目前只有阿里TTS，可以只文字交互）
```bash
# Windows (PowerShell)
$env:ALIYUN_ACCESS_KEY_ID= ""
# Linux/macOS
export ALIYUN_ACCESS_KEY_ID=""
```

#### 2. 配置文件

根目录的`config.yaml`文件：
```yaml
tts:
  enabled: true  # 是否启用TTS
  engine: "aliyun"  # TTS引擎选择，目前支持 "aliyun" 

mcp:
  enabled: true  # 是否默认启用MCP工具
  config_path: "mcp_server/temp_mcp_server.json"  # MCP服务器配置文件路径 
```

#### 3. MCP配置（可选）

如需使用MCP功能，请参考`mcp_server/temp_mcp_server.json`配置文件：
```json
{
    "mcpServers": {
      "general": {
        "type": "stdio",
        "command": "执行命令",
        "args": ["命令参数"],
        "env": {
          "OPENWEATHERMAP_API_KEY": "额外环境变量"
        }
      },
      "mcp-hotnews-server": {
        "type": "sse",
        "url": "https://mcp.modelscope.cn/sse/"
      }
    }
}
```

### 启动

运行主程序:
```bash
python kuon.py
```

程序启动后，直接输入文本与AI交互。输入"exit"或"quit"退出程序。

## 示例展示

下图展示了与久远助手的实际交互效果:

![交互示例](./images/2025年4月30日.png)


## 其他

目前对话记忆被直接存储在了`chat_engines/memory.json`文件中，可以根据需求进行删改。
特别是存储了一些奇怪的东西时。
