import asyncio
import json
import os
import re

import qrcode
from telethon import Button, events

from .. import BOT_SET, BOT_SET_JSON_FILE_USER, ch_name, chat_id, client, CONFIG_DIR, jdbot, QR_IMG_FILE
from ..bot.utils import press_event, row, split_list


def creat_qr(text):
    """实例化QRCode生成qr对象"""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.clear()
    # 传入数据
    qr.add_data(text)
    qr.make(fit=True)
    # 生成二维码
    img = qr.make_image()
    # 保存二维码
    img.save(QR_IMG_FILE)


def restart():
    text = "pm2 restart jbot"
    os.system(text)


def start():
    with open(BOT_SET_JSON_FILE_USER, 'r', encoding='utf-8') as f:
        myset = json.load(f)
    myset['开启user'] = 'True'
    with open(BOT_SET_JSON_FILE_USER, "w+", encoding="utf-8") as f:
        json.dump(myset, f, indent=2, ensure_ascii=False)
    restart()


def close():
    with open(BOT_SET_JSON_FILE_USER, 'r', encoding='utf-8') as f:
        myset = json.load(f)
    myset['开启user'] = 'False'
    with open(BOT_SET_JSON_FILE_USER, "w+", encoding="utf-8") as f:
        json.dump(myset, f, indent=2, ensure_ascii=False)
    restart()


def state():
    with open(BOT_SET_JSON_FILE_USER, 'r', encoding='utf-8') as f:
        myset = json.load(f)
    if myset['开启user'].lower() == 'true':
        return True
    else:
        return False


def delete():
    close()
    os.remove(f'{CONFIG_DIR}/user.session')
    restart()


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/user$'))
async def user_login(event):
    try:
        tellogin, qrlogin = False, False
        sender = event.sender_id
        async with jdbot.conversation(sender, timeout=120) as conv:
            while True:
                msg = await conv.send_message('请做出你的选择')
                buttons = [
                    Button.inline('重新登录', data='relogin') if client.is_connected() else Button.inline('我要登录', data='login'),
                    Button.inline('关闭user', data='close') if state() else Button.inline('开启user', data='start'),
                    Button.inline('删除Session', data='delete')
                ]
                opt_btns = [
                    Button.inline('上级目录', data='upper menu'),
                    Button.inline('取消会话', data='cancel')
                ]
                newbuttons = split_list(buttons, row)
                newbuttons.append([Button.inline('取消会话', data='cancel')])
                msg = await jdbot.edit_message(msg, '请做出你的选择：', buttons=newbuttons)
                convdata = await conv.wait_event(press_event(sender))
                res = bytes.decode(convdata.data)
                if res == 'cancel':
                    await jdbot.edit_message(msg, '对话已取消')
                    conv.cancel()
                    return False
                elif res == 'close':
                    await jdbot.edit_message(msg, "关闭成功，准备重启机器人！")
                    close()
                elif res == 'start':
                    await jdbot.edit_message(msg, "开启成功，准备重启机器人！")
                    start()
                elif res == 'delete':
                    await jdbot.edit_message(msg, "删除成功，自动重启机器人！\n启动后请重新登录")
                    delete()
                else:
                    btns = [
                        Button.inline('手机登录', data='tellogin'),
                        Button.inline('扫码登录', data='qrlogin')
                    ]
                    newbtns = split_list(btns, row)
                    newbtns.append(opt_btns)
                    msg = await jdbot.edit_message(msg, '请做出你的选择：', buttons=newbtns)
                    convdata = await conv.wait_event(press_event(sender))
                    res2 = bytes.decode(convdata.data)
                    if res2 == 'cancel':
                        await jdbot.edit_message(msg, '对话已取消')
                        conv.cancel()
                        return False
                    elif res2 == 'upper menu':
                        await msg.delete()
                        continue
                    elif res2 == 'tellogin':
                        tellogin = True
                        break
                    else:
                        qrlogin = True
                        break
            await msg.delete()
        if tellogin:
            await client.connect()
            async with jdbot.conversation(sender, timeout=120) as conv:
                loop = 3
                info = ''
                while loop:
                    msg = await conv.send_message(f'{info}请输入带区域号手机号：\n例如：+8618888888888\n\n回复 `cancel` 或 `取消` 即可取消登录')
                    phone = await conv.get_response()
                    if phone.raw_text == 'cancel' or phone.raw_text == '取消':
                        await msg.delete()
                        await conv.send_message('取消登录')
                        await client.disconnect()
                        return
                    elif re.search('^\+\d+$', phone.raw_text):
                        await client.send_code_request(phone.raw_text, force_sms=True)
                        break
                    else:
                        await msg.delete()
                        info = "手机号输入有误\n"
                        loop -= 1
                        continue
                else:
                    await conv.send_message('输入错误3次，取消登录')
                    await client.disconnect()
                    return
                loop = 3
                info = ''
                while loop:
                    msg = await conv.send_message(f'{info}请输入5位验证码：\n例如：code12345code`（两侧必须包含code）`\n\n回复 `cancel` 或 `取消` 即可取消登录')
                    code = await conv.get_response()
                    if code.raw_text == 'cancel' or code.raw_text == '取消':
                        await msg.delete()
                        await conv.send_message('取消登录')
                        await client.disconnect()
                        return
                    elif re.search('^code\d{5}code$', code.raw_text):
                        await client.sign_in(phone.raw_text, code.raw_text.replace('code', ''))
                        break
                    else:
                        await msg.delete()
                        info = "验证码输入有误\n"
                        loop -= 1
                        continue
                else:
                    await conv.send_message('输入错误3次，取消登录')
                    await client.disconnect()
                    return
                await jdbot.send_message(chat_id, '恭喜您已登录成功！\n自动重启中！')
            start()
        elif qrlogin:
            await client.connect()
            qr_login = await client.qr_login()
            creat_qr(qr_login.url)
            await jdbot.send_message(chat_id, '请使用TG扫描二维码以开启USER', file=QR_IMG_FILE)
            await qr_login.wait(timeout=120)
            await jdbot.send_message(chat_id, '恭喜您已登录成功！\n自动重启中！')
            os.remove(QR_IMG_FILE)
            start()
    except asyncio.exceptions.TimeoutError:
        await jdbot.edit_message(msg, '登录已超时，对话已停止')
    except Exception as e:
        await jdbot.send_message(chat_id, '登录失败\n 再重新登录\n' + str(e))
        await client.disconnect()


if ch_name:
    jdbot.add_event_handler(user_login, events.NewMessage(chats=chat_id, from_users=chat_id, pattern=BOT_SET['命令别名']['userlogin']))
