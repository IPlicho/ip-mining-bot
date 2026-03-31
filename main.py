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

# 管理员判断
def is_admin(user_id):
    return user_id in ADMIN_IDS

# ====================== /start 主菜单 ======================
@bot.message_handler(commands=['start'])
def main_menu(message):
    uid = message.from_user.id
    if user_data[uid]["banned"]:
        bot.send_message(message.chat.id, "❌ 你已被封禁，无法使用功能")
        return

    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton("⛏️ 開始IP節點挖礦", callback_data="start_mining")
    btn2 = InlineKeyboardButton("🚀 申請綁定IP節點", callback_data="apply_mining")
    btn3 = InlineKeyboardButton("🔄 申請回戶作業", callback_data="apply_withdraw")
    btn4 = InlineKeyboardButton("🧧 每日空投領取", callback_data="daily_airdrop")
    btn5 = InlineKeyboardButton("👤 個人資產總覽", callback_data="asset_overview")
    btn6 = InlineKeyboardButton("📜 項目資格說明書", callback_data="project_rules")
    btn7 = InlineKeyboardButton("💬 線上客服專區", callback_data="support")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)

    bot.send_message(
        message.chat.id,
        "IP節點挖礦系統 | 專業交易所版\n歡迎使用，請以下方按鈕操作",
        reply_markup=markup
    )

# ====================== 開始IP節點挖礦 ======================
@bot.callback_query_handler(func=lambda call: call.data == "start_mining")
def mining_coin_select(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    if not user_data[uid]["mining_approved"]:
        bot.answer_callback_query(call.id, "❌ 請先申請並通過挖礦權限")
        return
    if user_data[uid]["mining_today_locked"]:
        bot.answer_callback_query(call.id, "❌ 今日挖礦已結束，暫時無法繼續助力", show_alert=True)
        return
    if user_data[uid]["mine_count_today"] >= user_data[uid]["max_mine_per_day"]:
        bot.answer_callback_query(call.id, "❌ 今日挖礦次數已達上限", show_alert=True)
        return

    markup = InlineKeyboardMarkup(row_width=3)
    coin_btns = [InlineKeyboardButton(c, callback_data=f"mine_{c}") for c in COINS]
    markup.add(*coin_btns)
    bot.edit_message_text(
        "⛏️ 請選擇挖礦幣種\n選擇後開始節點驗證，等待挖礦完成",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("mine_"))
def mine_coin(call):
    uid = call.from_user.id
    u = user_data[uid]

    if u["banned"] or not u["mining_approved"] or u["mining_today_locked"]:
        return
    if u["mine_count_today"] >= u["max_mine_per_day"]:
        bot.answer_callback_query(call.id, "❌ 今日挖礦次數已達上限", show_alert=True)
        return

    coin = call.data.replace("mine_", "")
    level = u["level"]
    delay, _ = LEVEL_CONFIG.get(level, (8, 100))

    # 修复：读取你设置的币种奖励
    reward = coin_reward.get(coin, 100)

    bot.answer_callback_query(call.id, f"⏳ 正在挖礦 {coin}，節點驗證中…", show_alert=True)
    time.sleep(delay)

    u["boost"] += reward
    u["mine_count_today"] += 1

    bot.send_message(
        call.message.chat.id,
        f"✅ 挖礦完成：{coin}\nLv.{level} 節點\n🎉 獲得助力值：+{reward}\n💎 當前總助力值：{u['boost']}"
    )
    main_menu(call.message)

# ====================== 申請綁定IP節點 ======================
@bot.callback_query_handler(func=lambda call: call.data == "apply_mining")
def apply_mining(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    if user_data[uid]["mining_approved"]:
        bot.answer_callback_query(call.id, "✅ 你已經擁有挖礦權限")
        return

    for admin_id in ADMIN_IDS:
        bot.send_message(
            admin_id,
            f"🔔 新的挖礦權限申請\n用戶ID：{uid}\n請回覆：\n/agree {uid}  同意\n/refuse {uid}  拒絕"
        )
    bot.send_message(call.message.chat.id, "✅ 申請已提交，請等待管理員審批")

# ====================== 申請回戶作業 ======================
@bot.callback_query_handler(func=lambda call: call.data == "apply_withdraw")
def apply_withdraw(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    bot.send_message(call.message.chat.id, "✅ 請把需要回戶的數值+ID發送給客服 @fcff88")

# ====================== 每日空投領取 ======================
@bot.callback_query_handler(func=lambda call: call.data == "daily_airdrop")
def daily_airdrop(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    if user_data[uid]["airdrop_claimed"]:
        bot.answer_callback_query(call.id, "❌ 今日空投已領取，請明日再來")
        return
    
    points = AIRDROP_CONFIG["daily_points"]
    user_data[uid]["points"] += points
    user_data[uid]["airdrop_claimed"] = True
    bot.send_message(
        call.message.chat.id,
        f"🧧 每日空投領取成功！\n+{points} 積分\n當前積分：{user_data[uid]['points']}"
    )

# ====================== 個人資產總覽 ======================
@bot.callback_query_handler(func=lambda call: call.data == "asset_overview")
def show_asset(call):
    uid = call.from_user.id
    u = user_data[uid]
    mining_status = "已開通" if u["mining_approved"] else "待開通"
    lock_status = "🔴 暫停中" if u["mining_today_locked"] else "🟢 正常"
    
    info = (
        f"👤 個人資產總覽\n"
        f"等級：Lv.{u['level']}\n"
        f"今日挖礦：{u['mine_count_today']}/{u['max_mine_per_day']}\n"
        f"💎 助力值：{u['boost']}\n"
        f"🪙 TRX 餘額：{u['trx']}\n"
        f"✅ 挖礦權限：{mining_status}\n"
        f"📊 ID積分：{u['points']}\n"
        f"📈 累計回戶助力值：{u['total_withdraw_boost']}"
    )
    bot.send_message(call.message.chat.id, info)

# ====================== 項目資格說明書 ======================
@bot.callback_query_handler(func=lambda call: call.data == "project_rules")
def project_rules(call):
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
    bot.send_message(call.message.chat.id, text)

# ====================== 線上客服專區 ======================
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    bot.send_message(call.message.chat.id, "✅ 聯繫客服請 @fcff88，請稍候回覆")

# ====================== 管理員審批指令 ======================
@bot.message_handler(commands=['agree'])
def agree_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["mining_approved"] = True
        bot.send_message(message.chat.id, f"✅ 已同意用戶 {target_uid} 開通挖礦權限")
        bot.send_message(target_uid, "✅ 你的挖礦權限申請已通過！可開始挖礦")
    except:
        bot.send_message(message.chat.id, "格式：/agree [用戶ID]")

@bot.message_handler(commands=['refuse'])
def refuse_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["mining_approved"] = False
        bot.send_message(message.chat.id, f"❌ 已拒絕用戶 {target_uid} 挖礦權限")
        bot.send_message(target_uid, "❌ 你的挖礦權限申請被拒絕")
    except:
        bot.send_message(message.chat.id, "格式：/refuse [用戶ID]")

# ====================== 管理員指令 ======================
@bot.message_handler(commands=['miners'])
def show_all_miners(message):
    if not is_admin(message.from_user.id):
        return
    miner_list = []
    for uid, data in user_data.items():
        status = "封禁" if data["banned"] else ("正常" if data["mining_approved"] else "未審批")
        miner_list.append(f"ID:{uid} | Lv.{data['level']} | 助力:{data['boost']} | TRX:{data['trx']} | 狀態:{status}")
    reply = "\n".join(miner_list) if miner_list else "暫無礦工數據"
    bot.send_message(message.chat.id, f"📋 所有礦工列表：\n{reply}")

@bot.message_handler(commands=['withdraw'])
def admin_withdraw(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(message.chat.id, "✅ 管理員已手動處理回戶作業")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["banned"] = True
        bot.send_message(message.chat.id, f"❌ 已封禁用戶 {target_uid}")
    except:
        bot.send_message(message.chat.id, "格式：/ban [用戶ID]")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["banned"] = False
        bot.send_message(message.chat.id, f"✅ 已解封用戶 {target_uid}")
    except:
        bot.send_message(message.chat.id, "格式：/unban [用戶ID]")

@bot.message_handler(commands=['set_reward'])
def set_coin_reward(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, coin, val = message.text.split()
        val = int(val)
        if coin in coin_reward:
            coin_reward[coin] = val
            bot.send_message(message.chat.id, f"✅ {coin} 挖礦獎勵設為 {val}")
        else:
            bot.send_message(message.chat.id, f"❌ 幣種 {coin} 不存在")
    except:
        bot.send_message(message.chat.id, "格式：/set_reward [幣種] [數值]")

@bot.message_handler(commands=['add_trx'])
def add_trx(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, amount = message.text.split()
        target_uid = int(target_uid)
        amount = float(amount)
        user_data[target_uid]["trx"] += amount
        bot.send_message(message.chat.id, f"✅ 給用戶 {target_uid} 添加 {amount} TRX")
    except:
        bot.send_message(message.chat.id, "格式：/add_trx [用戶ID] [數量]")

@bot.message_handler(commands=['reduce_trx'])
def reduce_trx(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, amount = message.text.split()
        target_uid = int(target_uid)
        amount = float(amount)
        user_data[target_uid]["trx"] = max(0, user_data[target_uid]["trx"] - amount)
        bot.send_message(message.chat.id, f"✅ 扣減用戶 {target_uid} {amount} TRX")
    except:
        bot.send_message(message.chat.id, "格式：/reduce_trx [用戶ID] [數量]")

@bot.message_handler(commands=['reduce_boost'])
def reduce_boost(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, val = message.text.split()
        target_uid = int(target_uid)
        val = int(val)
        u = user_data[target_uid]
        old = u["boost"]
        u["boost"] = max(0, old - val)
        real = old - u["boost"]
        u["total_withdraw_boost"] += real
        bot.send_message(message.chat.id, f"✅ 扣減用戶 {target_uid} {real} 點助力值")
        bot.send_message(target_uid, f"⚠️ 你的助力值被管理員扣除 {real} 點\n當前總助力值：{u['boost']}\n📈 累計回戶：{u['total_withdraw_boost']}")
    except:
        bot.send_message(message.chat.id, "格式：/reduce_boost [用戶ID] [數值]")

@bot.message_handler(commands=['reduce_point'])
def reduce_point(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, val = message.text.split()
        target_uid = int(target_uid)
        val = int(val)
        user_data[target_uid]["points"] = max(0, user_data[target_uid]["points"] - val)
        bot.send_message(message.chat.id, f"✅ 扣減用戶 {target_uid} {val} 點積分")
    except:
        bot.send_message(message.chat.id, "格式：/reduce_point [用戶ID] [數值]")

@bot.message_handler(commands=['stop_mining'])
def stop_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["mining_today_locked"] = True
        bot.send_message(message.chat.id, f"✅ 已停止用戶 {target_uid} 今日挖礦")
    except:
        bot.send_message(message.chat.id, "格式：/stop_mining [用戶ID]")

@bot.message_handler(commands=['resume_mining'])
def resume_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid = message.text.split()
        target_uid = int(target_uid)
        user_data[target_uid]["mining_today_locked"] = False
        bot.send_message(message.chat.id, f"✅ 已恢復用戶 {target_uid} 今日挖礦")
    except:
        bot.send_message(message.chat.id, "格式：/resume_mining [用戶ID]")

@bot.message_handler(commands=['set_airdrop'])
def set_airdrop(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, points = message.text.split()
        points = int(points)
        AIRDROP_CONFIG["daily_points"] = points
        bot.send_message(message.chat.id, f"✅ 每日空投已設為：{points} 積分")
    except:
        bot.send_message(message.chat.id, "格式：/set_airdrop 數值")

@bot.message_handler(commands=['setlevel'])
def set_level(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, level = message.text.split()
        target_uid = int(target_uid)
        level = int(level)
        if 1 <= level <= 5:
            user_data[target_uid]["level"] = level
            bot.send_message(message.chat.id, f"✅ 已將用戶 {target_uid} 設為 Lv.{level}")
        else:
            bot.send_message(message.chat.id, "❌ 等級只能設置 1-5")
    except:
        bot.send_message(message.chat.id, "格式：/setlevel 用戶ID 等級(1-5)")

@bot.message_handler(commands=['setminetimes'])
def set_mine_times(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, times = message.text.split()
        target_uid = int(target_uid)
        times = int(times)
        user_data[target_uid]["max_mine_per_day"] = times
        bot.send_message(message.chat.id, f"✅ 用戶 {target_uid} 每日挖礦上限設為 {times} 次")
    except:
        bot.send_message(message.chat.id, "格式：/setminetimes 用戶ID 次數")

# ====================== 啟動機器人 ======================
if __name__ == "__main__":
    bot.polling(none_stop=True)
