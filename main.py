@bot.message_handler(commands=['start'])  # 只处理 /start 指令
def start(msg):
    bot.send_message(msg.chat.id, "✅ 机器人正常运行！")
