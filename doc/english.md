# KUON
"kuon, a simple chatbot that is currently integrated with QQ through Mirai and supports Bing and ChatGPT. It has also added the ability to crawl anime magnetic links. This chatbot is still in its early stages, so the code has few dependencies and it's a starting point for future iterations."


##  Current features

* QQ chatbot
* Crawling anime magnetic links
* Conversational AI with GPT-3.5-Turbo model (official documentation states that ChatGPT also uses this model)
    * Short-term memory, timeout forgetting, to prevent insufficient brain capacity (tokens)
    * Character design of kuon
    * Proxy
* bing AI

## 3 Usage

### environment


For information on setting up the [mirai](https://github.com/mamoe/mirai) service, please refer to this [blog](https://blog.kala.love/posts/c367c10b/). If you encounter any errors during login, you can refer to [this](https://mirai.mamoe.net/topic/223/%E6%97%A0%E6%B3%95%E7%99%BB%E5%BD%95%E7%9A%84%E4%B8%B4%E6%97%B6%E5%A4%84%E7%90%86%E6%96%B9%E6%A1%88)."

Code execution environment:
```
Python 3.10.8
pip install -r requirements.txt
```

### configuration
The configuration is saved in the cfg folder, where botconfig.json is the basic configuration, openAiConfig.json is the configuration for ChatGPT, and bingCookies.json is the configuration for Bing. These files are not included in the repository by default. You need to generate them by running a command and then fill in the configuration.
```
python utilty/createExampleCfg.py
```
You can also check the meaning of the configuration items in the createExampleCfg file. The configuration items that need to be filled in are as follows:：

* botconfig.json
    * Mirai configuration, including QQ number, verification code, and the address of the Mirai service.
* openAiConfig.json
    * chatgpt key
* bingCookies.json
    * Bing cookies. The createExampleCfg file does not create it. If you want to use the Bing chatbot, you need to have an account that can access the testing environment on bing.com to export cookies, and then save them to bingCookies.json.

### run

#### QQ
```
python QQbot.py
```
"Then, you can directly chat with the QQ chatbot via private messages. If it's in a group chat, you need to mention the chatbot by @ and then start the conversation."


#### cmd
Testing tools that do not integrate with QQ, enabling communication through local command lines. You can run app.py, but you still need to configure ChatGPT and Bing.

#### Rules during communication
```
/chatgpt xxx  to chatgpt
/bing xxx     to bing
/animate xxx  It is possible to search for and download anime magnetic links.
xxx           Default mode of communication can be configured in botconfig.json.
```

chatgpt的额外命令
```
cmd:tokens           The cost of tokens for retrieving chat history.
cmd:clear preset                
cmd:reset            Clear chat history.
```
