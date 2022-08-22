import json
import os
import traceback
from asyncio import exceptions

from telethon import Button, events

from .utils import logger, press_event, split_list
from .. import BOT_SET, BOT_SET_JSON_FILE_USER, ch_name, chat_id, jdbot


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern='^/set$'))
async def bot_set(event):
    SENDER = event.sender_id
    try:
        msg = await jdbot.send_message(chat_id, '请稍后，正在查询')
        with open(BOT_SET_JSON_FILE_USER, 'r', encoding='utf-8') as f:
            myset = json.load(f)
        info = '您目前设置如下：\n'
        for i in myset:
            if '命令别名' in i:
                continue
            else:
                info += f'\t\t- {i}-->{myset[i]} \n'
        info += '请点击您要设置的项目，选择后，输入要设置的值，重启生效,垃圾话以 | 进行区隔,黑名单以空格或逗号或顿号区隔'
        btn = [Button.inline(i, i) for i in myset if not isinstance(myset[i], dict)]
        btn.append(Button.inline('取消', data='cancel'))
        btn = split_list(btn, 3)
        async with jdbot.conversation(SENDER, timeout=90) as conv:
            msg = await jdbot.edit_message(msg, info, buttons=btn, link_preview=False)
            convdata = await conv.wait_event(press_event(SENDER))
            res = bytes.decode(convdata.data)
            if res == 'cancel':
                msg = await jdbot.edit_message(msg, '对话已取消')
                conv.cancel()
            else:
                await jdbot.delete_messages(chat_id, msg)
                msg = await conv.send_message(f'请输入您要修改的{res}\n如果需要取消，请输入`cancel`或`取消`\n如需自定义或快速修改，请直接修改config/botset.json\n如果为True或False首字符大写\n```{myset[res]}```')
                data = await conv.get_response()
                if data.raw_text == 'cancel' or data.raw_text == '取消':
                    await jdbot.delete_messages(chat_id, msg)
                    await jdbot.send_message(chat_id, '对话已取消')
                    conv.cancel()
                else:
                    markup = [Button.inline('确认', data='yes'), Button.inline('取消', data='cancel')]
                    await jdbot.delete_messages(chat_id, msg)
                    msg = await jdbot.send_message(chat_id, f'是否确认将 ** {res} ** 设置为 **{data.raw_text}**', buttons=markup)
                    convdata2 = await conv.wait_event(press_event(SENDER))
                    res2 = bytes.decode(convdata2.data)
                    if res2 == 'yes':
                        myset[res] = data.raw_text
                        with open(BOT_SET_JSON_FILE_USER, 'w+', encoding='utf-8') as f:
                            json.dump(myset, f, indent=2, ensure_ascii=False)
                        await jdbot.delete_messages(chat_id, msg)
                        msg = await jdbot.send_message(chat_id, '已完成修改，重启后生效')
                    else:
                        conv.cancel()
                        await jdbot.delete_messages(chat_id, msg)
                        msg = await jdbot.send_message(chat_id, '对话已取消')
                        return
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


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern='^/setname$'))
async def bot_setname(event):
    SENDER = event.sender_id
    try:
        msg = await jdbot.send_message(chat_id, '请稍后，正在查询')
        with open(BOT_SET_JSON_FILE_USER, 'r', encoding='utf-8') as f:
            myset = json.load(f)
        info = '您目前命令别名设置如下：\n'
        for i in myset['命令别名']:
            info += f'\t\t- {i}-->{myset["命令别名"][i]} \n'
        info += '请点击您要设置的项目，选择后，输入要设置的值，重启生效\n**请注意尽量不要重复，否则可能发生未知错误**'
        btn = [Button.inline(i, i) for i in myset['命令别名']]
        btn.append(Button.inline('取消', data='cancel'))
        btn = split_list(btn, 3)
        async with jdbot.conversation(SENDER, timeout=90) as conv:
            msg = await jdbot.edit_message(msg, info, buttons=btn, link_preview=False)
            convdata = await conv.wait_event(press_event(SENDER))
            res = bytes.decode(convdata.data)
            if res == 'cancel':
                msg = await jdbot.edit_message(msg, '对话已取消')
                conv.cancel()
            else:
                await jdbot.delete_messages(chat_id, msg)
                msg = await conv.send_message(f'请输入您要修改的{res}\n如果需要取消，请输入`cancel`或`取消`\n如需自定义或快速修改，请直接修改config/botset.json\n如果为True或False首字符大写\n```{myset["命令别名"][res]}```')
                data = await conv.get_response()
                if data.raw_text == 'cancel' or data.raw_text == '取消':
                    await jdbot.delete_messages(chat_id, msg)
                    msg = await jdbot.send_message(chat_id, '对话已取消')
                    conv.cancel()
                    return
                else:
                    markup = [Button.inline('确认', data='yes'), Button.inline('取消', data='cancel')]
                    await jdbot.delete_messages(chat_id, msg)
                    msg = await jdbot.send_message(chat_id, f'是否确认将 ** {res} ** 设置为 **{data.raw_text}**', buttons=markup)
                    convdata2 = await conv.wait_event(press_event(SENDER))
                    res2 = bytes.decode(convdata2.data)
                    if res2 == 'yes':
                        myset['命令别名'][res] = data.raw_text
                        with open(BOT_SET_JSON_FILE_USER, 'w+', encoding='utf-8') as f:
                            json.dump(myset, f, indent=2, ensure_ascii=False)
                        await jdbot.delete_messages(chat_id, msg)
                        msg = await jdbot.send_message(chat_id, '已完成修改，重启后生效')
                    else:
                        conv.cancel()
                        await jdbot.delete_messages(chat_id, msg)
                        msg = await jdbot.send_message(chat_id, '对话已取消')
                        return
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
    jdbot.add_event_handler(bot_set, events.NewMessage(chats=chat_id, from_users=chat_id, pattern=BOT_SET['命令别名']['set']))
    jdbot.add_event_handler(bot_setname, events.NewMessage(chats=chat_id, from_users=chat_id, pattern=BOT_SET['命令别名']['setname']))
