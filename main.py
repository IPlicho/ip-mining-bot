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

# ====================== 雙語完整文案（你給的完整版） ======================
TEXT = {
    "zh": {
        "home": """🏠 担保服务平台
安全 · 高效 · 可信 · 全程担保

本平台提供第三方中立担保服务，保障交易双方资金与权益安全。
所有担保人经过严格审核，订单可查、过程可控、售后可追溯。""",

        "service": """📌 担保项目

我们支持以下正规担保交易：

• USDT 转账担保
双方交易前由平台托管资金，确认无误后放行。

• 线上交易担保
商品/服务/账号/虚拟资产交易安全担保。

• 线下交易担保
当面交易资金托管，避免欺诈。

• 合约履约担保
按约定条件完成后才释放资金。

• 多人交易担保
支持多方参与的复杂交易担保。

担保流程
1. 用户发起担保 → 2. 资金托管 → 3. 履约确认 → 4. 放行结算
全程安全可查。""",

        "apply": """🛡️ 担保入驻

成为担保人即可接单赚取收益。

入驻要求
• 同意平台规则
• 提供基本资料审核
• 无违规记录

申请流程
1. 提交资料 → 2. 管理员审核 → 3. 开通权限 → 4. 开始接单

注意
• 违规将被永久封锁权限
• 订单必须按平台规则完成""",

        "create": """🚀 发起担保

請選擇担保類型：""",

        "help": """📖 帮助中心

• 担保项目：查看支持的交易类型
• 担保入驻：申请成为担保人
• 发起担保：创建新订单
• 帮助中心：使用说明""",

        "guarantor": "🛡️ 中间人中心\n可接單、查看訂單、確認完成",
        "back": "🏠 返回首頁",
        "lang": "🌐 English",

        "enter_amount": "請輸入担保金額（USDT）：",
        "enter_note": "請輸入訂單備註：",
        "order_success": "✅ 訂單提交成功！\n類型：{}\n金額：{} USDT\n備註：{}",
    },

    "en": {
        "home": """🏠 Escrow Platform
Safe · Efficient · Reliable

We provide a neutral third-party escrow service to protect both parties.
All guarantors are strictly vetted. Orders are traceable and secure.""",

        "service": """📌 Services

• USDT Transfer Escrow
• Online Trade Escrow
• Offline Trade Escrow
• Contract Performance Escrow
• Multi-Party Escrow

Process:
1. Create Order → 2. Deposit → 3. Confirm → 4. Release""",

        "apply": """🛡️ Become a Guarantor

Requirements:
• Agree to rules
• Submit info for review
• Clean record

Process:
Apply → Review → Approve → Start""",

        "create": """🚀 Create Order

Select type:""",

        "help": """📖 Help

• Services: Supported escrow types
• Apply: Become a guarantor
• Create: New order
• Help: Guide""",

        "guarantor": "🛡️ Guarantor Center",
        "back": "🏠 Back",
        "lang": "🌐 繁中",

        "enter_amount": "Enter amount (USDT):",
        "enter_note": "Enter note:",
        "order_success": "✅ Order submitted!\nType: {}\nAmount: {} USDT\nNote: {}",
    }
}

# ====================== 數據 ======================
user_lang = {}
user_step = {}  # 記錄用戶下單步驟
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

def type_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton("USDT 轉帳担保", callback_data="t_USDT"),
        InlineKeyboardButton("線上交易担保", callback_data="t_ONLINE"),
        InlineKeyboardButton("線下交易担保", callback_data="t_OFFLINE"),
        InlineKeyboardButton("合約履约担保", callback_data="t_CONTRACT"),
        InlineKeyboardButton("多人交易担保", callback_data="t_MULTI"),
        InlineKeyboardButton(TEXT[lang]["back"], callback_data="home")
    )
    return m

# ====================== 啟動 ======================
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    user_lang[user_id] = "zh"
    user_step[user_id] = None
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
        user_step[u] = None
        bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

    elif c.data == "service":
        bot.edit_message_text(t["service"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "apply":
        bot.edit_message_text(t["apply"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "create":
        bot.edit_message_text(t["create"], cid, mid, reply_markup=type_menu(u))

    elif c.data.startswith("t_"):
        # 選擇類型 → 進入輸入金額
        user_step[u] = {"step": "amount", "type": c.data[2:]}
        bot.edit_message_text(t["enter_amount"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "help":
        bot.edit_message_text(t["help"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "guarantor":
        bot.edit_message_text(t["guarantor"], cid, mid, reply_markup=back_menu(u))

    elif c.data == "lang":
        user_lang[u] = "en" if lang == "zh" else "zh"
        new_lang = user_lang[u]
        bot.edit_message_text(TEXT[new_lang]["home"], cid, mid, reply_markup=main_menu(u))

    bot.answer_callback_query(c.id)

# ====================== 接收用戶輸入（金額、備註） ======================
@bot.message_handler(func=lambda msg: True)
def handle_message(msg):
    u = msg.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]

    if u not in user_step or user_step[u] is None:
        bot.reply_to(msg, t["back"], reply_markup=main_menu(u))
        return

    step = user_step[u]
    if step["step"] == "amount":
        try:
            amount = float(msg.text.strip())
            user_step[u] = {"step": "note", "type": step["type"], "amount": amount}
            bot.reply_to(msg, t["enter_note"])
        except:
            bot.reply_to(msg, "❌ 請輸入有效數字")

    elif step["step"] == "note":
        note = msg.text.strip()
        typ = step["type"]
        amt = step["amount"]
        user_step[u] = None

        bot.reply_to(msg, t["order_success"].format(typ, amt, note))

# ====================== 管理員指令 ======================
@bot.message_handler(commands=['审核','拒绝','封锁','解除','派单','完成','用户信息'])
def admin_cmd(msg):
    if msg.from_user.id not in ADMIN_IDS:
        msg.reply_to("❌ 無權限")
        return
    msg.reply_to("🔐 管理員指令已接收")

# ====================== 運行 ======================
if __name__ == "__main__":
    print("✅ 機器人啟動成功")
    bot.infinity_polling()
