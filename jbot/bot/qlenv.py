import os
import traceback
from asyncio import exceptions

from telethon import Button, events

from .. import BOT_SET, ch_name, chat_id, jdbot, LOG_DIR, logger
from ..bot.utils import env_manage_QL, press_event, QL, ql_token, split_list


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/env'))
async def bot_env_ql(event):
    """接收/env后执行程序"""
    msg_text = event.raw_text.split(' ')
    try:
        SENDER = event.sender_id
        msg = await jdbot.send_message(chat_id, '正在查询请稍后')
        if QL:
            buttons = [{'name': '编辑', 'data': 'edit'},
                       {'name': '启用', 'data': 'enable'},
                       {'name': '禁用', 'data': 'disable'},
                       {'name': '删除', 'data': 'del'},
                       {'name': '上级', 'data': 'up'},
                       {'name': '取消', 'data': 'cancel'}]
        else:
            await jdbot.edit_message(msg, '目前仅QL支持环境变量查询修改，其他环境开发中')
            return
        if isinstance(msg_text, list) and len(msg_text) == 2:
            text = msg_text[-1]
        else:
            text = None
        if not text:
            await jdbot.edit_message(msg, '请正确使用env命令,后边需跟关键字\n/env abcd')
            return
        go_up = True
        async with jdbot.conversation(SENDER, timeout=120) as conv:
            while go_up:
                token = await ql_token()
                res = env_manage_QL('search', text, token)
                if res['code'] == 200:
                    await jdbot.delete_messages(chat_id, msg)
                    markup = [Button.inline(i['name'], data=str(res['data'].index(i))) for i in res['data']]
                    markup = split_list(markup, int(BOT_SET['每页列数']))
                    markup.append([Button.inline('取消', data='cancel')])
                    msg = await jdbot.send_message(chat_id, '查询结果如下，点击按钮查看详细信息', buttons=markup)
                    convdata = await conv.wait_event(press_event(SENDER))
                    resp = bytes.decode(convdata.data)
                    if resp == 'cancel':
                        await jdbot.edit_message(msg, '对话已取消')
                        conv.cancel()
                        return
                    if 'remarks' in res['data'][int(resp)]:
                        croninfo = '名称：\n\t{name}\n任务：\n\t{value}\n备注：\n\t{remarks}\n是否已禁用：\n\t{status}\n\t0--表示启用，1--表示禁用，2--表示未知'.format(**res['data'][int(resp)])
                    else:
                        croninfo = '名称：\n\t{name}\n任务：\n\t{value}\n是否已禁用：\n\t{status}\n\t0--表示启用，1--表示禁用，2--表示未知'.format(**res['data'][int(resp)])
                    markup = [Button.inline(i['name'], data=i['data']) for i in buttons]
                    markup = split_list(markup, int(BOT_SET['每页列数']))
                    msg = await jdbot.edit_message(msg, croninfo, buttons=markup)
                    convdata = await conv.wait_event(press_event(SENDER))
                    btnres = bytes.decode(convdata.data)
                    if btnres == 'cancel':
                        msg = await jdbot.edit_message(msg, '对话已取消')
                        conv.cancel()
                        return
                    elif btnres == 'up':
                        continue
                    elif btnres == 'edit':
                        go_up = False
                        if 'remarks' in res['data'][int(resp)]:
                            info = '```{name}-->{value}-->{remarks}```'.format(**res["data"][int(resp)])
                        else:
                            info = '```{name}-->{value}-->备注```'.format(**res["data"][int(resp)])
                        await jdbot.delete_messages(chat_id, msg)
                        msg = await conv.send_message(f'{info}\n请复制信息并进行修改')
                        respones = await conv.get_response()
                        respones = respones.raw_text
                        res['data'][int(resp)]['name'], res['data'][int(resp)]['value'], res['data'][int(resp)]['remarks'] = respones.split('-->')
                        cronres = env_manage_QL('edit', res['data'][int(resp)], token)
                    else:
                        go_up = False
                        envdata = res['data'][int(resp)]
                        cronres = env_manage_QL(btnres, envdata, token)
                    if cronres['code'] == 200:
                        if 'data' not in cronres.keys():
                            cronres['data'] = 'success'
                        await jdbot.delete_messages(chat_id, msg)
                        if len(cronres['data']) <= 4000:
                            msg = await jdbot.send_message(chat_id, f"指令发送成功，结果如下：\n{cronres['data']}")
                        elif len(res) > 4000:
                            _log = f'{LOG_DIR}/bot/qlcron.log'
                            with open(_log, 'w+', encoding='utf-8') as f:
                                f.write(cronres['data'])
                            msg = await jdbot.send_message(chat_id, '日志结果较长，请查看文件', file=_log)
                            os.remove(_log)
                    else:
                        await jdbot.edit_message(msg, f'something wrong,I\'m sorry\n{cronres["data"]}')
                else:
                    go_up = False
                    await jdbot.send_message(chat_id, f'something wrong,I\'m sorry\n{str(res["data"])}')
    except exceptions.TimeoutError:
        await jdbot.edit_message(msg, '选择已超时，对话已停止')
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/addenv'))
async def bot_addenv(event):
    try:
        SENDER = event.sender_id
        if QL:
            info = '名称-->变量值-->备注\n```JD_COOKIE-->pxxxxxxpxxxxxx;-->bot的cookie```'
        else:
            await jdbot.send_message(chat_id, '目前仅QL支持环境变量查询修改，其他环境开发中')
            return
        markup = [Button.inline('是', data='yes'),
                  Button.inline('否', data='cancel')]
        async with jdbot.conversation(SENDER, timeout=30) as conv:
            msg = await conv.send_message('是否确认添加新变量', buttons=markup)
            convdata = await conv.wait_event(press_event(SENDER))
            res = bytes.decode(convdata.data)
            if res == 'cancel':
                msg = await jdbot.edit_message(msg, '对话已取消')
                conv.cancel()
            else:
                await jdbot.delete_messages(chat_id, msg)
                msg = await conv.send_message(f'点击复制下方信息进行修改,并发送给我\n{info}')
                resp = await conv.get_response()
                resplist = resp.raw_text.split('-->')
                envdata = {'name': resplist[0], 'value': resplist[1], 'remarks': resplist[2]}
                token = await ql_token()
                res = env_manage_QL('add', envdata, token)
                if res['code'] == 200:
                    await jdbot.delete_messages(chat_id, msg)
                    msg = await jdbot.send_message(chat_id, '已成功添加新变量')
                else:
                    await jdbot.delete_messages(chat_id, msg)
                    msg = await jdbot.send_message(chat_id, f'添加新变量时发生了一些错误\n{res["data"]}')
    except exceptions.TimeoutError:
        await jdbot.edit_message(msg, '选择已超时，对话已停止')
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")


if ch_name:
    jdbot.add_event_handler(bot_env_ql, events.NewMessage(chats=chat_id, from_users=chat_id, pattern=BOT_SET['命令别名']['myenv']))
    jdbot.add_event_handler(bot_addenv, events.NewMessage(chats=chat_id, from_users=chat_id, pattern=BOT_SET['命令别名']['addenv']))
