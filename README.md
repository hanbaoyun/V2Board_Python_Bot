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
| 指令 | 参数 | 描述 |
|:-----:|:-----:|:-----:|
| ping | 无 | 获取聊天的ID |
| bind | 邮箱 密码 | 绑定该邮箱到Telegram |
| unbind | 邮箱 密码 | 解绑该邮箱的Telegram |
| mysub | 无 | 获取该账号的订阅链接 |
| myinfo | 无 | 获取该账号的订阅信息 |
| myusage | 无 | 获取该账号的流量明细 |
| myinvite | 无 | 获取该账号的邀请信息 |
| buyplan | 无 | 获取购买套餐链接 |
| website | 无 | 获取网站链接 |

## 如何使用

```
# apt install git 如果你没有git的话
git clone https://github.com/DyAxy/V2Board_Python_Bot.git
cd V2Board_Python_Bot
# 你需要安装好 pip3 的包管理
pip3 install -r requirements.txt
cp Config.py.example Config.py
nano Config.py
# 编辑 line 2 为你的Bot Token
# 编辑 line 4、5 为你的ID和群ID，通过 /ping 获取
# 编辑 line 7 为你的V2Board地址，最后请不要加 / 符号
# 编辑 line 9~13 为你的MySQL连接信息
# 编辑 line 15 如果你需要SSH连接数据库 则为True
# 编辑 line 16~19 为你的SSH连接信息
python3 bot.py
```

## 申请 Telegram Bot Token

1. 私聊 [https://t.me/BotFather](https://https://t.me/BotFather)
2. 输入 `/newbot`，并为你的bot起一个**响亮**的名字
3. 接着为你的bot设置一个username，但是一定要以bot结尾，例如：`v2board_bot`
4. 最后你就能得到bot的token了，看起来应该像这样：`123456789:gaefadklwdqojdoiqwjdiwqdo`