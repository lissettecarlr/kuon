import queue
import os
import threading
from loguru import logger
from .audio_player import AudioPlayer
import time

class SepeechThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.exit_flag = True
        #待播放的音频地址队列
        self.audio_queue = queue.Queue()
        #当前播放器
        self.player = None

    def input_audio(self,audio_path):
        if os.path.exists(audio_path):
            self.audio_queue.put(audio_path)
        else:
            raise ValueError("audio_path is not exists")

    def exit(self):
        if(self.player != None):
            self.player.stop() 
        self.exit_flag = False 

    def stop_play_all(self):
        # 清空即将播放的
        while(self.audio_queue.empty() == False):
            self.audio_queue.get()
        # 停止正在播放的    
        if(self.player != None):
            self.player.stop() 

    def run(self):
        logger.info("语音播放线程启动")
        while(self.exit_flag):
            while(not self.audio_queue.empty()):
                audio_path = self.audio_queue.get()
                self.player = AudioPlayer(audio_path)
                self.player.play()
                #等待播放完成
                while(self.player.is_alive() and self.exit_flag):
                    time.sleep(0.1)
            time.sleep(0.5)    
        logger.info("语音播放线程退出")

            

