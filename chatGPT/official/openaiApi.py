import requests
import sys
import json
import tiktoken
import threading
from loguru import logger
import os

class Chatbot():
    def __init__(self,secret_key,proxy="",temperature=0.7,preset=None,memoryTime=120) -> None:
        
        self.session = requests.Session()
        self.post_url = "https://api.openai.com/v1/chat/completions"
        self.post_headers = {
            'Authorization': 'Bearer ' + secret_key
        }
        self.model = "gpt-3.5-turbo"   # 或者 gpt-3.5-turbo-0301
        self.temperature = temperature # 请求时不传入默认为1 较高的值（如 0.8）将使输出更加随机，而较低的值（如 0.2）将使输出更加集中和确定
        self.conversationMaxSize = 3000 # gpt-3.5-turbo模型最大tokens数为4096，这里设置3K是为了给应答留空间
        
        self.preset = preset # 人设地址
        self.conversation = [] # 历史对话
        self.timer_last_conversation = None # 记忆的定时器
        self.memoryTime = memoryTime #记忆时间，单位秒，超时则清空对话历史，为0则不自动清除
         

        #是否使用代理
        # if proxy:
        #     self.session.proxies = {
        #         "http": proxy,
        #         "https": proxy,
        #     }
        #     print("使用代理:{}".format(proxy))
        #上面方式传入发现特么会报错连不上代理，暂时不晓得那里有问题，就先下面方式直接拼接url了
        if proxy:
            self.post_url = proxy + "/v1/chat/completions"
            print("使用代理:{}".format(self.post_url))

        self.init_conversation()
        

    # 当不使用时调用   
    def broken(self):
        if self.timer_last_conversation is not None:
            self.timer_last_conversation.cancel()

    def ask(self, msg: str):
        prompt = {"role": "user", "content": msg}
        self.conversation.append(prompt)
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

    
## 测试用
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
    print("基于openai接口，gpt-3.5-turbo模型的聊天测试")
    # Get API key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_key",
        type=str,
        required=True,
        help="OpenAI API key",
    )
    args = parser.parse_args()
    # Initialize chatbot
    # test preset
    preset = "../../cfg/kuon.json"
    
    #chatbot = Chatbot(args.api_key,memoryTime=10)
    chatbot = Chatbot(args.api_key,memoryTime=10,preset=preset)
    
    try:
        while True:
            prompt = get_input("\nYou:\n")
            print("Kuon:")
            result = chatbot.ask(prompt)
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