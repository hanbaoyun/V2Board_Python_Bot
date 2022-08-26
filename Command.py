import time
import pytz
import datetime

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import bot
import Config

Module = bot.Module
db = bot.db
# TineZone
tz = pytz.timezone('Asia/Shanghai')

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
    url = f'{Config.v2_url}/#/plan/'
    for i in plan:
        keyboard.append([InlineKeyboardButton(
            text=f'购买 {i[1]}', url=f"{url}{i[0]}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup

def onWebsite():
    text = '🗺*前往网站*\n\n🌐点击下方按钮来前往网站地址'
    keyboard = [[InlineKeyboardButton(
        text='打开网站', url=f"{Config.v2_url}")]]
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
    tolink = f'`{Config.v2_url}/api/v1/client/subscribe?token={token}`'
    buttom = '\n\n⚠️*如果订阅链接泄露请前往官网重置！*'
    keyboard = []
    text = f'{header}{tolink}{buttom}'
    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup

def onMyInvite(invite_code, invite_times):
    code = invite_code[0]
    header = '📚*邀请信息*\n\n🔮邀请地址为（点击即可复制）：\n'
    tolink = f'`{Config.v2_url}/#/register?code={code}`'
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
        text='流量明细', url=f"{Config.v2_url}/#/traffic")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup