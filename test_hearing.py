from hearing.hearing import hearing
from loguru import logger
from queue import Queue
import time

if __name__ == "__main__":
    msg_queue = Queue()    
    kuon_hearing = hearing(msg_queue)
    kuon_hearing.start()

    try:
        while True:
            while(not msg_queue.empty()):
                logger.info("收到: {}".format(msg_queue.get_nowait()))
            time.sleep(0.5)
    except:
        kuon_hearing.exit()