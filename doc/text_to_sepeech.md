## 文本转语言

### VITS

可以通过这个[仓库](https://github.com/Plachtaa/VITS-fast-fine-tuning/blob/main/README_ZH.md)进行训练，这里的部署代码来自[huggingface](https://huggingface.co/spaces/zomehwh/vits-uma-genshin-honkai)。

依赖：
* 需要安装[pytorch](https://pytorch.org/hub/)，先看看本机的cuda版本，然后安装对应的pytorch版本，我这里是11.6:
    ```
    conda install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.6 -c pytorch -c nvidia
    #或者
    pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116
    ```
* 其他去这儿安装text_to_sepeech\vits\requirements.txt
