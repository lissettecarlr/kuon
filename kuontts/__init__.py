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
    
    def convert(self,text:str,save_path:str=None):
        res,audio = self.server.run(text=text,save_path=save_path)
        if res == 'Success':
            return audio
        else:
            logger.warning("转换失败：{}".format(audio))
            return None