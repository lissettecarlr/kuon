from json import load, dump

class BotConfig:
    @staticmethod
    def load_config():
        with open('./cfg/botconfig.json') as file:
            data = load(file)
        return data
    
    @staticmethod
    def save_config(data):
        with open('./cfg/botconfig.json', 'w') as file:
            dump(data, file, indent=2)

class OpenAiConfig:
    @staticmethod
    def load_config():
        with open('./cfg/openAiConfig.json') as file:
            data = load(file)
        return data
    
    @staticmethod
    def save_config(data):
        with open('./cfg/openAiConfig.json', 'w') as file:
            dump(data, file, indent=2)