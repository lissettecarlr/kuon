# 外部通过监听audio_processed_event事件来判断是否有新的音频，然后通过audio_queue队列取出

from loguru import logger
from queue import Queue
import threading

class auditory():
    def __init__(self,config):
        #logger.debug(config)
        self.audio_processed_event = threading.Event()
        # 所有来源的音频地址换成队列
        self.audio_queue = Queue(maxsize=config['local_microphone']['queue_size'])

        self.ch_list = []
        if(config['local_microphone']['switch'] == True):
            from auditory_sense.local_microphone import LocalMicrophone
            ch = {"service":LocalMicrophone(config['local_microphone'],self.audio_processed_event,self.audio_queue),"name":"local_microphone"}
            self.ch_list.append(ch)
            
        # 启动线程
        for ch in self.ch_list:
            ch['service'].start()
    

    def exit(self):
        for ch in self.ch_list:
            ch['service'].exit()



