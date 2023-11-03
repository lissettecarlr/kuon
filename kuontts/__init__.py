import yaml
from loguru import logger
import time


class TTS:
    def __init__(self) -> None:
        with open('./kuontts/config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        if config['channel'] == "offline":
            from .offline import OfflineTTS
            self.server = OfflineTTS()
        elif config['channel'] == 'online':
            from .online import OnlineTTS
            self.server = OnlineTTS(config["api_url"])
        self.speaker = config["speaker"]
        logger.info("tts init [{}]".format(config['channel']))
        
    def convert(self,text:str,save_path:str=None):
        logger.debug("开始生成语音")
        res,output = self.server.run(text=text,save_path=save_path,speaker=self.speaker)
        logger.debug("语音生成结束")
        rate = output[0]
        audio = output[1]

        if res == 'Success':
            return audio
        else:
            raise Exception("语音生成失败:{}".format(output))