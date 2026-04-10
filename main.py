import telebot
import time

# 已填好你最新的有效Token，直接用
BOT_TOKEN = "8716451687:AAFDXBQ-gG4AhJNVzH09NQnSwYWosZ_6ImI"
bot = telebot.TeleBot(BOT_TOKEN)

# 收到/start就回复，保证能收到消息
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ SecureEscrow Bot 已成功上线！")

# 启动长轮询，彻底告别Webhook，绝对不崩
if __name__ == "__main__":
    # 只保留这一行，彻底删除所有Webhook
    bot.remove_webhook()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Bot error: {e}, 3秒后自动重启")
            time.sleep(3)
            continue
