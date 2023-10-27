# 外部通过监听audio_processed_event事件来判断是否有新的音频，然后通过audio_queue队列取出
from queue import Queue
import threading
from auditory.local_microphone import LocalMicrophone

#{"local_microphone" : {"switch":True,"threshold":1500,"channels":1,"rate":48000,"queue_size":10,}}
class auditory():
    def __init__(self,config=None,event:threading.Event=None):
        if config == None:
            import yaml
            with open('./auditory/config.yaml', 'r') as file:
                self.config = yaml.safe_load(file)
             
        else:
            self.config = config

        if(event == None):
            self.audio_processed_event = threading.Event()
        else:
            self.audio_processed_event = event
        # 所有来源的音频地址换成队列
        self.audio_queue = Queue(maxsize=self.config['local_microphone']['queue_size'])
        self.ch_list = []

    #绑定事件
    def bind_event(self,event:threading.Event):
        self.audio_processed_event = event
        for ch in self.ch_list:
            ch['service'].bind_event(event)
            
    def start(self):
        self.ch_list = []
        # 本地麦克风
        if(self.config['local_microphone']['switch'] == True):
            ch = {"service":LocalMicrophone(self.config['local_microphone'],self.audio_processed_event,self.audio_queue),"name":"local_microphone"}
            self.ch_list.append(ch)

        # 启动线程
        for ch in self.ch_list:
            if(ch['service'].is_alive() == True):
                raise Exception("{} 线程已经启动".format(ch['name']))
            else:
                ch['service'].start()

    def stop(self):
        for ch in self.ch_list:
            ch['service'].exit()



