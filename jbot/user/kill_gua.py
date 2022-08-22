#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import datetime, time
import random
import os
import re
import sys
import json
import traceback
import requests
import glob
from telethon import events

requests.packages.urllib3.disable_warnings()

from .. import chat_id, client, jdbot, logger, TOKEN, SCRIPTS_DIR
from ..bot.utils import TASK_CMD, execute, push_error, backup_file
from ..diy.utils import my_chat_id

bot_id = int(TOKEN.split(":")[0])

QL = [
    [
        'http://10.0.0.51:5700/',#url
        '_W69xE9nHgps',#Client ID
        'XV4DSwQgk3p0fu4ffa7d-H0N',#Client Secret
    ],
    [
        'http://10.0.0.52:5700/',#url
        'L7JR-e-9jKjK',#Client ID
        'KfcJg_-W9Z6OoN5cb6ho7Akp',#容量
    ],
    [
        'http://10.0.0.53:5700/',#url
        'GoxDtO1gnhZ_',#Client ID
        '5MiiHMXrRxn0_pyYQB-UgcIk',#Client Secret
    ],
    [
        'http://10.0.0.54:5700/',#url
        '9ORS-wO-1dja',#Client ID
        '48x8UcNxq4Uxy2uSGQpeJ1R_',#Client Secret
    ],
    [
        'http://10.0.0.55:5700/',#url
        'jJWyA-oScl4J',#Client ID
        'MikP0zDj0k-T0ZtI4LLKL4lU',#Client Secret
    ],
    [
        'http://10.0.0.56:5700/',#url
        'EIhnNgqJ2-7o',#Client ID
        'q4q4BstalUU6my_eYHZocKjM',#Client Secret
    ],
    [
        'http://10.0.0.57:5700/',#url
        'D8KUhL3-ykKP',#Client ID
        'bQYlw_fvWiHR2guyf1IzkEZw',#Client Secret
    ],
    [
        'http://10.0.0.58:5700/',#url
        '-jef3Cos73IJ',#Client ID
        'yrWlPayQ1Vi_mBIMy914LRGK',#Client Secret
    ],
]

botid = ['1783633979', '1976025383', '1933041447', '1975529450', '1956518262', '2072728265', '2114243913', '2144913897']


@client.on(events.NewMessage(from_users=chat_id, pattern=r"^-kg\s*\d*$"))
async def activity(event):
    try:
        message = event.message.text
        num = re.findall("\d+", message)[0]
        await event.delete()
        info = f'{num}号 · 西瓜熟了🍉\n'
        msg = await client.send_message(event.chat_id, info)
        node = 0
        filenames = f'gua_opencard{num}'
        for o in botid:
            Botid = botid[node]
            test1 = f'/cmd ps -ef | grep -E "node.*.js" | grep -v grep | grep -E "{filenames}"'
            test2 = r" | awk '{print $1}' | xargs kill -9"
            await client.send_message(int(Botid), f"{test1}{test2}")
            await asyncio.sleep(1)
            for _ in o:
                if node == 0:
                    nodes = '1'
                if node == 1:
                    nodes = '2'
                if node == 2:
                    nodes = '3'
                if node == 3:
                    nodes = '4'
                if node == 4:
                    nodes = '5'
                if node == 5:
                    nodes = '6'
                if node == 6:
                    nodes = '7'
                if node == 7:
                    nodes = '8'
            node += 1
            infos = info + f'  · P-{nodes} > 🔪'
            for u in range(6):
                await msg.edit(infos) #嚣张模式
                if u == 0 or u == 1 or u == 2:
                    infos += '·'
                if u == 3:
                    infos += '💢'
                if u == 4:  
                    infos += '🩸'
                if u == 5:
                    info += f'  · P-{nodes} ~ 开肚成功✅\n'
                    await msg.edit(info) #嚣张模式
        await asyncio.sleep(8)
        await msg.delete()
    except Exception as e:
        await push_error(e)
    

        

