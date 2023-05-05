# 使用whisper的方式进行语音转文字


import os
import openai
from loguru import logger
from .utils import read_config,save_config
import time
import langid


class Whispers():
    def __init__(self,config_path):
        self.config = read_config(config_path)
        openai.api_key = self.config["openaiKey"]

    def convert(self,audio_path):
        start_time = time.time()
        try:
            with open(audio_path, 'rb') as audio_file:
                response = openai.Audio.transcribe('whisper-1', audio_file,language="zh")
        except Exception as e:
            logger.warning("openai api error:{}".format(e))
            return ""
        end_time = time.time()
        result = response.get('text')
        logger.debug("文件 {} 转换完成 api耗时:{}，结果：{}".format(audio_path,round(end_time-start_time,2),result))
        if(self.filter(result) ==False):
            logger.debug("该结果不符合要求，已经被过滤")
            result = ""
        os.remove(audio_path)
        return result

    # 过滤 单个字符可能也会返回false
    def filter(self,text):
        lang, prob = langid.classify(text)
        if lang == 'zh' or lang == 'en':
            return True
        else:
            return False 