# brain

## 说明

通过队列输入消息，根据不同类型进行处理，然后通过另一个队列输出处理结果。

输入消息类别 : voice, torch
输出处理结果 : action, speech 

## 文件

chat.py ： 该文件用于对接大型语言模型，属于中间层
openai_chatgpt ：该文件是对接的chatpgt，然后被chat.py调用
Thinking ： 该文件就是主要的处理逻辑
