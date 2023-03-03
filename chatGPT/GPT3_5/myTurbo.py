# 调用openai的官方接口
# 参考 https://platform.openai.com/docs/api-reference/completions/create

import openai
import sys

class Chatbot:
    def __init__(self,secret_key,temperature=0.7,preset="你现在是名字叫久远的AI") -> None:
        openai.api_key  = secret_key   # openai的secret key，在https://platform.openai.com/account/api-keys这个页面去创建
        self.model = "gpt-3.5-turbo"   # 或者 gpt-3.5-turbo-0301
        self.temperature = temperature # 请求时不传入默认为1 较高的值（如 0.8）将使输出更加随机，而较低的值（如 0.2）将使输出更加集中和确定
        self.conversation = [{"role": "system", "content": preset}] # 历史对话 
    def ask(self, msg: str):
        prompt = {"role": "user", "content": msg}
        self.conversation.append(prompt)
        #print(self.conversation)
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages= self.conversation,
            )
            res = response.choices[0].message.content.strip()
            self.conversation.append({"role": "assistant", "content": res})
            return res
        except Exception as e:
            return f"发生错误: {e}"

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
    chatbot = Chatbot(args.api_key)
     
    try:
        while True:
            prompt = get_input("\nYou:\n")
            print("ChatGPT:")
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