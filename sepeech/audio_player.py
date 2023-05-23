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
            
    def is_alive(self):
        return self.thread.is_alive()
    
######################
# 以下是测试代码
import time


def main():
    global flag
    flag = False
    audio_file_path = r'J:\code\kuon\text_to_sepeech\temp\0.wav'

    player = AudioPlayer(audio_file_path)
    player.play()

    while True:
        if(player.is_alive()):
            print("播放中")
        else:
            print("播放结束")

        if(flag == True):
            print("触发回调")
            flag = False

        time.sleep(1)
        # if(flag == True):
        #     print("退出")
        #     break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("退出")


