import telebot
import time
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict

# 机器人配置（你的Token已直接填好）
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
bot = telebot.TeleBot(BOT_TOKEN)

# 管理员ID
ADMIN_IDS = [8256055083, 810821053]

# 用户数据
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

# 语言
user_lang = defaultdict(lambda: "zh")

# 币种与奖励
COINS = ["BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "MATIC", "DOT", "LINK"]
coin_reward = {c: 100 for c in COINS}
coin_delay = {c: 8 for c in COINS}
AIRDROP_REWARD = 10

# 等级配置
LEVEL_CONFIG = {
    1: (8, 100),
    2: (12, 120),
    3: (16, 150),
    4: (20, 180),
    5: (25, 220)
}

# ========== 新增：每日重置 + 币种冷却 独立字典 ==========
user_last_reset_date = {}
coin_cooldown = {}

# 语言文本
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
        "approved_notify": "✅ 恭喜！你的挖礦申請已通過，可開始挖礦"
    },
    "en": {
        "start_title": "IP Node Mining System\nWelcome! Use the buttons below.",
        "btn_start_mine": "⛏️ Start Mining",
        "btn_apply_ip": "🚀 Apply Mining Access",
        "btn_withdraw": "🔄 Withdraw",
        "btn_airdrop": "🧧 Daily Airdrop",
        "btn_asset": "👤 My Assets",
        "btn_rules": "📜 Project Rules",
        "btn_support": "💬 Support",
        "banned": "❌ You are banned.",
        "mine_select": "⛏️ Select a coin to mine",
        "mine_no_perm": "❌ Please apply for mining access first.",
        "mine_locked": "❌ Mining closed today.",
        "mine_max": "❌ Daily limit reached.",
        "mining_process": "Mining, please wait...",
        "mine_success": "✅ Mined: {}\nLv.{} Node\n🎉 Boost +{}\n💎 Total: {}",
        "apply_sent": "✅ Application sent, admin will review soon.",
        "already_approved": "✅ You already have mining access.",
        "withdraw_tip": "✅ Contact support @fcff88 with your UID.",
        "airdrop_done": "🧧 Airdrop claimed! Points +{}",
        "airdrop_today_claimed": "❌ Already claimed today.",
        "asset_title": "👤 My Assets",
        "level": "Level: Lv.{}",
        "mine_today": "Today: {}/{}",
        "boost": "💎 Boost: {}",
        "trx_balance": "🪙 TRX: {}",
        "mine_status": "✅ Mining: {}",
        "points": "📊 Points: {}",
        "total_withdraw": "📈 Total Withdraw: {}",
        "status_on": "Approved",
        "status_off": "Pending",
        "status_running": "🟢 Active",
        "status_stopped": "🔴 Stopped",
        "support_msg": "✅ Support @fcff88",
        "lang_switched": "✅ Language switched",
        "project_rules_text": "📜 Project Rules\n1. This system is for IP node mining, authorized users only\n2. Daily mining limits based on level\n3. Boost points can be used for exchange & withdrawal\n4. Cheating & multi-account abuse will be banned\n5. Platform reserves all rights of final interpretation",
        "approved_notify": "✅ Your mining application has been approved!"
    }
}

def t(uid, key):
    return lang[user_lang[uid]][key]

def is_admin(uid):
    return uid in ADMIN_IDS

# 主菜单
def show_main_menu(chat_id, uid):
    if user_data[uid]["banned"]:
        bot.send_message(chat_id, t(uid, "banned"))
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
    bot.send_message(chat_id, t(uid, "start_title"), reply_markup=mk)

@bot.message_handler(commands=['start'])
def cmd_start(msg):
    show_main_menu(msg.chat.id, msg.from_user.id)

@bot.message_handler(commands=['lang'])
def cmd_lang(msg):
    uid = msg.from_user.id
    user_lang[uid] = "en" if user_lang[uid] == "zh" else "zh"
    bot.send_message(msg.chat.id, t(uid, "lang_switched"))
    show_main_menu(msg.chat.id, uid)

# 挖矿选择币种
@bot.callback_query_handler(func=lambda c: c.data == "start_mining")
def cb_start_mining(call):
    uid = call.from_user.id
    u = user_data[uid]
    if u["banned"]:
        bot.answer_callback_query(call.id, t(uid, "banned"), show_alert=True)
        return
    if not u["mining_approved"]:
        bot.answer_callback_query(call.id, t(uid, "mine_no_perm"), show_alert=True)
        return
    if u["mining_today_locked"]:
        bot.answer_callback_query(call.id, t(uid, "mine_locked"), show_alert=True)
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        bot.answer_callback_query(call.id, t(uid, "mine_max"), show_alert=True)
        return
    mk = InlineKeyboardMarkup(row_width=3)
    btns = [InlineKeyboardButton(c, callback_data=f"mine_{c}") for c in COINS]
    mk.add(*btns)
    bot.edit_message_text(t(uid, "mine_select"), call.message.chat.id, call.message.id, reply_markup=mk)
    bot.answer_callback_query(call.id)

# 执行挖矿
@bot.callback_query_handler(func=lambda c: c.data.startswith("mine_"))
def cb_mine(call):
    uid = call.from_user.id
    u = user_data[uid]
    chat_id = call.message.chat.id

    # ========== 新增：每日自动重置挖矿次数 ==========
    today = datetime.now().strftime("%Y-%m-%d")
    if uid not in user_last_reset_date or user_last_reset_date[uid] != today:
        u["mine_count_today"] = 0
        user_last_reset_date[uid] = today

    # ========== 新增：单个币种60秒冷却 ==========
    coin = call.data.split("_")[1]
    cooldown_key = f"{uid}_{coin}"
    now = time.time()

    if cooldown_key in coin_cooldown and coin_cooldown[cooldown_key] > now:
        remain = int(coin_cooldown[cooldown_key] - now)
        bot.answer_callback_query(call.id, f"{coin} 冷却中…还剩 {remain} 秒", show_alert=True)
        return

    coin_cooldown[cooldown_key] = now + 60

    # ========== 以下完全是你原有逻辑 ==========
    if u["banned"] or not u["mining_approved"] or u["mining_today_locked"]:
        bot.answer_callback_query(call.id)
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        bot.answer_callback_query(call.id, t(uid, "mine_max"), show_alert=True)
        return

    lvl = u["level"]
    reward = coin_reward.get(coin, 100)
    delay = coin_delay.get(coin, 8)

    bot.answer_callback_query(call.id, t(uid, "mining_process"), show_alert=True)
    time.sleep(delay)

    u["boost"] += reward
    u["mine_count_today"] += 1

    bot.send_message(call.message.chat.id, t(uid, "mine_success").format(coin, lvl, reward, u["boost"]))
    show_main_menu(call.message.chat.id, uid)

# 申请权限
@bot.callback_query_handler(func=lambda c: c.data == "apply_mining")
def cb_apply(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id)
        return
    if user_data[uid]["mining_approved"]:
        bot.answer_callback_query(call.id, t(uid, "already_approved"), show_alert=True)
        return
    for a in ADMIN_IDS:
        bot.send_message(a, f"🔔 New apply\nUID: {uid}\n/agree {uid}  /refuse {uid}")
    bot.send_message(call.message.chat.id, t(uid, "apply_sent"))
    bot.answer_callback_query(call.id)

# 提现
@bot.callback_query_handler(func=lambda c: c.data == "apply_withdraw")
def cb_withdraw(call):
    uid = call.from_user.id
    bot.send_message(call.message.chat.id, t(uid, "withdraw_tip"))
    bot.answer_callback_query(call.id)

# 空投
@bot.callback_query_handler(func=lambda c: c.data == "daily_airdrop")
def cb_airdrop(call):
    uid = call.from_user.id
    u = user_data[uid]
    if u["banned"]:
        bot.answer_callback_query(call.id)
        return
    if u["airdrop_claimed"]:
        bot.answer_callback_query(call.id, t(uid, "airdrop_today_claimed"), show_alert=True)
        return
    u["airdrop_claimed"] = True
    u["points"] += AIRDROP_REWARD
    bot.send_message(call.message.chat.id, t(uid, "airdrop_done").format(AIRDROP_REWARD))
    bot.answer_callback_query(call.id)

# 资产
@bot.callback_query_handler(func=lambda c: c.data == "asset_overview")
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
    bot.send_message(call.message.chat.id, txt)
    bot.answer_callback_query(call.id)

# 项目规则
@bot.callback_query_handler(func=lambda c: c.data == "project_rules")
def cb_rules(call):
    uid = call.from_user.id
    bot.send_message(call.message.chat.id, t(uid, "project_rules_text"))
    bot.answer_callback_query(call.id)

# 客服
@bot.callback_query_handler(func=lambda c: c.data == "support")
def cb_support(call):
    uid = call.from_user.id
    bot.send_message(call.message.chat.id, t(uid, "support_msg"))
    bot.answer_callback_query(call.id)

# 管理员审批
@bot.message_handler(commands=['agree'])
def cmd_agree(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        uid = int(uid)
        user_data[uid]["mining_approved"] = True
        bot.send_message(msg.chat.id, f"✅ Approved {uid}")
        bot.send_message(uid, t(uid, "approved_notify"))
    except:
        bot.send_message(msg.chat.id, "Usage: /agree UID")

@bot.message_handler(commands=['refuse'])
def cmd_refuse(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["mining_approved"] = False
        bot.send_message(msg.chat.id, f"❌ Refused {uid}")
    except:
        bot.send_message(msg.chat.id, "Usage: /refuse UID")

# 查看矿工
@bot.message_handler(commands=['miners'])
def cmd_miners(msg):
    if not is_admin(msg.from_user.id):
        return
    lines = []
    for uid, d in user_data.items():
        ap = "Approved" if d["mining_approved"] else "Pending"
        ban = "BANNED" if d["banned"] else ""
        lines.append(f"ID:{uid} Lv{d['level']} B:{d['boost']} TRX:{d['trx']} {ap} {ban}")
    bot.send_message(msg.chat.id, "\n".join(lines[:20]))

# 封禁
@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["banned"] = True
        bot.send_message(msg.chat.id, f"❌ Banned {uid}")
    except:
        bot.send_message(msg.chat.id, "/ban UID")

@bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["banned"] = False
        bot.send_message(msg.chat.id, f"✅ Unbanned {uid}")
    except:
        bot.send_message(msg.chat.id, "/unban UID")

# TRX
@bot.message_handler(commands=['add_trx'])
def cmd_addtrx(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        user_data[int(uid)]["trx"] += float(v)
        bot.send_message(msg.chat.id, f"✅ +{v} TRX")
    except:
        bot.send_message(msg.chat.id, "/add_trx UID amount")

@bot.message_handler(commands=['reduce_trx'])
def cmd_rtrx(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        user_data[int(uid)]["trx"] = max(0, user_data[int(uid)]["trx"] - float(v))
        bot.send_message(msg.chat.id, f"✅ -{v} TRX")
    except:
        bot.send_message(msg.chat.id, "/reduce_trx UID amount")

# 等级
@bot.message_handler(commands=['setlevel'])
def cmd_lvl(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        user_data[int(uid)]["level"] = int(v)
        bot.send_message(msg.chat.id, f"✅ Lv{v}")
    except:
        bot.send_message(msg.chat.id, "/setlevel UID level")

# 挖矿开关
@bot.message_handler(commands=['stop_mining'])
def cmd_stop(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["mining_today_locked"] = True
        bot.send_message(msg.chat.id, "✅ Stopped")
    except:
        bot.send_message(msg.chat.id, "/stop_mining UID")

@bot.message_handler(commands=['resume_mining'])
def cmd_resume(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid = msg.text.split()
        user_data[int(uid)]["mining_today_locked"] = False
        bot.send_message(msg.chat.id, "✅ Resumed")
    except:
        bot.send_message(msg.chat.id, "/resume_mining UID")

# 扣除助力值 + 用户通知
@bot.message_handler(commands=['reduce_boost'])
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
        bot.send_message(msg.chat.id, f"✅ -{v} boost")

        # ========== 新增：用户收到通知 ==========
        try:
            bot.send_message(target_uid, f"🔔 系統通知\n管理員已扣除您的助力值：{v}\n當前剩餘助力值：{u['boost']}")
        except:
            pass
    except:
        bot.send_message(msg.chat.id, "/reduce_boost UID val")

# 扣除积分 + 用户通知
@bot.message_handler(commands=['reduce_point'])
def cmd_rpoint(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, v = msg.text.split()
        target_uid = int(uid)
        v = int(v)
        u = user_data[target_uid]
        u["points"] = max(0, u["points"] - v)
        bot.send_message(msg.chat.id, f"✅ 已扣除用户 {uid} 积分：{v}")

        # ========== 新增：用户收到通知 ==========
        try:
            bot.send_message(target_uid, f"🔔 系統通知\n管理員已扣除您的積分：{v}\n當前剩餘積分：{u['points']}")
        except:
            pass
    except:
        bot.send_message(msg.chat.id, "用法：/reduce_point UID 数值")

@bot.message_handler(commands=['withdraw'])
def cmd_withdraw(msg):
    if not is_admin(msg.from_user.id):
        return
    bot.send_message(msg.chat.id, "✅ Withdraw processed")

# 设置挖矿次数
@bot.message_handler(commands=['setminetimes'])
def cmd_setmines(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, uid, t = msg.text.split()
        user_data[int(uid)]["max_mine_per_day"] = int(t)
        bot.send_message(msg.chat.id, f"✅ 每日上限：{t}")
    except:
        bot.send_message(msg.chat.id, "/setminetimes UID times")

# 设置挖矿奖励
@bot.message_handler(commands=['set_reward'])
def cmd_setreward(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, coin, v = msg.text.split()
        coin = coin.upper()
        if coin in coin_reward:
            coin_reward[coin] = int(v)
            bot.send_message(msg.chat.id, f"✅ {coin} = {v}")
        else:
            bot.send_message(msg.chat.id, "❌ Coin not found")
    except:
        bot.send_message(msg.chat.id, "/set_reward BTC 200")

# 设置挖矿延迟时间
@bot.message_handler(commands=['set_delay'])
def cmd_setdelay(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, coin, sec = msg.text.split()
        coin = coin.upper()
        sec = int(sec)
        if coin in coin_delay:
            coin_delay[coin] = sec
            bot.send_message(msg.chat.id, f"✅ {coin} 挖矿延迟：{sec} 秒")
        else:
            bot.send_message(msg.chat.id, "❌ 币种不存在")
    except:
        bot.send_message(msg.chat.id, "用法：/set_delay BTC 10")

# 设置空投金额
@bot.message_handler(commands=['set_airdrop'])
def cmd_set_airdrop(msg):
    if not is_admin(msg.from_user.id):
        return
    try:
        _, amount = msg.text.split()
        global AIRDROP_REWARD
        AIRDROP_REWARD = int(amount)
        bot.send_message(msg.chat.id, f"✅ 空投红包已设置为：{amount} 积分")
    except:
        bot.send_message(msg.chat.id, "用法：/set_airdrop 88")

# 启动
if __name__ == "__main__":
    bot.infinity_polling()
