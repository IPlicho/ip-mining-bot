import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict
from datetime import datetime

# 机器人配置（已填好你的Token）
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
bot = telebot.TeleBot(BOT_TOKEN)

# 双管理员ID（你指定的两个号）
ADMIN_IDS = [8256055083, 8781082053]

# 用户数据存储
user_data = defaultdict(lambda: {
    "mining_approved": False,
    "boost": 0,
    "trx": 0,
    "points": 0,
    "total_withdraw_boost": 0,
    "banned": False,
    "airdrop_claimed": False
})

# 12个挖矿币种
COINS = ["BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "MATIC", "DOT", "LINK"]
coin_reward = {coin: 100 for coin in COINS}

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
    btn2 = InlineKeyboardButton("🚀 申請挖礦權限", callback_data="apply_mining")
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

# ====================== 開始IP節點挖礦（菜单不消失） ======================
@bot.callback_query_handler(func=lambda call: call.data == "start_mining")
def mining_coin_select(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    if not user_data[uid]["mining_approved"]:
        bot.answer_callback_query(call.id, "❌ 請先申請並通過挖礦權限")
        return

    markup = InlineKeyboardMarkup(row_width=3)
    coin_btns = [InlineKeyboardButton(c, callback_data=f"mine_{c}") for c in COINS]
    markup.add(*coin_btns)
    bot.edit_message_text(
        "⛏️ 請選擇挖礦幣種\n選擇後即可獲得對應助力值",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("mine_"))
def mine_coin(call):
    uid = call.from_user.id
    coin = call.data.replace("mine_", "")
    reward = coin_reward.get(coin, 100)
    user_data[uid]["boost"] += reward

    # 不替换菜单，只发提示
    bot.send_message(
        call.message.chat.id,
        f"✅ 選擇幣種：{coin}\n🎉 獲得助力值：+{reward}\n💎 當前總助力值：{user_data[uid]['boost']}"
    )
    # 自动重新呼出主菜单
    main_menu(call.message)

# ====================== 申請挖礦權限 ======================
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

# ====================== 每日空投領取（领积分，每日1次） ======================
@bot.callback_query_handler(func=lambda call: call.data == "daily_airdrop")
def daily_airdrop(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    if user_data[uid]["airdrop_claimed"]:
        bot.answer_callback_query(call.id, "❌ 今日空投已領取，請明日再來")
        return
    user_data[uid]["points"] += 10
    user_data[uid]["airdrop_claimed"] = True
    bot.send_message(call.message.chat.id, f"🧧 每日空投領取成功！\n+10 積分\n當前積分：{user_data[uid]['points']}")

# ====================== 個人資產總覽 ======================
@bot.callback_query_handler(func=lambda call: call.data == "asset_overview")
def show_asset(call):
    uid = call.from_user.id
    info = (
        f"👤 個人資產總覽\n"
        f"💎 助力值：{user_data[uid]['boost']}\n"
        f"🪙 TRX 餘額：{user_data[uid]['trx']} TRX\n"
        f"✅ 挖礦權限：{'已開通' if user_data[uid]['mining_approved'] else '待開通'}\n"
        f"📊 ID積分：{user_data[uid]['points']}\n"
        f"📈 累計回戶助力值：{user_data[uid]['total_withdraw_boost']}"
    )
    bot.send_message(call.message.chat.id, info)

# ====================== 項目資格說明書（精简版） ======================
@bot.callback_query_handler(func=lambda call: call.data == "project_rules")
def project_rules(call):
    text = """📜 項目資格說明書
⚡️ IP節點挖礦助力機制說明
在本機器人參與助力，即為區塊鏈網路貢獻算力與流量，提升節點驗證效率與安全性。系統依有效驗證行為發放助力值獎勵，助力值越高，回報越豐厚。

🔹 為什麼IP節點挖礦收益高且不違法？
買幣、囤幣、挖礦、炒幣均屬區塊鏈去中心化行為，目前全球並無統一法律將其定為非法。各國僅實施監管規範，並無明確刑法條款認定挖礦行為違法，去中心化特性不受單一中心機構管轄！

🏢 雲鼎資本集團控股
總部位於迪拜，業務覆蓋全球20餘國，專注數位經濟、金融科技、Web3.0領域。註冊資本逾90億美元，擁有20項技術專利及國際權威資質，通過美國貨幣監管體系審核，服務超50000+ TG客戶。

🌍 項目發展歷程
• 2018年：正式入駐TG平台
• 2021年：完成擔保機構對接，奠定合規運營基礎
• 2022年：IP節點挖礦正式上線
• 2024年：生態成熟，獲多方資本支持
• 2025年：持續優化，堅持低門檻、低風險、易上手，與用戶共贏數位財富新未來"""
    bot.send_message(call.message.chat.id, text)

# ====================== 線上客服專區 ======================
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    uid = call.from_user.id
    bot.send_message(call.message.chat.id, "✅ 聯繫客服請 @fcff88，請稍候回覆")

# ====================== 管理員審批指令 ======================
@bot.message_handler(commands=['agree'])
def agree_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        target_uid = int(message.text.split()[1])
        user_data[target_uid]["mining_approved"] = True
        bot.send_message(message.chat.id, f"✅ 已同意用戶 {target_uid} 挖礦權限")
        bot.send_message(target_uid, "✅ 你的挖礦權限申請已通過！可開始挖礦")
    except:
        bot.send_message(message.chat.id, "格式：/agree [用戶ID]")

@bot.message_handler(commands=['refuse'])
def refuse_mining(message):
    if not is_admin(message.from_user.id):
        return
    try:
        target_uid = int(message.text.split()[1])
        user_data[target_uid]["mining_approved"] = False
        bot.send_message(message.chat.id, f"❌ 已拒絕用戶 {target_uid} 挖礦權限")
        bot.send_message(target_uid, "❌ 你的挖礦權限申請被拒絕")
    except:
        bot.send_message(message.chat.id, "格式：/refuse [用戶ID]")

# ====================== 你指定的管理員指令 ======================
@bot.message_handler(commands=['miners'])
def show_all_miners(message):
    if not is_admin(message.from_user.id):
        return
    miner_list = []
    for uid, data in user_data.items():
        status = "封禁" if data["banned"] else ("正常" if data["mining_approved"] else "未審批")
        miner_list.append(f"ID:{uid} | 助力:{data['boost']} | TRX:{data['trx']} | 積分:{data['points']} | 狀態:{status}")
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
        target_uid = int(message.text.split()[1])
        user_data[target_uid]["banned"] = True
        bot.send_message(message.chat.id, f"❌ 已封禁用戶 {target_uid}")
    except:
        bot.send_message(message.chat.id, "格式：/ban [用戶ID]")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.from_user.id):
        return
    try:
        target_uid = int(message.text.split()[1])
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

# ====================== 新增扣除助力值/積分指令 ======================
@bot.message_handler(commands=['reduce_boost'])
def reduce_boost(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target_uid, val = message.text.split()
        target_uid = int(target_uid)
        val = int(val)
        user_data[target_uid]["boost"] = max(0, user_data[target_uid]["boost"] - val)
        bot.send_message(message.chat.id, f"✅ 扣減用戶 {target_uid} {val} 點助力值")
        bot.send_message(target_uid, f"⚠️ 你的助力值被管理員扣除 {val} 點，當前總助力值：{user_data[target_uid]['boost']}")
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
        bot.send_message(target_uid, f"⚠️ 你的積分被管理員扣除 {val} 點，當前總積分：{user_data[target_uid]['points']}")
    except:
        bot.send_message(message.chat.id, "格式：/reduce_point [用戶ID] [數值]")

# ====================== 啟動機器人 ======================
if __name__ == "__main__":
    bot.polling(none_stop=True)
