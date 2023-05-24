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

    def suspend(self):
        self.service.audio_processed_event.clear()
        self.service.exit()

    #退出线程
    def exit(self):
        self.service.exit()
        self.exit_flag = False
        self.service.audio_processed_event.set()  
            

class auditory_sense_controller():
    def __init__(self):
        super().__init__()
        self.config = read_yaml(r'cfg/kuon.yaml')
        self.service = auditory(self.config)
    
    def start(self):
        self.service.start()

    def stop(self):
        self.service.stop()

    def output(self):
        while(not self.service.audio_queue.empty()):
            audio_file = self.service.audio_queue.get_nowait()
            logger.debug("接收到语音：{}".format(audio_file))
            
if __name__ == "__main__":
    test = auditory_sense_controller()
    while True:
        user_input = input("请输入指令（a-录制，b-停止，c-退出，d-输出接收内容）：")
        if user_input == "a":
            test.start()
        elif user_input == "b":
            test.stop()
        elif user_input == "c":
            test.stop()
            break
        elif user_input == "d":
            test.output()
        else:
            print("无效的指令，请重新输入")
