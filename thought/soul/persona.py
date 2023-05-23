
from loguru import logger
import time
from thought.soul.openai_chatgpt import Chatgpt


class persona():
    def __init__(self, config):
        
        self.counter = 0
        if config['chatgpt']['amnesiac_mode']:
            memoryTime = config['chatgpt']['memoryTime']
        else:
            memoryTime = 0

        if config['chatgpt']['rpg_mode']:
            preset = config['chatgpt']['preinstall']
        else:
            preset = None

        self.chatbot = Chatgpt(secret_key=config['OPENAI']['key'],
                               proxy=config['OPENAI']['proxy'],
                               memoryTime = memoryTime,
                               temperature=config['chatgpt']['temperature'],
                               preset=preset)
        logger.info('init Chatgpt')

    def ask(self, text):
        complete_text = ""
        #stime = time.time()

        self.counter += 1
        try:
            for data in self.chatbot.ask_stream(text):
                message =  data
                if ("。" in message or "！" in message or "？" in message or "\n" in message) and len(complete_text) > 3:
                    complete_text += message
                    #logger.debug('ChatGPT Stream Response: %s, @Time %.2f' % (complete_text, time.time() - stime))
                    yield complete_text.strip()
                    complete_text = ""
                else:
                    complete_text += message
            if complete_text.strip():
                #logger.debug('ChatGPT Stream Response: %s, @Time %.2f' % (complete_text, time.time() - stime))
                yield complete_text.strip()
        except Exception as e:
            logger.error('ChatGPT Stream Error: %s' % e)
            yield "我好像迷失了"

 
