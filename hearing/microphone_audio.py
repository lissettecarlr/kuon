from loguru import logger
import tempfile
import wave
import numpy as np
import sounddevice as sd
import webrtcvad
import threading
from queue import Queue


def record(status_queue=None, stop_recording_flag=None, config=None):
    sample_rate = 16000
    frame_duration = 30  # 30ms, supported values: 10, 20, 30
    buffer_duration = 300  # 300ms
    # 停止转录前等待的静默时长
    silence_duration =  900 

    vad = webrtcvad.Vad(3)  # Aggressiveness mode: 3 (highest)
    buffer = []
    recording = []
    num_silent_frames = 0
    num_buffer_frames = buffer_duration // frame_duration
    # 以为是30ms一次检测，所有这里除以30
    num_silence_frames = silence_duration // frame_duration
    # try:
    print('开始录制...')

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16', blocksize=sample_rate * frame_duration // 1000,
                        callback=lambda indata, frames, time, status: buffer.extend(indata[:, 0])):
        # 循环读取
        # while not stop_recording_flag():
        while True:
            # 最小判断，480个采样点
            if len(buffer) < sample_rate * frame_duration // 1000:
                continue

            frame = buffer[:sample_rate * frame_duration // 1000]
            buffer = buffer[sample_rate * frame_duration // 1000:]

            # 检测是否是语音，也即有没有人说话
            is_speech = vad.is_speech(np.array(frame).tobytes(), sample_rate)
            if is_speech:
                recording.extend(frame)
                num_silent_frames = 0
            else:
                if len(recording) > 0:
                    num_silent_frames += 1

                if num_silent_frames >= num_silence_frames:
                    break

    audio_data = np.array(recording, dtype=np.int16)
    print('Recording finished. Size:', audio_data.size)
    
    # 将音频保存到本地
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
        with wave.open(temp_audio_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes (16 bits) per sample
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())

    logger.info("Saved audio to {}".format(temp_audio_file.name))
    return temp_audio_file.name


class RecordThread(threading.Thread):
    def __init__(self, queue: Queue):
        super().__init__()
        self._stop_event = threading.Event()
        self.audio_queue = queue

        self.sample_rate = 16000
        self.frame_duration = 30 # ms, supported values: 10, 20, 30
        self.buffer_duration = 300 # ms
        self.silence_duration = 900 # ms
        self.vad = webrtcvad.Vad(3) # Aggressiveness mode: 3 (highest)
        self.buffer = []
        self.recording = []
        self.num_silent_frames = 0
        self.num_buffer_frames = self.buffer_duration // self.frame_duration
        self.num_silence_frames = self.silence_duration // self.frame_duration

    def run(self):
        print('开始录制...')  
        with sd.InputStream(samplerate=self.sample_rate,
                            channels=1, dtype='int16',
                            blocksize=self.sample_rate * self.frame_duration // 1000,
                            callback=lambda indata, frames, time, status: self.buffer.extend(indata[:, 0])):   
            while not self._stop_event.is_set():
                # 最小判断，480个采样点
                if len(self.buffer) < self.sample_rate * self.frame_duration // 1000:
                    continue

                frame = self.buffer[:self.sample_rate * self.frame_duration // 1000]
                self.buffer = self.buffer[self.sample_rate * self.frame_duration // 1000:]

                # 检测是否是语音，也即有没有人说话
                is_speech = self.vad.is_speech(np.array(frame).tobytes(), self.sample_rate)
                if is_speech:
                    self.recording.extend(frame)
                    self.num_silent_frames = 0
                else:
                    if len(self.recording) > 0:
                        self.num_silent_frames += 1

                    if self.num_silent_frames >= self.num_silence_frames:
                        audio_data = np.array(self.recording, dtype=np.int16)
                        logger.info('片段录制完成. Size:', audio_data.size)

                        # 将音频保存到本地
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
                            with wave.open(temp_audio_file.name, 'wb') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)  # 2 bytes (16 bits) per sample
                                wf.setframerate(self.sample_rate)
                                wf.writeframes(audio_data.tobytes())
                        logger.info("保存： {}".format(temp_audio_file.name))

                        self.audio_queue.put(temp_audio_file.name)
                        self.buffer = []
                        self.recording = []
                        self.num_silent_frames = 0
                  
    def stop(self):
        self._stop_event.set()


import time
import signal

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
        except:
            continue
        # 处理获取到的音频文件地址
        print(audio_file) # 示例代码，打印音频文件地址
        # 可以在这里将处理后的结果传递给主线程进行进一步处理