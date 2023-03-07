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
        self.extraCommandKeyword = "cmd:"

    def activate(self):
        if (
            not self.config["secretKey"]
        ):
            logger.error("openAiConfig.json 配置文件出错！请配置 OpenAI 的 session_token")
            return False
        try:
            if(self.config["AmnesiacMode"] == "False"):
                memoryTime = 0
            else:
                memoryTime = self.config["memoryTime"]

            if(self.config["preinstall"] != "" and self.config["isloadRPG"] =="True"):
                self.thinking = Chatbot(
                    secret_key = self.config["secretKey"],
                    preset = self.config["preinstall"],
                    memoryTime = memoryTime
                )
            else:
                self.thinking = Chatbot(
                    secret_key = self.config["secretKey"],
                    memoryTime = memoryTime
                )
        except Exception as e:
            logger.warning("{} 初始化失败：{}".format(self.name, e))
            return False
        self.status = True
        return True

    # message：对话，id：谁说的
    async def response(self, message :str) -> str:
        # 从消息中去除keyword
        self.status = False
        for i in self.keyword:
            message = message.replace(i, "")

        resp = ""
        # 判断是否是额外命令
        if message.startswith(self.extraCommandKeyword):
            resp = self.extraCommand(message.replace(self.extraCommandKeyword, ""))
        else:
            async with self.lock:
                resp = self.thinking.ask(message)
        self.status = True
        return resp
        
    #处理额外命令，该类不属于对话    
    def extraCommand(self,message):
        logger.debug("收到额外命令：{}".format(message))
        if(message == "tokens"):
            return "当前消耗tokens={}".format(self.thinking.get_tokens_from_conversation())
        elif(message == "clear preset"):
            self.thinking.set_preset()
            return "清除人设完成"
        elif(message == "reset"):
            self.thinking.clear_conversation()
            return "清空聊天历史"
        else:
            return "未知命令：{}".format(message)
        
    