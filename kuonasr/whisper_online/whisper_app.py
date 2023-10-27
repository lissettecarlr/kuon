# 使用whisper的方式进行语音转文字

import openai
import langid

class Whispers():
    def __init__(self,key):
        openai.api_key = key

    def infer(self,audio_path):
        try:
            with open(audio_path, 'rb') as audio_file:
                response = openai.Audio.transcribe('whisper-1', audio_file,language="zh")
        except Exception as e:
            raise ValueError("语音转换失败，错误信息：{}".format(e))
        result = response.get('text')
        if(self.filter(result) ==False):
            raise ValueError("该结果不符合要求，已经被过滤")
        return result

    # 过滤 单个字符可能也会返回false
    def filter(self,text):
        lang, prob = langid.classify(text)
        if lang == 'zh' or lang == 'en':
            return True
        else:
            return False 
        

if __name__ == '__main__':
    key = ""
    audio_path = "../audio/asr_example.wav"
    service = Whispers(key)
    result = service.infer(audio_path) 
    print(result)        