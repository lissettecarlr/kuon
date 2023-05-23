from .rapid_paraformer import RapidParaformer
from loguru import logger


config_path = r'sepeech_to_text/Paraformer/resources/config.yaml'

class paraformer():
    def __init__(self):
        logger.info('init paraformer')
        self.paraformer = RapidParaformer(config_path)

    def infer(self, wav_path):
        result = self.paraformer(wav_path)
        return result[0]
    
