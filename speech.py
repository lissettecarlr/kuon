# 该文件用于播放语音

import multiprocessing

# windows中需要修改源码
# Lib\site-packages\playsound.py，中移除使用utf-16进行解码的部分
from playsound import playsound

class AudioPlayer:
    '''
    音频播放器
    通过传入音频文件地址，开启新进程进行播放
    '''
    def __init__(self, audio_file_path):
        self.audio_file_path = audio_file_path
        self.thread = multiprocessing.Process(target=playsound, args=(audio_file_path,))

    def play(self):
        self.thread.start()

    def stop(self):
        self.thread.terminate()
            
    def is_alive(self):
        return self.thread.is_alive()
    


import queue
import os
import threading
import time

class SpeechThread(threading.Thread):
    '''
    播放管理器
    - 根据播放队列进行逐个播放
    '''
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
        try:
            while(self.exit_flag):
                while(not self.audio_queue.empty()):
                    #print("开始播放")
                    audio_path = self.audio_queue.get()
                    #logger.debug("开始播放:{}".format(audio_path))
                    self.player = AudioPlayer(audio_path)
                    self.player.play()
                    #等待播放完成
                    while(self.player.is_alive() and self.exit_flag):
                        time.sleep(0.1)
                    #logger.debug("播放完成:{}".format(audio_path))
                time.sleep(0.1)    
        except Exception as e:
            raise e
        #logger.info("语音播放线程退出")    