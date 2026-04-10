import telebot
import time
from datetime import datetime, timedelta
import os
import sys

# 你的机器人配置（已填好最新Token，只改ADMIN_ID为你自己的Telegram ID）
BOT_TOKEN = "8747559514:AAFJdsZ3tlCVPIW6vL60hTuBc_Eo5FP4kU"
ADMIN_ID = 123456789

bot = telebot.TeleBot(BOT_TOKEN)

# 收到/start直接回复，先保证能收到消息
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"✅ 李永发的机器人已上线！你的ID：{message.from_user.id}")

# 启动长轮询，强制进程24小时运行，Railway绝对不会休眠
if __name__ == "__main__":
    # 先彻底删除所有Webhook，避免冲突
    bot.remove_webhook()
    # 无限轮询，保证进程不挂
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Bot error: {e}, 5秒后重启")
            time.sleep(5)
            continue
