from hearing.hearing import hearing
from brain.Thinking import Thinking
from speaking import kuon_spesking

from loguru import logger
from queue import Queue
import time


if __name__ == "__main__":
    #该队列用于存放输入消息
    input_msg_queue = Queue()    
    output_msg_queue = Queue()

    # 启动听觉
    kuon_hearing = hearing(input_msg_queue)
    kuon_hearing.start()

    # 启动思考
    kuon_thinking = Thinking(input_msg_queue,output_msg_queue)
    kuon_thinking.start()

    try:
        while True:
            if(not output_msg_queue.empty()):
                msg = output_msg_queue.get_nowait()
                logger.info("处理消息输出: {}".format(msg))
                # 语音输出
                if(msg["type"] == "speech"):
                    audio_file = kuon_spesking.convert(msg["content"])
                    kuon_spesking.speaking(audio_file)
                # 操作命令相关处理    
                elif(msg["type"] == "cmd"):
                    if(msg["content"] == "stop"):
                        kuon_spesking.stop()
            # logger.info("输入队列状态：{}，输出队列状态：{}".format(input_msg_queue.qsize(),output_msg_queue.qsize()))
            time.sleep(1)
    except:
        kuon_hearing.exit()
        kuon_thinking.exit()