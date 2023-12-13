<p align="center">
 <img src="./pic/logo.png" align="middle" width = "300"/>
<p align="center">
</p>

# KUON

Kuon is an in-development voice assistant that supports both language and text input, and provides text and voice output. It can integrate with the openai interface for dialogue modeling. The various functional modules are independent and can be freely combined.

## 1 Development Overview

Based on previous branches, Kuon has been restructured extensively, with the main focus on separating the various functional modules and using an interface-based approach instead of the previous integrated approach, greatly improving speed. This also allows for running on different terminals in the future.

## 2 Features

- [x] Communication using text input, with text and voice output
- [x] Communication using voice input, with text and voice output
- [x] Check function to test if each part is working properly
- [ ] Development of Kuon's character using anime subtitles as prompts (in progress)
- [x] Train a better VITS model
- [x] Text commands
- [ ] Voice commands
- [ ] Assistants mode

## 3 Usage

### 3.1 Environment

Since the various functions have been separated as much as possible, the configuration has also changed from one to multiple, but it's not too difficult.

#### 3.1.1 Basic Environment

* Conda virtual environment
    ```bash
    conda create -n kuon python=3.10
    conda activate kuon
    ```

* PyTorch (not necessary if using the interface approach):
    ```bash
    #  CUDA 11.8
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    ```

* Install basic packages:
    ```bash
    pip install -r requirements.txt
    ```
    For language playback, the `playsound` package is used. If you are using Windows, you need to modify the source code and remove the part that decodes using UTF-16 in `Lib\site-packages\playsound.py`.

* Alternatively, clone the conda configuration file (instead of the previous steps)
    Export:
    ```bash
    conda create --name kuon --file environment.yml
    ```
    Export:
    ```bash
    conda env export > environment.yml
    ```

#### 3.1.2 Speech-to-Text Functionality

This functionality has been separated into the repository [AutomaticSpeechRecognition](https://github.com/lissettecarlr/AutomaticSpeechRecognition). The relevant code has been added to the `kuonasr` folder in this repository. By default, the `funasr` interface is used. For service deployment, please refer to the instructions in the [AutomaticSpeechRecognition](https://github.com/lissettecarlr/AutomaticSpeechRecognition/blob/main/README.md) repository. If you want to use a different method, please refer to the instructions in that repository.

Before using, please modify the configuration file `kuonasr/config.yaml` according to the location of the funasr service:
```yaml
funasr:
   url: ws://172.0.0.1:1234

You can use the following script to fetch the latest code (usually not necessary):

```bash
cd script
python asr_update.py
```

#### 3.1.3 Text-to-Speech Functionality

This functionality has been separated into the repository TextToSpeech. The repository is divided into the fineturn part for training models and the kuontts part for inference. The inference code has been added to the kuontts folder in this repository.

By default, the interface approach is used, so there is no need to install any environment or include any models here. You need to modify the request URL and speaker in the kuontts/config.yaml file according to the deployed service. For service deployment and other issues, please refer to the instructions in the TextToSpeech repository.

If you want to use the offline approach, modify the configuration file kuontts/config.yaml by changing online to offline, and place the model in kuontts/offline/OUTPUT_MODEL. For now, I have trained a model for Paimon to use.

If you need to update the code, you can execute:

```bash
cd script
python tts_update.py
```

#### 3.1.4 Dialogue Model

The dialogue model is integrated using the openai API. Specify the integration object in the llm/config.yaml file.

```yaml
url : http://172.0.0.1:1234/v1/chat/completions
key : qmdr-xxxx
model : gpt-3.5-turbo-16k
timeout : 120 # 历史对话的遗忘时间
preset : ./llm/kuon.json 
```

The timeout parameter represents the time after which historical conversations are forgotten. The preset parameter is used for role-playing prompts.

Currently, there are other open-source models that can be deployed using the openai API. After deploying them, modify this configuration file accordingly. I tried using qwen-7b, but the role-playing effect was very poor. Currently, gpt-4 is the best solution.

### 3.2 Testing (Optional)

Before using, you can test each function to see if it is working properly. There are tests for voice input, speech-to-text, dialogue model, text-to-speech, and playback. Each test is independent and can be skipped.

```bash
python check.py
```

### Running

By default, all logs will be printed. You can modify the log filter section in the configuration file to only output error logs, for example:

```yaml
log_filter : True
log_filter_level : WARNING
```

Modify some default options in the configuration file in the root directory:

```yaml
# 是否开启语音输出
voice_output_sw : True

# 是否开启文本输出
text_output_sw : True

# 是否启动时开启语音输入
audio_input_sw : False
```

Start the program:
```bash
python kuon.py
```
