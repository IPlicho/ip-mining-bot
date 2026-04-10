import telebot

BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
bot = telebot.TeleBot(BOT_TOKEN)

# 处理所有消息，不管是/start还是普通文字，都回复
@bot.message_handler(func=lambda msg: True)
def handle_all(msg):
    bot.send_message(msg.chat.id, "✅ 机器人收到消息了！")

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except:
            continue
