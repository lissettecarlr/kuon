#该分裂思维正用于bingChat

from chatGPT.bingchat.EdgeGPT import Chatbot 
from loguru import logger
import asyncio
from cfg.botConfig import OpenAiConfig
import os

class MultiplethinkingB:
    def __init__(self):
        self.name = "bingChat"
        self.sessions = {} #保存对话对象
        self.lock = asyncio.Lock()
        self.thinking =None
        self.config = OpenAiConfig.load_config()
        self.status = False
        self.keyword = ["/bing","/必应"]

    def activate(self):
        #判断是否存在cookies文件
        cookiesPath = os.path.join(os.path.dirname(__file__),"cfg","bingCookies.json")
        if not os.path.exists(cookiesPath):
            logger.error("bingCookies.json 配置文件未找到！请配置 Bing 到 {}".format(cookiesPath))
            return False
        try:
            self.thinking = Chatbot(cookiePath=cookiesPath)
        except Exception as e:
            logger.warning("{} 初始化失败：{}".format(self.name,e))
            return False
        self.status = True
        return True        

    # message：对话
    async def response(self, message) -> str:
        if(self.thinking == None):
            return ""
        async with self.lock:
            #resp = ""
            resp = (await self.thinking.ask(prompt=message))["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"],
            logger.info("bingChat: {}".format(resp))
            return resp
    
    async def close(self):
        await self.thinking.close()


#测试
if __name__ == "__main__":
    thinking = MultiplethinkingB()
    thinking.activate()
    asyncio.run(thinking.response("你好"))