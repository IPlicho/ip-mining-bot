import telebot
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict
from datetime import datetime

# 机器人配置
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
bot = telebot.TeleBot(BOT_TOKEN)

# 双管理员ID
ADMIN_IDS = [8256055083, 810821053]

# 用户数据存储
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

# 语言存储
user_lang = defaultdict(lambda: "zh")

# 12个挖矿币种
COINS = ["BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "MATIC", "DOT", "LINK"]
coin_reward = {coin: 100 for coin in COINS}

# 空投配置
AIRDROP_CONFIG = {
    "daily_points": 10
}

# 等级配置：等级 -> (挖矿延迟秒数, 单次助力值)
LEVEL_CONFIG = {
    1: (8, 100),
    2: (12, 120),
    3: (16, 150),
    4: (20, 180),
    5: (25, 220)
}

# ====================== 多语言文本库 ======================
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
        "mine_select": "⛏️ 請選擇挖礦幣種\n選擇後開始節點驗證，等待挖礦完成",
        "mine_no_perm": "❌ 請先申請並通過挖礦權限",
        "mine_locked": "❌ 今日挖礦已結束，暫時無法繼續助力",
        "mine_max": "❌ 今日挖礦次數已達上限",
        "mining_process": "⏳ 正在挖礦 {}，節點驗證中…",
        "mine_success": "✅ 挖礦完成：{}\nLv.{} 節點\n🎉 獲得助力值：+{}\n💎 當前總助力值：{}",
        "apply_sent": "✅ 申請已提交，請等待管理員審批",
        "already_approved": "✅ 你已經擁有挖礦權限",
        "withdraw_tip": "✅ 請把需要回戶的數值+ID發送給客服 @fcff88",
        "airdrop_done": "🧧 每日空投領取成功！\n+{} 積分\n當前積分：{}",
        "airdrop_today_claimed": "❌ 今日空投已領取，請明日再來",
        "asset_title": "👤 個人資產總覽",
        "level": "等級：Lv.{}",
        "mine_today": "今日挖礦：{}/{}",
        "boost": "💎 助力值：{}",
        "trx_balance": "🪙 TRX 餘額：{}",
        "mine_status": "✅ 挖礦權限：{}",
        "points": "📊 ID積分：{}",
        "total_withdraw": "📈 累計回戶助力值：{}",
        "status_on": "已開通",
        "status_off": "待開通",
        "status_running": "🟢 正常",
        "status_stopped": "🔴 暫停中",
        "support_msg": "✅ 聯繫客服請 @fcff88，請稍候回覆",
        "lang_switched": "✅ 語言切換成功"
    },
    "en": {
        "start_title": "IP Node Mining System | Pro Exchange Version\nWelcome, use the buttons below.",
        "btn_start_mine": "⛏️ Start IP Node Mining",
        "btn_apply_ip": "🚀 Apply Bind IP Node",
        "btn_withdraw": "🔄 Apply Withdraw",
        "btn_airdrop": "🧧 Daily Airdrop",
        "btn_asset": "👤 My Assets",
        "btn_rules": "📜 Project Rules",
        "btn_support": "💬 Support",
        "banned": "❌ You are banned.",
        "mine_select": "⛏️ Select a coin to mine\nNode verification will start after selection.",
        "mine_no_perm": "❌ Please apply for mining permission first.",
        "mine_locked": "❌ Mining closed for today.",
        "mine_max": "❌ Daily mining limit reached.",
        "mining_process": "⏳ Mining {}... Please wait for node verification.",
        "mine_success": "✅ Mining Complete: {}\nLv.{} Node\n🎉 Boost Earned: +{}\n💎 Total Boost: {}",
        "apply_sent": "✅ Application submitted, waiting for admin approval.",
        "already_approved": "✅ You already have mining access.",
        "withdraw_tip": "✅ Contact support @fcff88",
        "airdrop_done": "🧧 Daily Airdrop Claimed!\n+{} Points",
        "airdrop_today_claimed": "❌ Already claimed today.",
        "asset_title": "👤 My Asset Overview",
        "level": "Level: Lv.{}",
        "mine_today": "Mined Today: {}/{}",
        "boost": "💎 Boost: {}",
        "trx_balance": "🪙 TRX Balance: {}",
        "mine_status": "✅ Mining Status: {}",
        "points": "📊 Points: {}",
        "total_withdraw": "📈 Total Withdraw Boost: {}",
        "status_on": "Approved",
        "status_off": "Pending",
        "status_running": "🟢 Active",
        "status_stopped": "🔴 Stopped",
        "support_msg": "✅ Contact support @fcff88",
        "lang_switched": "✅ Language switched"
    }
}

def t(uid, key):
    return lang[user_lang[uid]][key]

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ====================== 语言切换 ======================
@bot.message_handler(commands=['lang'])
def switch_lang(message):
    uid = message.from_user.id
    user_lang[uid] = "en" if user_lang[uid] == "zh" else "zh"
    bot.send_message(message.chat.id, t(uid, "lang_switched"))
    main_menu(message)

# ====================== 主菜单 ======================
@bot.message_handler(commands=['start'])
def main_menu(message):
    uid = message.from_user.id
    if user_data[uid]["banned"]:
        bot.send_message(message.chat.id, t(uid, "banned"))
        return

    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(t(uid, "btn_start_mine"), callback_data="start_mining")
    btn2 = InlineKeyboardButton(t(uid, "btn_apply_ip"), callback_data="apply_mining")
    btn3 = InlineKeyboardButton(t(uid, "btn_withdraw"), callback_data="apply_withdraw")
    btn4 = InlineKeyboardButton(t(uid, "btn_airdrop"), callback_data="daily_airdrop")
    btn5 = InlineKeyboardButton(t(uid, "btn_asset"), callback_data="asset_overview")
    btn6 = InlineKeyboardButton(t(uid, "btn_rules"), callback_data="project_rules")
    btn7 = InlineKeyboardButton(t(uid, "btn_support"), callback_data="support")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)

    bot.send_message(message.chat.id, t(uid, "start_title"), reply_markup=markup)

# ====================== 挖矿 ======================
@bot.callback_query_handler(func=lambda call: call.data == "start_mining")
def mining_coin_select(call):
    uid = call.from_user.id
    u = user_data[uid]
    if u["banned"]:
        bot.answer_callback_query(call.id, t(uid, "banned"))
        return
    if not u["mining_approved"]:
        bot.answer_callback_query(call.id, t(uid, "mine_no_perm"))
        return
    if u["mining_today_locked"]:
        bot.answer_callback_query(call.id, t(uid, "mine_locked"), show_alert=True)
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        bot.answer_callback_query(call.id, t(uid, "mine_max"), show_alert=True)
        return

    markup = InlineKeyboardMarkup(row_width=3)
    coin_btns = [InlineKeyboardButton(c, callback_data=f"mine_{c}") for c in COINS]
    markup.add(*coin_btns)
    bot.edit_message_text(t(uid, "mine_select"), call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mine_"))
def mine_coin(call):
    uid = call.from_user.id
    u = user_data[uid]

    if u["banned"] or not u["mining_approved"] or u["mining_today_locked"]:
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        bot.answer_callback_query(call.id, t(uid, "mine_max"), show_alert=True)
        return

    coin = call.data.replace("mine_", "")
    level = u["level"]
    delay, _ = LEVEL_CONFIG.get(level, (8, 100))
    reward = coin_reward.get(coin, 100)

    bot.answer_callback_query(call.id, t(uid, "mining_process").format(coin), show_alert=True)
    time.sleep(delay)

    u["boost"] += reward
    u["mine_count_today"] += 1

    bot.send_message(call.message.chat.id, t(uid, "mine_success").format(coin, level, reward, u['boost']))
    main_menu(call.message)

# ====================== 申请绑定 ======================
@bot.callback_query_handler(func=lambda call: call.data == "apply_mining")
def apply_mining(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, t(uid, "banned"))
        return
    if user_data[uid]["mining_approved"]:
        bot.answer_callback_query(call.id, t(uid, "already_approved"))
        return

    for admin_id in ADMIN_IDS:
        bot.send_message(
            admin_id,
            f"🔔 New Mining Application\nUser ID: {uid}\n/agree {uid}  /refuse {uid}"
        )
    bot.send_message(call.message.chat.id, t(uid, "apply_sent"))

# ====================== 申请回户 ======================
@bot.callback_query_handler(func=lambda call: call.data == "apply_withdraw")
def apply_withdraw(call):
    uid = call.from_user.id
    bot.send_message(call.message.chat.id, t(uid, "withdraw_tip"))

# ====================== 每日空投 ======================
@bot.callback_query_handler(func=lambda call: call.data == "daily_airdrop")
def daily_airdrop(call):
    uid = call.from_user.id
    u = user_data[uid]
    if u["airdrop_claimed"]:
        bot.answer_callback_query(call.id, t(uid, "airdrop_today_claimed"))
        return
    u["airdrop_claimed"] = True
    u["points"] += AIRDROP_CONFIG["daily_points"]
    bot.send_message(call.message.chat.id, t(uid, "airdrop_done").format(AIRDROP_CONFIG["daily_points"]))

# ====================== 资产总览 ======================
@bot.callback_query_handler(func=lambda call: call.data == "asset_overview")
def show_asset(call):
    uid = call.from_user.id
    u = user_data[uid]

    mining_status = t(uid, "status_on") if u["mining_approved"] else t(uid, "status_off")
    lock_status = t(uid, "status_stopped") if u["mining_today_locked"] else t(uid, "status_running")

    info = (
        f"{t(uid, 'asset_title')}\n"
        f"{t(uid, 'level').format(u['level'])}\n"
        f"{t(uid, 'mine_today').format(u['mine_count_today'], u['max_mine_per_day'])}\n"
        f"{t(uid, 'boost')}{u['boost']}\n"
        f"{t(uid, 'trx_balance')}{u['trx']}\n"
        f"{t(uid, 'mine_status')}{mining_status}\n"
        f"{t(uid, 'points')}{u['points']}\n"
        f"{t(uid, 'total_withdraw')}{u['total_withdraw_boost']}"
    )
    bot.send_message(call.message.chat.id, info)

# ====================== 项目说明书 ======================
@bot.callback_query_handler(func=lambda call: call.data == "project_rules")
def project_rules(call):
    uid = call.from_user.id
    if user_lang[uid] == "zh":
        text = """📜 項目資格說明書
⚡️ IP節點挖礦助力機制說明
在本機器人參與助力，即為區塊鏈網路貢獻算力流量，提升節點驗證效率與安全性。系統依驗證行為發放助力值獎勵，助力值越高，回報越豐厚。

🔹 為什麼IP節點挖礦收益高且不違法？
買幣、囤幣、挖礦、炒幣均屬區塊鏈去中心化行為，目前全球並無統一法律將其定為非法。各國僅實施監管規範，並無明確刑法條款認定挖礦行為違法，去中心化特性不受單一中心機構管轄！

🏢 雲鼎資本集團控股
總部位於迪拜，業務覆蓋全球20餘國，專注數位經濟、金融科技、Web3.0領域。註冊資本逾90億美元，擁有20項技術專利及國際權威資質，通過美國貨幣監管體系審核，服務超50000+ TG用戶。"""
    else:
        text = """📜 Project Rules
IP Node Mining provides computing power to the blockchain network.
Rewards are based on your node contribution.
Legal and regulated worldwide, not illegal.

🏢 Yunding Capital Group
Dubai-based, serving 50,000+ users."""
    bot.send_message(call.message.chat.id, text)

# ====================== 客服 ======================
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    uid = call.from_user.id
    bot.send_message(call.message.chat.id, t(uid, "support_msg"))

# ====================== 管理员审批 ======================
@bot.message_handler(commands=['agree'])
def agree_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["mining_approved"] = True
        bot.send_message(message.chat.id, f"✅ Approved user {target_uid}")
    except:
        bot.send_message(message.chat.id, "Usage: /agree user_id")

@bot.message_handler(commands=['refuse'])
def refuse_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["mining_approved"] = False
        bot.send_message(message.chat.id, f"❌ Refused user {target_uid}")
    except:
        bot.send_message(message.chat.id, "Usage: /refuse user_id")

# ====================== 管理员功能 ======================
@bot.message_handler(commands=['miners'])
def show_all_miners(message):
    if not is_admin(message.from_user.id):
        return
    miner_list = []
    for uid, data in user_data.items():
        status = "Banned" if data["banned"] else ("Approved" if data["mining_approved"] else "Pending")
        miner_list.append(f"ID:{uid} | Lv.{data['level']} | Boost:{data['boost']} | TRX:{data['trx']} | {status}")
    reply = "\n".join(miner_list) if miner_list else "No miners"
    bot.send_message(message.chat.id, f"📋 Miners:\n{reply}")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        user_data[int(target_uid)]["banned"] = True
        bot.send_message(message.chat.id, "✅ Banned")
    except:
        bot.send_message(message.chat.id, "Usage: /ban user_id")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        user_data[int(target_uid)]["banned"] = False
        bot.send_message(message.chat.id, "✅ Unbanned")
    except:
        bot.send_message(message.chat.id, "Usage: /unban user_id")

@bot.message_handler(commands=['add_trx'])
def add_trx(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, amount = message.text.split()
        user_data[int(target_uid)]["trx"] += float(amount)
        bot.send_message(message.chat.id, "✅ TRX added")
    except:
        bot.send_message(message.chat.id, "Usage: /add_trx user_id amount")

@bot.message_handler(commands=['reduce_trx'])
def reduce_trx(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, amount = message.text.split()
        user_data[int(target_uid)]["trx"] = max(0, user_data[int(target_uid)]["trx"] - float(amount))
        bot.send_message(message.chat.id, "✅ TRX reduced")
    except:
        bot.send_message(message.chat.id, "Usage: /reduce_trx user_id amount")

@bot.message_handler(commands=['setlevel'])
def set_level(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, level = message.text.split()
        user_data[int(target_uid)]["level"] = int(level)
        bot.send_message(message.chat.id, "✅ Level set")
    except:
        bot.send_message(message.chat.id, "Usage: /setlevel user_id level")

# ====================== 【新增】设置挖矿次数 ======================
@bot.message_handler(commands=['setminetimes'])
def set_mine_times(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, times = message.text.split()
        target_uid = int(target_uid)
        times = int(times)
        user_data[target_uid]["max_mine_per_day"] = times
        bot.send_message(message.chat.id, f"✅ Success! Set to {times} times/day")
    except:
        bot.send_message(message.chat.id, "Usage: /setminetimes user_id times")

@bot.message_handler(commands=['stop_mining'])
def stop_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        user_data[int(target_uid)]["mining_today_locked"] = True
        bot.send_message(message.chat.id, "✅ Mining stopped")
    except:
        bot.send_message(message.chat.id, "Usage: /stop_mining user_id")

@bot.message_handler(commands=['resume_mining'])
def resume_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        user_data[int(target_uid)]["mining_today_locked"] = False
        bot.send_message(message.chat.id, "✅ Mining resumed")
    except:
        bot.send_message(message.chat.id, "Usage: /resume_mining user_id")

# ====================== 启动机器人 ======================
if __name__ == "__main__":
    bot.polling(none_stop=True)
