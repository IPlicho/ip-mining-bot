# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
from datetime import datetime

# ====================== 配置 ======================
ADMIN_IDS = [8401979801, 8401979801]
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ====================== 雙語文案 ======================
TEXT = {
    "zh": {
        "home": "🏠 擔保服務平台\n安全 · 高效 · 可信\n\n本平台提供第三方中立擔保服務。",
        "service": "📌 擔保項目\n• USDT 轉帳\n• 線上交易\n• 線下交易\n• 合約履約\n• 多人交易",
        "apply": "🛡️ 申請成為擔保人\n提交後等待管理員審核",
        "create": "🚀 發起擔保\n選擇類型 → 填金額 → 提交",
        "help": "📖 說明\n使用前請詳閱規則",
        "guarantor": "🛡️ 擔保人中心\n可接單、查看訂單、確認完成",
        "orders": "📋 我的訂單",
        "accept": "✅ 接單",
        "complete": "✅ 確認完成",
        "back": "🏠 返回",
        "lang": "🌐 English"
    },
    "en": {
        "home": "🏠 Escrow Platform\nSafe · Fast · Reliable\n\nWe provide neutral escrow service.",
        "service": "📌 Services\n• USDT Transfer\n• Online Trade\n• Offline Trade\n• Contract\n• Multi-party",
        "apply": "🛡️ Apply to be Guarantor",
        "create": "🚀 Create Order",
        "help": "📖 Help",
        "guarantor": "🛡️ Guarantor Center",
        "orders": "📋 My Orders",
        "accept": "✅ Accept",
        "complete": "✅ Complete",
        "back": "🏠 Back",
        "lang": "🌐 繁中"
    }
}

user_lang = {}
data = {"users": {}, "orders": {}}

# ====================== 選單 ======================
def main_menu(u):
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton(t["service"], callback="service"),
        InlineKeyboardButton(t["apply"], callback="apply"),
        InlineKeyboardButton(t["create"], callback="create"),
        InlineKeyboardButton(t["help"], callback="help"),
        InlineKeyboardButton(t["guarantor"], callback="guarantor"),
        InlineKeyboardButton(t["lang"], callback="lang")
    )
    return m

def back_menu(u):
    lang = user_lang.get(u, "zh")
    m = InlineKeyboardMarkup(row_width=1)
    m.add(InlineKeyboardButton(TEXT[lang]["back"], callback="home"))
    return m

# ====================== 啟動 ======================
@bot.message_handler(commands=["start"])
def start(msg):
    u = msg.from_user.id
    user_lang[u] = "zh"
    bot.send_message(msg.chat.id, TEXT["zh"]["home"], reply_markup=main_menu(u))

# ====================== 按鈕 ======================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    u = c.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    m = c.message.id
    ch = c.message.chat.id

    if c.data == "home":
        bot.edit_message_text(t["home"], ch, m, reply_markup=main_menu(u))
    elif c.data == "service":
        bot.edit_message_text(t["service"], ch, m, reply_markup=back_menu(u))
    elif c.data == "apply":
        bot.edit_message_text(t["apply"], ch, m, reply_markup=back_menu(u))
    elif c.data == "create":
        bot.edit_message_text(t["create"], ch, m, reply_markup=back_menu(u))
    elif c.data == "help":
        bot.edit_message_text(t["help"], ch, m, reply_markup=back_menu(u))
    elif c.data == "guarantor":
        bot.edit_message_text(t["guarantor"], ch, m, reply_markup=back_menu(u))
    elif c.data == "lang":
        user_lang[u] = "en" if lang == "zh" else "zh"
        new_lang = user_lang[u]
        bot.edit_message_text(TEXT[new_lang]["home"], ch, m, reply_markup=main_menu(u))
    bot.answer_callback_query(c.id)

# ====================== 運行 ======================
if __name__ == "__main__":
    print("✅ 雙語擔保機器人啟動")
    bot.infinity_polling()
