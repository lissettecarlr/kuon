[首页](../README.md) |

# 本地部署对话模型

## 通义千文

### 通常方式

该方式对平台没有要求，但是需要安装cuda，可参考[文章](https://blog.kala.love/posts/868a5118/)

下载模型放置到`llm\local\models`中

```bash
git lfs install
git clone https://huggingface.co/Qwen/Qwen-1_8B-Chat
```


根据上面安装的cuda安装pytorch，如果是11.8则直接执行下列命令，否则请参考[pytorch](https://pytorch.org/get-started/locally/)

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

安装环境
```bash
cd kuon/llm/local/
pip install -r qwen_requirements.txt
```

运行
```bash
python qwen_api.py --server-port 1234 --server-name "0.0.0.0" -c "./model/Qwen-1_8B-Chat/"
```

之后在`llm\config.yaml`中填入即可
```
url : http://127.0.0.1:1234/v1/chat/completions
model : Qwen-7B
```

### docker方式

该方式不需要安装cuda，但是只能在Linux平台，参考[文章](https://blog.kala.love/posts/e6563228/)

