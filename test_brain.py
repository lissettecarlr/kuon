from brain.Thinking import Thinking
from loguru import logger
from queue import Queue
import time


if __name__ == "__main__":
    input_msg_queue = Queue()
    output_msg_queue = Queue()
    kuon_thinking = Thinking(input_msg_queue,output_msg_queue)
    kuon_thinking.start()

    input_msg_queue.put_nowait({"type":"voice","content":"你好"})

    try:
        while True:
            while(not output_msg_queue.empty()):
                logger.info("收到: {}".format(output_msg_queue.get_nowait()))
            time.sleep(0.5)         
    except:
        kuon_thinking.exit()


   
            
        