# 该分裂思维正用于chatgpt

from revChatGPT.V3 import Chatbot
from loguru import logger
import asyncio
from cfg.botConfig import OpenAiConfig


class MultiplethinkingD:
    def __init__(self):
        self.name = "chatGPT-official"
        self.sessions = {}  # 保存对话对象
        self.lock = asyncio.Lock()
        self.thinking = None
        self.config = OpenAiConfig.load_config()
        self.status = False
        self.keyword = ["/chatgpt_official"]

    def activate(self):
        if not (self.config["api_key"]):
            logger.error(
                "openAiConfig.json 配置文件出错！api_key不存在")
            return False
        try:
            self.thinking = Chatbot(api_key=self.config["api_key"])
            logger.info("chatGPT: 初始化成功")
            # self.thinking.clear_conversations()
        except Exception as e:
            logger.warning("{} 初始化失败：{}".format(self.name, e))
            return False
        self.status = True
        return True

    # message：对话，id：谁说的
    async def response(self, message) -> str:
        # 从消息中去除keyword
        for i in self.keyword:
            message = message.replace(i, "")
        async with self.lock:
            resp = ""
            try:
                resp = self.thinking.ask(message)
                #    resp = data
                #    print(data, end="", flush=True)
                logger.info("chatGPT: {}".format(resp))
            except Exception as e:
                resp = "太坏了~已经溢出来了 >_<\n不过我还要❤️"
                logger.warning("{} 出现异常：{}".format(self.name, e))
                self.status = False
            return resp


# 测试
if __name__ == "__main__":
    thinking = MultiplethinkingD()
    thinking.activate()
    asyncio.run(thinking.response("你好"))
