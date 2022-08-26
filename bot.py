#!/usr/bin/env python

import logging
import requests
import pymysql
import time
import pytz
import datetime
from sshtunnel import SSHTunnelForwarder

from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters

# Telegram Bot Token
bot_token = ''
# Hook Infomation
tg_admin = 0
tg_group = 0
# V2Board Infomation
v2_url = 'https://awesomeV2Board.com' # without '/' symbol
# V2Board MySQL Database
v2_db_url = '127.0.0.1'
v2_db_user = 'root'
v2_db_pass = 'password'
v2_db_name = 'database'
v2_db_port = 3306
# Connect MySQL via SSH
ssh_enable = False
ssh_ip = '127.0.0.1'
ssh_port = 22
ssh_user = 'root'
ssh_pass = 'password'

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
bot = Bot(bot_token)

# Enable ssh
if ssh_enable is True:
    ssh = SSHTunnelForwarder(
        ssh_address_or_host=(ssh_ip, ssh_port),
        ssh_username=ssh_user,
        ssh_password=ssh_pass,
        remote_bind_address=(v2_db_url, v2_db_port))
    ssh.start()
    v2_db_port = ssh.local_bind_port
# Database Connection
db = pymysql.connect(host=v2_db_url,
                     user=v2_db_user,
                     password=v2_db_pass,
                     database=v2_db_name,
                     port=v2_db_port,
                     autocommit=True)
# TineZone
tz = pytz.timezone('Asia/Shanghai')


def s(update: Update, context: CallbackContext) -> None:
    # Debugging
    print(update)


def ping(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    text = '💥*嘭*\n'
    utid = f'{text}\n你的ID为：`{tid}`'

    if chat_type == 'private':
        reply(utid)
    else:
        group = f'\n群组ID为：`{gid}`'
        if update.message.from_user.is_bot is False:
            callback = reply(f'{utid}{group}')
        else:
            callback = reply(f'{text}{group}')
        Module.autoDelete(update, callback.chat.id, callback.message_id)


def bind(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Module.onLogin(email, password) is True:
                    result, tig = Module.getTGbyMail(email)
                    if result is False:
                        reply('✔️*成功*\n你已成功绑定 Telegram 了！')
                        Command.onBind(tid, email)
                    else:
                        reply('❌*错误*\n这个账号已绑定到别的 Telegram 了！')
                else:
                    reply('❌*错误*\n邮箱或密码错误了！')
            else:
                reply('❌*错误*\n正确的格式为：/bind 邮箱 密码')
        else:
            reply('❌*错误*\n你已经绑定过账号了！')
    else:
        if gid == tg_group:
            if result is False:
                callback = reply('❌*错误*\n为了你的账号安全，请私聊我！')
            else:
                callback = reply('❌*错误*\n你已经绑定过账号了！')
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def unbind(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            reply('❌*错误*\n你还没有绑定过账号！')
        else:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Module.onLogin(email, password) is True:
                    result, id = Module.getTGbyMail(email)
                    if id == tid:
                        reply('✔️*成功*\n你已成功解绑 Telegram 了！')
                        Command.onUnBind(email)
                    else:
                        reply('❌*错误*\n这个账号与绑定的 Telegram 不匹配！')
                else:
                    reply('❌*错误*\n邮箱或密码错误了！')
            else:
                reply('❌*错误*\n正确的格式为：/unbind 邮箱 密码')
    else:
        if gid == tg_group:
            if result is False:
                callback = reply('❌*错误*\n你还没有绑定过账号！')
            else:
                callback = reply('❌*错误*\n为了你的账号安全，请私聊我！')
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def mysub(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            reply('❌*错误*\n请先绑定账号后才进行操作！')
        else:
            # 根据客户端
            text, reply_markup = Command.onMySub(user['token'])
            reply(text)
    else:
        if gid == tg_group:
            if result is False:
                callback = reply('❌*错误*\n请先绑定账号后才进行操作！')
            else:
                callback = reply('❌*错误*\n为了你的账号安全，请私聊我！')
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myinfo(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private' or gid == tg_group:
        if result is False:
            callback = reply('❌*错误*\n请先绑定账号后才进行操作！')
        else:
            if user['plan'] is not None:
                text = Command.onMyInfo(user)
                callback = reply(text)
            else:
                callback = reply('❌*错误*\n你的账号没有购买过订阅！')
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myusage(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)
    if chat_type == 'private' or gid == tg_group:
        if result is False:
            callback = reply('❌*错误*\n请先绑定账号后才进行操作！')
        else:
            result, statlist = Module.getUserStat(user['uid'])
            if result is True:
                text, reply_markup = Command.onMyUsage(statlist)
                callback = reply(text, reply_markup=reply_markup)
            else:
                callback = reply('❌*错误*\n你还没有消耗过流量！')
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myinvite(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private' or gid == tg_group:
        if result is False:
            callback = reply('❌*错误*\n请先绑定账号后才进行操作！')
        else:
            invite_code = Module.getInviteCode(user['id'])
            if invite_code is not None:
                invite_times = Module.getInviteTimes(user['id'])
                text = Command.onMyInvite(invite_code, invite_times)
                callback = reply(text)
            else:
                keyboard = [[InlineKeyboardButton(
                    text=f'点击打开网站', url=f"{v2_url}/#/invite")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                callback = reply('❌*错误*\n你还没有生成过邀请码，点击前往网站生成一个吧！',
                                 reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def buyplan(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    if chat_type == 'private' or gid == tg_group:
        text, reply_markup = Command.onBuyPlan()
        callback = reply(text, reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def website(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    if chat_type == 'private' or gid == tg_group:
        text, reply_markup = Command.onWebsite()
        callback = reply(text, reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


class Module:
    def autoDelete(update, chatid, messageid):
        time.sleep(30)
        bot.deleteMessage(chat_id=chatid, message_id=messageid)
        update.message.delete()

    def onLogin(email, password):
        login = {
            "email": email,
            "password": password
        }
        x = requests.post(
            f'{v2_url}/api/v1/passport/auth/login', login)
        if x.status_code == 200:
            return True
        else:
            return False

    def getUser(t, id):
        # args t = id or telegram_id
        # return boolean, userdata as dict
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(f"SELECT * FROM v2_user WHERE `{t}` = {id}")
            result = cursor.fetchone()
            if result is None:
                user = {}
                return False, user
            else:
                user = {
                    'uid': result[0],
                    'tg': result[2],
                    'email': result[3],
                    'money': result[7],
                    'time': result[12],
                    'upload': result[13],
                    'download': result[14],
                    'total': result[15],
                    'plan': result[23],
                    'token': result[26],
                    'expire': result[28],
                    'register': result[29]}
                return True, user

    def getUserStat(uid):
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM v2_stat_user WHERE `user_id` = {uid}")
            result = cursor.fetchall()
            print(result)
            if len(result) < 1:
                return False, result
            else:
                return True, result

    def getTGbyMail(email):
        # args email
        # return boolean, TelegramID
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT telegram_id FROM v2_user WHERE email = %s", (email))
            result = cursor.fetchone()
            if result[0] is None:
                return False, 0
            else:
                return True, result[0]

    def getPlanName(planid):
        # args planid
        # return planname
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM v2_plan WHERE id = %s", (planid))
            result = cursor.fetchone()
            return result[0]

    def getInviteCode(uid):
        # args user id
        # return code,status,pv
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT code,status,pv FROM v2_invite_code WHERE user_id = %s", (uid))
            result = cursor.fetchone()
            return result

    def getPlanAll():
        # return planID & Name (Only enable plan)
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id,name FROM v2_plan WHERE `show` = 1")
            result = cursor.fetchall()
            return result

    def getInviteTimes(uid):
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM v2_user WHERE invite_user_id =  %s", (uid))
            result = cursor.fetchall()
            return len(result)


class Command:
    def onBind(tid, email):
        # args tid,email
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE v2_user SET telegram_id = %s WHERE email = %s", (int(tid), email))

    def onUnBind(email):
        # args email
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE v2_user SET telegram_id = NULL WHERE email = %s", (email))

    def onBuyPlan():
        text = '📦*购买套餐*\n\n🌐点击下方按钮来前往购买地址'
        plan = Module.getPlanAll()
        keyboard = []
        url = f'{v2_url}/#/plan/'
        for i in plan:
            keyboard.append([InlineKeyboardButton(
                text=f'购买 {i[1]}', url=f"{url}{i[0]}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        return text, reply_markup

    def onWebsite():
        text = '🗺*前往网站*\n\n🌐点击下方按钮来前往网站地址'
        keyboard = [[InlineKeyboardButton(text='打开网站', url=f"{v2_url}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return text, reply_markup

    def onMyInfo(user):
        text = '📋*个人信息*\n'
        User_id = user['uid']
        Register_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(user['register']))
        Plan_id = Module.getPlanName(user['plan'])
        Expire_time = '长期有效'
        if user['expire'] is not None:
            Expire_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(user['expire']))
        Data_Upload = round(user['upload'] / 1024 / 1024 / 1024, 2)
        Data_Download = round(user['download'] / 1024 / 1024 / 1024, 2)
        Data_Total = round(user['total'] / 1024 / 1024 / 1024, 2)
        Data_Last = round(
            (user['total']-user['download']-user['upload']) / 1024 / 1024 / 1024, 2)
        Data_Time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(user['time']))

        text = f'{text}\n🎲*UID：* {User_id}'
        text = f'{text}\n⌚️*注册时间：* {Register_time}'
        text = f'{text}\n📚*套餐名称：* {Plan_id}'
        text = f'{text}\n📌*到期时间：* {Expire_time}'
        text = f'{text}\n'
        text = f'{text}\n📤*上传流量：* {Data_Upload} GB'
        text = f'{text}\n📥*下载流量：* {Data_Download} GB'
        text = f'{text}\n📃*剩余流量：* {Data_Last} GB'
        text = f'{text}\n📜*总计流量：* {Data_Total} GB'
        text = f'{text}\n📊*上次使用：* {Data_Time}'
        return text

    def onMySub(token):
        header = '📚*订阅链接*\n\n🔮通用订阅地址为（点击即可复制）：\n'
        tolink = f'`{v2_url}/api/v1/client/subscribe?token={token}`'
        buttom = '\n\n⚠️*如果订阅链接泄露请前往官网重置！*'
        keyboard = []
        text = f'{header}{tolink}{buttom}'
        reply_markup = InlineKeyboardMarkup(keyboard)

        return text, reply_markup

    def onMyInvite(invite_code, invite_times):
        code = invite_code[0]
        header = '📚*邀请信息*\n\n🔮邀请地址为（点击即可复制）：\n'
        tolink = f'`{v2_url}/#/register?code={code}`'
        buttom = f'\n\n👪*邀请人数：* {invite_times}'
        text = f'{header}{tolink}{buttom}'

        return text

    def onMyUsage(stat):
        current_date = datetime.datetime.now(tz).strftime("%Y-%m-%d")
        today_usage = 0
        for i in stat:
            today_date = i[6]
            ltime = time.localtime(today_date)
            today_date = time.strftime("%Y-%m-%d", ltime)
            if today_date == current_date:
                today_usage = today_usage + i[4]
        today_usage = round(today_usage / 1024 / 1024 / 1024, 2)

        text = f'📚*今日流量*\n\n📈本日总计使用流量为：*{today_usage} GB*\n'
        text = f'{text}\n📜*详细流量记录请点击下方按钮*'
        keyboard = [[InlineKeyboardButton(
            text='流量明细', url=f"{v2_url}/#/traffic")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        return text, reply_markup


def main() -> None:
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("s", s, run_async=True))
    dispatcher.add_handler(CommandHandler("ping", ping, run_async=True))
    dispatcher.add_handler(CommandHandler("bind", bind, run_async=True))
    dispatcher.add_handler(CommandHandler("unbind", unbind, run_async=True))
    dispatcher.add_handler(CommandHandler("mysub", mysub, run_async=True))
    dispatcher.add_handler(CommandHandler("myinfo", myinfo, run_async=True))
    dispatcher.add_handler(CommandHandler("myusage", myusage, run_async=True))
    dispatcher.add_handler(CommandHandler(
        "myinvite", myinvite, run_async=True))
    dispatcher.add_handler(CommandHandler("buyplan", buyplan, run_async=True))
    dispatcher.add_handler(CommandHandler("website", website, run_async=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
