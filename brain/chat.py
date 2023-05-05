from .openai_chatgpt import Chatgpt
from .utils import read_config
from loguru import logger

class Chat():
    def __init__(self,config_path):
        # 加载配置
        self.config = read_config(config_path)
        if (not self.config["secretKey"]):
            logger.error("配置文件缺少openai的key")
        try:
            if(self.config["AmnesiacMode"] == "False"):
                memoryTime = 0
            else:
                memoryTime = self.config["memoryTime"]

            if(self.config["preinstall"] != "" and self.config["isloadRPG"] =="True"):
                chatgpt = Chatgpt(
                    secret_key = self.config["secretKey"],
                    preset = self.config["preinstall"],
                    memoryTime = memoryTime,
                    proxy = self.config["proxy"],
                    url=self.config["apiUrl"],
                    model=self.config["model"],
                )
            else:
                chatgpt = Chatgpt(
                    secret_key = self.config["secretKey"],
                    memoryTime = memoryTime
                )
            self.core = chatgpt
        except Exception as e:
            logger.warning("chatgpt 初始化失败：{}".format(e))     

    def ack(self,message):
        resp = self.core.ask(message)
        return resp
