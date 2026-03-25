import telebot
BOT_TOKEN = "8727191543:AAEw0kZC80MxIVEY7In8NQa0oXdGFQL551Q"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ 测试成功！机器人已启动！")

bot.infinity_polling()
