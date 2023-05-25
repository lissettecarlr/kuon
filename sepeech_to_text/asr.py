import time
from loguru import logger

class ASR():
    def __init__(self,config):
        self.ch_list = []
        
        if config['ASR']['parafomer'] == True:
            from sepeech_to_text.Paraformer import paraformer   
            service = paraformer()
            ch = {"service":service,"name":"parafomer"}
            self.ch_list.append(ch)

        if config['ASR']['whisper_online'] == True:
            from sepeech_to_text.whisper_online.whisper_app import Whispers
            service = Whispers(config['OPENAI']['key'])
            ch = {"service":service,"name":"whisper_online"}
            self.ch_list.append(ch)
    
    # 选择一个进行转换
    def convert(self,audio_path,ch_name = 'parafomer'):
        # 通过ch_name找到service
        for ch in self.ch_list:
            if ch['name'] == ch_name:
                service = ch['service']
                break
        logger.debug("开始语音转文本")    
        start_time = time.time()            
        result = service.infer(audio_path)    
        logger.debug("结束语音转文本，文件 {} ,使用 {} ,转换耗时:{}，结果：{}".format(audio_path,ch_name,round(time.time()-start_time,2),result))
        return result
    
