from chatGPT.revChatGPT.V1 import Chatbot
from cfg.botConfig import OpenAiConfig
config = OpenAiConfig.load_config()

thinking = Chatbot(
    config={
        "email": config["email"],
        "password": config["password"],
    }
)

prompt = "你好"
response = ""

for data in thinking.ask(
  prompt,
  conversation_id="kuon"
): 
    response = data["message"]
print(response)