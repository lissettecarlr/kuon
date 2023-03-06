# 该分裂思维用于chatgpt
from loguru import logger
import asyncio
from cfg.botConfig import OpenAiConfig
import os
from chatGPT.GPT3_5.myTurbo import Chatbot

class MultiplethinkingA:
    def __init__(self):
        self.name = "chatGPT"
        self.lock = asyncio.Lock()
        self.thinking = None   #作为存活判断
        self.config = OpenAiConfig.load_config()
        self.status = False    #作为是否忙的判断
        self.keyword = ["/chatgpt"]

    def activate(self):
        if (
            not self.config["secretKey"]
        ):
            logger.error("openAiConfig.json 配置文件出错！请配置 OpenAI 的 session_token")
            return False
        try:
            if(self.config["preinstall"] != "" and self.config["isloadRPG"] =="True"):
                self.thinking = Chatbot(
                    secret_key = self.config["secretKey"],
                    preset = self.config["preinstall"]
                )
            else:
                self.thinking = Chatbot(
                    secret_key = self.config["secretKey"]
                )
        except Exception as e:
            logger.warning("{} 初始化失败：{}".format(self.name, e))
            return False
        self.status = True
        return True

    # message：对话，id：谁说的
    async def response(self, message) -> str:
        # 从消息中去除keyword
        self.status = False
        for i in self.keyword:
            message = message.replace(i, "")
        async with self.lock:
            resp = ""
            resp = self.thinking.ask(message)
            self.status = True
            return resp
        
    def knowingOneself(self):
        self.thinking.setPreset(self.config["preinstall"])
