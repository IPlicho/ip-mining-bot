# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import os

# ===================== 配置（已填入你的Token）=====================
# 从BotFather获取的完整Token，已直接填入
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
# 你的管理员ID
ADMIN_ID = 8401979801
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 双语文案（模板C 繁体列式风格）=====================
TEXT = {
    "zh": {
        "home": "🏠 擔保服務平台\n\n安全 · 高效 · 可信 · 全程擔保\n\n本平台提供第三方中立擔保服務，保障交易雙方資金與權益安全。",
        "personal": "👤 個人中心\n\n用戶ID: {}\n錢包餘額: {:.2f} USDT",
        "create_escrow": "🚀 發起擔保",
        "join_escrow": "📥 輸入口令擔保",
        "input_amount": "💰 請輸入擔保金額（USDT）：",
        "input_tip": "🔒 請設置交易口令（數字/英文均可）：",
        "input_sell_tip": "🔑 請輸入擔保口令以配對訂單：",
        "escrow_success": "✅ 擔保已發起！\n\n金額: {:.2f} USDT\n口令: {}\n\n請將口令發給賣方，等待配對。",
        "pair_success": "✅ 訂單配對成功！\n\n買方: {}\n賣方: {}\n金額: {:.2f} USDT\n口令: {}\n\n管理員已收到訂單，將安排中間人擔保。",
        "no_money": "❌ 餘額不足，無法發起擔保",
        "tip_error": "❌ 口令錯誤或訂單不存在",
        "back": "🏠 返回首頁",
        "lang": "🌐 English",
        "admin_add_success": "✅ 已給用戶 {} 充值 {:.2f} USDT",
        "admin_add_format": "❌ 格式錯誤，正確格式：/add 用戶ID 金額"
    },
    "en": {
        "home": "🏠 Escrow Platform\n\nSafe · Efficient · Reliable\n\nWe provide third-party neutral escrow service to protect both parties' funds and rights.",
        "personal": "👤 Personal Center\n\nUser ID: {}\nBalance: {:.2f} USDT",
        "create_escrow": "🚀 Create Escrow",
        "join_escrow": "📥 Enter Code",
        "input_amount": "💰 Enter escrow amount (USDT):",
        "input_tip": "🔒 Set your escrow code (numbers/letters):",
        "input_sell_tip": "🔑 Enter escrow code to pair order:",
        "escrow_success": "✅ Escrow created!\n\nAmount: {:.2f} USDT\nCode: {}\n\nSend code to seller to pair.",
        "pair_success": "✅ Order paired!\n\nBuyer: {}\nSeller: {}\nAmount: {:.2f} USDT\nCode: {}\n\nAdmin notified, guarantor will be arranged.",
        "no_money": "❌ Insufficient balance",
        "tip_error": "❌ Invalid code or order",
        "back": "🏠 Home",
        "lang": "🌐 繁中",
        "admin_add_success": "✅ Added {:.2f} USDT to user {}",
        "admin_add_format": "❌ Invalid format, use: /add user_id amount"
    }
}

# ===================== 數據存儲 =====================
user_lang = {}
user_step = {}
user_balance = {}  # 用戶錢包餘額
escrows = {}       # 擔保訂單: {口令: {buyer_id, amount, create_time}}

# ===================== 菜單生成（模板C 列式風格）=====================
def main_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton(t["create_escrow"], callback_data="create"),
        InlineKeyboardButton(t["join_escrow"], callback_data="join"),
        InlineKeyboardButton(t["personal"], callback_data="personal"),
        InlineKeyboardButton(t["lang"], callback_data="lang")
    )
    return m

def back_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(InlineKeyboardButton(t["back"], callback_data="home"))
    return m

# ===================== 啟動指令 =====================
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    # 初始化用戶語言、狀態、餘額
    user_lang.setdefault(user_id, "zh")
    user_step[user_id] = None
    user_balance.setdefault(user_id, 0.0)
    
    t = TEXT[user_lang[user_id]]
    bot.send_message(msg.chat.id, t["home"], reply_markup=main_menu(user_id))

# ===================== 按鈕回調處理 =====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]

    try:
        if call.data == "home":
            # 返回首頁，重置狀態
            user_step[user_id] = None
            bot.edit_message_text(t["home"], chat_id, message_id, reply_markup=main_menu(user_id))

        elif call.data == "lang":
            # 切換語言
            new_lang = "en" if lang == "zh" else "zh"
            user_lang[user_id] = new_lang
            t = TEXT[new_lang]
            bot.edit_message_text(t["home"], chat_id, message_id, reply_markup=main_menu(user_id))

        elif call.data == "personal":
            # 個人中心
            balance = user_balance.get(user_id, 0.0)
            text = t["personal"].format(user_id, balance)
            bot.edit_message_text(text, chat_id, message_id, reply_markup=back_menu(user_id))

        elif call.data == "create":
            # 買方：發起擔保，第一步輸入金額
            user_step[user_id] = "create_amount"
            bot.edit_message_text(t["input_amount"], chat_id, message_id, reply_markup=back_menu(user_id))

        elif call.data == "join":
            # 賣方：輸入口令配對
            user_step[user_id] = "join_tip"
            bot.edit_message_text(t["input_sell_tip"], chat_id, message_id, reply_markup=back_menu(user_id))

        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"按鈕回調錯誤: {e}")

# ===================== 用戶輸入處理 =====================
@bot.message_handler(func=lambda msg: True)
def message_handler(msg):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    text = msg.text.strip()
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    user_balance.setdefault(user_id, 0.0)

    # ========== 管理員充值指令 ==========
    if user_id == ADMIN_ID and text.startswith("/add"):
        parts = text.split()
        if len(parts) == 3:
            try:
                target_uid = int(parts[1])
                amount = float(parts[2])
                if amount <= 0:
                    bot.send_message(chat_id, t["admin_add_format"])
                    return
                # 給用戶充值
                user_balance[target_uid] = user_balance.get(target_uid, 0.0) + amount
                bot.send_message(chat_id, t["admin_add_success"].format(target_uid, amount))
                return
            except:
                bot.send_message(chat_id, t["admin_add_format"])
        else:
            bot.send_message(chat_id, t["admin_add_format"])
        return

    # 初始化用戶狀態
    if user_id not in user_step:
        user_step[user_id] = None

    # ========== 買方：發起擔保-輸入金額 ==========
    if user_step[user_id] == "create_amount":
        try:
            amount = float(text)
            if amount <= 0:
                bot.send_message(chat_id, t["input_amount"], reply_markup=back_menu(user_id))
                return
            # 保存金額，進入設置口令步驟
            user_step[user_id] = {"step": "create_tip", "amount": amount}
            bot.send_message(chat_id, t["input_tip"], reply_markup=back_menu(user_id))
        except:
            bot.send_message(chat_id, t["input_amount"], reply_markup=back_menu(user_id))
        return

    # ========== 買方：發起擔保-設置口令 ==========
    elif isinstance(user_step[user_id], dict) and user_step[user_id]["step"] == "create_tip":
        amount = user_step[user_id]["amount"]
        code = text

        # 檢查餘額
        if user_balance[user_id] < amount:
            bot.send_message(chat_id, t["no_money"], reply_markup=main_menu(user_id))
            user_step[user_id] = None
            return

        # 扣除餘額，保存訂單
        user_balance[user_id] -= amount
        escrows[code] = {
            "buyer_id": user_id,
            "amount": amount,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 回復用戶
        bot.send_message(chat_id, t["escrow_success"].format(amount, code), reply_markup=main_menu(user_id))
        user_step[user_id] = None
        return

    # ========== 賣方：輸入口令配對 ==========
    elif user_step[user_id] == "join_tip":
        code = text
        # 檢查口令是否存在
        if code not in escrows:
            bot.send_message(chat_id, t["tip_error"], reply_markup=main_menu(user_id))
            user_step[user_id] = None
            return

        # 獲取訂單信息
        order = escrows[code]
        buyer_id = order["buyer_id"]
        amount = order["amount"]

        # 配對成功，刪除待配對訂單
        del escrows[code]

        # 回復賣方
        bot.send_message(
            chat_id,
            t["pair_success"].format(buyer_id, user_id, amount, code),
            reply_markup=main_menu(user_id)
        )

        # 通知管理員（派給中間人）
        admin_text = f"""📥 新訂單配對成功
口令: {code}
買方ID: {buyer_id}
賣方ID: {user_id}
金額: {amount} USDT
創建時間: {order['create_time']}
"""
        bot.send_message(ADMIN_ID, admin_text)

        user_step[user_id] = None
        return

    # ========== 閒置狀態，返回首頁 ==========
    else:
        bot.send_message(chat_id, t["home"], reply_markup=main_menu(user_id))
        return

# ===================== 啟動機器人 =====================
if __name__ == "__main__":
    print("✅ TrustEscrow Bot 用戶端啟動成功！")
    print(f"🤖 機器人: @trustescrow_pro_bot")
    print(f"🔑 Token: {BOT_TOKEN}")
    bot.infinity_polling()
