# -*- coding: utf-8 -*-
import telebot
import os
from flask import Flask
from threading import Thread

# 你最新的TOKEN
BOT_TOKEN = "8727191543:AAFwx7dpoGK1icoCxhS0Xp3qpi4W5n4nfHE"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask("")

@app.route("/")
def home():
    return "Bot Alive"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, "✅ 机器人正常工作！")

@bot.message_handler(func=lambda m: True)
def reply_all(msg):
    bot.send_message(msg.chat.id, "📩 收到：" + msg.text)

if __name__ == "__main__":
    Thread(target=run, daemon=True).start()
    print("✅ Bot started")
    bot.infinity_polling()
