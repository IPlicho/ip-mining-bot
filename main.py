import telebot
import time

# 已填好你最新的Token，直接用
BOT_TOKEN = "8716451687:AAFDXBQ-gG4AhJNVzH09NQnSwYWosZ_6ImI"
bot = telebot.TeleBot(BOT_TOKEN)

# 收到/start就回复，保证能收到消息
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ SecureEscrow Bot 已成功上线！")

# 启动长轮询，和你能成功的代码完全一致
if __name__ == "__main__":
    bot.remove_webhook()
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            time.sleep(3)
            continue
