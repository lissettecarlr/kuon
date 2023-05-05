from json import load, dump
from threading import Lock


class KuonStatus:
    lock = Lock()

    @staticmethod
    def load_config():
        with KuonStatus.lock:
            with open('./cfg/status.json') as file:
                data = load(file)
        return data
    
    @staticmethod
    def save_config(data):
        with KuonStatus.lock:
            with open('./cfg/status.json', 'w') as file:
                dump(data, file, indent=2)
    
    @staticmethod
    def add(key):
        with KuonStatus.lock:
            with open('./cfg/status.json') as file:
                data = load(file)
            if(data[key] <= 0):
                data[key] = 0
            else:
                data[key] = data[key] + 1
            with open('./cfg/status.json', 'w') as file:
                dump(data, file, indent=2)

    @staticmethod
    def sub(key):
        with KuonStatus.lock:
            with open('./cfg/status.json') as file:
                data = load(file)
            if(data[key] <= 0):
                data[key] = 0
            else:
                data[key] = data[key] - 1
            with open('./cfg/status.json', 'w') as file:
                dump(data, file, indent=2)