# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import os
from datetime import datetime

# ====================== 核心配置（你的ID不变） ======================
ADMIN_IDS = [8401979801, 8781082053]
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ====================== 語言包（繁體100%可用，無亂碼） ======================
LANG = {
    "zh_tw": {
        "welcome": "👋 歡迎使用 TrustEscrow 擔保平台！\n安全交易 · 全程託管",
        "select_lang": "請選擇語言",
        "lang_set": "✅ 語言已設定為繁體中文",
        "no_permission": "❌ 您無權使用此功能",
        "invalid_cmd": "❌ 無效指令",
        "back": "🔙 返回首頁",

        "btn": {
            "home": "🏠 首頁",
            "service": "📌 擔保項目",
            "create": "🚀 發起擔保",
            "level": "📊 合夥人",
            "lang": "🌐 語言",
            "my_order": "📜 我的擔保",
            "apply": "🛡️ 擔保申請",
            "submit_apply": "✅ 提交申請"
        },

        "apply_text": "🛡️ 成為擔保人即可接單賺取收益\n點擊「提交申請」等待審核",
        "apply_sent": "✅ 申請已提交，等待管理員審核",
        "apply_already": "⚠️ 您已申請過，請等待",

        "admin_new_apply": "📥 新擔保人申請\n用戶ID：{}\n用戶名：@{}\n時間：{}"
    },
    "en": {
        "welcome": "👋 Welcome to TrustEscrow!",
        "select_lang": "Select Language",
        "lang_set": "✅ Language set to English",
        "no_permission": "❌ No permission",
        "invalid_cmd": "❌ Invalid command",
        "back": "🔙 Back",

        "btn": {
            "home": "🏠 Home",
            "service": "📌 Service",
            "create": "🚀 Create",
            "level": "📊 Level",
            "lang": "🌐 Lang",
            "my_order": "📜 My Order",
            "apply": "🛡️ Apply",
            "submit_apply": "✅ Submit"
        },

        "apply_text": "🛡️ Apply to be Guarantor\nClick Submit to apply",
        "apply_sent": "✅ Application sent",
        "apply_already": "⚠️ Already applied",

        "admin_new_apply": "📥 New Application\nID: {}\nUser: @{}\nTime: {}"
    }
}

# ====================== 數據存儲（UTF-8強制） ======================
DATA_FILE = "bot_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"users": {}, "applications": {}}
        save_data(data)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====================== 工具函數 ======================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_lang(user_id, data):
    return data["users"].get(str(user_id), {}).get("lang", "zh_tw")

def t(user_id, key, data):
    lang = get_lang(user_id, data)
    keys = key.split(".")
    res = LANG[lang]
    for k in keys:
        res = res[k]
    return res

# ====================== 發送管理員通知（強制必達） ======================
def send_admin_notify(text):
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text)
        except Exception as e:
            print(f"發送失敗 {admin_id}: {e}")
            continue

# ====================== 按鈕選單（極簡，不亂） ======================
def lang_menu():
    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton("繁體中文", callback_data="lang_tw"),
        InlineKeyboardButton("English", callback_data="lang_en")
    )
    return m

def main_menu(lang):
    b = LANG[lang]["btn"]
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton(b["home"], callback_data="home"))
    m.row(
        InlineKeyboardButton(b["service"], callback_data="service"),
        InlineKeyboardButton(b["create"], callback_data="create")
    )
    m.row(
        InlineKeyboardButton(b["level"], callback_data="level"),
        InlineKeyboardButton(b["lang"], callback_data="lang")
    )
    return m

def apply_menu(lang):
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(
        LANG[lang]["btn"]["submit_apply"],
        callback_data="do_apply"
    ))
    return m

# ====================== 語言設定 ======================
@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def set_lang(call):
    data = load_data()
    user_id = call.from_user.id
    uid = str(user_id)
    lang = "zh_tw" if call.data == "lang_tw" else "en"

    if uid not in data["users"]:
        data["users"][uid] = {
            "username": call.from_user.username or "",
            "lang": lang,
            "guarantor_status": "none"
        }
    else:
        data["users"][uid]["lang"] = lang
    save_data(data)

    bot.answer_callback_query(call.id, t(user_id, "lang_set", data))
    bot.edit_message_text(
        t(user_id, "welcome", data),
        call.message.chat.id, call.message.id,
        reply_markup=main_menu(lang)
    )

# ====================== 首頁按鈕 ======================
@bot.callback_query_handler(func=lambda c: c.data in ["home","service","create","level","lang"])
def main_btn(call):
    data = load_data()
    user_id = call.from_user.id
    lang = get_lang(user_id, data)
    bot.edit_message_text(
        t(user_id, "welcome", data),
        call.message.chat.id, call.message.id,
        reply_markup=main_menu(lang)
    )
    bot.answer_callback_query(call.id)

# ====================== 申請擔保人 ======================
@bot.message_handler(func=lambda m: m.text in ["🛡️ 擔保申請", "🛡️ Apply"])
def apply_page(msg):
    data = load_data()
    user_id = msg.from_user.id
    lang = get_lang(user_id, data)
    bot.send_message(
        msg.chat.id,
        t(user_id, "apply_text", data),
        reply_markup=apply_menu(lang)
    )

@bot.callback_query_handler(func=lambda c: c.data == "do_apply")
def do_apply(call):
    data = load_data()
    user_id = call.from_user.id
    uid = str(user_id)
    lang = get_lang(user_id, data)
    user = data["users"].setdefault(uid, {"username": call.from_user.username or "", "lang": lang, "guarantor_status": "none"})

    if user.get("guarantor_status") == "pending":
        bot.answer_callback_query(call.id, t(user_id, "apply_already", data))
        return

    user["guarantor_status"] = "pending"
    save_data(data)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    bot.edit_message_text(
        t(user_id, "apply_sent", data),
        call.message.chat.id, call.message.id
    )

    # 發送管理員通知
    send_admin_notify(
        t(user_id, "admin_new_apply", data).format(
            user_id,
            call.from_user.username or "-",
            now
        )
    )

# ====================== /start ======================
@bot.message_handler(commands=['start'])
def start(msg):
    data = load_data()
    bot.send_message(
        msg.chat.id,
        "請選擇語言 / Select Language",
        reply_markup=lang_menu()
    )

# ====================== 主選單 ======================
@bot.message_handler(func=lambda msg: True)
def all_msg(msg):
    data = load_data()
    user_id = msg.from_user.id
    lang = get_lang(user_id, data)
    if msg.text in [LANG[lang]["btn"]["my_order"], LANG[lang]["btn"]["apply"]]:
        apply_page(msg)
    else:
        bot.reply_to(msg, t(user_id, "invalid_cmd", data))

# ====================== 啟動 ======================
if __name__ == "__main__":
    print("✅ 繁體穩定版啟動完成")
    bot.infinity_polling()
