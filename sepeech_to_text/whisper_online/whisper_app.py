# 使用whisper的方式进行语音转文字


import os
import openai
from loguru import logger
import time
import langid


class Whispers():
    def __init__(self,key):
        logger.info('init whispers_online')
        openai.api_key = key

    def infer(self,audio_path):
        start_time = time.time()
        try:
            with open(audio_path, 'rb') as audio_file:
                response = openai.Audio.transcribe('whisper-1', audio_file,language="zh")
        except Exception as e:
            logger.warning("openai api error:{}".format(e))
            return ""
        result = response.get('text')
        if(self.filter(result) ==False):
            logger.debug("该结果不符合要求，已经被过滤")
            result = ""
        #os.remove(audio_path)
        return result

    # 过滤 单个字符可能也会返回false
    def filter(self,text):
        lang, prob = langid.classify(text)
        if lang == 'zh' or lang == 'en':
            return True
        else:
            return False 