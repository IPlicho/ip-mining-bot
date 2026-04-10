# -*- coding: utf-8 -*-
import telebot
import os
import sys

# 你的机器人Token（和BotFather完全一致，不要改）
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"

# 初始化机器人（Railway 必须加 threaded=True）
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# 只保留/start响应，最简单、最稳定
@bot.message_handler(commands=['start'])
def start(msg):
    print(f"✅ 收到/start，用户ID: {msg.from_user.id}")
    bot.send_message(msg.chat.id, "✅ 机器人正常运行！测试成功！\n🤖 @MyEscrowBot88bot")

# Railway专属启动，必须用none_stop=True
if __name__ == "__main__":
    print("="*60)
    print("✅ Railway 测试机器人启动成功！")
    print(f"🤖 机器人: @MyEscrowBot88bot")
    print(f"🔑 Token: {BOT_TOKEN}")
    print("="*60)
    try:
        # Railway必须用这个长轮询配置，绝对不会崩溃
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        sys.exit(1)
