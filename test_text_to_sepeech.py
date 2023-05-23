# 用于测试文本转语言

import wave
import numpy as np
import pyaudio
from text_to_sepeech.TTService import TTService

def test_tts():
    from text_to_sepeech.tts import TTS
    from cfg.config import read_yaml
    config = read_yaml(r'cfg/kuon.yaml')
    tts = TTS(config)
    tts.convert("你好，我是kuon，我是一个智能机器人，我可以回答你的问题，也可以和你聊天。")


if __name__ == '__main__':
    test_tts()
