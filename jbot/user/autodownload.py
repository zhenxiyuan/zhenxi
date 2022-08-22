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
from ..bot.utils import TASK_CMD, push_error, backup_file
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



@client.on(events.NewMessage(chats=-1001235868507, from_users=1049578757))
@client.on(events.NewMessage(chats=-1001583753746))
async def guaopencard(event):
    try:
        if event.message.file:
            filename = event.message.file.name
            try:
                #chat = await event.get_chat()
                #title = chat.title
                if "gua_open" in filename and filename.endswith("js") or "gua_join" in filename and filename.endswith("js"):
                    info = ''
                    go = False
                    #msg = await user.send_message(event.chat_id, f'{filename.replace(".js", "")}来了！') #嚣张模式
                    msg = await jdbot.send_message(chat_id, f'{filename.replace(".js", "")}来了！') #低调低调
                    path = f'{SCRIPTS_DIR}/{filename}'
                    #logger.info(path)
                    backup_file(path)
                    try:
                        await client.download_media(event.message, SCRIPTS_DIR)
                    except Exception as e:
                        logger.info(e)
                        await client.download_media(event.message, SCRIPTS_DIR)
                    #await asyncio.sleep(1)
                    #filenames = filename.replace('.js', '')
                    await msg.edit(f'保存 [{filename}](https://t.me/c/{event.chat.id}/{event.message.id})成功') #
                    #await msg.delete()
                    cmd = f'{TASK_CMD} {filename} desi JD_COOKIE 1'
                    code = await execute(cmd)
                    if code:
                        await msg.edit(code)
                        info = f'🎯分发[{filename}](https://t.me/c/{event.chat.id}/{event.message.id})脚本:\n'
                        #await msg.edit(f'获取到助力码:{str(code)}')
                        await msg.edit(info)
                        path = f'{SCRIPTS_DIR}/{filename}'
                        await fenfa(info, msg, path)
                        await asyncio.sleep(1)
                        info = f'🐝运行[{filename}](https://t.me/c/{event.chat.id}/{event.message.id})脚本:\n'
                        #await msg.edit(info) #嚣张模式
                    
                        await task_run(info, msg, path, code)
                        infos = await kill(event, event.message, path)
                        #await event.delete()
                        #await msg.delete()
                        if event.chat_id != my_chat_id:
                            await client.send_message(event.chat_id, infos) #嚣张模式
                            await client.send_message(-1001294678882, infos)
                        else:
                            await client.send_message(event.chat_id, infos)
                        #await user.send_message(bot_id, f'/cmd task {filename} desi JD_COOKIE 1 20-30 80-90 180-190 230-240')
                    else:
                        await msg.edit('未能获取到互助码')
                        return
            except Exception as e:
                await push_error(e)
    except Exception as e:
        await push_error(e)
        

#分发脚本
async def fenfa(info, msg, name):
    try:
        a = requests.session()
        '''token = login(a, QL[0][0], QL[0][1], QL[0][2])
        content = getscript(a, QL[0][0], "open", jsname, "", token)
        data_script = {
            "filename": jsname,
            "content": content,
        }'''
        with open(name, 'r') as file:
            data = file.read()
            
        data_script = {
            "filename": name.split('/')[-1],
            "content": data,
        }
        
        node = 0
        for k in QL:
            login(a, QL[node][0], QL[node][1], QL[node][2])
            res = pushscript(a, QL[node][0], "open", data_script, '')
            response = json.loads(res)["code"]
            for _ in k:
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
            if response == 200:
                info += f'  · 节点{nodes} - 分发完成✅\n'
            else:
                info += f'  · 节点{nodes} - 分发失败❌\n'
            node += 1
            await msg.edit(info) #嚣张模式
            #await jdbot.send_message(chat_id, info) #静默运行
            
            #await asyncio.sleep(1)
        return info
    except Exception as e:
        await push_error(e)
        info = f'节点 - __分发错误__❌'
        return info
    finally:
        file.close()

#调用bot cmd运行
async def task_run(info, msg, name, code):
    try:
        n = 0
        num = re.findall('\d+', name)[0]
        uuidcode = f'export guaopencard_shareUuid{num}="{code}"'
        for o in botid:
            Botid = botid[n]
            if 'gua_opencard' in name or '00' in name:
                await client.send_message(int(Botid), f'/cmd {uuidcode} && task ptask.py -t4 task {name}')
                await asyncio.sleep(1)
                #break
            else:
                await client.send_message(int(Botid), f'/cmd task {name} desi JD_COOKIE 1-888')
            for _ in o:
                if n == 0:
                    nodes = '1'
                if n == 1:
                    nodes = '2'
                if n == 2:
                    nodes = '3'
                if n == 3:
                    nodes = '4'
                if n == 4:
                    nodes = '5'
                if n == 5:
                    nodes = '6'
                if n == 6:
                    nodes = '7'
                if n == 7:
                    nodes = '8'
            n += 1
            info += f'  · 容器{nodes} - 运行成功✅\n'
            await msg.edit(info) #嚣张模式
            #await jdbot.send_message(chat_id, info) #静默运行
            #await asyncio.sleep(1)
            
    except Exception as e:
        await push_error(e)

#收尾
async def kill(event, message, filename):
    filename = filename.split('/')[-1]
    filenames = filename.split('.')[0]
    test1 = f'/cmd ps -ef | grep -E "node.*.js" | grep -v grep | grep -E "{filenames}"'
    test2 = r" | awk '{print $1}' | xargs kill -9"
    infos = f"[{filename}](https://t.me/c/{event.chat.id}/{message.id}), 已经在后台运行了\n\n🤪手动刹车:`{test1}{test2}`"
    return infos

#时间戳
def gettimestamp():
    return str(int(time.time() * 1500))

#保存token
def gettoken(self, url_token):
    r = requests.get(url_token).text
    res = json.loads(r)["data"]["token"]
    self.headers.update({"Authorization": "Bearer " + res})
    return res

#获取token
def login(self, baseurl, client_id_temp, client_secret_temp):
    url_token = baseurl + 'open/auth/token?client_id=' + client_id_temp + '&client_secret=' + client_secret_temp
    gettoken(self, url_token)

#列表
#def getitem(self, baseurl, typ):
#    url = baseurl + typ + "/scripts/files?t={}".format(gettimestamp())
#    r = self.get(url)
#    item = json.loads(r.text)["data"]
#    return item

#scripts目录
def getscript(self, baseurl, typ, filename, path, token):
    headers = {'Authorization': f'Bearer {token}'}
    url = baseurl + typ + "/scripts/" + filename + "?t=%s" % gettimestamp()
    r = self.get(url=url, headers=headers)
    response = json.loads(r.text)["code"]
    if response == 500:
        url = baseurl + typ + "/scripts/" + filename + "?path=" + path
        r = self.get(url=url, headers=headers)
    script = json.loads(r.text)["data"]
    return script

#put上传脚本
def pushscript(self, baseurl, typ, data, path):
    url = baseurl + typ + "/scripts?t=%s" % gettimestamp()
    self.headers.update({"Content-Type": "application/json;charset=UTF-8", 'Connection': 'close'})
    r = self.put(url, data=json.dumps(data))
    response = json.loads(r.text)["code"]
    if response == 500:
        data["path"] = path
        r = self.put(url, data=json.dumps(data))
    return r.text


async def execute(exectext):
    try:
        
        p = await asyncio.create_subprocess_shell(exectext, shell=True, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=os.environ)
        res_bytes, res_err = await p.communicate()
        res = res_bytes.decode('utf-8')
        if len(res) == 0:
            info += '\n已执行，但返回值为空'
            msg = await msg.edit(info)
        else:
            
            if re.search('后面的号都会助力:', res, re.S):
                code = re.findall(r'后面的号都会助力:(\w+)?',res)[0]
            return code
    except Exception as e:
        await push_error(e)
