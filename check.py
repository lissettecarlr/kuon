from speech import SpeechThread
import time
import os


# 测试播放
def check_speech():
    print("播放测试开始")
    try:
        sp = SpeechThread()
        sp.start()
        sp.input_audio("./kuonasr/audio/asr_example.wav")
        time.sleep(5)
        sp.exit()
        return True
    except:
        return False


# 测试语音合成
def check_tts():
    print("语音合成测试开始")
    from kuontts import TTS

    tts = TTS()
    temp_file = "./temp/tts-test.wav"
    if os.path.exists(temp_file):
        # 删除文件
        os.remove(temp_file)
    res = tts.convert(text="你好，很高兴认识你", save_path=temp_file)
    if res == None:
        print("语音合成失败")
        return False
    if os.path.exists(temp_file):
        print("语音合成成功")
        return True
    return False


# 测试语音转文字
def check_asr():
    print("语音转文字测试开始")
    from kuonasr import ASR

    asr = ASR()
    try:
        result = asr.convert("./kuonasr/audio/asr_example.wav")
        print(result)
        return True
    except:
        print("语音转文字失败")
        return False


# 测试对话模型
def check_llm():
    from llm.chatgpt import ghost

    print("对话模型测试开始")
    try:
        result = ghost.ask("你好")
        print("你好")
        print("llm :{}".format(result))
        ghost.broken()
        return result
    except Exception as e:
        print(e)
        return None


# 测试语言接收
from auditory import auditory
import threading

# from loguru import logger
# logger.remove()
# logger.level("DEBUG")


class auditorySenseTest(threading.Thread):
    def __init__(self):
        super().__init__()
        self.config = {
            "local_microphone": {
                "switch": True,
                "threshold": 1000,
                "channels": 1,
                "rate": 48000,
                "queue_size": 10,
            }
        }
        self.service = auditory(self.config)
        self.exit_flag = True

    def run(self):
        while self.exit:
            # 当接收到音频后会触发该事件
            self.service.audio_processed_event.wait()
            if self.exit_flag == False:
                break
            # 触发事件后查看音频队列中是否有内容
            while not self.service.audio_queue.empty():
                if self.exit_flag == False:
                    break
                # 取出内容
                audio_file = self.service.audio_queue.get_nowait()
                print("接收到语音：{}".format(audio_file))
                os.remove(audio_file)
            # 清除事件标志
            self.service.audio_processed_event.clear()
            if self.exit_flag == False:
                break

    def open_microphone(self):
        self.service.start()

    def close_microphone(self):
        self.service.audio_processed_event.clear()
        self.service.stop()

    # 退出线程
    def exit(self):
        self.service.stop()
        self.exit_flag = False
        self.service.audio_processed_event.set()


def check_auditory():
    print("语言接收测试开始")
    test = auditorySenseTest()
    test.start()
    while True:
        user_input = input("请输入指令（a-录制，b-停止，c-退出）：")
        if user_input == "a":
            test.open_microphone()
        elif user_input == "b":
            test.close_microphone()
        elif user_input == "c":
            test.exit()
            break
        else:
            print("无效的指令，请重新输入")
    print("语言接收测试接收")


if __name__ == "__main__":
    choice = input("是否需要测试语音输入? (Y/N): ")
    while choice.upper() not in ["Y", "N"]:
        print("输入错误。Please enter Y or N.")
        choice = input("是否需要测试语音输入? (Y/N): ")
    if choice.upper() == "Y":
        check_auditory()
    print("-" * 20)

    choice = input("是否需要测试语音播放? (Y/N): ")
    while choice.upper() not in ["Y", "N"]:
        print("输入错误。Please enter Y or N.")
        choice = input("是否需要测试语音播放? (Y/N): ")
    if choice.upper() == "Y":
        check_speech()
    print("-" * 20)

    choice = input("是否需要测试文本转语音? (Y/N): ")
    while choice.upper() not in ["Y", "N"]:
        print("输入错误。Please enter Y or N.")
        choice = input("是否需要测试文本转语音? (Y/N): ")
    if choice.upper() == "Y":
        check_tts()
    print("-" * 20)

    choice = input("是否需要测试语音转文本? (Y/N): ")
    while choice.upper() not in ["Y", "N"]:
        print("输入错误。Please enter Y or N.")
        choice = input("是否需要测试语音转文本? (Y/N): ")
    if choice.upper() == "Y":
        check_asr()
    print("-" * 20)

    choice = input("是否需要测试对话模型? (Y/N): ")
    while choice.upper() not in ["Y", "N"]:
        print("输入错误。Please enter Y or N.")
        choice = input("是否需要测试对话模型? (Y/N): ")
    if choice.upper() == "Y":
        check_llm()
    print("-" * 20)
