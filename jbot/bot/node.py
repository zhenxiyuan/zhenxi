import os
import traceback

from telethon import events

from .utils import execute, TASK_CMD
from .. import BOT_SET, ch_name, chat_id, jdbot, logger


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern='/node'))
async def bot_node(event):
    """接收/node命令后执行程序"""
    try:
        msg_text = event.raw_text.split(' ')
        if isinstance(msg_text, list) and len(msg_text) == 2:
            text = ''.join(msg_text[1:])
        else:
            text = None
        if not text:
            res = '''请正确使用/node命令，如
    /node /abc/123.js 运行abc/123.js脚本
    /node /own/abc.js 运行own/abc.js脚本'''
            await jdbot.send_message(chat_id, res)
        else:
            await execute(chat_id, f'执行 {text} 命令', f'{TASK_CMD} {text}')
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")


if ch_name:
    jdbot.add_event_handler(bot_node, events.NewMessage(chats=chat_id, from_users=chat_id, pattern=BOT_SET['命令别名']['node']))
