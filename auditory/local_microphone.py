# 使用pyaudio录制音频
import wave
import numpy as np
import pyaudio
from loguru import logger
from threading import Event
# 线程
import threading
from queue import Queue
import tempfile

class LocalMicrophone(threading.Thread):
    def __init__(self,config,event:threading.Event,audio_queue):
        super().__init__()
        self.event = event
        self.config = config

        self.audio_queue = audio_queue
        self.chunk = 4096 #采样位数
        self.format = pyaudio.paInt16
        self.rate = self.config["rate"] #48000 #采样率
        self.channels =  self.config["channels"] #1 #通道数
        self.threshold = self.config["threshold"] #1600 #录音阈值

        self.exit_flag = True
        logger.info("init LocalMicrophone")
    
    def bind_event(self,event:threading.Event):
        self.event = event

    # 退出线程
    def exit(self):
        self.exit_flag = False
        self.event.set()

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk )

        logger.info('本地麦克风接收启动,当前阈值:{}'.format(self.threshold))
        frames = []
        recording=False
        nowavenum=0
        while (self.exit_flag):
            # 检测是否有声音
            if recording==False:
                #print('检测中... ')
                # 采集小段声音
                frames=[]
                for i in range(0, 4):
                    data = stream.read(self.chunk ,exception_on_overflow=False)
                    frames.append(data)

                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                large_sample_count = np.sum( audio_data >= self.threshold/3 )

                # 如果有符合条件的声音，则开始录制
                # temp = np.max(audio_data)
                # if temp > THRESHOLD :

                if large_sample_count >= self.threshold*1.8:
                    logger.debug("检测到人声，开始录制")
                    recording=True
            else:
                while True:
                    logger.debug("持续录音中...")
                    subframes=[]
                    for i in range(0, 5):
                        data = stream.read(self.chunk ,exception_on_overflow=False)
                        subframes.append(data)
                        frames.append(data)

                    audio_data = np.frombuffer(b''.join(subframes), dtype=np.int16)
                    temp = np.max(audio_data)

                    if temp <= self.threshold*0.8:
                        nowavenum+=1
                    else:
                        nowavenum=0

                    if nowavenum>=1 or self.exit_flag == False:
                        logger.debug("录制结束")
                        j=1
                        while j>0:
                            frames.pop()
                            j-=1
             
                        # 将音频保存到本地
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
                            with wave.open(temp_audio_file.name, 'wb') as wf:
                                wf.setnchannels(self.channels)
                                wf.setsampwidth(p.get_sample_size(self.format))
                                wf.setframerate(self.rate)
                                wf.writeframes(b''.join(frames))
                        logger.debug("保存： {}".format(temp_audio_file.name))
                        # 将保存的录音地址存入队列，并且发出事件
                        self.audio_queue.put_nowait(temp_audio_file.name)
                        self.event.set()

                        nowavenum=0
                        frames=[]
                        recording=False

                        if(self.exit_flag == False):
                            return
                        break
                    
        stream.stop_stream()
        stream.close()
        p.terminate()
        logger.info("本地麦克风接收线程退出")

 