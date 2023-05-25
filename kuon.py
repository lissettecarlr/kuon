from loguru import logger
from queue import Queue
import time
import threading
import concurrent.futures
# 模块
from auditory_sense.auditory_sense import auditory
from sepeech_to_text.asr import ASR
from thought.Thinking import Thinking
from text_to_sepeech.tts import TTS
from sepeech.sepeech import SepeechThread

from cfg.config import read_yaml


# 输入消息处理线程
# 将接收到的消息转化为固定格式仍到input_message_queue
class input_message_thread(threading.Thread):
    def __init__(self,input_message_queue:Queue,modules):
        super().__init__()
        self.event = threading.Event()
        self.config = read_yaml(r'cfg/kuon.yaml')

        if "audio_reception" in modules:
            self.audio_reception = modules["audio_reception"]
            self.audio_reception.bind_event(self.event)
        else:
            raise Exception("audio_reception模块不存在")
        
        if "asr" in modules:
            self.asr = modules["asr"]
        else:
            raise Exception("asr模块不存在")
        
        self.exit_flag = True        
        self.input_message_queue = input_message_queue
        
        # 绑定事件组 
        # self.events = [self.event,self.audio_reception.audio_processed_event]

    def run(self):
        while(self.exit_flag):
            self.event.wait()
            self.event.clear()
            if(self.exit_flag == False):
                break
            self.audio_input_loop()
  
    def exit(self):
        self.exit_flag = False
        self.event.set()
     
    def audio_input_loop(self):
        while(not self.audio_reception.audio_queue.empty()):
            if(self.exit_flag == False):
                break
            audio_file = self.audio_reception.audio_queue.get_nowait()
            audio_convert = self.asr.convert(audio_file)
            if(audio_convert == ""):
                logger.debug("转换结果为空，不存入消息队列")
                continue
            #logger.debug("转换结果为：{}".format(audio_convert))
            msg = {"type":"auditory","content":audio_convert}
            self.input_message_queue.put_nowait(msg)
            time.sleep(0.1)
            
    def control(self,type,cmd):
        if type == "audio_input":
            if(cmd == "start"):
                self.audio_reception.start()
            elif(cmd == "stop"):
                self.audio_reception.stop()
            else:
                raise ValueError("cmd is not support")

# 输出消息处理线程
class output_message_thread(threading.Thread):
    def __init__(self,output_message_queue:Queue,modules,event:threading.Event=None):
        super().__init__()
        self.event = event
        self.exit_flag = True
        self.output_message_queue = output_message_queue

        if "player" in modules:
            self.player = modules["player"]
        else:
            raise Exception("player模块不存在")
        
        if "tts" in modules:
            self.tts = modules["tts"]
        else:
            raise Exception("tts模块不存在")
        
        if "audio_reception" in modules:
            self.audio_reception = modules["audio_reception"]
    

    def run(self):
        self.player.start()
        while(self.exit_flag):
            while(not self.output_message_queue.empty()):
                    msg = self.output_message_queue.get()
                    self.signal_processor(msg)
            time.sleep(1)
            
    def signal_processor(self,msg):
        # 语音输出消息
        if(msg["type"] == "speech"):
            # 将文本转化为语音
            audio_path = self.tts.convert(msg["content"])
            # 添加进入播放列表
            self.player.input_audio(audio_path)
            
        # 执行命令
        elif(msg["type"] == "cmd"):
            if(msg["content"] == "stop"):
                self.player.stop_play_all()
            elif(msg["content"] == "exit"):
                if(self.event != None):
                    self.event.set()
        else:
            raise ValueError("msg type is not support")

    def exit(self):
        self.player.exit()
        self.exit_flag = False

    def output_message(self,msg):
        logger.debug("输出消息：{}".format(msg))
        


class kuon():
    def __init__(self):
        #该队列用于存放输入消息
        self.input_msg_queue = Queue()    
        self.output_msg_queue = Queue()     

        self.config = read_yaml(r'cfg/kuon.yaml')
        # 将会启动语音的接收
        self.audio_reception = auditory(self.config)        
        # 语音转文字
        self.asr = ASR(self.config)
        # 文本转语音
        self.tts = TTS(self.config)
        # 播放器
        self.player = SepeechThread()

        # 输入消息处理线程，用于将所有输入消息转化为固定通信格式
        modules = { "audio_reception":self.audio_reception,
                    "asr":self.asr,
                    "player":self.player,
                    "tts":self.tts
                }
        self.input_message_manager = input_message_thread(self.input_msg_queue,modules)
        # 输出消息处理线程
        self.output_message_manager = output_message_thread(self.output_msg_queue,modules)
        # 思考线程
        self.thinking = Thinking(self.input_msg_queue,self.output_msg_queue)

    def start(self):
        self.input_message_manager.start()
        self.output_message_manager.start()
        self.thinking.start()
    
    def exit(self):
        self.audio_reception.stop()
        self.player.exit()
        self.input_message_manager.exit()
        self.output_message_manager.exit()
        self.thinking.exit()



if __name__ == "__main__":
    kuon = kuon()
    kuon.start()

    ## 测试代码
    title = "请输入指令（a-录制，b-停止录制，exit-退出）"
    while True:
        user_input = input("{} :".format(title))
        if user_input == "a":
            kuon.audio_reception.start()
        elif user_input == "b":
            kuon.audio_reception.stop()
        elif user_input == "test":
            # msg = {"type":"speech","content":"你好，我是kuon，我是一个智能机器人，我可以回答你的问题，也可以和你聊天。"}  
            # kuon.output_msg_queue.put_nowait(msg)
            kuon.player.input_audio()
        elif user_input == "exit":
            break
        else:
            print("无效的指令，请重新输入")

    kuon.exit()