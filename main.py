import telebot

BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
bot = telebot.TeleBot(BOT_TOKEN)

# 同时处理 /start 和所有普通消息，彻底防崩溃
@bot.message_handler(func=lambda msg: True)
def echo_all(msg):
    if msg.text == "/start":
        bot.send_message(msg.chat.id, "✅ 机器人稳定运行！")
    else:
        bot.send_message(msg.chat.id, "收到消息！")

# 用最稳的启动方式，Railway 绝对不杀进程
if __name__ == "__main__":
    print("✅ 机器人启动成功，持续运行中...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"⚠️ 连接中断，自动重连: {e}")
            continue
