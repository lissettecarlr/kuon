from hearing.utils import read_config,save_config
from hearing.microphone_audio_pa import RecordAudioThread
from hearing.audio_to_text_wsp import Whispers

import threading
from threading import Event
from queue import Queue
import threading
from loguru import logger

class audioToTextThread(threading.Thread):
    def __init__(self,config_path,event:Event,converter,audio_queue:Queue,text_queue:Queue=None):
        super().__init__()
        # 接收音频信号
        self.event = event
        # 接收音频的队列
        self.audio_queue = audio_queue
        # 转换器
        self.converter = converter

        self.config = read_config(config_path)
        self.exit_flag = True
 
        # text_queue 作为输出队列
        if(text_queue == None):
            logger.info("未传入输出队列，使用内部队列")
            self.text_queue = Queue(maxsize=self.config["recordTextQueueSize"])
        else:
            self.text_queue = text_queue
       
    #退出线程
    def exit(self):
        self.exit_flag = False
        self.event.set()   

    #清空队列
    def clear_queue(self):
        while not self.audio_queue.empty():
            self.audio_queue.get()
        # while not self.text_queue.empty():
        #     self.text_queue.get()

    def run(self):
        logger.info("音频转换线程启动")
        while(self.exit_flag):
            self.event.wait()
            #退出
            if(self.exit_flag == False):
                break
            
            while(not self.audio_queue.empty()):
                if(self.exit_flag == False):
                    break
                audio_file = self.audio_queue.get_nowait()
                result = self.converter.convert(audio_file)
                if(result == ""):
                    logger.debug("转换结果为空，不存入队列")
                else:
                    msg = {"type":"voice","content":result}
                    self.text_queue.put_nowait(msg)
            self.event.clear()
            if(self.exit_flag == False):
                break    
        logger.info("音频转换线程退出")


class hearing():
    def __init__(self,text_queue:Queue=None):
        config_path="./cfg/hearing_config.json"
        self.voice_processed_event = threading.Event()
        self.record_aduio = RecordAudioThread(config_path,self.voice_processed_event)
        self.whispers = Whispers(config_path)
        self.audio_to_text = audioToTextThread(config_path,self.voice_processed_event,self.whispers,self.record_aduio.audio_queue,text_queue)
    
    def start(self):
        self.record_aduio.start()
        self.audio_to_text.start()

    def exit(self):
        self.audio_to_text.exit()
        self.record_aduio.exit()

