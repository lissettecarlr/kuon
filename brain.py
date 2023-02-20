from chatGPT.revChatGPT.V1 import Chatbot 
from loguru import logger
from MultiplethinkingA import MultiplethinkingA
from MultiplethinkingB import MultiplethinkingB
from MultiplethinkingC import MultiplethinkingC

from cfg.botConfig import OpenAiConfig
config = OpenAiConfig.load_config()

thinking =None
thinkingA = MultiplethinkingA()
thinkingB = MultiplethinkingB()
thinkingC = MultiplethinkingC()

# 启动时默认思维
def defaultActivate(name = "A"):
    if(activateThinking(name) == False):
        return(False)
    if(changeThinking(name) == False):
        return(False)
    return True

#激活思维
def activateThinking(name = "A"):
    if(name == "A"):
        if thinkingA.status:
            return(True)
        else:
            return(thinkingA.activate())
    elif(name == "B"):
        if thinkingB.status:
            return(True)
        else:
            return(thinkingB.activate())
    elif(name == "C"):
        if thinkingC.status:
            return(True)
        else:
            return(thinkingC.activate())
    else:
        return(False)

#切换思维
def changeThinking(name = "A"):
    global thinking
    if(name == "A" and thinkingA.status):
        thinking = thinkingA
    elif(name == "B" and thinkingB.status):
        thinking = thinkingB
    elif(name == "C" and thinkingC.status):
        thinking = thinkingC
        
        logger.info("切换到思维C")
        logger.info(type(thinking))
    else:
        return(False)
    return(True)

def matchingThinking(text):
    # text 是否包含keyword
    for i in thinkingB.keyword:
        if i in text:
            return 'B'
    for i in thinkingC.keyword:
        if i in text:
            return 'C'
    return 'A'
    
    
async def response(message,ghost = "A"):
    global thinking
    # if(changeThinking(ghost) ==False):
    #     return("切换思维 {} 失败，无法对其应答".format(ghost))
    # else:
    resp = await thinking.response(message)
    return resp
