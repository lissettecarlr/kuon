from loguru import logger
from MultiplethinkingA import MultiplethinkingA
from MultiplethinkingB import MultiplethinkingB
from MultiplethinkingC import MultiplethinkingC
from MultiplethinkingD import MultiplethinkingD

from cfg.botConfig import OpenAiConfig
from cfg.botConfig import BotConfig

#config = OpenAiConfig.load_config()

#默认思维
defaultThinking = BotConfig.load_config()["defaultThinking"]

thinking = None
thinkingA = MultiplethinkingA()
thinkingB = MultiplethinkingB()
thinkingC = MultiplethinkingC()
thinkingD = MultiplethinkingD()

# 启动时默认思维
async def defaultActivate():
    if(activateThinking(defaultThinking) == False):
        return False
    if(changeThinking(defaultThinking) == False):
        return False
    return True

# 激活思维
def activateThinking(name="A"):
    if name in ['A','B','C','D']:
        if name == "A" and thinkingA.thinking is None:
            return thinkingA.activate()
        elif name == "B" and thinkingB.thinking is None:
            return thinkingB.activate()
        elif name == "C" and thinkingC.thinking is None:
            return thinkingC.activate()
        elif name == "D" and thinkingD.thinking is None:
            return thinkingD.activate()
        else:
            return True
    else:
        return False

# 切换思维
def changeThinking(name="A"):
    global thinking
    if name == "A" and thinkingA.thinking is not None:
        thinking = thinkingA
    elif name == "B" and thinkingB.thinking is not None:
        thinking = thinkingB
    elif name == "C" and thinkingC.thinking is not None:
        thinking = thinkingC
    elif name == "D" and thinkingD.thinking is not None:
        thinking = thinkingD
    else:
        return False
    return True

# 通过消息判断判断选用什么思维，例如 /bing xxx， /animate xxx
# 返回 思维名和去掉命令的文本
def matchingThinking(text:str):
    if text.startswith("/"):
        #以/开头则认为是指定思维，否则则使用默认思维
        parts = text.split(" ", maxsplit=1)
        character = parts[0]
        message = parts[1] if len(parts) > 1 else ""
        for i in thinkingA.keyword:
            if i in character:
                return "A",message
        for i in thinkingB.keyword:
            if i in character:
                return "B",message
        for i in thinkingC.keyword:
            if i in character:
                return "C",message
        for i in thinkingD.keyword:
            if i in character:
                return "D",message
    else:
        return defaultThinking,text

async def response(message, ghost="A"):
    global thinking
    if(thinking.status == False):
        return("思考中，别烦我啦")
    # if(changeThinking(ghost) ==False):
    #     return("切换思维 {} 失败，无法对其应答".format(ghost))
    # else:
    resp = await thinking.response(message)
    return resp

def closs():
    thinkingA.deactivate()
