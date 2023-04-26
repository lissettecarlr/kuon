import wave
import datetime
import numpy as np
import pyaudio
from loguru import logger
# 线程
import threading
from queue import Queue
import tempfile


class RecordThread(threading.Thread):
    def __init__(self, queue: Queue):
        super().__init__()
        self._stop_event = threading.Event()
        self.audio_queue = queue

    def stop(self):
        self._stop_event.set()

    def run(self):
        
        CHUNK = 4096 #录音时每次采集的帧数
        FORMAT = pyaudio.paInt16 #采样位数
        CHANNELS = 1 #通道数
        RATE = 48000 #采样率
        THRESHOLD = 1000 #录音阈值

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        logger.info('开始监听,当前阈值:{}'.format(THRESHOLD))
        frames = []
        recording=False
        nowavenum=0

        while (not self._stop_event.is_set()):
            # 检测是否有声音
            if recording==False:
                # print('检测中... ')
                # 采集小段声音
                frames=[]
                for i in range(0, 4):
                    data = stream.read(CHUNK,exception_on_overflow=False)
                    frames.append(data)

                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                large_sample_count = np.sum( audio_data >= THRESHOLD/3 )

                # 如果有符合条件的声音，则开始录制
                # temp = np.max(audio_data)
                # if temp > THRESHOLD :
                if large_sample_count >= THRESHOLD*1.8:
                    logger.debug("检测到人声，开始录制")
                    recording=True
            else:
                while True:
                    logger.debug("持续录音中...")
                    subframes=[]
                    for i in range(0, 5):
                        data = stream.read(CHUNK,exception_on_overflow=False)
                        subframes.append(data)
                        frames.append(data)

                    audio_data = np.frombuffer(b''.join(subframes), dtype=np.int16)
                    temp = np.max(audio_data)
                    if temp <= THRESHOLD*0.8:
                        nowavenum+=1
                    else:
                        nowavenum=0

                    if nowavenum>=1:
                        logger.debug("录制结束")
                        j=1
                        while j>0:
                            frames.pop()
                            j-=1
             
                        # 将音频保存到本地
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
                            with wave.open(temp_audio_file.name, 'wb') as wf:
                                wf.setnchannels(CHANNELS)
                                wf.setsampwidth(p.get_sample_size(FORMAT))
                                wf.setframerate(RATE)
                                wf.writeframes(b''.join(frames))
                        logger.debug("保存： {}".format(temp_audio_file.name))

                        self.audio_queue.put(temp_audio_file.name)
                        nowavenum=0
                        frames=[]
                        recording=False
                        break


        stream.stop_stream()
        stream.close()
        p.terminate()





import time
import signal
import os
flag =True

def sigint_handler(signal, frame):
    global flag
    print("正在停止录制，请稍候...")
    thread.stop()
    thread.join()
    flag = False
    exit(0)

if __name__ == "__main__":
    #show_microphone_info()
    q = Queue()
    thread = RecordThread(q)
    thread.start()

    signal.signal(signal.SIGINT, sigint_handler)

    while flag:
        try:
            audio_file = q.get(timeout=1)
            print(audio_file) 
            os.remove(audio_file)
        except:
            continue
        
 