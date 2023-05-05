from loguru import logger
from queue import Queue
from brain.utils import read_config
from brain.chat import Chat
import threading
import time

class ThinkingThread(threading.Thread):
    def __init__(self,config_path,chat,input_queue:Queue,output_queue:Queue):
        super().__init__()
        self.chat = chat
        self.config = read_config(config_path)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.exit_flag = True
        # 停止命令
        self.cmd_stop_list = self.config["cmdStop"]

    def exit(self):
        self.exit_flag = False
          
    def run(self):
        logger.info("思考线程启动")
        while(self.exit_flag):
            while(not self.input_queue.empty()):
                if(self.exit_flag == False):
                    break
                msg = self.input_queue.get_nowait()
                self.scheduling(msg)
            time.sleep(0.1)
        logger.info("思考线程退出")

    # 传入消息格式{"type":"","content":}
    def scheduling(self,msg):
        if(msg["type"] == "voice"):
            self.voice_thinking(msg["content"])   

    # 处理voice标签的消息
    def voice_thinking(self,text):
        if(self.voice_filtering(text) == False):
            return False
        
        # 判断消息是否属于命令
        if(self.check_cmd(text,self.cmd_stop_list,0.4)):
            msg = {"type":"cmd","content":"stop"}
            return 
        else:
        # 属于聊天则
            response = self.chat.ack(text)
            msg = {"type":"speech","content":response}
        logger.debug("思考线程输出: {}".format(msg))
        self.output_queue.put_nowait(msg)

    # 判断该文本是否值得处理    
    def voice_filtering(self,string):
        return True
    
    # 检测字符串中是否有命令
    def check_cmd(self,s,key_list,percentage):
        for key in key_list:
            if key in s and len(key)/len(s) >= percentage:
                return True
            else:
                return False

class Thinking():
    def __init__(self,input_queue:Queue,output_queue:Queue,config_path = "./cfg/brain_config.json"):

        self.config = read_config(config_path)
        self.chat = Chat(config_path)
        self.thinking_thread = ThinkingThread(config_path,self.chat,input_queue,output_queue)

    def start(self):
        self.thinking_thread.start()
    
    def exit(self):
        self.thinking_thread.exit()