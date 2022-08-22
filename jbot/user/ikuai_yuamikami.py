#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import traceback
import base64
import hashlib
from random import choice

from requests import post
from telethon import events

try:
    from jbot import chat_id, jdbot, logger, TOKEN
    from jbot.bot.utils import push_error
    from jbot.user.login import user
except:
    from .. import chat_id, jdbot, logger, TOKEN
    from ..bot.utils import push_error
    from .. import client
    user = client



bot_id = int(TOKEN.split(":")[0])

########################## 配置区域 #######################

ikuai_ip = '10.0.0.1'  # 爱快网址,优先内网ip
node = '1'
device = f'青龙{node}'  # 需切换线路的设备
ql_open = [f'ovpn_zx{node}',f'ovpn_zx1{node}'] #指定线路名
username = 'admin'  # 用户名
passwd = 'caofan66^'  # 密码加密数据passwd
#pa_ss = 'c2FsdF8xMWEyNjgyNzIyMw=='  # 密码验证pass

#########################################################


@user.on(events.MessageEdited(chats=[bot_id], pattern=r'(?s).*493，.*'))
@user.on(events.NewMessage(from_users=chat_id, pattern=r"(?s).*493，.*"))
@user.on(events.NewMessage(chats=[bot_id], from_users=chat_id, pattern=r"ip"))
#@user.on(events.NewMessage(from_users=chat_id, pattern=r'^qip$'))
async def ikuai(event):
    '''
    爱快自动切换线路
    '''
    try:
        info = ''
        go = True
        async for message in user.iter_messages(event.chat_id, limit=10):
            if '  └当前线路' in message.message:
                go = False
        if 'ip' in event.text:
            go = True
        if go:
            info += f'监控到 `{device}` IP可能黑了，准备切换线路……'
            msg = await jdbot.send_message(chat_id, info)
            cookie = getcookie()  # 获取cookie
            params = await stream_ipport_show2(cookie)  # 端口分流列表
            param = await stream_ipport_show(cookie) #端口分流
            interface = param['interface']  # 线路名
            info += '\n\t\t└当前线路: ' + interface
            try:
                ql_open.remove(interface) #删除青龙已使用的线路
            except:
                pass
            new_interface = ql_open[0]  # 随机选择剩余线路
            info += '\n\t\t└准备切换线路: ' + new_interface
            param['interface'] = new_interface  # 替换新线路
            i = 0
            while i < 5:  # 循环5次
                i += 1
                await stream_ipport_edit(cookie, param)  # 切换线路
                query_param = await stream_ipport_show(cookie)  # 查询修改后线路
                query = query_param['interface']
                if query == new_interface:  # 对比前后线路
                    info += "\n\t\t└线路切换完成"
                    break
                else:
                    continue
            else:
                info += "\n\t\t线路切换失败，请手动切换……"
            await msg.edit(info)
    except Exception as e:
        await push_error(e)


def getcookie():
    """
    获取cookie
    """
    url = f'http://{ikuai_ip}/Action/login'
    data = {"username": username, "passwd": hashlib.md5(passwd.encode('utf-8')).hexdigest(), "pass": base64.b64encode(('salt_11%s' % passwd).encode('utf-8')).decode('utf-8'), "remember_password": ""}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Connection': 'close',
        'Content-Length': '128',
        'Content-Type': 'application/json;charset=utf-8',
        'Host': ikuai_ip,
        'Origin': f'http://{ikuai_ip}',
        'Referer': f'http://{ikuai_ip}/login',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44'
    }
    res = post(url=url, headers=headers, json=data, timeout=5)
    cookie = res.headers.get('Set-Cookie').split('; ')[0]
    return cookie


async def ikuaicall(cookie, data):
    '''
    爱快请求接口
    '''
    url = f'http://{ikuai_ip}/Action/call'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Connection': 'close',
        'Content-Type': 'application/json;charset=utf-8',
        'Cookie': f'login=1; {cookie}; username={username};',
        'Host': ikuai_ip,
        'Origin': f'http://{ikuai_ip}',
        'Referer': f'http://{ikuai_ip}/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44'
    }
    res = post(url=url, headers=headers, json=data, timeout=5)
    respond = res.json()
    return respond


async def stream_ipport_show(cookie):
    '''
    端口分流参数
    '''
    data = {
        "func_name": "stream_ipport", "action": "show",
        "param": {
            "TYPE": "total,data",
            "limit": "0,20",
            "ORDER_BY": "",
            "ORDER": ""
        }
    }
    respond = await ikuaicall(cookie, data)
    info = respond['Data']['data']
    param = [i for i in info if i['comment'] == device][0]
    return param

async def stream_ipport_show2(cookie):  # (cookie, 分流备注)
    """
    端口分流参数
    """
    data = {
        "func_name": "stream_ipport", "action": "show",
        "param": {
            "TYPE": "total,data",
            "limit": "0,20",
            "ORDER_BY": "",
            "ORDER": ""
        }
    }
    respond = await ikuaicall(cookie, data)
    info = respond['Data']['data']
    #param = [i for i in info if i['comment'] in device][0]
    param = [i for i in info if '青龙' in i['comment']]
    return param

async def stream_ipport_edit(cookie, param):
    '''
    修改分流参数
    '''
    data = {
        "func_name": "stream_ipport",
        "action": "edit",
        "param": param
    }
    await ikuaicall(cookie, data)


async def vlan_list(cookie):
    '''
    线路列表
    '''
    data = {
        "func_name": "wan",
        "action": "show",
        "param": {
            "TYPE": "vlan_data,vlan_total",
            "ORDER_BY": "vlan_name",
            "ORDER": "asc",
            "vlan_internet": 2,
            "interface": "wan1",
            "limit": "0,20"
        }
    }
    respond = await ikuaicall(cookie, data)
    info = respond['Data']['vlan_data']
    vlan_name = [i['vlan_name'] for i in info]
    return vlan_name

async def openvpn_list(cookie):  # (cookie)
    """
    openvpn线路列表
    """
    data = {
        "func_name": "openvpn-client",
        "action": "show",
        "param": {
            "TYPE" : "total,data,interface",
            "brief" : 1
        }
    }
    respond = await ikuaicall(cookie, data)
    info = respond['Data']['data']
    vlan_name = [i['name'] for i in info]
    return vlan_name
