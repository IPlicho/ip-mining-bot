# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
from datetime import datetime

# ====================== 核心配置 ======================
ADMIN_IDS = [8401979801, 8401979801]
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
bot = telebot.TeleBot(BOT_TOKEN)

# ====================== 雙語完整文案 ======================
TEXT = {
    "zh": {
        "home": """🏠 擔保服務平台
安全 · 高效 · 可信 · 全程擔保

本平台提供第三方中立擔保服務，保障交易雙方資金與權益安全。""",
        "service": """📌 擔保項目
• USDT 轉帳擔保
• 線上交易擔保
• 線下交易擔保
• 合約履約擔保
• 多人交易擔保""",
        "apply": "🛡️ 申請成為中間人\n提交後等待管理員審核",
        "create": "🚀 發起擔保\n選擇類型 → 填金額 → 提交訂單",
        "help": "📖 使用說明",
        "guarantor": "🛡️ 中間人中心\n可接單、查看訂單、確認完成",
        "back": "🏠 返回首頁",
        "lang": "🌐 English"
    },
    "en": {
        "home": """🏠 Escrow Platform
Safe · Efficient · Reliable

We provide neutral escrow service to protect both parties.""",
        "service": """📌 Services
• USDT Transfer Escrow
• Online Trade Escrow
• Offline Trade Escrow
• Contract Escrow
• Multi-party Escrow""",
        "apply": "🛡️ Apply to be Guarantor",
        "create": "🚀 Create Order\nChoose type → Enter amount → Submit",
        "help": "📖 Help",
        "guarantor": "🛡️ Guarantor Center\nView & Accept Orders",
        "back": "🏠 Back",
        "lang": "🌐 繁中"
    }
}

# ====================== 數據 ======================
user_lang = {}
data = {
    "users": {},
    "orders": {},
    "guarantors": {},
    "applications": {}
}

# ====================== 選單 ======================
def main_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton(t["service"], callback_data="service"),
        InlineKeyboardButton(t["apply"], callback_data="apply"),
        InlineKeyboardButton(t["create"], callback_data="create"),
        InlineKeyboardButton(t["help"], callback_data="help"),
        InlineKeyboardButton(t["guarantor"], callback_data="guarantor"),
        InlineKeyboardButton(t["lang"], callback_data="lang")
    )
    return m

def back_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    m = InlineKeyboardMarkup(row_width=1)
    m.add(InlineKeyboardButton(TEXT[lang]["back"], callback_data="home"))
    return m

# ====================== 啟動 ======================
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    user_lang[user_id] = "zh"
    bot.send_message(msg.chat.id, TEXT["zh"]["home"], reply_markup=main_menu(user_id))

# ====================== 按鈕回調 ======================
@bot.callback_query_handler(func=lambda c: True)
def callback_all(c):
    u = c.from_user.id
    cid = c.message.chat.id
    mid = c.message.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]

    if c.data == "home":
        bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

    elif c.data == "service":
        bot.edit_message_text(t["service"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "apply":
        bot.edit_message_text(t["apply"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "create":
        bot.edit_message_text(t["create"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "help":
        bot.edit_message_text(t["help"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "guarantor":
        bot.edit_message_text(t["guarantor"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "lang":
        user_lang[u] = "en" if lang == "zh" else "zh"
        new_lang = user_lang[u]
        bot.edit_message_text(TEXT[new_lang]["home"], cid, mid, reply_markup=main_menu(u))

    bot.answer_callback_query(c.id)

# ====================== 管理員指令 ======================
@bot.message_handler(commands=['审核','拒绝','封锁','解除','派单','完成','用户信息'])
def admin_cmd(msg):
    if msg.from_user.id not in ADMIN_IDS:
        msg.reply("❌ 無權限")
        return
    msg.reply("🔐 管理員指令已接收")

# ====================== 運行 ======================
if __name__ == "__main__":
    print("✅ 機器人啟動成功 - 100% 可回覆")
    bot.infinity_polling()
