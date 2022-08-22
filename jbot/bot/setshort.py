import os
import traceback

from telethon import events

from .. import BOT_SET, ch_name, chat_id, jdbot, logger, SHORTCUT_FILE


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/setshort$'))
async def bot_set_short(event):
    try:
        SENDER = event.sender_id
        info = '请在2分钟内'
        exist = False
        if os.path.exists(SHORTCUT_FILE):
            with open(SHORTCUT_FILE, 'r', encoding='utf-8') as f:
                short_text = f.read()
            if 0 < len(short_text) <= 4000:
                info += '复制并修改以上内容，修改完成后发回机器人'
                send = await jdbot.send_message(chat_id, short_text)
                exist = True
        if not exist:
            info += '按格式输入您的快捷命令。\n例如：\n京豆通知-->jtask jd_bean_change\n更新脚本-->jup\n获取互助码-->jcode\nnode运行XX脚本-->node /XX/XX.js\nbash运行abc/123.sh脚本-->bash /abc/123.sh\n-->前边为要显示的名字，-->后边为要运行的命令\n 如添加运行脚本立即执行命令记得在后边添加now\n如不等待运行结果请添加nohup，如京豆通知-->nohup jtask jd_bean_change now\n如不添加nohup 会等待程序执行完，期间不能交互\n建议运行时间短命令不添加nohup\n部分功能青龙可能不支持，请自行测试，自行设定 '
        info += '\n回复`cancel`或`取消`即可取消本次对话'
        async with jdbot.conversation(SENDER, timeout=180) as conv:
            msg = await conv.send_message(info)
            shortcut = await conv.get_response()
            if shortcut.raw_text == 'cancel' or shortcut.raw_text == '取消':
                if exist:
                    await send.delete()
                await jdbot.edit_message(msg, '已取消修改快捷命令')
                conv.cancel()
                return
            with open(SHORTCUT_FILE, 'w+', encoding='utf-8') as f:
                f.write(shortcut.raw_text)
            await jdbot.delete_messages(chat_id, [send, msg] if exist else msg)
            await conv.send_message('快捷命令设置成功，通过`/a`或`/b`使用')
            conv.cancel()
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")


if ch_name:
    jdbot.add_event_handler(bot_set_short, events.NewMessage(chats=chat_id, from_users=chat_id, pattern=BOT_SET['命令别名']['setshort']))
