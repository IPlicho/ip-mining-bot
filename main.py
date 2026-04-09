# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# ===================== 配置 =====================
BOT_TOKEN = "你的机器人Token"
ADMIN_ID = 8401979801  # 你的ID
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 双语文案 =====================
TEXT = {
    "zh": {
        "home": "🏠 擔保服務平台\n\n安全 · 高效 · 可信 · 全程擔保\n\n本平台提供第三方中立擔保服務。",
        "personal": "👤 個人中心\n\n用戶ID: {}\n錢包餘額: {:.2f} USDT",
        "wallet": "💰 錢包餘額: {:.2f} USDT",
        "create_escrow": "🚀 發起擔保",
        "input_amount": "💰 請輸入擔保金額（USDT）：",
        "input_tip": "🔒 請設置交易口令（數字/英文均可）：",
        "input_sell_tip": "🔑 請輸入擔保口令以配對訂單：",
        "escrow_success": "✅ 擔保已發起！\n\n金額: {:.2f} USDT\n口令: {}\n\n請將口令發給賣方。",
        "pair_success": "✅ 訂單配對成功！\n\n買方: {}\n賣方: {}\n金額: {:.2f} USDT\n口令: {}\n\n管理員已收到訂單。",
        "no_money": "❌ 餘額不足",
        "tip_error": "❌ 口令錯誤或訂單不存在",
        "back": "🏠 返回首頁",
        "lang": "🌐 English",
        "join_escrow": "📥 輸入口令擔保"
    },
    "en": {
        "home": "🏠 Escrow Platform\n\nSafe · Efficient · Reliable\n\nWe provide third-party neutral escrow service.",
        "personal": "👤 Personal Center\n\nUser ID: {}\nBalance: {:.2f} USDT",
        "wallet": "💰 Balance: {:.2f} USDT",
        "create_escrow": "🚀 Create Escrow",
        "input_amount": "💰 Enter escrow amount (USDT):",
        "input_tip": "🔒 Set your escrow code (numbers/letters):",
        "input_sell_tip": "🔑 Enter escrow code to pair:",
        "escrow_success": "✅ Escrow created!\n\nAmount: {:.2f} USDT\nCode: {}\n\nSend code to seller.",
        "pair_success": "✅ Order paired!\n\nBuyer: {}\nSeller: {}\nAmount: {:.2f} USDT\nCode: {}\n\nAdmin notified.",
        "no_money": "❌ Insufficient balance",
        "tip_error": "❌ Invalid code or order",
        "back": "🏠 Home",
        "lang": "🌐 繁中",
        "join_escrow": "📥 Enter Code"
    }
}

# ===================== 數據 =====================
user_lang = {}
user_step = {}
user_balance = {}  # 錢包
escrows = {}       # 訂單: {口令: {buyer, amount, time}}

# ===================== 菜單 =====================
def main_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton(t["create_escrow"], callback_data="create"),
        InlineKeyboardButton(t["join_escrow"], callback_data="join"),
        InlineKeyboardButton(t["personal"], callback_data="personal"),
        InlineKeyboardButton(t["lang"], callback_data="lang"),
    )
    return m

def back_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(t["back"], callback_data="home"))
    return m

# ===================== 開始 =====================
@bot.message_handler(commands=['start'])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    user_step[u] = None
    user_balance.setdefault(u, 0.0)
    t = TEXT[user_lang[u]]
    bot.send_message(msg.chat.id, t["home"], reply_markup=main_menu(u))

# ===================== 按鈕 =====================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    u = c.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    try:
        if c.data == "home":
            user_step[u] = None
            bot.edit_message_text(t["home"], c.message.chat.id, c.message.id, reply_markup=main_menu(u))

        elif c.data == "lang":
            user_lang[u] = "en" if lang == "zh" else "zh"
            t = TEXT[user_lang[u]]
            bot.edit_message_text(t["home"], c.message.chat.id, c.message.id, reply_markup=main_menu(u))

        elif c.data == "personal":
            txt = t["personal"].format(u, user_balance[u])
            bot.edit_message_text(txt, c.message.chat.id, c.message.id, reply_markup=back_menu(u))

        elif c.data == "create":
            user_step[u] = "create_amount"
            bot.edit_message_text(t["input_amount"], c.message.chat.id, c.message.id, reply_markup=back_menu(u))

        elif c.data == "join":
            user_step[u] = "join_tip"
            bot.edit_message_text(t["input_sell_tip"], c.message.chat.id, c.message.id, reply_markup=back_menu(u))
    except:
        pass

# ===================== 輸入處理 =====================
@bot.message_handler(func=lambda m: True)
def msg(msg):
    u = msg.from_user.id
    cid = msg.chat.id
    txt = msg.text.strip()
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    user_balance.setdefault(u, 0.0)

    # 管理員加錢
    if u == ADMIN_ID and txt.startswith("/add"):
        parts = txt.split()
        if len(parts) == 3:
            try:
                uid = int(parts[1])
                amt = float(parts[2])
                user_balance[uid] = user_balance.get(uid, 0.0) + amt
                bot.send_message(cid, f"✅ 已給用戶 {uid} 充值 {amt} USDT")
                return
            except:
                bot.send_message(cid, "❌ 格式: /add 用戶ID 金額")
        return

    if u not in user_step:
        user_step[u] = None

    # 發起擔保 - 輸入金額
    if user_step[u] == "create_amount":
        try:
            amt = float(txt)
            if amt <= 0:
                bot.send_message(cid, "❌ 金額錯誤", reply_markup=back_menu(u))
                return
            user_step[u] = {"step": "create_tip", "amount": amt}
            bot.send_message(cid, t["input_tip"], reply_markup=back_menu(u))
        except:
            bot.send_message(cid, "❌ 請輸入數字", reply_markup=back_menu(u))

    # 發起擔保 - 設置口令
    elif user_step[u] != None and type(user_step[u]) == dict and user_step[u]["step"] == "create_tip":
        amt = user_step[u]["amount"]
        tip = txt
        if user_balance[u] < amt:
            bot.send_message(cid, t["no_money"], reply_markup=back_menu(u))
            user_step[u] = None
            return
        # 扣錢
        user_balance[u] -= amt
        escrows[tip] = {
            "buyer": u,
            "amount": amt,
            "time": datetime.now().strftime("%m-%d %H:%M")
        }
        bot.send_message(cid, t["escrow_success"].format(amt, tip), reply_markup=back_menu(u))
        user_step[u] = None

    # 賣家輸入口令配對
    elif user_step[u] == "join_tip":
        tip = txt
        if tip not in escrows:
            bot.send_message(cid, t["tip_error"], reply_markup=back_menu(u))
            return
        order = escrows[tip]
        buyer = order["buyer"]
        amt = order["amount"]
        # 配對成功
        text = t["pair_success"].format(buyer, u, amt, tip)
        bot.send_message(cid, text, reply_markup=main_menu(u))
        # 發送給管理員
        bot.send_message(ADMIN_ID, f"📥 新訂單配對\n口令: {tip}\n買方: {buyer}\n賣方: {u}\n金額: {amt} USDT")
        del escrows[tip]
        user_step[u] = None

bot.infinity_polling()
