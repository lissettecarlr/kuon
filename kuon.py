from loguru import logger
from queue import Queue
import time
import threading
from config import read_yaml
from llm.chatgpt import ghost
import os
import platform

# 文本输入下的命令
_HELP_MSG = '''\
文本命令（冒号+命令）:
    :help / :h          显示帮助信息
    :exit / :quit / :q  退出
    :clear / :cl        清屏
    :clear-his / :clh   清除对话历史
    :history / :his     显示对话历史
    :audio-on / :ao     开启语音输出
    :audio-off / :af    关闭语音输出
    
语音命令:
    停止/别说了    将会停止播放语音
'''

# 输入消息处理线程
# 将接收到的消息转化为固定格式仍到input_message_queue
class input_message_thread(threading.Thread):
    def __init__(self,input_message_queue:Queue,event:threading.Event=None):
        super().__init__()
        self.input_event = threading.Event()
        self.output_event = threading.Event()
        self.config = read_yaml('kuon.yaml')

        # 音频输入线程
        from auditory import auditory
        self.audio_input = auditory(event=self.input_event)  
        
        # 文本输入线程
        from text_input import TextInput
        self.text_input = TextInput(self.input_event)
   
        # 语音转文字
        from kuonasr import ASR
        self.asr = ASR()

        self.exit_flag = True        
        self.input_message_queue = input_message_queue
        

    def run(self):
        logger.info("信息输入线程启动")
        # 固定开启文本输入
        self.text_input.start()
        # 根据配置开启语音输入
        if self.config["audio_input_sw"] == True:
            self.audio_input.start()

        while(self.exit_flag):
            self.input_event.wait()
            self.input_event.clear()
            if(self.exit_flag == False):
                break
            self.audio_input_loop()
        logger.info("信息输入线程退出")
    
    def exit(self):
        self.exit_flag = False
        self.audio_input.stop()
        self.text_input.exit()
        self.input_event.set()
     
    def audio_input_loop(self):
        if self.exit_flag == False:
            return
        # 处理音频输入内容
        while not self.audio_input.audio_queue.empty():
            if self.exit_flag == False:
                return
            # 取出音频
            audio_file = self.audio_input.audio_queue.get_nowait()
            # 转换音频
            audio_text = self.asr.convert(audio_file)
            # 将转换结果存入消息队列
            if(audio_text != ""):
                msg = {"from":"audio","content":audio_text}
            self.input_message_queue.put_nowait(msg)
            self.output_event.set()

        # 处理文本输入内容
        while not self.text_input.text_queue.empty():
            if self.exit_flag == False:
                return
            # 取出文本
            text = self.text_input.text_queue.get_nowait()
            # 将文本存入消息队列
            msg = {"from":"text","content":text}
            self.input_message_queue.put_nowait(msg)
            self.output_event.set()

        if self.exit_flag == False:
            return
            
    def control(self,type,cmd):
        if type == "audio_input":
            if(cmd == "start"):
                self.audio_input.start()
            elif(cmd == "stop"):
                self.audio_input.stop()
            else:
                raise ValueError("cmd is not support")
        if type == "text_input":
            if(cmd == "start"):
                self.text_input.start()
            elif(cmd == "stop"):
                self.text_input.exit()
            else:
                raise ValueError("cmd is not support")
# 将线程用于处理输出任务
class digestion_output_thread(threading.Thread):
    def __init__(self,output_message_queue:Queue,event:threading.Event=None):
        super().__init__()
        self.event = event
        self.exit_flag = True
        self.output_message_queue = output_message_queue
        self.config = read_yaml('kuon.yaml')

        from speech import SpeechThread
        self.player = SpeechThread()
        self.player.start()

        from kuontts import TTS
        self.tts = TTS()

  
    def run(self):
        logger.info("信息输出线程启动")
        audio_num = 0
        while(self.exit_flag):
            while not self.output_message_queue.empty():
                msg = self.output_message_queue.get()
                # 如果是文本显示
                if msg["type"] == "text":
                    print("KUON: " + msg["content"])
                # 该任务是播放语音的话
                if(msg["type"] == "speech"):
                    # 将文本转化为语音
                    audio_path = self.tts.convert(msg["content"],"./temp/tts-{}.wav".format(audio_num))
                    audio_num += 1
                    # 添加进入播放列表
                    self.player.input_audio(audio_path)

                # 停止播放语音
                if(msg["type"] in self.config["voice_stop_cmd"]):
                    logger.debug("接收到停止播放语音命令")
                    self.player.stop_play_all()
                

            time.sleep(1)
        logger.info("信息输出线程退出")
            
    def exit(self):
        self.player.exit()
        self.exit_flag = False

        
def kuon():
    config = read_yaml('kuon.yaml')
    if config["log_sw"] == True:
        import sys
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    #该队列用于存放输入消息
    input_msg_queue = Queue()    
    output_msg_queue = Queue()     

    # config = read_yaml('kuon.yaml')

    # 该线程主要用于接收输入，将其转化为统一信息存入self.input_msg_queue
    input_message_manager = input_message_thread(input_msg_queue)
    input_message_manager.start()

    # 输出消息处理线程
    output_message_manager = digestion_output_thread(output_msg_queue)
    output_message_manager.start()

    def kuon_stop():
        logger.info("退出程序")
        ghost.broken()
        input_message_manager.exit()
        output_message_manager.exit()

    def output_text(text):
        if config["text_output_sw"] == True:
            msg = {"type":"text","content":text}
            output_msg_queue.put_nowait(msg)

    def output_speech(text):
        if config["voice_output_sw"] == True:
            msg = {"type":"speech","content":text}
            output_msg_queue.put_nowait(msg)

    while True:
        input_message_manager.output_event.wait()
        input_message_manager.output_event.clear()

        while not input_msg_queue.empty():
            msg = input_msg_queue.get_nowait()
            logger.debug("接收到消息：{}".format(msg))
            content = msg["content"]
            # 首先是文本类命令
            if content.startswith(':'):
                command_words = content[1:].strip().split()
                if not command_words:
                    command = ''
                else:
                    command = command_words[0]

                if command in ['exit','q','quit']:
                    kuon_stop()
                    time.sleep(1)
                    return
                elif command in ['clear', 'cl']:
                    if platform.system() == "Windows":
                        os.system("cls")
                    else:
                        os.system("clear")
                    continue
                elif command in ['help', 'h']:
                    print(_HELP_MSG)
                    continue   
                elif command in ['history', 'his']:
                    print(ghost.conversation)
                    for i in ghost.conversation:
                        print(i["role"] + ":" + i["content"])
                    continue   
                elif command in ['clear-history', 'clh']:
                    ghost.init_conversation()
                    print("\n>>>>历史以清空<<<<\n")
                    continue   
                elif command in ['audio-on', 'ao']:
                    input_message_manager.control("audio_input","start")
                    continue
                elif command in ['audio-off', 'af']:
                    input_message_manager.control("audio_input","stop")
                    continue           
                else:
                    print("未知命令=>{}".format(command))
                    continue

            # 检测字符串中是否有命令
            def check_cmd(s,key_list,percentage):
                for key in key_list:
                    if key in s and len(key)/len(s) >= percentage:
                        return True
                    else:
                        return False   
    
            if(check_cmd(content,config["voice_stop_cmd"],0.4)):
                msg = {"type":"cmd","content":"stop"}
                output_msg_queue.put_nowait(msg)
                continue

            # 正常对话
            try:    
                output_text("（久远思考中）")
                chat_response = ghost.ask(content)
            except Exception as e:
                logger.warning("llm对话失败：{}".format(e))

            # 将其放入到执行任务的队列中去
            output_text(chat_response)
            output_speech(chat_response)

if __name__ == "__main__":
    kuon()
 