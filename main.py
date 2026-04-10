import telebot
from flask import Flask, request
import os

# 你的机器人Token
BOT_TOKEN = "8716451687:AAFDXBQ-gG4AhJNVzH09NQnSwYWosZ_6ImI"
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Flask服务，Railway自动分配端口
app = Flask(__name__)

# 收到/start就回复
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ SecureEscrow Bot 已成功上线！")

# Webhook回调入口
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Forbidden", 403

# 初始化Webhook
@app.route("/")
def set_webhook():
    # Railway自动分配的域名，直接用环境变量获取
    webhook_url = f"https://{os.environ.get('RAILWAY_STATIC_URL')}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to: {webhook_url}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
