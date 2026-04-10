import telebot
import os
from flask import Flask, request

# 你的中间人机器人专属Token
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
# 管理员ID（填你自己的Telegram用户ID）
ADMIN_ID = 123456789  # 替换为你的真实ID

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 中间人端主菜单
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("📋 待接单列表")
    btn2 = telebot.types.KeyboardButton("✅ 已派单订单")
    btn3 = telebot.types.KeyboardButton("ℹ️ 管理员说明")
    markup.add(btn1, btn2, btn3)
    return markup

# /start 触发菜单
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "✅ 中间人端管理员已登录！欢迎使用接单/派单系统👇",
            reply_markup=main_menu()
        )
    else:
        bot.send_message(message.chat.id, "❌ 您无权限使用此系统！")

# 菜单按钮响应
@bot.message_handler(func=lambda msg: True)
def handle_menu(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ 您无权限使用此系统！")
        return
    
    if message.text == "📋 待接单列表":
        bot.send_message(message.chat.id, "📋 待接单订单列表")
    elif message.text == "✅ 已派单订单":
        bot.send_message(message.chat.id, "✅ 已派单订单列表")
    elif message.text == "ℹ️ 管理员说明":
        bot.send_message(message.chat.id, "ℹ️ 中间人端仅管理员可操作，用于接单/派单")
    else:
        bot.send_message(message.chat.id, f"收到：{message.text}")

# Webhook 入口
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Forbidden", 403

# 健康检查
@app.route("/")
def health():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
