#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import datetime, time
import os
import re
import sys
import traceback
import random
from telethon import events

from .. import chat_id, client, jdbot, logger
from ..bot.utils import TASK_CMD, execute, push_error
from ..diy.utils import my_chat_id


@client.on(events.NewMessage(chats=[-1001284907085, -1001294678882, -1001320212725, my_chat_id],
                           pattern=r"(?s).*export\s(jd_zdjr_activity(Url|Id)|jd_joinTeam_activity(Url|Id)|pp_wxPointShopView_activity(Url|Id)|CompleteInfo_AllUrl|BirthGift_All(Url|Id)|jdjoyInvite_AllUrl|WxHbShare_AllUrl|jd_smiek_package_activity(Url|Id)|OPEN_CARD_(SHOP|VENDER)_ID|ISV_(SHOP_ID|VENDER_ID|RED_URL|SIGN)|FAV_(SHOP|VENDER)_ID|jd_smiek_luckDraw_activityUrl|comm_activityIDList|jd_smiek_shareVideo_activityUrl)=(\".*\"|\'.*\')"))
async def activity(event):
    """
    监控运行变量
    """
    #global rk
    try:
        msg = await jdbot.send_message(chat_id, '监控到活动变量')
        group = f'[{event.chat.title}](https://t.me/c/{event.chat.id}/{event.message.id})'
        if "jd_zdjr_activity" in event.message.text:
            urls = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            acId = re.findall(r'(?<=activityId=")[a-zA-Z0-9]+', event.message.text)[0].replace('"', '')
            url = f'{urls}/wxTeam/activity?activityId={acId}'
            #rk = f'[活动入口]({url})'
            name = f'[组队瓜分京豆]({url})'
            variables = f'\n\n`{event.message.text}`'
            cmd = f"{TASK_CMD} gua_zdjr.js now"
        elif "joinTeam" in event.message.text:
            name = '组队瓜分京豆2'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} gua_joinTeam.js now'
        elif "FAV" in event.message.text:
            name = '收藏有礼'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} jd_fav_shop_gift.js desi JD_COOKIE 1-8'
        elif "ISV" in event.message.text:
            name = '特效关注有礼'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} jd_follow_wxshop_gift.js desi JD_COOKIE 1-5'
        elif "jdjoyInvite_AllUrl" in event.message.text:
            url = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            name = '邀新人入会送京豆'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} gua_invite_join_shop.js'
        elif "WxHbShare_AllUrl" in event.message.text:
            url = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            name = '拆红包'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} 0jd_WxHbShare.js'
        elif "CompleteInfo_AllUrl" in event.message.text:
            url = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            name = '完善有礼'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} 0jd_CompleteInfo.js desi JD_COOKIE 1-7'
        elif "BirthGift_All" in event.message.text:
            url = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            name = '生日礼包'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} jd_BirthGifts.js desi JD_COOKIE 1-10'
        elif "wxPointShopView" in event.message.text:
            url = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            name = '积分兑换'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} pp_wxPointShopView.js desi JD_COOKIE 1-10'
        elif "package" in event.message.text:
            url = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            name = '让福袋飞'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} gua_packages.js desi JD_COOKIE 1-10'
        elif "OPEN_CARD" in event.message.text:
            name = '会员开卡'
            #rk = f'暂无活动入口'
            variables = f''
            cmd = f'{TASK_CMD} jd_open_card_by_shopid.js desi JD_COOKIE 1-20'
        elif "addCart" in event.message.text:
            url = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            #rk = f'[活动入口]({url})'
            name = f'[加购有礼]({url})'
            variables = f'\n\n`{event.message.text}`'
            cmd = f"{TASK_CMD} gua_addCart.js desi JD_COOKIE 8-20"
        elif "luckDraw" in event.message.text:
            url = re.findall(r'[a-zA-z]+://[^\s]*', event.message.text)[0].replace('"', '')
            #rk = f'[活动入口]({url})'
            name = f'[转盘抽奖]({url})'
            variables = f'\n\n`{event.message.text}`'
            random_num = []
            matrix=[str(8+i) for i in range(40)]
            random_num = random.sample(matrix, 15)
            num_list = ' '.join(random_num)
            cmd = f"{TASK_CMD} gua_luckDraw2.js desi JD_COOKIE {num_list}"
        elif "comm_activity" in event.message.text:
            name = 'joyjd_通用ID'
            variables = f''
            cmd = f"{TASK_CMD} jd_joyjd_open.js desi JD_COOKIE 1-5"
        elif "shareVideo" in event.message.text:
            name = '视频分享'
            variables = f''
            cmd = f"{TASK_CMD} gua_shareVideo.js desi JD_COOKIE 1-10"
        else:
            return
        messages = event.message.raw_text.split("\n")
        invalid, unchange = False, True
        for message in messages:
            if "export " not in message:
                continue
            kv = re.sub(r'.*export ', '', message)
            key = kv.split("=")[0]
            value = re.findall(r'"([^"]*)"', kv)[0]
            if "zdjr" in key and len(value) != 32:
                invalid = True
            elif os.environ.get(key) != value:
                os.environ[key] = value
                unchange = False
        if invalid:
            await jdbot.send_message(chat_id, f"监控到 {group} 的 **{name}** 活动，变量不正确停止运行……")
            return
        elif unchange:
            await jdbot.send_message(chat_id, f"监控到 {group} 的 **{name}** 活动，变量已重复停止运行……")
            return
        else:
            info = f"监控到 {group} 的 **{name}** 活动\n{event.message.raw_text}"
            #asyncio.sleep(1)
            await execute(chat_id, info, cmd)
    except Exception as e:
        await push_error(e)