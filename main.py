import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict

# 机器人配置（已填好你的Token）
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
bot = telebot.TeleBot(BOT_TOKEN)

# 管理员ID（你本人）
ADMIN_ID = 8781082053

# 用户数据存储
user_data = defaultdict(lambda: {
    "mining_approved": False,
    "boost": 0,
    "trx": 0,
    "banned": False
})

# 12个挖矿币种（不含TRX）
COINS = ["BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "MATIC", "DOT", "LINK"]
coin_reward = {coin: 100 for coin in COINS}

# 管理员判断
def is_admin(user_id):
    return user_id == ADMIN_ID

# ====================== /start 主菜单（完整可用） ======================
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

# ====================== 開始IP節點挖礦（12币种选择，真实可用） ======================
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

    bot.edit_message_text(
        f"✅ 選擇幣種：{coin}\n🎉 獲得助力值：+{reward}\n💎 當前總助力值：{user_data[uid]['boost']}",
        call.message.chat.id,
        call.message.message_id
    )

# ====================== 申請挖礦權限（真实发送审批消息） ======================
@bot.callback_query_handler(func=lambda call: call.data == "apply_mining")
def apply_mining(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    if user_data[uid]["mining_approved"]:
        bot.answer_callback_query(call.id, "✅ 你已經擁有挖礦權限")
        return

    # 發送審批請求給管理員
    bot.send_message(
        ADMIN_ID,
        f"🔔 新的挖礦權限申請\n用戶ID：{uid}\n請回覆：\n/agree {uid}  同意\n/refuse {uid}  拒絕"
    )
    bot.send_message(call.message.chat.id, "✅ 申請已提交，請等待管理員審批")

# ====================== 申請回戶作業（真实可用） ======================
@bot.callback_query_handler(func=lambda call: call.data == "apply_withdraw")
def apply_withdraw(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    bot.send_message(
        ADMIN_ID,
        f"🔔 用戶申請回戶\n用戶ID：{uid}\nTRX餘額：{user_data[uid]['trx']}\n請管理員使用 /withdraw 處理"
    )
    bot.send_message(call.message.chat.id, "✅ 回戶申請已提交，管理員將盡快處理")

# ====================== 每日空投領取（真实可用） ======================
@bot.callback_query_handler(func=lambda call: call.data == "daily_airdrop")
def daily_airdrop(call):
    uid = call.from_user.id
    if user_data[uid]["banned"]:
        bot.answer_callback_query(call.id, "❌ 你已被封禁")
        return
    # 每日空投固定奖励
    user_data[uid]["trx"] += 5
    bot.send_message(call.message.chat.id, f"🧧 每日空投領取成功！\n+5 TRX\n當前TRX：{user_data[uid]['trx']}")

# ====================== 個人資產總覽（真实可用） ======================
@bot.callback_query_handler(func=lambda call: call.data == "asset_overview")
def show_asset(call):
    uid = call.from_user.id
    info = (
        f"👤 個人資產總覽\n"
        f"💎 助力值：{user_data[uid]['boost']}\n"
        f"🪙 TRX 餘額：{user_data[uid]['trx']}\n"
        f"✅ 挖礦權限：{'已開通' if user_data[uid]['mining_approved'] else '未開通'}"
    )
    bot.send_message(call.message.chat.id, info)

# ====================== 項目資格說明書（真实文案） ======================
@bot.callback_query_handler(func=lambda call: call.data == "project_rules")
def project_rules(call):
    text = """📜 項目資格說明書
1. 需申請並通過挖礦權限才可開始挖礦
2. 選擇幣種挖礦可獲得對應助力值
3. 每日可領取空投TRX獎勵
4. 助力值與TRX可申請回戶兌現"""
    bot.send_message(call.message.chat.id, text)

# ====================== 線上客服專區（真实可用） ======================
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    uid = call.from_user.id
    bot.send_message(
        ADMIN_ID,
        f"💬 用戶諮詢客服\n用戶ID：{uid}\n請及時回覆"
    )
    bot.send_message(call.message.chat.id, "✅ 已聯繫客服，請稍候回覆")

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

# ====================== 你指定的7條管理員指令 ======================
@bot.message_handler(commands=['miners'])
def show_all_miners(message):
    if not is_admin(message.from_user.id):
        return
    miner_list = []
    for uid, data in user_data.items():
        status = "封禁" if data["banned"] else ("正常" if data["mining_approved"] else "未審批")
        miner_list.append(f"ID:{uid} | 助力:{data['boost']} | TRX:{data['trx']} | 狀態:{status}")
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

# ====================== 啟動機器人 ======================
if __name__ == "__main__":
    bot.polling(none_stop=True)
