#!/usr/bin/env python

import logging
import requests
import pymysql
import time
from sshtunnel import SSHTunnelForwarder

from telegram import Update, Bot,InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

# Telegram Bot Token
bot_token = ''
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
                     port=v2_db_port)
cursor = db.cursor()

# Debugging
def s(update: Update, context: CallbackContext) -> None:
    print(update)


def bind(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    try:
        if Module.onSearchViaTG(uid) is False:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Command.onBind(email,password) is True:
                    if Module.onSearchViaMail(email) is False:
                        reply('✔️*成功*\n你已成功绑定账号了！')
                        cursor.execute(
                            "UPDATE v2_user SET telegram_id = %s WHERE email = %s", (int(uid), email))
                        db.commit()
                    else:
                        reply(
                            '❌*错误*\n这个账号已绑定到别的Telegram了！')
                else:
                    reply('❌*错误*\n邮箱或密码错误了！')
            else:
                reply('❌*错误*\n正确的格式为：/bind 邮箱 密码')
        else:
            reply('❌*错误*\n你已经绑定过账号了！')
    except Exception as error:
        logging.error(error)


def bindingroup(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    callback = None
    try:
        result, user = Module.onSearchViaTG(uid)
        if result is False:
            callback = reply('❌*错误*\n为了你的账号安全，请私聊我来绑定')
        else:
            callback = reply('❌*错误*\n你已经绑定过账号了！')
        Module.autoDelete(update, callback.chat.id, callback.message_id)
    except Exception as error:
        logging.error(error)


def myinfo(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    callback = None
    try:
        result, user = Module.onSearchViaTG(uid)
        if result is False:
            callback = reply('❌*错误*\n请先绑定账号后才进行操作！')
        else:
            if user['plan'] is not None:
                text = '📋*个人信息*\n'
                User_id = user['id']
                Register_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(user['register']))
                Plan_id = Module.onSearchPlan(user['plan'])
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
                text = f'{text}\n📚*套餐类型：* {Plan_id}'
                text = f'{text}\n📌*到期时间：* {Expire_time}'
                text = f'{text}\n'
                text = f'{text}\n📤*上传流量：* {Data_Upload} GB'
                text = f'{text}\n📥*下载流量：* {Data_Download} GB'
                text = f'{text}\n📃*剩余流量：* {Data_Last} GB'
                text = f'{text}\n📜*总计流量：* {Data_Total} GB'
                text = f'{text}\n📊*上次使用：* {Data_Time}'
                callback = reply(text)
            else:
                callback = reply('❌*错误*\n你的账号没有购买过订阅！')
        if update.message.chat.type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)
    except Exception as error:
        logging.error(error)


def buyplan(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    callback = None
    try:
        reply_markup = Module.onBuyPlan()
        callback = reply('📦*购买套餐*\n\n🌐点击下方按钮来前往购买地址',reply_markup=reply_markup)
        if update.message.chat.type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)
    except Exception as error:
        logging.error(error)


class Module():
    def autoDelete(update, chatid, messageid):
        time.sleep(30)
        bot.deleteMessage(chat_id=chatid, message_id=messageid)
        update.message.delete()

    def onSearchViaTG(uid):
        #args TelegramID
        #return boolean, userdata as dict
        cursor.execute(f"SELECT * FROM v2_user WHERE telegram_id = {uid}")
        result = cursor.fetchone()
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
                'expire': result[28],
                'register': result[29]
            }
            return True, user

    def onSearchViaMail(email):
        #args email
        #return boolean, TelegramID
        cursor.execute(
            "SELECT telegram_id FROM v2_user WHERE email = %s", (email))
        result = cursor.fetchone()
        if result[0] is None:
            return False,0
        else:
            return True, result[0]

    def onSearchPlan(planid):
        #args planid
        #return planname
        cursor.execute(
            "SELECT name FROM v2_plan WHERE id = %s", (planid))
        result = cursor.fetchone()
        return result[0]

    def getAllPlan():
        #return planID & Name (Only enable plan)
        cursor.execute(
            "SELECT id,name FROM v2_plan WHERE `show` = 1")
        result = cursor.fetchall()
        return result
        # {v2_url}/#/plan/1

    def onBuyPlan():
        plan = Module.getAllPlan()
        keyboard = []
        url = f'{v2_url}/#/plan/'
        for i in plan:
            keyboard.append([InlineKeyboardButton(text=f'购买 {i[1]}', url=f"{url}{i[0]}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        return reply_markup
        



class Command():
    def onBind(email,password):
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


def main() -> None:
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("s", s, run_async=True))
    dispatcher.add_handler(CommandHandler(
        "bind", bind, filters=Filters.chat_type.private, run_async=True))
    dispatcher.add_handler(CommandHandler(
        "bind", bindingroup, filters=Filters.chat_type.groups, run_async=True))
    dispatcher.add_handler(CommandHandler("myinfo", myinfo, run_async=True))
    dispatcher.add_handler(CommandHandler("buyplan", buyplan, run_async=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
