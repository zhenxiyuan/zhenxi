#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import datetime
import os
import re
import time
import traceback
import requests
import json
import random
from random import sample
from datetime import timedelta, timezone

import httpx
from telethon import events

from .. import chat_id, client, jdbot, logger
#from jbot.bot.utils import ql_token

async def msgs():
    return ''.join(sample(["正在查询🔎", "✅收到...", "🧐好的..", "🥲来了，别急...", "⏳查询中...", "🤡去喝杯水等待一下...", "收到,等待时间可以抬肛放松一下哦😘"], 1))

@client.on(events.NewMessage(from_users=chat_id, pattern=r'^查询\s?\d*$'))
async def bean_detail(event):
    try:
        
        if re.search(f'\d', event.raw_text):
            num = int(re.findall("\d+", event.raw_text)[0])
        else:
            num = 1
        await event.edit(f"{await msgs()}")
        res = await get_bean_info(num)
        #logger.info(res['data'][2])
        if res['code'] != 200:
            info = f'{str(res["data"])}'
        else:
            info = f"||👴🏼**账号🆔{num}实时收入：{res['data'][0]}京豆**||\n\n"
            bean_S = 0
            send = ''
            for i in res['data'][1]:
                if res['data'][1][i] >= 201:
                    info += f"  ✴︎ **【{res['data'][1][i]}豆】**__{i}__\n"
                if res['data'][1][i] >= 21 and res['data'][1][i] <= 200:
                    info += f"  ✳︎ 【{res['data'][1][i]}豆】{i}\n"
            for p in res['data'][2]:
                send += f"  ⋅ 【{p['amount']}豆】 {p['userVisibleInfo']} ⋙ ({p['createDate'].split(' ')[-1]})\n"
            if '【' in info:
                info += f"  ⊹   ⋙ ⋅⋅⋅\n\n"
            if res['data'][0] >= 1:
                info += "  ⊘ __已经隐藏２０豆以下店铺收入__"
            if len(send) >= 10:
                info += f'\n\n▍**最新收入**:\n__{send}__'
        await event.delete()
        msg = await client.send_message(event.chat_id, info)
        await asyncio.sleep(8+random.randint(1, 18))
        await msg.edit('__您无权限查看此消息。请通过订阅 Telegram Premium 获取查看权限。__')
        await asyncio.sleep(8+random.randint(1, 8))
        await msg.delete()
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")

async def get_bean_info(i):
    try:
        cookies = await get_cks()
        if cookies:
            if i <= len(cookies):
                ck = cookies[i - 1]
                async with httpx.AsyncClient(verify=False) as session:
                    beans_res = await get_beans_history(ck, session, 1)
                if beans_res['code'] != 200:
                    return {'code': 400, 'data': f'账号{i}收入详情查询失败，此账号已过期'} if '未登录' in str(beans_res['data']) else beans_res
                else:
                    date = beans_res['data'][3][0]
                    beanall, infolist, createdate = 0, {}, []
                    for i in beans_res['data'][2][date]:
                        if not re.search('退还|扣赠', i['userVisibleInfo']):
                            i['userVisibleInfo'] = i['userVisibleInfo'].replace("参加[", "").replace("]-奖励", "").replace("]店铺活动-奖励", "")
                            i['userVisibleInfo'] = i['userVisibleInfo'].replace("京东自营旗舰店", "(自营)").replace("京东自营官方旗舰店", "(自营官方)").replace("京东官方自营旗舰店", "(自营官方)")
                            i['userVisibleInfo'] = i['userVisibleInfo'].replace("（", "(").replace("）", ")").replace("官方自营旗舰店", "(自营官方)")
                            i['userVisibleInfo'] = i['userVisibleInfo'].replace("官方旗舰店", "(官方)").replace("品牌闪购抽盲盒得京豆", "闪购盲盒")
                            i['userVisibleInfo'] = i['userVisibleInfo'].replace("旗舰店", "(旗舰)").replace("专营店", "(专营)").replace("专卖店", "(专卖)")
                            i['userVisibleInfo'] = i['userVisibleInfo'].replace("转盘抽奖活动", "(抽奖)")
                            i['userVisibleInfo'] = i['userVisibleInfo'].replace("京东自营专区", "(自营)")
                            i['userVisibleInfo'] = i['userVisibleInfo'].replace("京东云无线宝", "韭菜云积分换豆")
                            beanall += int(i['amount'])
                            #i['userVisibleInfo'] = i['userVisibleInfo'].replace("京东超店会员福利社", "购物返京豆")
                            #beanall += int(i['amount'])

                            if i['userVisibleInfo'] in infolist:
                                infolist[i['userVisibleInfo']] += int(i['amount'])
                            else:
                                infolist[i['userVisibleInfo']] = int(i['amount'])
                    createdate += beans_res['data'][2][date][:3]
                            
                    infolist = dict(sorted(infolist.items(), key=lambda x: x[1], reverse=True))
                    
                    #infolist = dict(sorted(infolist.items(), key=lambda x: x[1]))
                    return {'code': 200, 'data': [beanall, infolist, createdate]}
            else:
                return {'code': 400, 'data': f'账号{i}收入详情查询失败，你只有{len(cookies)}个账号，没点B数吗'}
        return {'code': 400, 'data': f'账号收入详情查询失败，您还未添加账号'}
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        return {'code': 400, 'data': f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}"}

async def getBeanDetail(page, cookie):
    try:
        headers = {
            'Cookie': cookie,
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'api.m.jd.com',
            'User-Agent': await userAgent()
        }
        data = 'body={"pageSize": "20", "page": "' + str(page) + '"}&appid=ld'
        url = f"https://api.m.jd.com/client.action?functionId=getJingBeanBalanceDetail"
        async with httpx.AsyncClient(verify=False) as session:
            res = await session.post(url, headers=headers, data=data, timeout=10)
        return res.json()
    except:
        return ""

async def get_beans_history(ck, session, num: int = 7):
    try:
        headers = {
            "Host": "api.m.jd.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": await userAgent(),
            "Content-Type": "application/x-www-form-urlencoded;",
            "Accept-Encoding": "gzip, compress, deflate, br",
            "Cookie": ck,
            "Referer": "https://servicewechat.com/wxa5bf5ee667d91626/141/page-frame.html",
        }
        url = "https://api.m.jd.com/api"
        days = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, num)]
        beans_in = {key: 0 for key in days}
        beans_out = {key: 0 for key in days}
        beans_info = {key: [] for key in days}
        page = 0
        loop = True
        while loop:
            page += 1
            res = await session.get(url, params=gen_params(page), headers=headers, timeout=10)
            resp = res.text
            res = json.loads(resp)
            if res['resultCode'] == 0:
                if len(res['data']['list']) != 0:
                    for i in res['data']['list']:
                        for date in days:
                            if str(date) in i['createDate'] and i['amount'] > 0:
                                beans_in[str(date)] = beans_in[str(date)] + i['amount']
                                beans_info[str(date)].append(i)
                                break
                            elif str(date) in i['createDate'] and i['amount'] < 0:
                                beans_out[str(date)] = beans_out[str(date)] + i['amount']
                                break
                        if i['createDate'].split(' ')[0] not in str(days):
                            loop = False
                else:
                    loop = False
            else:
                return {'code': 400, 'data': res}
        return {'code': 200, 'data': [beans_in, beans_out, beans_info, days]}
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        logger.error(f"错误---↓\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}")
        return {'code': 400, 'data': f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}"}

def gen_params(page):
    body = gen_body(page)
    params = {
        "functionId": "jposTradeQuery",
        "appid": "swat_miniprogram",
        "client": "tjj_m",
        "sdkName": "orderDetail",
        "sdkVersion": "1.0.0",
        "clientVersion": "3.1.3",
        "timestamp": int(round(time.time() * 1000)),
        "body": json.dumps(body)
    }
    return params

def gen_body(page):
    SHA_TZ = timezone(timedelta(hours=8), name='Asia/Shanghai')
    body = {
        "beginDate": datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(SHA_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "endDate": datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(SHA_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "pageNo": page,
        "pageSize": 20,
    }
    return body

async def userAgent():
    """
    随机生成一个UA
    """
    uuid = ''.join(sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 40))
    addressid = ''.join(sample('1234567898647', 10))
    iosVer = ''.join(sample(["14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1", "13.7", "13.1.2", "13.1.1"], 1))
    iosV = iosVer.replace('.', '_')
    iPhone = ''.join(sample(["8", "9", "10", "11", "12", "13"], 1))
    ADID = ''.join(sample('0987654321ABCDEF', 8)) + '-' + ''.join(sample('0987654321ABCDEF', 4)) + '-' + ''.join(sample('0987654321ABCDEF', 4)) + '-' + ''.join(sample('0987654321ABCDEF', 4)) + '-' + ''.join(sample('0987654321ABCDEF', 12))
    return f'jdapp;iPhone;10.0.4;{iosVer};{uuid};network/wifi;ADID/{ADID};model/iPhone{iPhone},1;addressid/{addressid};appBuild/167707;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/null;supportJDSHWK/1'
QL = True
async def get_cks():
    if QL:
        url = 'http://127.0.0.1:5600/open/envs'
        params = {
            't': int(round(time.time() * 1000)),
            'searchValue': 'JD_COOKIE'
        }
        token = await ql_token()
        headers = {'Authorization': f'Bearer {token}'}
        res = requests.get(url, params=params, headers=headers).json()
        cks = [i['value'] for i in res['data']]
    else:
        res = re.findall(r'pt_key=\S*?;.*?pt_pin=\S*?;', rwcon("str"))
        cks = [i for i in res if 'pin=xxxx;' not in i]
    return cks

async def ql_token():
    with open("/ql/db/app.db", "r", encoding="utf-8") as file:
        appfile = file.readlines()
    app = json.loads(appfile[0])
    if app.get('tokens') and int(time.time()) < app['tokens'][-1]['expiration']:
        token = app['tokens'][-1]['value']
    else:
        url = 'http://127.0.0.1:5600/open/auth/token'
        headers = {'client_id': app['client_id'],
                   'client_secret': app['client_secret']}
        token = requests.get(url, params=headers, timeout=5).json()['data']['token']
    return token
