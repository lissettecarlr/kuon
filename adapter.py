import requests
import numpy as np
from loguru import logger
from config import read_yaml


# 文本转语音，目前使用的是接口方式
def adapter_tts(text:str,aduio_path=None):
    cfg = read_yaml('kuon.yaml')

    # 如果是接口方式使用
    url = cfg["TTS"]["api_url"]
    response = requests.post(url, json= {"text": text})
    if response.status_code == 200:
        data = response.json()
        if data["result"] == "Success":
            rate = data["rate"]
            audio = np.array(data["audio"], dtype=np.float32)
            if aduio_path != None:
                import scipy.io.wavfile as wavf
                wavf.write(aduio_path,rate, audio)
                logger.debug("tts转换完成：{}".format(aduio_path))
                return aduio_path
            else:
                logger.debug("tts转换完成")
                return audio 
        logger.warning("tts转换失败：{}".format(data["message"]))
        return None
    else:
        logger.warning("请求错误,status_code:{}", response.status_code)
        return None
    
    # 如果是本地方式使用
    # 待写

## 语音转文本
def adapter_asr(audio_path:str):
    from kuonasr import ASR
    import os
    asr = ASR()
    if os.path.exists(audio_path):
        try:
            result = asr.convert(audio_path)
            logger.debug("asr转换完成：{}".format(result))
            return result
        except Exception as e:
            logger.warning("asr转换失败：{}".format(e))
            return None
    else:
        logger.warning("asr文件不存在：{}".format(audio_path))
        return None



if __name__ == '__main__':
    adapter_tts("你好！很高兴见到你","./temp/tts-test.wav")
    #adapter_asr(r"kuonasr\audio\asr_example.wav")