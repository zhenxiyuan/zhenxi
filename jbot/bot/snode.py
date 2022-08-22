import os
import traceback

from telethon import events

from .utils import execute, snode_btn
from .. import BOT_SET, ch_name, chat_id, JD_DIR, jdbot, logger


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/snode'))
async def my_snode(event):
    """定义supernode文件命令"""
    try:
        SENDER = event.sender_id
        path = JD_DIR
        page = 0
        filelist = None
        async with jdbot.conversation(SENDER, timeout=60) as conv:
            msg = await conv.send_message('正在查询，请稍后')
            while path:
                path, msg, page, filelist = await snode_btn(conv, SENDER, path, msg, page, filelist)
        if filelist and filelist.startswith('CMD-->'):
            await execute(chat_id, '', filelist.replace('CMD-->', ''))
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")


if ch_name:
    jdbot.add_event_handler(my_snode, events.NewMessage(chats=chat_id, from_users=chat_id, pattern=BOT_SET['命令别名']['snode']))
