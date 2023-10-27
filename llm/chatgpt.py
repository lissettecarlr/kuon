# 该文件使用请求方式与openai的chatgpt模型通信

import requests
import sys
import json
import tiktoken
import threading
from loguru import logger
import os

class Chatgpt():
    def __init__(self,secret_key,temperature=0.7,preset=None,
                  memoryTime=120, # 对话保存时间
                  url = "https://api.openai.com/v1/chat/completions",
                  model = "gpt-3.5-turbo-16k",
                 ) -> None:
        
        self.session = requests.Session()
        self.post_url = url
        self.post_headers = {
            'Authorization': 'Bearer ' + secret_key
        }
        self.model = model   # 或者 gpt-3.5-turbo-0301
        self.temperature = temperature # 请求时不传入默认为1 较高的值（如 0.8）将使输出更加随机，而较低的值（如 0.2）将使输出更加集中和确定
        self.conversationMaxSize = 8000 # 使用16k模型 输入输出均分8k
        
        self.preset = preset # 人设地址
        self.conversation = [] # 历史对话
        self.timer_last_conversation = None # 记忆的定时器
        self.memoryTime = memoryTime #记忆时间，单位秒，超时则清空对话历史，为0则不自动清除

        self.init_conversation()
      
    def __del__(self):
        self.broken()

    # 当不使用时调用   
    def broken(self):
        if self.timer_last_conversation is not None:
            self.timer_last_conversation.cancel()

    def ask(self, msg: str):
        prompt = {"role": "user", "content": msg}
        self.conversation.append(prompt)

        if(self.model not in ["Qwen-7B"]):
            tokens = self.get_tokens_from_conversation()
            if tokens > self.conversationMaxSize :
                return "对话太长了，我记不住了，请清空对话历史"
            logger.debug("输入消耗tokens:{}".format(tokens)) #测试
        try:
            #清除定时器
            if self.timer_last_conversation is not None:
                self.timer_last_conversation.cancel()

            response = self.session.post(
                self.post_url,
                headers=self.post_headers,
                json={
                    "model": self.model,
                    "messages":self.conversation,
                    "stream": False,
                    "temperature": self.temperature,
                }
            )

            if response.status_code != 200:
                self.conversation.pop() # 对话失败，将输入从历史中移除
                return f"请求错误: {response.status_code} {response.text}"
            else:
                response_json = response.json()
                completions = response_json['choices']
                ret = []
                for completion in completions:
                    role = completion['message']["role"]
                    content =  completion['message']["content"]   
                    self.conversation.append({"role": role, "content": content})
                    if(role == "assistant"):
                        ret.append(content)
            
            # 开启定时器
            self.__startTimer()
            return " ".join(ret)
        except Exception as e:
            return f"发生错误: {e}"
        
    def ask_stream(self,msg: str):
        prompt = {"role": "user", "content": msg}
        self.conversation.append(prompt)
        tokens = self.get_tokens_from_conversation()
        if tokens > self.conversationMaxSize :
            return "对话太长了，我记不住了，请清空对话历史"
        logger.debug("输入消耗tokens:{}".format(tokens)) #测试 


        response = self.session.post(
            self.post_url,
            headers=self.post_headers,
            json={
                "model": self.model,
                "messages":self.conversation,
                "stream": True,
                "temperature": self.temperature,
            },
            timeout=60,
            stream=True,
        )
        if response.status_code != 200:
            self.conversation.pop() # 对话失败，将输入从历史中移除
            return f"请求错误: {response.status_code} {response.text}"
        
        response_role: str or None = None

        full_response: str = ""
        for line in response.iter_lines():
            if not line:
                continue
            # Remove "data: "
            line = line.decode("utf-8")[6:]
            if line == "[DONE]":
                break
            resp: dict = json.loads(line)
            choices = resp.get("choices")
            if not choices:
                continue
            delta = choices[0].get("delta")
            if not delta:
                continue

            if "role" in delta:
                response_role = delta["role"]

            if "content" in delta:
                content = delta["content"]
                full_response += content
                yield content

        self.conversation.append({"role": response_role, "content": full_response})
        
    #初始化历史对话
    def init_conversation(self):
        #如果人设配置地址文件存在
        if(self.preset is not None and os.path.exists(self.preset)):
            re = self.load_conversation(self.preset)
            if(re == False):
                logger.warning("人设配置文件加载失败")
        else:
            self.conversation=[]
    
    #清除人设
    def clear_preset(self):
        self.preset = None
        self.init_conversation()

    # 加载历史对话，会清空当前的对话历史
    def load_conversation(self,file):
        self.conversation = []
        try:
            with open(file, encoding="utf-8") as f:
                self.conversation = json.load(f)
        except Exception as e:
            return None
        return True
    
    def save_conversation(self,file):
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.conversation, f, ensure_ascii=False, indent=4)
        except Exception as e:
            return f"保存对话发送错误: {e}"
        return "保存对话成功"
    
    # 获取当前conversation中的tokens数量
    def get_tokens_from_conversation(self):
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except Exception as e:
            print(f"Error: {e}")
            return 0
        num_tokens = 0
        #print(self.conversation) #!!!!!!!!!!!!!!
        for message in self.conversation:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    #启动超时定时器
    def __startTimer(self):
        if(self.memoryTime != 0):
            self.timer_last_conversation = threading.Timer(self.memoryTime, self.__timeout_last_conversation)
            self.timer_last_conversation.start()

    #上一次对话超时，用于清空历史
    def __timeout_last_conversation(self):
        self.init_conversation()
        logger.debug("超时，清空对话")

    # 输出配置参数
    def self_introduction(self):
        it = "api方案，使用{}模型，应答误差值为{}，限制tokens<{}，对话记忆时间为{}秒".format(self.model,self.temperature,self.conversationMaxSize,self.memoryTime)
        if self.preset is None :
            it += "，未加载人设"
        else:
            it += "，已加载人设"
        if self.proxy is None or self.proxy == "":
            it += "，未使用代理"
        else:
            it += "，使用代理:{}".format(self.proxy)
        return it
    
import yaml

def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config

cfg = load_config("llm/config.yaml")

ghost = Chatgpt(url = cfg["url"],
                secret_key= cfg["key"],
                model = cfg["model"],
                memoryTime= cfg["timeout"],
                preset=cfg["preset"])

#####################################################################
# 以下为本文将测试代码

def get_input(prompt):
    print(prompt, end="")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    user_input = "\n".join(lines)
    return user_input

def main():
    import argparse
    print("模型的聊天测试")
    try:
        while True:
            prompt = get_input("\nYou:\n")
            print("Kuon:")
            result = ghost.ask(prompt)
            print(result, end="")
            print("\n")
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()