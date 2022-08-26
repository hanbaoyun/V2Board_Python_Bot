#!/usr/bin/env python

import logging
import requests
import pymysql
import time
from sshtunnel import SSHTunnelForwarder

from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext

import Message
import Config
import Command

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
bot = Bot(Config.bot_token)

# Enable ssh
if Config.ssh_enable is True:
    ssh = SSHTunnelForwarder(
        ssh_address_or_host=(Config.ssh_ip, Config.ssh_port),
        ssh_username=Config.ssh_user,
        ssh_password=Config.ssh_pass,
        remote_bind_address=(Config.v2_db_url, Config.v2_db_port))
    ssh.start()
    v2_db_port = ssh.local_bind_port
# Database Connection
db = pymysql.connect(host=Config.v2_db_url,
                     user=Config.v2_db_user,
                     password=Config.v2_db_pass,
                     database=Config.v2_db_name,
                     port=v2_db_port,
                     autocommit=True)


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
                        reply(Message.Success_Bind)
                        Command.onBind(tid, email)
                    else:
                        reply(Message.Error_BindOther)
                else:
                    reply(Message.Error_Login)
            else:
                reply(Message.Error_BindUsage)
        else:
            reply(Message.Error_BindAlready)
    else:
        if gid == Config.tg_group:
            if result is False:
                callback = reply(Message.Error_PrivateOnly)
            else:
                callback = reply(Message.Error_BindAlready)
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def unbind(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            reply(Message.Error_NotBind)
        else:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Module.onLogin(email, password) is True:
                    result, id = Module.getTGbyMail(email)
                    if id == tid:
                        reply(Message.Success_UnBind)
                        Command.onUnBind(email)
                    else:
                        reply(Message.Error_UnBindNoMatch)
                else:
                    reply(Message.Error_Login)
            else:
                reply(Message.Error_UnBindUsage)
    else:
        if gid == Config.tg_group:
            if result is False:
                callback = reply(Message.Error_NotBind)
            else:
                callback = reply(Message.Error_PrivateOnly)
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def mysub(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            reply(Message.Error_NotBind)
        else:
            # 根据客户端
            text, reply_markup = Command.onMySub(user['token'])
            reply(text)
    else:
        if gid == Config.tg_group:
            if result is False:
                callback = reply(Message.Error_NotBind)
            else:
                callback = reply(Message.Error_PrivateOnly)
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myinfo(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private' or gid == Config.tg_group:
        if result is False:
            callback = reply(Message.Error_NotBind)
        else:
            if user['plan'] is not None:
                text = Command.onMyInfo(user)
                callback = reply(text)
            else:
                callback = reply(Message.Error_MyInfoNotFound)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myusage(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)
    if chat_type == 'private' or gid == Config.tg_group:
        if result is False:
            callback = reply(Message.Error_NotBind)
        else:
            result, statlist = Module.getUserStat(user['uid'])
            if result is True:
                text, reply_markup = Command.onMyUsage(statlist)
                callback = reply(text, reply_markup=reply_markup)
            else:
                callback = reply(Message.Error_MyUsageNotFound)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myinvite(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private' or gid == Config.tg_group:
        if result is False:
            callback = reply(Message.Error_NotBind)
        else:
            invite_code = Module.getInviteCode(user['uid'])
            if invite_code is not None:
                invite_times = Module.getInviteTimes(user['uid'])
                text = Command.onMyInvite(invite_code, invite_times)
                callback = reply(text)
            else:
                keyboard = [[InlineKeyboardButton(
                    text=f'点击打开网站', url=f"{Config.v2_url}/#/invite")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                callback = reply(Message.Error_MyInviteNotFound,
                                 reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def buyplan(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    if chat_type == 'private' or gid == Config.tg_group:
        text, reply_markup = Command.onBuyPlan()
        callback = reply(text, reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def website(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    if chat_type == 'private' or gid == Config.tg_group:
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
            f'{Config.v2_url}/api/v1/passport/auth/login', login)
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



def main() -> None:
    updater = Updater(Config.bot_token)

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
