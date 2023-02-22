#该分裂思维正用于chatgpt

from chatGPT.revChatGPT.V1 import Chatbot 
from loguru import logger
import asyncio
from cfg.botConfig import OpenAiConfig
import os

class MultiplethinkingA:
    def __init__(self):
        self.name = "chatGPT-unofficial"
        self.sessions = {} #保存对话对象
        self.lock = asyncio.Lock()
        self.thinking =None
        self.config = OpenAiConfig.load_config()
        self.status = False
        self.keyword = ["/chatgpt"]

    def activate(self):
        if not (self.config["email"] and self.config["password"]) and not self.config["sessionToken"]:
            logger.error("openAiConfig.json 配置文件出错！请配置 OpenAI 的邮箱、密码，或者 session_token")
            return False
        try:
            self.thinking = Chatbot(config={
                        "email": self.config["email"],
                        "password": self.config["password"]
                    })
            logger.info("清空所有对话")
            self.thinking.clear_conversations()
        except Exception as e:
            logger.warning("{} 初始化失败：{}".format(self.name,e))
            return False
        self.status = True
        return True        

    # message：对话，id：谁说的
    async def response(self, message) -> str:
        #从消息中去除keyword
        for i in self.keyword:
            message = message.replace(i,"")
        async with self.lock:
            resp = ""
            for data in self.thinking.ask(
                prompt = message,
                #conversation_id = self.conversation_id
            ):
                resp = data["message"]
            return resp
    

    async def knowingOneself(self):
        if(self.thinking == None):
            return False
        logger.info("开始认识自我")
        for tel in self.config["preinstall"]:
            resp = await self.response(tel)
            logger.info("{}".format(resp))
        logger.info("结束认识自我")