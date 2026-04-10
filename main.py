import telebot
import os
from flask import Flask, request

# 你的机器人Token（和BotFather完全一致）
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
bot = telebot.TeleBot(BOT_TOKEN)

# Flask 服务（Railway 自动分配端口，不用改）
app = Flask(__name__)

# 处理 /start 指令
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "✅ 机器人稳定运行！Webhook 模式，永不掉线！")

# Webhook 入口（Telegram 主动推消息，Railway 绝对不杀进程）
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Forbidden", 403

# 健康检查（Railway 要求，防止休眠）
@app.route("/")
def health():
    return "Bot is running!", 200

if __name__ == "__main__":
    # Railway 自动分配端口，直接用
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
