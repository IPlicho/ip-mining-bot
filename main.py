import telebot

# 你的中间人机器人Token，和BotFather完全一致
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "✅ 机器人正常运行！")

# 启动，和你用户端完全一样的写法
if __name__ == "__main__":
    bot.polling(none_stop=True)
