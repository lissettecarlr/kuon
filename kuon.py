

from thought.Thinking import Thinking

# from speaking import kuon_spesking

from loguru import logger
from queue import Queue
import time

from auditory_sense.auditory_sense import auditory
from cfg.config import read_yaml
import threading
from sepeech_to_text.asr import ASR



# 语音接收处理线程
class auditoryThread(threading.Thread):
    def __init__(self,audio_text_queue:Queue):
        super().__init__()
        self.config = read_yaml(r'cfg/kuon.yaml')
        # 将会启动语音的接收
        self.service = auditory(self.config)
        # 语音转文字
        self.asr = ASR(self.config)

        self.exit_flag = True
        self.audio_text_queue = audio_text_queue
        
    def run(self):
        while(self.exit):
            self.service.audio_processed_event.wait()
            if(self.exit_flag == False):
                break
            while(not self.service.audio_queue.empty()):
                if(self.exit_flag == False):
                    break
                audio_file = self.service.audio_queue.get_nowait()
                # 进行语音转文字

                result = self.asr.convert(audio_file)
                if(result == ""):
                    logger.debug("转换结果为空，不存入队列")
                else:
                    msg = {"type":"auditory","content":result}
                    self.audio_text_queue.put_nowait(msg)

            self.service.audio_processed_event.clear()
            if(self.exit_flag == False):
                break    
        logger.info("auditory_sense测试线程退出")


    #退出线程
    def exit(self):
        self.service.exit()
        self.exit_flag = False
        self.service.audio_processed_event.set()  



if __name__ == "__main__":
    #该队列用于存放输入消息
    input_msg_queue = Queue()    
    output_msg_queue = Queue()

    #听觉线程，用于将声音转化为文本存入input_msg_queue
    kuon_auditory = auditoryThread(input_msg_queue)
    kuon_auditory.start()

    # 启动思考
    kuon_thinking = Thinking(input_msg_queue,output_msg_queue)
    kuon_thinking.start()

    try:
        while True:
            if(not output_msg_queue.empty()):
                msg = output_msg_queue.get_nowait()
                logger.info("处理消息输出: {}".format(msg))
                
                # 语音输出
                # if(msg["type"] == "speech"):
                #     audio_file = kuon_spesking.convert(msg["content"])
                #     kuon_spesking.speaking(audio_file)
                # 操作命令相关处理    
                # elif(msg["type"] == "cmd"):
                #     if(msg["content"] == "stop"):
                #         kuon_spesking.stop()
            # logger.info("输入队列状态：{}，输出队列状态：{}".format(input_msg_queue.qsize(),output_msg_queue.qsize()))
            time.sleep(1)
    except:
        kuon_auditory.exit()
        kuon_thinking.exit()