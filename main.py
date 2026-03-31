import os
import sqlite3
from datetime import datetime, timedelta
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===================== 已填好你的机器人配置 =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
# 请把下面的数字替换成你自己的TG数字ID（纯数字，比如123456789）
ADMIN_ID = 0  

bot = telebot.TeleBot(BOT_TOKEN)

# 支持的币种列表（可自行添加）
SUPPORTED_COINS = {
    "BTC": "比特幣",
    "ETH": "以太坊",
    "TRX": "波場",
    "BNB": "幣安幣",
    "SOL": "索拉納",
    "XRP": "瑞波幣",
    "ADA": "卡爾達諾",
    "DOGE": "狗狗幣",
    "AVAX": "雪崩",
    "DOT": "波卡",
    "LINK": "鏈聯",
    "LTC": "萊特幣",
    "MATIC": "Polygon",
    "USDT": "泰達幣"
}

# ===================== SQLite 数据库初始化 =====================
def init_db():
    conn = sqlite3.connect("ip_mining.db")
    c = conn.cursor()
    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        trx REAL DEFAULT 0,
        power INTEGER DEFAULT 0,
        ip TEXT DEFAULT "",
        ip_status TEXT DEFAULT "none",
        air_drop_time TEXT DEFAULT "",
        last_mining_time TEXT DEFAULT "",
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    # 全局奖励配置表
    c.execute('''CREATE TABLE IF NOT EXISTS rewards (
        coin TEXT PRIMARY KEY,
        amount REAL DEFAULT 0
    )''')
    # 初始化支持的币种
    for coin in SUPPORTED_COINS.keys():
        c.execute("INSERT OR IGNORE INTO rewards (coin, amount) VALUES (?, 0)", (coin,))
    conn.commit()
    conn.close()

init_db()

# ===================== 数据库操作工具函数 =====================
def get_user(user_id):
    conn = sqlite3.connect("ip_mining.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(user_id, username):
    conn = sqlite3.connect("ip_mining.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?,?)", (user_id, username))
    conn.commit()
    conn.close()

def get_reward(coin):
    conn = sqlite3.connect("ip_mining.db")
    c = conn.cursor()
    c.execute("SELECT amount FROM rewards WHERE coin=?", (coin.upper(),))
    res = c.fetchone()
    conn.close()
    return res[0] if res else 0

def set_reward(coin, amount):
    conn = sqlite3.connect("ip_mining.db")
    c = conn.cursor()
    c.execute("UPDATE rewards SET amount=? WHERE coin=?", (amount, coin.upper()))
    conn.commit()
    conn.close()

def give_mining_reward(user_id):
    """发放所有币种奖励到用户TRX余额"""
    total_reward = 0
    for coin in SUPPORTED_COINS.keys():
        amount = get_reward(coin)
        total_reward += amount
    if total_reward > 0:
        conn = sqlite3.connect("ip_mining.db")
        c = conn.cursor()
        c.execute("UPDATE users SET trx = trx + ? WHERE user_id=?", (total_reward, user_id))
        conn.commit()
        conn.close()
    return total_reward

# ===================== 主菜单 =====================
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⛏️ IP節點挖礦", callback_data="mining_panel"),
        InlineKeyboardButton("🔗 綁定IP", callback_data="bind_ip"),
        InlineKeyboardButton("🔄 申請回戶", callback_data="apply_back"),
        InlineKeyboardButton("🧧 每日空投", callback_data="daily_air"),
        InlineKeyboardButton("👤 我的資產", callback_data="my_asset"),
        InlineKeyboardButton("📜 項目說明", callback_data="proj_info"),
        InlineKeyboardButton("💬 聯繫客服", callback_data="contact_service")
    )
    return keyboard

# ===================== /start 命令 =====================
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    create_user(user.id, user.username)
    bot.send_message(
        message.chat.id,
        f"👋 歡迎 {user.first_name}，NodeVerse Bot 已啟動\n請選擇功能：",
        reply_markup=main_menu()
    )

# ===================== 管理员命令 =====================
@bot.message_handler(commands=['set_reward'])
def admin_set_reward(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ 您無權使用此命令！")
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "⚠️ 格式錯誤！正確格式：/set_reward [幣種] [數值]\n範例：/set_reward BTC 1000")
            return
        coin = parts[1].upper()
        amount = float(parts[2])
        if coin not in SUPPORTED_COINS:
            bot.send_message(message.chat.id, f"❌ 幣種 {coin} 不存在！支持幣種：{', '.join(SUPPORTED_COINS.keys())}")
            return
        set_reward(coin, amount)
        bot.send_message(message.chat.id, f"✅ {coin} 挖礦獎勵設為 {amount}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ 設置失敗：{str(e)}")

@bot.message_handler(commands=['agree'])
def admin_agree(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ 您無權使用此命令！")
        return
    try:
        target_id = int(message.text.split()[1])
        conn = sqlite3.connect("ip_mining.db")
        c = conn.cursor()
        c.execute("UPDATE users SET ip_status='approved' WHERE user_id=?", (target_id,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ 已同意用戶 {target_id} 的 IP 綁定！")
        bot.send_message(target_id, "✅ 您的 IP 已審核通過，可正常挖礦！")
    except:
        bot.send_message(message.chat.id, "用法：/agree 用户ID")

@bot.message_handler(commands=['add_trx'])
def add_trx(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ 您無權使用此命令！")
        return
    try:
        target_id = int(message.text.split()[1])
        amount = float(message.text.split()[2])
        conn = sqlite3.connect("ip_mining.db")
        c = conn.cursor()
        c.execute("UPDATE users SET trx = trx + ? WHERE user_id=?", (amount, target_id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ 已給 {target_id} 增加 {amount} TRX")
        bot.send_message(target_id, f"✅ 管理員已給您發放 {amount} TRX 獎勵！")
    except:
        bot.send_message(message.chat.id, "用法：/add_trx 用户ID 數量")

# ===================== 按钮回调 =====================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    user_id = call.from_user.id
    user = get_user(user_id)
    if not user:
        create_user(user_id, call.from_user.username)
        user = get_user(user_id)

    if data == "mining_panel":
        # 检查挖矿冷却（24小时一次）
        last_mining = user[7] if user[7] else None
        now = datetime.now()
        can_mining = True
        remaining_str = ""
        if last_mining:
            last_time = datetime.strptime(last_mining, "%Y-%m-%d %H:%M:%S")
            if now - last_time < timedelta(hours=24):
                can_mining = False
                remaining = timedelta(hours=24) - (now - last_time)
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                remaining_str = f"{hours} 小時 {minutes} 分鐘"

        # 发放奖励
        reward_msg = ""
        if can_mining and user[5] == "approved":
            total_reward = give_mining_reward(user_id)
            # 更新挖矿时间
            conn = sqlite3.connect("ip_mining.db")
            c = conn.cursor()
            c.execute("UPDATE users SET last_mining_time=? WHERE user_id=?", (now.strftime("%Y-%m-%d %H:%M:%S"), user_id))
            conn.commit()
            conn.close()
            reward_msg = f"\n✅ 挖礦成功！已發放總獎勵 {total_reward} TRX"
        elif user[5] != "approved":
            reward_msg = "\n⚠️ 您的 IP 未審核通過，無法挖礦！"
        elif not can_mining:
            reward_msg = f"\n⚠️ 挖礦冷卻中！剩餘 {remaining_str} 可再次挖礦"

        # 生成挖矿面板
        panel = "⛏️ 多幣種挖礦面板\n"
        for coin, name in SUPPORTED_COINS.items():
            amount = get_reward(coin)
            panel += f"{coin}  {amount}\n"
        panel += reward_msg

        bot.edit_message_text(
            panel.strip(),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "bind_ip":
        bot.edit_message_text(
            "🔗 請直接發送您的 IP 地址，提交後等待管理員審核",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "my_asset":
        trx = user[2]
        power = user[3]
        ip_st = "已綁定（審核通過）" if user[5] == "approved" else "未綁定/審核中"
        msg = f"👤 資產總覽\nTRX 餘額：{trx}\n助力值：{power}\nIP 狀態：{ip_st}"
        bot.edit_message_text(
            msg,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "daily_air":
        # 每日空投逻辑
        air_time = user[6] if user[6] else None
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        if air_time == today:
            msg = "🧧 今日空投已領取，請明天再來！"
        else:
            # 发放空投奖励（可自定义金额）
            air_amount = 1000
            conn = sqlite3.connect("ip_mining.db")
            c = conn.cursor()
            c.execute("UPDATE users SET trx = trx + ?, air_drop_time=? WHERE user_id=?", (air_amount, today, user_id))
            conn.commit()
            conn.close()
            msg = f"🧧 每日空投成功！已發放 {air_amount} TRX"
        bot.edit_message_text(
            msg,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "apply_back":
        bot.edit_message_text(
            "🔄 回戶申請已開放，請聯繫客服辦理",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "proj_info":
        bot.edit_message_text(
            "📜 NodeVerse IP 節點挖礦項目：\n通過貢獻節點流量獲得穩定收益\n支持多幣種挖礦，每日空投，助力值升級",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "contact_service":
        bot.edit_message_text(
            "💬 客服：@fcff88",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

# ===================== 接收 IP 地址 =====================
@bot.message_handler(func=lambda message: True)
def receive_ip(message):
    user_id = message.from_user.id
    text = message.text.strip()
    # 简单IP校验
    if "." in text and len(text) >= 7 and text.count(".") == 3:
        conn = sqlite3.connect("ip_mining.db")
        c = conn.cursor()
        c.execute("UPDATE users SET ip=?, ip_status='pending' WHERE user_id=?", (text, user_id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "✅ IP 已提交，等待管理員審核")
        try:
            bot.send_message(ADMIN_ID, f"🆕 用戶 {user_id}（@{message.from_user.username}）提交 IP：{text}")
        except:
            pass
    else:
        bot.send_message(message.chat.id, "📩 已收到您的消息，客服將盡快回覆！")

# ===================== 启动机器人 =====================
if __name__ == "__main__":
    print("NodeVerse Bot 启动中...")
    bot.polling(none_stop=True)
