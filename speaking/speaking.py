#from moegoe.speaking_moegoe import TextToAudio

from speaking.vits.text_to_audio import TextToAudio
from speaking.audio_player import AudioPlayer

from loguru import logger
from json import load, dump,dumps
import os
import random

# config_path配置文件地址
class mouth():
    def __init__(self,config_path):
        self.config = mouth.read_config(config_path)
        if(self.config == None):
            raise Exception("{} config error".format(config_path))
        # 转换后的文件保存位置
        self.output_path = self.config["output_path"]
        # 状态 busy or idle or exit
        self.status = "idle"
        # 传入模型和模型的配置文件位置
        self.text_to_audio = TextToAudio(self.config["model"],self.config["model_config"])
        # 播放器
        self.player = None

    def convert(self,text):
        output_file = "output_" + str(random.randint(999,100000))+".wav"
        output_file = os.path.join(self.output_path,output_file)
   
        audio = self.text_to_audio.convert(text)
        self.text_to_audio.save(audio,output_file)
        return output_file
    
    def speaking(self,audio_file):
        # 判断该位置文件是否存在
        if not os.path.exists(audio_file):
            logger.error("Audio file {} not found".format(audio_file))
            return None
        
        self.player = AudioPlayer(audio_file)
        self.player.play()

        # output_file = self.convert(text)
        # # 临时播放方式
        # from winsound import PlaySound
        # PlaySound(output_file,1)
        # return output_file
    
    def stop(self):
        if(self.player != None):
            self.player.stop()
            self.player = None

    @staticmethod
    def read_config(config_path):
        # 判断config_path是否存在
        if not os.path.exists(config_path):
            logger.error("Config file {} not found".format(config_path))
            return None
        # 判断文件后缀是否是json
        if not config_path.endswith(".json"):
            logger.error("Config file {} is not a json file".format(config_path))
            return None
        # 加载配置
        with open(config_path) as file:
            config = load(file)
        return config