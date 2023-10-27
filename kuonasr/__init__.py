import yaml
with open('./kuonasr/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    
from loguru import logger
import time
class ASR:
    def __init__(self) -> None:
        if config['channel'] == "parafomer":
            from kuonasr.Paraformer import paraformer 
            self.service = paraformer()  
        elif config['channel'] == "whisper_online":
            from kuonasr.whisper_online.whisper_app import Whispers
            key = config['OPENAI']['key']
            self.service = Whispers(key)
        elif config['channel'] == 'funasr':
            from kuonasr.funasr.client import FunASRClient
            self.service = FunASRClient(config['funasr']['url'])

        logger.info("asr init : {}".format(config['channel']))
   
    def test(self):
        logger.debug("asr test")
        audio_path = "./kuonasr/audio/asr_example.wav"
        result = self.convert(audio_path) 
        logger.debug("asr test result:{}".format(result))
     

    def convert(self,audio_path):
        if config['channel'] == "parafomer" or config['channel'] == "whisper_online":
            start_time = time.time()
            try:
                result = self.service.infer(audio_path) 
            except Exception as e:
                raise ValueError("语音转换失败，错误信息：{}".format(e))
            logger.info("asr over. 文件 {} ,转换耗时:{}，结果：{}".format(audio_path,round(time.time()-start_time,2),result))
            return result
        
        elif config['channel'] == 'funasr':
            import asyncio
            start_time = time.time()
            try:
                result = asyncio.run(self.service.filter(audio_path))
            except Exception as e:
                raise ValueError("语音转换失败，错误信息：{}".format(e))
            logger.info("asr over. 文件 {} ,转换耗时:{}，结果：{}".format(audio_path,round(time.time()-start_time,2),result))
            return result
        
        else:
            raise ValueError("不支持的asr服务,请检查配置文件channel字段")