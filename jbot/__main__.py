#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import json
import os
import random
import sqlite3

from . import BOT_DIR, BOT_SET, BOT_SET_JSON_FILE, BOT_SET_JSON_FILE_USER, chat_id, jdbot, LOG_DIR, logger, QL_SQLITE_FILE
from .bot.update import botlog, version
from .utils import load_module

BOT_UP_LOG = f'{LOG_DIR}/bot/up.log'
BOT_M_DIR = f'{BOT_DIR}/bot/'
BOT_D_DIR = f'{BOT_DIR}/diy/'
BOT_U_DIR = f'{BOT_DIR}/user/'
logger.info('加载 user 模块')
load_module('user', BOT_U_DIR)
logger.info('加载 bot 模块')
load_module('bot', BOT_M_DIR)
logger.info('加载 diy 模块')
load_module('diy', BOT_D_DIR)


async def new_ver():
    info = '[项目地址](https://github.com/chiupam/JD_Diy.git) \t| \t[交流频道](https://t.me/JD_Diy_Channel) '
    if os.path.exists(BOT_UP_LOG):
        with open(BOT_UP_LOG, 'r', encoding='utf-8') as f:
            logs = f.read()
        if version in logs:
            return
        else:
            with open(BOT_UP_LOG, 'a', encoding='utf-8') as f:
                f.writelines([version, botlog])
            await jdbot.send_message(chat_id, f'[机器人上新了](https://github.com/chiupam/JD_Diy.git)\n{botlog}\n运行日志为log/bot/run.log\n\n\t{info}', link_preview=False)
    else:
        with open(BOT_UP_LOG, 'w+', encoding='utf-8') as f:
            f.writelines([version, botlog])
        await jdbot.send_message(chat_id, f'[机器人上新了](https://github.com/chiupam/JD_Diy.git)\n{botlog}\n运行日志为log/bot/run.log\n\n\t{info}', link_preview=False)


async def bot_set_init():
    try:
        with open(BOT_SET_JSON_FILE, 'r', encoding='utf-8') as f:
            bot_set = json.load(f)
        if os.path.exists(BOT_SET_JSON_FILE_USER):
            with open(BOT_SET_JSON_FILE_USER, 'r', encoding='utf-8') as f:
                user_set = json.load(f)
            if user_set['版本'] != bot_set['版本']:
                for i in user_set:
                    if '版本' not in i and not isinstance(user_set[i], dict):
                        bot_set[i] = user_set[i]
                    elif isinstance(user_set[i], dict):
                        for j in user_set[i]:
                            bot_set[i][j] = user_set[i][j]
                    else:
                        continue
                with open(BOT_SET_JSON_FILE_USER, 'w+', encoding='utf-8') as f:
                    json.dump(bot_set, f, indent=2, ensure_ascii=False)
        else:
            with open(BOT_SET_JSON_FILE_USER, 'w+', encoding='utf-8') as f:
                json.dump(bot_set, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.info(str(e))


async def hello():
    if BOT_SET.get('启动问候') and BOT_SET['启动问候'].lower() == 'true':
        info = '[项目地址](https://github.com/chiupam/JD_Diy.git) \t| \t[交流频道](https://t.me/JD_Diy_Channel) '
        hello_words = BOT_SET["启动问候语"].split("|")
        hello_word = hello_words[random.randint(0, len(hello_words) - 1)]
        await jdbot.send_message(chat_id, f'{str(hello_word)}\n\n\t{info}', link_preview=False)


async def ql_check():
    try:
        if os.getenv('QL_DIR'):
            if os.path.exists(QL_SQLITE_FILE):
                con = sqlite3.connect(QL_SQLITE_FILE)
                cur = con.cursor()
                cur.execute("select scopes from Apps")
                apps = cur.fetchone()
                con.close()
                if apps:
                    scopes = eval(apps[0])
                    if not {'crons', 'envs'}.issubset(scopes):
                        await jdbot.send_message(chat_id, '【💥错误💥】\n\n青龙应用权限不足,请增加权限\n\n `定时任务` `环境变量` ')
                else:
                    await jdbot.send_message(chat_id, '【💥错误💥】\n\n未找到青龙应用,请新建应用\n\n`青龙面板--系统设置--新建应用`')
            elif os.path.exists("/ql/db/app.db"):
                with open("/ql/db/app.db", "r", encoding="utf-8") as file:
                    appfile = file.readlines()
                if appfile and json.loads(appfile[0]):
                    scopes = json.loads(appfile[0])['scopes']
                    if not {'crons', 'envs'}.issubset(scopes):
                        await jdbot.send_message(chat_id, '【💥错误💥】\n\n青龙应用权限不足,请增加权限\n\n `定时任务` `环境变量` ')
                else:
                    await jdbot.send_message(chat_id, '【💥错误💥】\n\n未找到青龙应用,请新建应用\n\n`青龙面板--系统设置--新建应用`')
            else:
                await jdbot.send_message(chat_id, f'【💥错误💥】\n\n未找到青龙数据库')
    except Exception as e:
        logger.info(str(e))

if __name__ == "__main__":
    with jdbot:
        jdbot.loop.create_task(new_ver())
        jdbot.loop.create_task(bot_set_init())
        jdbot.loop.create_task(hello())
        jdbot.loop.create_task(ql_check())
        jdbot.loop.run_forever()
