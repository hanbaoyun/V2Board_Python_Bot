#!/usr/bin/env python

import logging
import requests
import pymysql
import time
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


def s(update: Update, context: CallbackContext) -> None:
    # Debugging
    print(update)


def ping(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    text = '💥*嘭*\n'
    uuid = f'{text}\n你的ID为：`{uid}`'

    if chat_type == 'private':
        reply(uuid)
    elif gid == tg_group:
        group = f'\n群组ID为：`{gid}`'
        if update.message.from_user.is_bot is False:
            callback = reply(f'{uuid}{group}')
        else:
            callback = reply(f'{text}{group}')
        Module.autoDelete(update, callback.chat.id, callback.message_id)


def bind(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.onSearchViaID('telegram_id', uid)

    if chat_type == 'private':
        if result is False:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Module.onLogin(email, password) is True:
                    result, tig = Module.onSearchViaMail(email)
                    if result is False:
                        reply('✔️*成功*\n你已成功绑定 Telegram 了！')
                        Command.onBind(uid, email)
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
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.onSearchViaID('telegram_id', uid)

    if chat_type == 'private':
        if result is False:
            reply('❌*错误*\n你还没有绑定过账号！')
        else:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Module.onLogin(email, password) is True:
                    result, tid = Module.onSearchViaMail(email)
                    if tid == uid:
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
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.onSearchViaID('telegram_id', uid)

    if chat_type == 'private':
        if result is False:
            reply('❌*错误*\n请先绑定账号后才进行操作！')
        else:
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
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.onSearchViaID('telegram_id', uid)
    
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


def myinvite(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.onSearchViaID('telegram_id', uid)

    if chat_type == 'private' or gid == tg_group:
        if result is False:
            callback = reply('❌*错误*\n请先绑定账号后才进行操作！')
        else:
            invite_code = Module.onSearchInvite(user['id'])
            if invite_code is not None:
                text = Command.onMyInvite(invite_code)
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
        reply_markup = Command.onBuyPlan()
        callback = reply('📦*购买套餐*\n\n🌐点击下方按钮来前往购买地址',
                         reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


class Module():
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

    def onSearchViaID(t, id):
        # args t = id or telegram_id
        # return boolean, userdata as dict
        with db.cursor() as cursor:
            cursor.execute(f"SELECT * FROM v2_user WHERE `{t}` = {id}")
            result = cursor.fetchone()
            print(result)
            if result is None:
                user = {}
                return False, user
            else:
                user = {
                    'id': result[0],
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

    def onSearchViaMail(email):
        # args email
        # return boolean, TelegramID
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT telegram_id FROM v2_user WHERE email = %s", (email))
            result = cursor.fetchone()
            print(result)
            if result[0] is None:
                return False, 0
            else:
                return True, result[0]

    def onSearchPlan(planid):
        # args planid
        # return planname
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM v2_plan WHERE id = %s", (planid))
            result = cursor.fetchone()
            print(result)
            return result[0]

    def onSearchInvite(id):
        # args user id
        # return code,status,pv
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT code,status,pv FROM v2_invite_code WHERE user_id = %s", (id))
            result = cursor.fetchone()
            print(result)
            return result

    def getAllPlan():
        # return planID & Name (Only enable plan)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id,name FROM v2_plan WHERE `show` = 1")
            result = cursor.fetchall()
            print(result)
            return result


class Command():
    def onBind(uid, email):
        # args uid,email
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE v2_user SET telegram_id = %s WHERE email = %s", (int(uid), email))

    def onUnBind(email):
        # args email
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE v2_user SET telegram_id = NULL WHERE email = %s", (email))

    def onBuyPlan():
        plan = Module.getAllPlan()
        keyboard = []
        url = f'{v2_url}/#/plan/'
        for i in plan:
            keyboard.append([InlineKeyboardButton(
                text=f'购买 {i[1]}', url=f"{url}{i[0]}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        return reply_markup

    def onMyInfo(user):
        text = '📋*个人信息*\n'
        User_id = user['id']
        Register_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(user['register']))
        Plan_id = Module.onSearchPlan(user['plan'])
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

    def onMyInvite(invite_code):
        code, status, pv = invite_code[0], invite_code[1], invite_code[2]
        header = '📚*邀请信息*\n\n🔮邀请地址为（点击即可复制）：\n'
        tolink = f'`{v2_url}/#/register?code={code}`'
        buttom = f'\n\n⚙️*状态：* {status}\n👪*人数：* {pv}'
        text = f'{header}{tolink}{buttom}'

        return text


def main() -> None:
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("s", s, run_async=True))
    dispatcher.add_handler(CommandHandler("ping", ping, run_async=True))
    dispatcher.add_handler(CommandHandler("bind", bind, run_async=True))
    dispatcher.add_handler(CommandHandler("unbind", unbind, run_async=True))
    dispatcher.add_handler(CommandHandler("mysub", mysub, run_async=True))
    dispatcher.add_handler(CommandHandler("myinfo", myinfo, run_async=True))
    dispatcher.add_handler(CommandHandler(
        "myinvite", myinvite, run_async=True))
    dispatcher.add_handler(CommandHandler("buyplan", buyplan, run_async=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
