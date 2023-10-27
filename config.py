from pathlib import Path
import yaml
from typing import Dict, Union


def read_yaml(yaml_path: Union[str, Path]) -> Dict:
    if not Path(yaml_path).exists():
        raise FileExistsError(f"The {yaml_path} does not exist.")

    with open(str(yaml_path), "rb") as f:
        data = yaml.load(f, Loader=yaml.Loader)

    # 如果存在include字段，则递归读取include的yaml文件
    if "include" in data:
        include = data.pop("include")

        if isinstance(include, str):
            include = [include]
        for i in include:
            data.update(read_yaml(Path(yaml_path).parent / i))
    return data


from json import load, dump
from threading import Lock


class KuonStatus:
    lock = Lock()

    @staticmethod
    def load_config():
        with KuonStatus.lock:
            with open("./cfg/status.json") as file:
                data = load(file)
        return data

    @staticmethod
    def save_config(data):
        with KuonStatus.lock:
            with open("./cfg/status.json", "w") as file:
                dump(data, file, indent=2)

    @staticmethod
    def add(key):
        with KuonStatus.lock:
            with open("./cfg/status.json") as file:
                data = load(file)
            if data[key] <= 0:
                data[key] = 0
            else:
                data[key] = data[key] + 1
            with open("./cfg/status.json", "w") as file:
                dump(data, file, indent=2)

    @staticmethod
    def sub(key):
        with KuonStatus.lock:
            with open("./cfg/status.json") as file:
                data = load(file)
            if data[key] <= 0:
                data[key] = 0
            else:
                data[key] = data[key] - 1
            with open("./cfg/status.json", "w") as file:
                dump(data, file, indent=2)
