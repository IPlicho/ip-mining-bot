import telebot

BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda msg: True)
def all_msg(msg):
    if msg.text == "/start":
        bot.send_message(msg.chat.id, "✅ 机器人正常运行！")

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except:
            continue
