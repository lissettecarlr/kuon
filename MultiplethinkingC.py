#该分裂思维正用于爬虫

from scraper.animate.app import spiderAnimate
from loguru import logger
import asyncio
from cfg.botConfig import OpenAiConfig
import os

class MultiplethinkingC:
    def __init__(self):
        self.name = "spiderAnimate"
        self.thinking = None
        self.config = OpenAiConfig.load_config()
        self.status = False
        self.keyword = ["/animate","/动画"]
        self.lock = asyncio.Lock()

    def activate(self):
        try:
            self.thinking = spiderAnimate()
        except Exception as e:
            logger.warning("{} 初始化失败：{}".format(self.name,e))
            return False
        self.status = True
        return True        

    async def response(self, message) -> str:
        if(self.thinking == None):
            return ""
        #从消息中去除keyword
        for i in self.keyword:
            message = message.replace(i,"")
        async with self.lock:
            l = {"name":message,"key":""}
            #resp = ""
            logger.info("开始爬取：{}".format(l))
            resp = (await self.thinking.task(l))
            if resp is not None:
                text = ""
                for i in resp:
                    text += i["title"] + "：" + i["magent"] + "\n"
                logger.info("爬取完成：{}".format(text))                
                return text
            else:
                return "未找到资源 ：{}".format(message)
          

#测试
if __name__ == "__main__":
    thinking = MultiplethinkingC()
    thinking.activate()
    asyncio.run(thinking.response("冰海战记 s2 06"))