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
        "welcome": "IP節點挖礦系統 | 專業交易所版\n歡迎使用，請以下方按鈕操作",
        "start_mining": "⛏️ 開始IP節點挖礦",
        "apply_ip": "🚀 申請綁定IP節點",
        "apply_withdraw": "🔄 申請回戶作業",
        "daily_airdrop": "🧧 每日空投領取",
        "asset_overview": "👤 個人資產總覽",
        "project_rules": "📜 項目資格說明書",
        "support": "💬 線上客服專區",

        "banned": "❌ 你已被封禁，無法使用功能",
        "no_permission": "❌ 請先申請並通過挖礦權限",
        "mining_locked": "❌ 今日挖礦已結束，暫時無法繼續助力",
        "mine_limit_reached": "❌ 今日挖礦次數已達上限",
        "select_coin": "⛏️ 請選擇挖礦幣種\n選擇後開始節點驗證，等待挖礦完成",
        "mining": "⏳ 正在挖礦 {}，節點驗證中…",
        "mining_success": "✅ 挖礦完成：{}\nLv.{} 節點\n🎉 獲得助力值：+{}\n💎 當前總助力值：{}",
        "apply_sent": "✅ 申請已提交，請等待管理員審批",
        "already_approved": "✅ 你已經擁有挖礦權限",
        "contact_service": "✅ 請把需要回戶的數值+ID發送給客服 @fcff88",
        "airdrop_success": "🧧 每日空投領取成功！\n+{} 積分\n當前積分：{}",
        "airdrop_claimed": "❌ 今日空投已領取，請明日再來",

        "asset_title": "👤 個人資產總覽",
        "level": "等級：Lv.{}",
        "mine_today": "今日挖礦：{}/{}",
        "boost": "💎 助力值：{}",
        "trx": "🪙 TRX 餘額：{}",
        "mining_status": "✅ 挖礦權限：{}",
        "points": "📊 ID積分：{}",
        "total_withdraw_boost": "📈 累計回戶助力值：{}",
        "enabled": "已開通",
        "disabled": "待開通",
        "normal": "🟢 正常",
        "stopped": "🔴 暫停中",

        "contact_admin": "✅ 聯繫客服請 @fcff88，請稍候回覆",
        "lang_changed": "✅ 語言已切換為中文",
    },
    "en": {
        "welcome": "IP Node Mining System | Pro Exchange Version\nWelcome, please use the buttons below.",
        "start_mining": "⛏️ Start IP Node Mining",
        "apply_ip": "🚀 Apply Bind IP Node",
        "apply_withdraw": "🔄 Apply Withdraw",
        "daily_airdrop": "🧧 Daily Airdrop",
        "asset_overview": "👤 My Assets",
        "project_rules": "📜 Project Rules",
        "support": "💬 Support",

        "banned": "❌ You are banned.",
        "no_permission": "❌ Please apply for mining permission first.",
        "mining_locked": "❌ Mining is closed today.",
        "mine_limit_reached": "❌ Daily mining limit reached.",
        "select_coin": "⛏️ Select a coin to start mining.",
        "mining": "⏳ Mining {}... Please wait.",
        "mining_success": "✅ Mining Complete: {}\nLv.{} Node\n🎉 Boost Earned: +{}\n💎 Total Boost: {}",
        "apply_sent": "✅ Application submitted, waiting for approval.",
        "already_approved": "✅ You already have mining access.",
        "contact_service": "✅ Send your amount and ID to support @fcff88",
        "airdrop_success": "🧧 Daily Airdrop Claimed!\n+{} Points\nCurrent Points: {}",
        "airdrop_claimed": "❌ Already claimed today.",

        "asset_title": "👤 My Asset Overview",
        "level": "Level: Lv.{}",
        "mine_today": "Mined Today: {}/{}",
        "boost": "💎 Boost: {}",
        "trx": "🪙 TRX Balance: {}",
        "mining_status": "✅ Mining Status: {}",
        "points": "📊 Points: {}",
        "total_withdraw_boost": "📈 Total Withdraw Boost: {}",
        "enabled": "Approved",
        "disabled": "Pending",
        "normal": "🟢 Active",
        "stopped": "🔴 Stopped",

        "contact_admin": "✅ Contact support @fcff88",
        "lang_changed": "✅ Language switched to English",
    }
}

def txt(uid, key):
    return lang[user_lang[uid]][key]

# 管理员判断
def is_admin(user_id):
    return user_id in ADMIN_IDS

# ====================== 语言切换 ======================
@bot.message_handler(commands=['lang'])
def change_lang(message):
    uid = message.from_user.id
    user_lang[uid] = "en" if user_lang[uid] == "zh" else "zh"
    bot.send_message(message.chat.id, txt(uid, "lang_changed"))
    main_menu(message)

# ====================== 主菜单 ======================
@bot.message_handler(commands=['start'])
def main_menu(message):
    uid = message.from_user.id
    if user_data[uid]["banned"]:
        bot.send_message(message.chat.id, txt(uid, "banned"))
        return

    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(txt(uid, "start_mining"), callback_data="start_mining")
    btn2 = InlineKeyboardButton(txt(uid, "apply_ip"), callback_data="apply_mining")
    btn3 = InlineKeyboardButton(txt(uid, "apply_withdraw"), callback_data="apply_withdraw")
    btn4 = InlineKeyboardButton(txt(uid, "daily_airdrop"), callback_data="daily_airdrop")
    btn5 = InlineKeyboardButton(txt(uid, "asset_overview"), callback_data="asset_overview")
    btn6 = InlineKeyboardButton(txt(uid, "project_rules"), callback_data="project_rules")
    btn7 = InlineKeyboardButton(txt(uid, "support"), callback_data="support")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)

    bot.send_message(message.chat.id, txt(uid, "welcome"), reply_markup=markup)

# ====================== 挖矿 ======================
@bot.callback_query_handler(func=lambda call: call.data == "start_mining")
def mining_coin_select(call):
    uid = call.from_user.id
    u = user_data[uid]
    if u["banned"]:
        bot.answer_callback_query(call.id, txt(uid, "banned"))
        return
    if not u["mining_approved"]:
        bot.answer_callback_query(call.id, txt(uid, "no_permission"))
        return
    if u["mining_today_locked"]:
        bot.answer_callback_query(call.id, txt(uid, "mining_locked"), show_alert=True)
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        bot.answer_callback_query(call.id, txt(uid, "mine_limit_reached"), show_alert=True)
        return

    markup = InlineKeyboardMarkup(row_width=3)
    coin_btns = [InlineKeyboardButton(c, callback_data=f"mine_{c}") for c in COINS]
    markup.add(*coin_btns)
    bot.edit_message_text(txt(uid, "select_coin"), call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mine_"))
def mine_coin(call):
    uid = call.from_user.id
    u = user_data[uid]

    if u["banned"] or not u["mining_approved"] or u["mining_today_locked"]:
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        bot.answer_callback_query(call.id, txt(uid, "mine_limit_reached"), show_alert=True)
        return

    coin = call.data.replace("mine_", "")
    level = u["level"]
    delay, _ = LEVEL_CONFIG.get(level, (8, 100))
    reward = coin_reward.get(coin, 100)

    bot.answer_callback_query(call.id, txt(uid, "mining").format(coin), show_alert=True)
    time.sleep(delay)

    u["boost"] += reward
    u["mine_count_today"] += 1

    bot.send_message(call.message.chat.id, txt(uid, "mining_success").format(coin, level, reward, u['boost']))
    main_menu(call.message)

# ====================== 申请挖矿 ======================
@bot.callback_query_handler(func=lambda call: call.data == "apply_mining")
def apply_mining(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, txt(uid, "banned"))
        return
    if user_data[uid]["mining_approved"]:
        bot.answer_callback_query(call.id, txt(uid, "already_approved"))
        return

    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, f"🔔 New Application\nUser ID: {uid}\n/agree {uid}\n/refuse {uid}")
    bot.send_message(call.message.chat.id, txt(uid, "apply_sent"))

# ====================== 申请回户 ======================
@bot.callback_query_handler(func=lambda call: call.data == "apply_withdraw")
def apply_withdraw(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, txt(uid, "banned"))
        return
    bot.send_message(call.message.chat.id, txt(uid, "contact_service"))

# ====================== 每日空投 ======================
@bot.callback_query_handler(func=lambda call: call.data == "daily_airdrop")
def daily_airdrop(call):
    uid = call.from_user.id
    u = user_data[uid]
    if u["banned"]:
        bot.answer_callback_query(call.id, txt(uid, "banned"))
        return
    if u["airdrop_claimed"]:
        bot.answer_callback_query(call.id, txt(uid, "airdrop_claimed"))
        return

    points = AIRDROP_CONFIG["daily_points"]
    u["points"] += points
    u["airdrop_claimed"] = True
    bot.send_message(call.message.chat.id, txt(uid, "airdrop_success").format(points, u["points"]))

# ====================== 资产 ======================
@bot.callback_query_handler(func=lambda call: call.data == "asset_overview")
def show_asset(call):
    uid = call.from_user.id
    u = user_data[uid]

    mining_status = txt(uid, "enabled") if u["mining_approved"] else txt(uid, "disabled")
    lock_status = txt(uid, "stopped") if u["mining_today_locked"] else txt(uid, "normal")

    info = (
        f"{txt(uid, 'asset_title')}\n"
        f"{txt(uid, 'level').format(u['level'])}\n"
        f"{txt(uid, 'mine_today').format(u['mine_count_today'], u['max_mine_per_day'])}\n"
        f"{txt(uid, 'boost')}{u['boost']}\n"
        f"{txt(uid, 'trx')}{u['trx']}\n"
        f"{txt(uid, 'mining_status')}{mining_status}\n"
        f"{txt(uid, 'points')}{u['points']}\n"
        f"{txt(uid, 'total_withdraw_boost')}{u['total_withdraw_boost']}"
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
總部位於迪拜，業務覆蓋全球20餘國，專注數位經濟、金融科技、Web3.0領域。註冊資本逾90億美元，擁有20項技術專利及國際權威資質，通過美國貨幣監管體系審核，服務超50000+ TG用戶。

🌍 項目發展歷程
• 2018年：正式入駐TG平台
• 2021年：完成擔保機構對接，奠定合規運營基礎
• 2022年：IP節點挖礦正式上線
• 2024年：生態成熟，獲多方資本支持
• 2025年：持續優化，堅持低門檻、低風險、易上手，與用戶共贏數位財富未來"""
    else:
        text = """📜 Project Qualification & Rules
⚡️ IP Node Mining Mechanism
By participating in mining through this bot, you contribute computing power and traffic to the blockchain network, improving node verification efficiency and security.
The system distributes boost rewards based on your node activity — higher boost means higher returns.

🔹 Why IP Node Mining is High-Yield & LEGAL
Buying, holding, mining, and trading crypto are all decentralized blockchain behaviors.
There is currently no unified global law that classifies these actions as illegal.
Most countries only implement regulatory frameworks, not criminal penalties for mining.
Decentralized projects are not controlled by any single authority.

🏢 Yunding Capital Group
Headquartered in Dubai, operating in over 20 countries.
Focus: digital economy, fintech, Web3.0.
Registered capital: over $9 billion.
20+ tech patents & international certifications.
Approved by US financial regulatory systems.
Serving 50,000+ Telegram users.

🌍 Project History
• 2018: Officially launched on Telegram
• 2021: Partnered with guarantee institutions for compliant operation
• 2022: IP Node Mining officially released
• 2024: Ecosystem matured with multiple capital supports
• 2025: Continuous optimization — low threshold, low risk, easy to use, for long-term wealth growth"""
    bot.send_message(call.message.chat.id, text)

# ====================== 客服 ======================
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    uid = call.from_user.id
    bot.send_message(call.message.chat.id, txt(uid, "contact_admin"))

# ====================== 管理员命令 ======================
@bot.message_handler(commands=['agree'])
def agree_mining(message):
    if not is_admin(message.from_user.id): return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["mining_approved"] = True
        bot.send_message(message.chat.id, f"✅ Approved {target_uid}")
        bot.send_message(target_uid, "✅ Your mining access approved!")
    except:
        bot.send_message(message.chat.id, "Usage: /agree uid")

@bot.message_handler(commands=['refuse'])
def refuse_mining(message):
    if not is_admin(message.from_user.id): return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["mining_approved"] = False
        bot.send_message(message.chat.id, f"❌ Rejected {target_uid}")
        bot.send_message(target_uid, "❌ Your application rejected")
    except:
        bot.send_message(message.chat.id, "Usage: /refuse uid")

@bot.message_handler(commands=['miners'])
def show_miners(message):
    if not is_admin(message.from_user.id): return
    msg = []
    for uid, d in user_data.items():
        s = "Banned" if d["banned"] else ("Approved" if d["mining_approved"] else "Pending")
        msg.append(f"UID:{uid} Lv{d['level']} Boost:{d['boost']} TRX:{d['trx']} {s}")
    bot.send_message(message.chat.id, "\n".join(msg) if msg else "No miners")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message.from_user.id): return
    try:
        _, uid = message.text.split()
        user_data[int(uid)]["banned"] = True
        bot.send_message(message.chat.id, "✅ Banned")
    except: pass

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.from_user.id): return
    try:
        _, uid = message.text.split()
        user_data[int(uid)]["banned"] = False
        bot.send_message(message.chat.id, "✅ Unbanned")
    except: pass

@bot.message_handler(commands=['add_trx'])
def add_trx(message):
    if not is_admin(message.from_user.id): return
    try:
        _, uid, amt = message.text.split()
        user_data[int(uid)]["trx"] += float(amt)
        bot.send_message(message.chat.id, "✅ Done")
    except: pass

@bot.message_handler(commands=['setlevel'])
def set_level(message):
    if not is_admin(message.from_user.id): return
    try:
        _, uid, lv = message.text.split()
        user_data[int(uid)]["level"] = int(lv)
        bot.send_message(message.chat.id, "✅ Level set")
    except: pass

@bot.message_handler(commands=['stop_mining'])
def stop_mining(message):
    if not is_admin(message.from_user.id): return
    try:
        _, uid = message.text.split()
        user_data[int(uid)]["mining_today_locked"] = True
        bot.send_message(message.chat.id, "✅ Stopped")
    except: pass

@bot.message_handler(commands=['resume_mining'])
def resume_mining(message):
    if not is_admin(message.from_user.id): return
    try:
        _, uid = message.text.split()
        user_data[int(uid)]["mining_today_locked"] = False
        bot.send_message(message.chat.id, "✅ Resumed")
    except: pass

# ====================== 启动机器人 ======================
if __name__ == "__main__":
    bot.polling(none_stop=True)
