import telebot

# 【中间人端专属Token】从@BotFather复制，和用户端分开
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
bot = telebot.TeleBot(BOT_TOKEN)

# 收到/start直接回复
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "✅ 中间人端机器人已正常回复！")

# 收到任意消息都回复
@bot.message_handler(func=lambda msg: True)
def echo(msg):
    bot.send_message(msg.chat.id, f"中间人端收到：{msg.text}")

# 运行入口（和用户端完全一致）
if __name__ == "__main__":
    bot.polling(none_stop=True)
