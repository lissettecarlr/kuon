# 用于测试思维

from loguru import logger
from cfg.botConfig import BotConfig
config = BotConfig.load_config()
import brain
import asyncio

def main():
    def handle_commands(command: str) -> bool:
        if command == "!help":
            print(
            """
            输入问答后敲击两次回车进行发送，由于是回答一次显示，所以可能会比较慢
            其他命令则以!开始，如下
            !reset - 清空历史对话（还没做）
            !exit - 退出程序
            """,
            )
        elif command == "!reset":
            pass
        elif command == "!exit":
            exit(0)
        else:
            return False
        return True

    while True:
        print("\n输入:\n", end="")
        lines = []
        while True:
            line = input()
            #检测到输入空字符时退出
            if line == "":
                break
            lines.append(line)
        user_input = "\n".join(lines)

        #检测到命令符
        if user_input.startswith("!"):
            if handle_commands(user_input):
                continue

        tk,contents = brain.matchingThinking(user_input)
        logger.info("切换到思维：{}".format(tk))
        brain.activateThinking(tk) #激活
        brain.changeThinking(tk) #切换
       
        if brain.thinking is None:
            logger.error("不存在激活的思维")
            return 
        
        print("Kuon: ")
        res = asyncio.run(brain.response(contents))
        print(res,end="")
        # prev_text = ""
        # for data in chatbot.ask(
        #     prompt,
        # ):
        #     message = data["message"][len(prev_text) :]
        #     print(message, end="", flush=True)
        #     prev_text = data["message"]
        # print()
        # print(message["message"])


def init():
    res = asyncio.run(brain.defaultActivate())
    if(res):
        logger.info("思维A启动成功")
        return True
    else:
        logger.info("思维A启动失败，程序即将退出")
        return False

if __name__ == '__main__':
    logger.info("开始唤醒")
    if(init() == False):
        exit(0)
    logger.info("启动完成，可以输入:!help查看说明")
    main()