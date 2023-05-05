import multiprocessing

# windows中需要修改源码
# Lib\site-packages\playsound.py，中移除使用utf-16进行解码的部分
from playsound import playsound

class AudioPlayer:
    def __init__(self, audio_file_path):
        self.audio_file_path = audio_file_path
        self.thread = multiprocessing.Process(target=playsound, args=(audio_file_path,))
    def play(self):
        self.thread.start()
    def stop(self):
        self.thread.terminate()
            
######################
# 以下是测试代码
if __name__ == "__main__":
    import time
    # 实例化 AudioPlayer 对象并播放音频
    audio_file_path = r'J:\\code\\kuon\\temp\\output_28473.wav'
    player = AudioPlayer(audio_file_path)
    player.play()
    # 播放 5 秒钟后停止音频
    time.sleep(5)
    print("停止播放")
    player.stop()
