from loguru import logger
from json import load, dump,dumps
import os

def read_config(config_path):
    # 判断config_path是否存在
    if not os.path.exists(config_path):
        logger.error("Config file {} not found".format(config_path))
        return None
    # 判断文件后缀是否是json
    if not config_path.endswith(".json"):
        logger.error("Config file {} is not a json file".format(config_path))
        return None
    # 加载配置
    with open(config_path) as file:
        config = load(file)
    return config


def save_config(data,config_path):
    with open(config_path, 'w') as file:
        dump(data, file, indent=2)