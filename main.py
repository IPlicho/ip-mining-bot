import telebot
import sqlite3
import random
import re
from datetime import datetime, timedelta

# ==================== 配置 ====================
BOT_TOKEN = "8727191543:AAEwOkZC8OMxIVEY7In8NQaOoXdGFQL551Q"
ADMIN_ID = 8256055083
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==================== 数据库初始化 ====================
def init_db():
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        miner_id TEXT UNIQUE,
        trx REAL DEFAULT 2.0,
        coin INTEGER DEFAULT 0,
        power INTEGER DEFAULT 0,
        last_airdrop TEXT DEFAULT '',
        air_day INTEGER DEFAULT 0,
        air_total INTEGER DEFAULT 0,
        mining_status INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cooldown (
        user_id INTEGER, coin TEXT, end_time TEXT,
        PRIMARY KEY (user_id, coin)
    )''')
    conn.commit()
    conn.close()

# ==================== 工具函数 ====================
def get_user(uid, username=None):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    user = c.fetchone()
    if not user:
        mid = ''.join(random.choices("0123456789", k=8))
        c.execute("INSERT INTO users (user_id, username, miner_id) VALUES (?,?,?)",
                  (uid, username, mid))
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        user = c.fetchone()
    conn.close()
    return user

def update_user_field(uid, field, value):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, uid))
    conn.commit()
    conn.close()

def check_user_ban(uid):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT is_banned FROM users WHERE user_id=?", (uid,))
    res = c.fetchone()
    conn.close()
    return res and res[0] == 1

# ==================== 主菜单 ====================
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "⛏ IP节点挖矿", "👤个人中心",
        "🔄回户", "🧧区块链空投",
        "📌ip挖矿频道", "📋集团介绍",
        "📊结算记录", "📢回户播报",
        "📝申请挖矿权限"
    )
    return markup

# ==================== 用户功能 ====================
@bot.message_handler(commands=['start'])
def cmd_start(message):
    uid = message.from_user.id
    if check_user_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 出错请联系客服")
        return
    user = get_user(uid, message.from_user.username)
    text = f"""
<b>🚀 IP节点挖矿机器人</b>
🆔 矿工ID：<code>{user[2]}</code>
💰 TRX：{user[3]:.1f}
📈 助力值：{user[5]}
"""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "👤个人中心")
def user_profile(message):
    uid = message.from_user.id
    if check_user_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 出错请联系客服")
        return
    user = get_user(uid)
    mining_state = "✅ 已开通" if user[9] == 2 else "⏳ 待审核" if user[9] == 1 else "❌ 未开通"
    text = f"""
<b>👤 个人中心</b>
矿工ID：<code>{user[2]}</code>
TRX：{user[3]:.1f}
助力值：{user[5]}
累计空投：{user[8]} CNY
挖矿权限：{mining_state}
"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🔄回户")
def user_huihu(message):
    uid = message.from_user.id
    if check_user_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 出错请联系客服")
        return
    user = get_user(uid)
    if user[3] < 2:
        bot.send_message(message.chat.id, "❌ TRX不足，回户失败")
        return
    update_user_field(uid, "trx", user[3] - 2)
    new_trx = get_user(uid)[3]
    bot.send_message(message.chat.id, f"✅ 回户成功\n剩余TRX：{new_trx:.1f}")

@bot.message_handler(func=lambda m: m.text == "🧧区块链空投")
def user_airdrop(message):
    uid = message.from_user.id
    if check_user_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 出错请联系客服")
        return
    user = get_user(uid)
    today = datetime.now().strftime("%Y-%m-%d")
    if user[6] == today:
        bot.send_message(message.chat.id, "❌ 今日已领取空投")
        return
    day = user[7] + 1
    amount = 2000 if day == 5 else random.randint(20, 300)
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute('''UPDATE users 
                 SET last_airdrop=?, air_day=?, air_total=air_total+? 
                 WHERE user_id=?''',
              (today, day, amount, uid))
    conn.commit()
    new_total = get_user(uid)[8]
    conn.close()
    bot.send_message(message.chat.id, f"🧧 区块链空投\n获得：{amount} CNY\n累计空投：{new_total} CNY")

@bot.message_handler(func=lambda m: m.text == "📝申请挖矿权限")
def user_apply_mining(message):
    uid = message.from_user.id
    if check_user_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 出错请联系客服")
        return
    user = get_user(uid)
    if user[9] == 2:
        bot.send_message(message.chat.id, "✅ 你已拥有挖矿权限")
        return
    if user[9] == 1:
        bot.send_message(message.chat.id, "⏳ 申请已提交，等待审核")
        return
    update_user_field(uid, "mining_status", 1)
    bot.send_message(message.chat.id, "📤 申请已提交，请等待管理员审核")
    bot.send_message(ADMIN_ID, f"🔔 新挖矿申请\n用户ID：{uid}\n用户名：{user[1]}")

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and msg.reply_to_message is not None)
def admin_approve(message):
    if message.text.strip() != "通过":
        return
    try:
        match = re.search(r"用户ID：(\d+)", message.reply_to_message.text)
        if match:
            target_uid = int(match.group(1))
            update_user_field(target_uid, "mining_status", 2)
            bot.send_message(message.chat.id, f"✅ 已通过用户 {target_uid} 的挖矿申请")
            bot.send_message(target_uid, "🎉 你的挖矿权限已开通，可开始挖矿")
        else:
            bot.send_message(message.chat.id, "❌ 未识别到用户ID")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ 审核操作失败")

@bot.message_handler(func=lambda m: m.text == "⛏ IP节点挖矿")
def open_mining(message):
    uid = message.from_user.id
    if check_user_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 出错请联系客服")
        return
    user = get_user(uid)
    if user[9] != 2:
        bot.send_message(message.chat.id, "❌ 请先申请并通过挖矿权限")
        return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 开始辅助")
    bot.send_message(message.chat.id, "🔍 节点挖矿已就绪", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 开始辅助")
def choose_coin(message):
    coins = ["LISTA","ULT","MATHER","NEXG","PEW","PARAM",
             "JENNER","TREMP","ALU","MON","NIM","MAGA"]
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for c in coins:
        markup.add(c)
    bot.send_message(message.chat.id, "⚡ 选择币种开始挖矿", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["LISTA","ULT","MATHER","NEXG","PEW","PARAM",
                                              "JENNER","TREMP","ALU","MON","NIM","MAGA"])
def do_mining(message):
    uid = message.from_user.id
    coin = message.text
    now = datetime.now()
    if check_user_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 出错请联系客服")
        return
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT end_time FROM cooldown WHERE user_id=? AND coin=?", (uid, coin))
    res = c.fetchone()
    if res:
        end = datetime.fromisoformat(res[0])
        if now < end:
            sec = int((end - now).total_seconds())
            m_val = sec // 60
            s_val = sec % 60
            bot.send_message(message.chat.id, f"⏳ 冷却中：{m_val}分{s_val}秒")
            conn.close()
            return
    add_power = random.randint(1, 88)
    c.execute("UPDATE users SET power=power+? WHERE user_id=?", (add_power, uid))
    end_time = (now + timedelta(minutes=random.randint(1,5))).isoformat()
    c.execute("REPLACE INTO cooldown (user_id, coin, end_time) VALUES (?,?,?)",
              (uid, coin, end_time))
    conn.commit()
    new_power = get_user(uid)[5]
    conn.close()
    bot.send_message(message.chat.id, f"✅ 挖矿辅助成功\n获得助力值：+{add_power}\n当前总助力值：{new_power}")

@bot.message_handler(func=lambda m: m.text == "📌ip挖矿频道")
def link1(message): bot.send_message(message.chat.id, "https://t.me/+8eM4xNGNMlgwNjRh")
@bot.message_handler(func=lambda m: m.text == "📋集团介绍")
def link2(message): bot.send_message(message.chat.id, "https://t.me/+8eM4xNGNMlgwNjRh")
@bot.message_handler(func=lambda m: m.text == "📊结算记录")
def link3(message): bot.send_message(message.chat.id, "https://t.me/+9tgv3ibhiw40NDdh")
@bot.message_handler(func=lambda m: m.text == "📢回户播报")
def link4(message): bot.send_message(message.chat.id, "https://t.me/+9tgv3ibhiw40NDdh")

if __name__ == "__main__":
    init_db()
    print("✅ 机器人启动成功")
    bot.infinity_polling()
# ==================== 极简管理员命令 ====================
# 加200 TRX：/t200 用户ID
@bot.message_handler(commands=['t200'])
def add_200trx(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT trx FROM users WHERE user_id=?", (uid,))
        trx = c.fetchone()[0]
        new_trx = trx + 200
        c.execute("UPDATE users SET trx=? WHERE user_id=?", (new_trx, uid))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ 给 {uid} 加200 TRX")
    except:
        bot.send_message(message.chat.id, "用法：/t200 用户ID")

# 扣2000助力值：/p2000 用户ID
@bot.message_handler(commands=['p2000'])
def sub_2000power(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT power FROM users WHERE user_id=?", (uid,))
        power = c.fetchone()[0]
        if power < 2000:
            bot.send_message(message.chat.id, "❌ 助力值不足")
            return
        new_power = power - 2000
        c.execute("UPDATE users SET power=? WHERE user_id=?", (new_power, uid))
        conn.commit()
        conn.close()
        bot.send_message(uid, "✅ 已成功回户")
        bot.send_message(message.chat.id, f"✅ 给 {uid} 扣2000助力")
    except:
        bot.send_message(message.chat.id, "用法：/p2000 用户ID")

# 扣60助力值：/p60 用户ID
@bot.message_handler(commands=['p60'])
def sub_60power(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT power FROM users WHERE user_id=?", (uid,))
        power = c.fetchone()[0]
        if power < 60:
            bot.send_message(message.chat.id, "❌ 助力值不足")
            return
        new_power = power - 60
        c.execute("UPDATE users SET power=? WHERE user_id=?", (new_power, uid))
        conn.commit()
        conn.close()
        bot.send_message(uid, "✅ 已成功回户")
        bot.send_message(message.chat.id, f"✅ 给 {uid} 扣60助力")
    except:
        bot.send_message(message.chat.id, "用法：/p60 用户ID")
