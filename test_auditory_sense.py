from auditory_sense.auditory_sense import auditory
from cfg.config import read_yaml
import threading
from loguru import logger

class auditorySenseTest(threading.Thread):
    def __init__(self):
        super().__init__()
        self.config = read_yaml(r'cfg/kuon.yaml')
        self.service = auditory(self.config)
        self.exit_flag = True
        
    def run(self):
        while(self.exit):
            self.service.audio_processed_event.wait()
            if(self.exit_flag == False):
                break
            while(not self.service.audio_queue.empty()):
                if(self.exit_flag == False):
                    break
                audio_file = self.service.audio_queue.get_nowait()
                logger.debug("接收到语音：{}".format(audio_file))
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
    test = auditorySenseTest()
    test.start()
    input("按任意键退出")
    test.exit()
    test.join()


        



