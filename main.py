# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import random
import os
import sys

# ===================== 配置（已填好你的Token，Railway专属）=====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU")
ADMIN_ID = 8401979801

# 初始化机器人
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", threaded=True)

# ===================== 数据存储 =====================
guarantor = {}
orders = {}
user_lang = {}
step = {}

# ===================== 双语文案 =====================
TEXT = {
    "zh": {
        "home": """🤝 TrustEscrow 中间人专区
【已认证中间人专属后台】
实时接单｜垫资结算｜佣金秒结

📊 佣金规则：
🔹 抢单利润：固定 5%
🔹 派单利润：15%~25%

⚠️ 平台规则：
● 派单强制接单，不可拒绝
● 派单需 12 小时内完成垫资
● 逾期未处理将冻结账号""",
        "not_verified": "⚠️ 您尚未成为认证中间人，请申请入驻",
        "banned": "❌ 您的账号已被冻结，联系@fcff88",
        "apply": "📝 申请成为中间人，请输入真实姓名",
        "apply_inviter": "📎 请输入推荐人ID（无则输0）",
        "apply_sent": "✅ 申请已提交，等待管理员审核",
        "balance": "👤 个人中心\nID：{}\n姓名：{}\n余额：{:.2f} USDT",
        "deposit": "💰 储值入口\n联系客服@fcff88",
        "withdraw": "💳 提现入口\n联系客服@fcff88",
        "grab_orders": "🚀 抢单大厅（5%利润）\n{}",
        "no_grab": "📭 暂无可抢订单",
        "my_orders": "📋 我的订单\n{}",
        "no_my_orders": "📭 暂无订单",
        "order_detail": "📥 订单详情\n金额：{} USDT\n状态：{}",
        "fund_btn": "✅ 确认已垫资",
        "funded": "✅ 已确认垫资",
        "back": "🏠 返回首页",
        "lang": "🌐 English"
    },
    "en": {
        "home": """🤝 TrustEscrow Guarantor Panel
【Verified Only】
Real-time Orders · Fast Commission

📊 Commission:
🔹 Grab: 5% Fixed
🔹 Assign: 15%~25%

⚠️ Rules:
● Assigned orders CANNOT refuse
● Fund within 12 hours""",
        "not_verified": "⚠️ Not verified, apply now",
        "banned": "❌ Banned, contact @fcff88",
        "apply": "📝 Apply, enter your name",
        "apply_inviter": "📎 Enter inviter ID (0 if none)",
        "apply_sent": "✅ Application submitted",
        "balance": "👤 Profile\nID: {}\nName: {}\nBalance: {:.2f} USDT",
        "deposit": "💰 Deposit\nContact @fcff88",
        "withdraw": "💳 Withdraw\nContact @fcff88",
        "grab_orders": "🚀 Grab Orders (5% Profit)\n{}",
        "no_grab": "📭 No orders",
        "my_orders": "📋 My Orders\n{}",
        "no_my_orders": "📭 No orders",
        "order_detail": "📥 Order Details\nAmount: {} USDT\nStatus: {}",
        "fund_btn": "✅ Confirm Funded",
        "funded": "✅ Confirmed",
        "back": "🏠 Home",
        "lang": "🌐 繁中"
    }
}

# ===================== 菜单生成 =====================
def main_menu(u):
    lang = user_lang.get(u, "zh")
    t = TEXT[lang]
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🚀 抢单大厅", callback_data="grab"),
        InlineKeyboardButton("📋 我的订单", callback_data="my"),
        InlineKeyboardButton("👤 个人中心", callback_data="bal"),
        InlineKeyboardButton("💰 储值", callback_data="dep"),
        InlineKeyboardButton("💳 提现", callback_data="wdr"),
        InlineKeyboardButton(t["lang"], callback_data="lang"),
    )
    return m

def back(u):
    t = TEXT[user_lang.get(u, "zh")]
    return InlineKeyboardMarkup().add(InlineKeyboardButton(t["back"], callback_data="home"))

def fund_btn(code):
    return InlineKeyboardMarkup().add(InlineKeyboardButton("✅ 确认已垫资", callback_data=f"fd_{code}"))

# ===================== 启动指令 =====================
@bot.message_handler(commands=['start'])
def start(msg):
    print(f"收到 /start 来自用户: {msg.from_user.id}")
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    step[u] = None
    guarantor.setdefault(u, {
        "status": "none",
        "balance": 0.0,
        "commission": 0.0,
        "inviter": 0,
        "banned": False,
        "name": "未设置"
    })
    t = TEXT[user_lang[u]]
    g = guarantor[u]
    if g["banned"]:
        bot.send_message(msg.chat.id, t["banned"])
        return
    if g["status"] != "verified":
        bot.send_message(msg.chat.id, t["not_verified"], reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📝 申请入驻", callback_data="apply")
        ))
        return
    bot.send_message(msg.chat.id, t["home"], reply_markup=main_menu(u))

# ===================== 按钮回调 =====================
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
            s = "✅ 已认证" if g["status"] == "verified" else "⚠️ 未认证"
            txt = t["balance"].format(u, g["name"], g["balance"])
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
                m.add(InlineKeyboardButton(f"抢 {o}", callback_data=f"g_{o}"))
            bot.edit_message_text(t["grab_orders"].format(txt), cid, mid, reply_markup=m)

        elif data.startswith("g_"):
            code = data[2:]
            if code not in orders or orders[code]["status"] != "open":
                bot.answer_callback_query(c.id, "❌ 订单已被抢走")
                return
            o = orders[code]
            o["status"] = "progress"
            o["guar"] = u
            amt = o["amount"]
            com = amt * 0.05
            o["commission"] = com
            bot.answer_callback_query(c.id, "✅ 抢单成功！")
            bot.send_message(u, t["order_detail"].format(amt, "处理中"), reply_markup=fund_btn(code))

        elif data.startswith("fd_"):
            code = data[3:]
            if code not in orders:
                return
            o = orders[code]
            if o.get("guar") != u:
                return
            o["status"] = "funded"
            bot.edit_message_text(t["funded"], cid, mid, reply_markup=back(u))
            bot.send_message(ADMIN_ID, f"🔔 中间人{u} 已垫资订单 {code}")

        elif data == "my":
            lst = [o for o in orders if orders[o].get("guar") == u and orders[o]["status"] in ["progress", "funded"]]
            if not lst:
                bot.edit_message_text(t["my_orders"].format(t["no_my_orders"]), cid, mid, reply_markup=back(u))
                return
            txt = "\n".join([f"• {o} {orders[o]['amount']} USDT | {orders[o]['status']}" for o in lst[:6]])
            bot.edit_message_text(t["my_orders"].format(txt), cid, mid, reply_markup=back(u))

        bot.answer_callback_query(c.id)
    except Exception as e:
        print(f"按钮错误: {e}")

# ===================== 用户输入处理 =====================
@bot.message_handler(func=lambda m: True)
def msg(msg):
    print(f"收到消息: {msg.text} 来自用户: {msg.from_user.id}")
    u = msg.from_user.id
    txt = msg.text.strip()
    if u not in step:
        step[u] = None

    if step[u] == "apply_name":
        step[u] = f"apply_inviter|{txt}"
        bot.send_message(u, TEXT[user_lang[u]]["apply_inviter"])
        return

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
        bot.send_message(ADMIN_ID, f"🆕 新入驻申请\nID: {u}\n名称: {name}\n推荐人: {inv_id}")
        step[u] = None
        return

# ===================== 管理员指令 =====================
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin(msg):
    t = msg.text.split()
    try:
        if t[0] == "/verify":
            uid = int(t[1])
            guarantor[uid]["status"] = "verified"
            bot.send_message(uid, "✅ 您已成为认证中间人")
            bot.send_message(msg.chat.id, f"✅ 已通过 {uid}")

        elif t[0] == "/ban":
            uid = int(t[1])
            guarantor[uid]["banned"] = True
            bot.send_message(uid, "❌ 您的账号已被冻结")
            bot.send_message(msg.chat.id, f"✅ 已封锁 {uid}")

        elif t[0] == "/unban":
            uid = int(t[1])
            guarantor[uid]["banned"] = False
            bot.send_message(uid, "✅ 您的账号已解封")
            bot.send_message(msg.chat.id, f"✅ 已解封 {uid}")

        elif t[0] == "/add":
            uid = int(t[1])
            amt = float(t[2])
            guarantor[uid]["balance"] += amt
            bot.send_message(uid, f"✅ 已增加 {amt} USDT")
            bot.send_message(msg.chat.id, f"✅ 已给 {uid} 加 {amt} USDT")

        elif t[0] == "/reduce":
            uid = int(t[1])
            amt = float(t[2])
            guarantor[uid]["balance"] -= amt
            bot.send_message(uid, f"❌ 已扣除 {amt} USDT")
            bot.send_message(msg.chat.id, f"✅ 已给 {uid} 扣 {amt} USDT")

        elif t[0] == "/assign":
            code = t[1]
            amt = float(t[2])
            gid = int(t[3])
            com = amt * random.choice([0.15,0.20,0.25])
            orders[code] = {"type":"assign","amount":amt,"guar":gid,"status":"progress","commission":com}
            bot.send_message(gid, TEXT[user_lang.get(gid, "zh")]["order_detail"].format(amt, "处理中"), reply_markup=fund_btn(code))
            bot.send_message(msg.chat.id, f"✅ 已派单 {code} 给 {gid}")

        elif t[0] == "/grab":
            code = t[1]
            amt = float(t[2])
            orders[code] = {"type":"grab","amount":amt,"status":"open"}
            bot.send_message(msg.chat.id, f"✅ 已创建抢单 {code} {amt} USDT")

    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ 指令错误: {e}")

# ===================== Railway 专属启动 =====================
if __name__ == "__main__":
    print("✅ Railway 中间人机器人启动成功！")
    print(f"🤖 机器人: @MyEscrowBot88bot")
    print(f"🔑 Token: {BOT_TOKEN}")
    try:
        # Railway 必须用 none_stop=True 长轮询
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"启动错误: {e}")
        sys.exit(1)
