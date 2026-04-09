# -*- coding: utf-8 -*-
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ====================== 你的配置 ======================
ADMIN_IDS = [8401979801, 8781082053]
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
bot = telebot.TeleBot(BOT_TOKEN)

# ====================== 語言 ======================
TEXT = {
    "tw": {
        "welcome": "👋 歡迎使用 TrustEscrow 擔保平台",
        "menu": "🏠 主選單",
        "service": "📌 擔保項目\n• USDT 轉帳\n• 線上交易\n• 線下交易",
        "level": "📊 合夥人制度\nLv1 5%\nLv2 7%\nLv3 10%\nLv4 15%\nLv5 25%",
        "apply": "🛡️ 點擊送出擔保申請",
        "applied": "✅ 申請已送出，管理員已收到",
        "start": "🔢 輸入 /start 重新開始"
    },
    "en": {
        "welcome": "👋 Welcome to TrustEscrow",
        "menu": "🏠 Menu",
        "service": "📌 Services\n• USDT\n• Online\n• Offline",
        "level": "📊 Levels\nLv1 5%\nLv2 7%\nLv3 10%\nLv4 15%\nLv5 25%",
        "apply": "🛡️ Submit application",
        "applied": "✅ Applied successfully",
        "start": "🔢 Type /start"
    }
}

user_lang = {}

# ====================== 主菜單 ======================
def main_menu(user_id):
    lang = user_lang.get(user_id, "tw")
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("🏠 首頁" if lang == "tw" else "🏠 Home")
    btn2 = KeyboardButton("📌 擔保項目" if lang == "tw" else "📌 Services")
    btn3 = KeyboardButton("📊 合夥人制度" if lang == "tw" else "📊 Levels")
    btn4 = KeyboardButton("🛡️ 擔保申請" if lang == "tw" else "🛡️ Apply")
    btn5 = KeyboardButton("🌐 中文" if lang == "tw" else "🌐 English")
    menu.add(btn1, btn2, btn3, btn4, btn5)
    return menu

# ====================== 啟動 ======================
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    user_lang[user_id] = "tw"
    bot.send_message(msg.chat.id, TEXT["tw"]["welcome"], reply_markup=main_menu(user_id))

# ====================== 所有按鈕 ======================
@bot.message_handler(func=lambda msg: True)
def reply(msg):
    user_id = msg.from_user.id
    txt = msg.text
    lang = user_lang.get(user_id, "tw")

    if txt in ["🏠 首頁", "🏠 Home"]:
        bot.send_message(msg.chat.id, TEXT[lang]["menu"], reply_markup=main_menu(user_id))

    elif txt in ["📌 擔保項目", "📌 Services"]:
        bot.send_message(msg.chat.id, TEXT[lang]["service"], reply_markup=main_menu(user_id))

    elif txt in ["📊 合夥人制度", "📊 Levels"]:
        bot.send_message(msg.chat.id, TEXT[lang]["level"], reply_markup=main_menu(user_id))

    elif txt in ["🛡️ 擔保申請", "🛡️ Apply"]:
        # 傳送給管理員
        for admin in ADMIN_IDS:
            try:
                bot.send_message(admin, f"📥 新申請\n用戶: {msg.from_user.id}\n@{msg.from_user.username}")
            except:
                pass
        bot.send_message(msg.chat.id, TEXT[lang]["applied"], reply_markup=main_menu(user_id))

    elif txt in ["🌐 中文", "🌐 English"]:
        user_lang[user_id] = "en" if lang == "tw" else "tw"
        bot.send_message(msg.chat.id, "語言已切換 / Language changed", reply_markup=main_menu(user_id))

# ====================== 啟動 ======================
if __name__ == "__main__":
    print("✅ 穩定版啟動")
    bot.infinity_polling()
