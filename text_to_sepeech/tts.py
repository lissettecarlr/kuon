import time
from loguru import logger
from text_to_sepeech.vits.text_to_audio import TextToAudio
#from vits.text_to_audio import TextToAudio

# 文本转语言
class TTS():
    def __init__(self,config):
        self.ch_list = []
        #print(config)
        if config['TTS']['VITS']['switch'] == True:
            service = TextToAudio(config['TTS']['VITS']['model_path'],config['TTS']['VITS']['config_path'])
            ch = {"service":service,"name":"vits"}
            self.ch_list.append(ch)
        self.count = 0

    # 选择一个进行转换
    def convert(self,text,ch_name = 'vits'):
        # 通过ch_name找到service
        if(self.ch_list == []):
            raise ValueError("ch_list is empty")
        for ch in self.ch_list:
            if ch['name'] == ch_name:
                service = ch['service']
                break
        start_time = time.time()            
        result = service.infer(text)
        #将时间作为文件名   
        result = service.save(result,'text_to_sepeech/temp/{}'.format(str(self.count)))
        self.count += 1 
        logger.debug("转语言文件 {} ,使用 {} ,转换耗时:{}，结果：{}".format(text,ch_name,round(time.time()-start_time,2),result))
        return result
    

if __name__ == "__main__":
    service = TextToAudio("./vits/model/ayaka_167k.pth","./vits/model/ayaka.json")