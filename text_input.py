# 文本输入交互的功能
# 开启新线程持续监听输入，当有输入时，事件通知，并将其存入队列
import threading
from queue import Queue
from loguru import logger
import time

class TextInput(threading.Thread):
    def __init__(self,event:threading.Event=None) -> None:
        super().__init__()
        # 该事件用于通知外部有新的文本输入
        if(event == None):
            self.event = threading.Event()
        else:
            self.event = event

        self.text_queue = Queue(maxsize=3)
        self.exit_flag = True
        self.show_text = ""

    # 退出线程
    def exit(self):
        self.exit_flag = False
        self.event.set()

    #绑定事件
    def bind_event(self,event:threading.Event):
        self.event = event

    def run(self):
        logger.info("文本输入线程启动")
        while self.exit_flag:
            try:
                self.text = input(self.show_text).strip()
            except UnicodeDecodeError:
                print('[ERROR] Encoding error in input')
            except KeyboardInterrupt:
                break

            if self.exit_flag == False:
                break
            if self.text:
                self.text_queue.put_nowait(self.text)
                self.event.set()
                time.sleep(1)

        logger.info("文本输入线程退出")
            

if __name__ == "__main__":
    text_input = TextInput()
    text_input.start()
   
    while True:
        text_input.event.wait()
        text_input.event.clear()
        while not text_input.text_queue.empty():
            text = text_input.text_queue.get_nowait()
            print("输入的文本：{}".format(text))
            if(text == "q" or text == "exit"):
                text_input.exit()
                exit()
    

