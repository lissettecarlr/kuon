
from loguru import logger
from cfg.config import read_yaml
from thought.soul.persona import persona 

if __name__ == '__main__':
    config = read_yaml(r'cfg/kuon.yaml')
    test = persona(config)
    for i in test.ask_stream('你现在要回复我一段中文的文字，这段文字需要超过两句话。回复中必须用中文标点'):
        logger.info(i)
    #print(test.chatbot.conversation)
