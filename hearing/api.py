try:
    from audio_to_text import whisper_openai
except:
    from hearing.audio_to_text import whisper_openai

try:
    from microphone_audio_pa import RecordThread
except:
    from hearing.microphone_audio_pa import RecordThread

from queue import Queue
import threading

# * inin初始化
# * audio2text音频转文字
# * auto持续监听，将通过关键词进行触发对话
# * stop停止监听

class hearing(threading.Thread):
    def __init__(self, queue: Queue):
        super().__init__()
        self._stop_event = threading.Event()
        self.voice_queue = Queue()
        self.text_queue = queue
        self.rcv_audio_thread = RecordThread(self.voice_queue)

    def stop(self):
        self.rcv_audio_thread.stop()
        self._stop_event.set()

    def run(self):
        self.rcv_audio_thread.start()
        while (not self._stop_event.is_set()):
            try:
                audio_file = self.voice_queue.get(timeout=1)
                result = whisper_openai(audio_file)
                self.text_queue.put(result)
            except:
                pass


#test improt
import signal
from loguru import logger
flag = True

def sigint_handler(signal, frame):
    global flag
    logger.info("正在停止录制，请稍候...")
    thread.stop()
    flag = False
    exit(0)

if __name__ == "__main__":

    # 启动录音线程
    text_queue = Queue()
    thread = hearing(text_queue)
    thread.start()

    signal.signal(signal.SIGINT, sigint_handler)
    while flag:
        try:
            text = text_queue.get(timeout=1)
            logger.info(text)
        except:
            pass


