import os, sys

sys.path.append(os.getcwd())

from io import BytesIO
from typing import Union
from typing_extensions import Annotated
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config as ariadne_config,
)
from graia.ariadne.message import Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import DetectPrefix, MentionMe
from graia.ariadne.event.mirai import (
    NewFriendRequestEvent,
    BotInvitedJoinGroupRequestEvent,
)
from graia.ariadne.message.element import Image
from graia.ariadne.model import Friend, Group
from graia.ariadne.event.lifecycle import AccountLaunch
from loguru import logger

import asyncio
from utils.text_to_img import text_to_image
from cfg.botConfig import BotConfig

config = BotConfig.load_config()
import brain


# Refer to https://graia.readthedocs.io/ariadne/quickstart/
# 使用graia对接mirai
app = Ariadne(
    ariadne_config(
        config["mirai"]["qq"],
        config["mirai"]["verifyKey"],
        HttpClientConfig(host=config["mirai"]["http"]),
        WebsocketClientConfig(host=config["mirai"]["ws"]),
    ),
)

# 当会话超时则需要回复config.response.timeout_format
async def create_timeout_task(target: Union[Friend, Group], source: Source):
    await asyncio.sleep(config["responseTimeout"])
    await app.send_message(
        target,
        config["responseText"]["timeout"],
        quote=source if config["responseQuoteTextFlag"] == "True" else False,
    )


# 处理消息
async def handle_message(
    target: Union[Friend, Group], session_id: str, message: str, source: Source
) -> str:
    if not message.strip():
        return config["responseText"]["nullText"]

    # 匹配关键词 切换思维
    tk,contents = brain.matchingThinking(message)
    logger.info("匹配到的思维：{}".format(tk))
    if(brain.activateThinking(tk) == False):  # 激活
        return "激活思维：{} 失败".format(tk)
    brain.changeThinking(tk)  # 切换
    if brain.thinking is None:
        return "目前处于失魂状态，无法回复消息。"
    
    timeout_task = asyncio.create_task(create_timeout_task(target, source))
    try:
        # session = brain.matching_session(session_id)
        # 重置会话
        # if message.strip() in "重置会话":
        #     session.reset_conversation()
        #     return "重置会话"
        #
        # if message.strip() in "回滚":
        #     resp = session.rollback_conversation()
        #     if resp:
        #         return config.response.rollback_success + '\n' + resp
        #     return "回滚"

        # 手动激活思维 例： /激活 /bing 激活
        if contents.strip() == "激活":
            if(brain.thinking.activate() == True):
                return "激活成功"
            else:
                return "激活失败"

        # 正常交流
        resp = await brain.response(message)
        logger.info("对{}的消息：[{}],进行应答：".format(session_id, message))
        return resp

        # resp = await session.chat_response(message)
        # logger.info("对{}的消息：[{}],进行应答：".format(session_id,message))
        # logger.info(resp)
        # return resp

    except Exception as e:
        if "Too many requests" in str(e):
            return config["responseText"]["tooFast"]
        if "Connection aborted" in str(e):
            return "大概是代理服务器挂了"
        logger.exception(e)
        return "出现故障：{}".format(e)
    finally:
        timeout_task.cancel()


# 接收好友消息
@app.broadcast.receiver("FriendMessage")
async def friend_message_listener(
    app: Ariadne,
    friend: Friend,
    source: Source,
    chain: Annotated[MessageChain, DetectPrefix(config["prefix"])],
):
    if friend.id == config["mirai"]["qq"]:  # 不对自己进行回复
        return
    
    response = await handle_message(
        friend, f"friend-{friend.id}", chain.display, source
    )
    await app.send_message(
        friend,
        response,
        quote=source if config["responseQuoteTextFlag"] == "True" else False,
    )


GroupTrigger = (
    Annotated[
        MessageChain,
        MentionMe(config["mention"] != "at"),
        DetectPrefix(config["prefix"]),
    ]
    if config["mention"] != "none"
    else Annotated[MessageChain, DetectPrefix(config["prefix"])]
)

# 接收群组消息
@app.broadcast.receiver("GroupMessage")
async def group_message_listener(group: Group, source: Source, chain: GroupTrigger):
    response = await handle_message(group, f"group-{group.id}", chain.display, source)
    event = await app.send_message(
        group,
        response,
        quote=source if config["responseQuoteTextFlag"] == "True" else False,
    )
    # event = await app.send_message(group, response)
    if event.source.id < 0:
        img = text_to_image(text=response)
        b = BytesIO()
        img.save(b, format="png")
        await app.send_message(
            group,
            Image(data_bytes=b.getvalue()),
            quote=source if config["responseQuoteTextFlag"] == "True" else False,
        )


# 接收好友请求
@app.broadcast.receiver("NewFriendRequestEvent")
async def on_friend_request(event: NewFriendRequestEvent):
    if config["acceptFriendRequest"] == "True":
        await event.accept()


# 接收群组邀请
@app.broadcast.receiver("BotInvitedJoinGroupRequestEvent")
async def on_friend_request(event: BotInvitedJoinGroupRequestEvent):
    if config["acceptGroupRequest"] == "True":
        await event.accept()


# 启动时连接到OpenAI
@app.broadcast.receiver(AccountLaunch)
async def start_background(loop: asyncio.AbstractEventLoop):
    logger.info("激活默认思维: {}".format(config["defaultThinking"]))
    if await brain.defaultActivate():
        logger.info("激活成功，尝试连接到 Mirai 服务")
    else:
        logger.info("激活失败，在连接上 Mirai 服务后请手动激活")

app.launch_blocking()
