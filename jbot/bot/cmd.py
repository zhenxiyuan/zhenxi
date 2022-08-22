import os
import asyncio, random
from random import sample
from telethon import events
from .. import jdbot, START_CMD, chat_id, logger, BOT_SET, ch_name
from .utils import execute, push_error


ddd = [
	['luckDraw', '转盘抽奖'],
	['jd_smiek_addCart', '关注加购有礼'],
	['BirthGift', '生日礼包'],
	['pp_wxPointShopView', '积分兑换'],
	['jd_wxCollectCard', '集卡抽奖'],
	['shareVideo', '视频分享'],
	['OPEN_CARD', '会员开卡'],
       ['CompleteInfo','完善有礼'],
       ['jdTeam3', '瓜分京豆(微定制)'],
       ['grep', '进程结束'],
       ['_opencard', '开卡活动'],
       ['kill', '进程结束'],
       ['package_activityUrl', '让福袋飞'],
       ['WxHbShare', '拆红包'],
	]

@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern='/cmd'))
async def my_cmd(event):
    """接收/cmd命令后执行程序"""
    msg_text = event.raw_text.split(' ')
    try:
        if isinstance(msg_text, list):
            text = ' '.join(msg_text[1:])
        else:
            text = None
        if 'task gua_opencard' in text:
            sta = random.randint(10, 35) + random.randint(1, 30)
            info = f'收到 {xxxx(text)} 命令\n延迟 {sta} 秒运行'
            msg = await jdbot.send_message(chat_id, info) 
            #await asyncio.sleep(sta)
            await msg.delete()
        if START_CMD and text:
            info = f'执行 `{xxxx(text)}` 命令'
            await execute(chat_id, info, text)
        elif START_CMD:
            msg = '请正确使用/cmd命令，如：\n/cmd date  # 系统时间\n不建议直接使用cmd命令执行脚本，请使用/node或/snode'
            await jdbot.send_message(chat_id, msg)
        else:
            await jdbot.send_message(chat_id, '未开启CMD命令，如需使用请修改配置文件')
    except Exception as e:
        await push_error(e)

def xxxx(text):
    n = 0
    for i in ddd:
        if ddd[n][0] in text:
            res = ddd[n][1]
            return res
        n += 1
    return text

if ch_name:
    jdbot.add_event_handler(my_cmd, events.NewMessage(
        chats=chat_id, pattern=BOT_SET['命令别名']['cmd']))
