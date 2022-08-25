# V2Board Telegram Bot via Python

一个简单的项目，让 V2Board Telegram Bot 支持更丰富的功能。

Python 版本需求 >= 3.8

## 现有功能
- 基于MySQl，支持以SSH方式登录
- 自动删除群聊中信息
- 支持Bot内绑定、解绑
- 支持获取用户信息、订阅、邀请
- 支持获取套餐并生成购买按钮

## 现有指令
- 聊天信息（/ping）
- 账号绑定（/bind） - 仅限私聊
- 账号解绑（/unbind） - 仅限私聊
- 订阅链接（/mysub） - 仅限私聊
- 订阅信息（/myinfo）
- 邀请信息（/myinvite）
- 套餐购买（/buyplan)
- 打开网页（/website)

## 如何使用

```
# apt install git 如果你没有git的话
git clone https://github.com/DyAxy/V2Board_Python_Bot.git
cd V2Board_Python_Bot
# 你需要安装好 pip3 的包管理
pip3 install -r requirements.txt
nano bot.py
# 编辑 line 13 为你的Bot Token
# 编辑 line 15 为你的V2Board地址，最后请不要加 / 符号
# 编辑 line 17~21 为你的MySQL连接信息
# 编辑 line 23 如果你需要SSH连接数据库 则为True
# 编辑 line 24~27 为你的SSH连接信息
python3 bot.py
```

## 申请 Telegram Bot Token

1. 私聊 [https://t.me/BotFather](https://https://t.me/BotFather)
2. 输入 `/newbot`，并为你的bot起一个**响亮**的名字
3. 接着为你的bot设置一个username，但是一定要以bot结尾，例如：`v2board_bot`
4. 最后你就能得到bot的token了，看起来应该像这样：`123456789:gaefadklwdqojdoiqwjdiwqdo`