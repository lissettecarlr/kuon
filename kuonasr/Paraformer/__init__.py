from .src import RapidParaformer
config_path = r'kuonasr/Paraformer/config.yaml'

class paraformer():
    def __init__(self):
        self.paraformer = RapidParaformer(config_path)
    def infer(self, wav_path):
        result = self.paraformer(wav_path)
        return result[0]
    
