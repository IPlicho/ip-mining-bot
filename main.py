import telebot
import sqlite3
import random
from datetime import datetime
from telebot import types

# ==================== 配置 ====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = 8256055083
CUSTOMER_SERVICE = "@fcff88"
GLOBAL_MINING_ENABLED = True

# ==================== 数据库（修复字段顺序） ====================
def init_db():
    conn = sqlite3.connect("mining_pro.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        miner_id TEXT UNIQUE,
        trx REAL DEFAULT 0,
        power INTEGER DEFAULT 0,
        total_power INTEGER DEFAULT 0,
        air_today INTEGER DEFAULT 0,
        air_total INTEGER DEFAULT 0,
        air_hu_total INTEGER DEFAULT 0,
        power_hu_total INTEGER DEFAULT 0,
        trx_consumed_total REAL DEFAULT 0,
        mining_status INTEGER DEFAULT 0,
        mining_paused INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

init_db()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ==================== 工具函数（字段完全修复） ====================
def get_user(uid):
    conn = sqlite3.connect("mining_pro.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    res = c.fetchone()
    conn.close()
    return res

def update_user(uid, field, value):
    conn = sqlite3.connect("mining_pro.db")
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, uid))
    conn.commit()
    conn.close()

def gen_miner_id():
    return str(random.randint(100000, 999999))

# ==================== 菜单 ====================
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⛏️ 開始IP節點挖礦", callback_data="start_mine"),
        types.InlineKeyboardButton("🚀 申請挖礦權限", callback_data="apply_mining"),
        types.InlineKeyboardButton("👤 個人資產", callback_data="profile"),
        types.InlineKeyboardButton("📜 項目說明書", callback_data="doc_1"),
        types.InlineKeyboardButton("💬 聯繫客服", callback_data="service"),
    )
    return markup

# ==================== 按钮逻辑 ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handle(call):
    uid = call.from_user.id
    u = get_user(uid)
    if not u:
        bot.answer_callback_query(call.id, "❌ 請先發送 /start", show_alert=True)
        return

    if call.data == "start_mine":
        if u[11] != 2:
            bot.answer_callback_query(call.id, "❌ 請先申請並通過挖礦權限", show_alert=True)
            return
        if u[12] == 1:
            bot.answer_callback_query(call.id, "🛑 您的挖礦已被暫停", show_alert=True)
            return
        add = random.randint(1, 88)
        update_user(uid, "power", u[4] + add)
        update_user(uid, "total_power", u[5] + add)
        bot.answer_callback_query(call.id, f"✅ 挖礦成功｜助力值 +{add}", show_alert=True)

    elif call.data == "apply_mining":
        update_user(uid, "mining_status", 1)
        bot.send_message(ADMIN_ID, f"🔔 用戶申請挖礦\n用戶ID: {uid}\n礦工ID: {u[2]}")
        bot.answer_callback_query(call.id, "✅ 申請已提交，等待管理員審核", show_alert=True)

    elif call.data == "profile":
        txt = f"👤 個人資訊\n礦工ID: {u[2]}\n助力值: {u[4]}\n累計: {u[5]}\n挖礦權限: {'已開通' if u[11]==2 else '未開通'}"
        bot.answer_callback_query(call.id, txt, show_alert=True)

    elif call.data == "service":
        bot.answer_callback_query(call.id, f"📩 客服: {CUSTOMER_SERVICE}", show_alert=True)

# ==================== start ====================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not get_user(uid):
        mid = gen_miner_id()
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, username, miner_id) VALUES (?,?,?)", (uid, message.from_user.username or "", mid))
        conn.commit()
        conn.close()
    bot.send_message(message.chat.id, "🏧 IP節點挖礦系統", reply_markup=main_menu())

# ==================== 管理员指令 ====================
@bot.message_handler(commands=['agree'])
def agree_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("UPDATE users SET mining_status=2 WHERE user_id=?", (uid,))
        conn.commit()
        conn.close()
        bot.reply_to(message, "✅ 已強制開通挖礦權限")
    except:
        bot.reply_to(message, "用法: /agree 用戶ID")

@bot.message_handler(commands=['info'])
def info_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        u = c.fetchone()
        conn.close()
        if u:
            bot.reply_to(message, f"✅ 用戶ID: {u[0]}\n礦工ID: {u[2]}\n挖礦狀態: {u[11]} (2=開通)")
        else:
            bot.reply_to(message, "❌ 無此用戶")
    except:
        bot.reply_to(message, "用法: /info 用戶ID或礦工ID")

# ==================== 强制挖矿指令（兜底100%可用） ====================
@bot.message_handler(commands=['mine'])
def force_mine(message):
    uid = message.from_user.id
    u = get_user(uid)
    if not u:
        bot.reply_to(message, "❌ 請先 /start")
        return
    add = random.randint(1, 88)
    update_user(uid, "power", u[4] + add)
    update_user(uid, "total_power", u[5] + add)
    bot.reply_to(message, f"✅ 強制挖礦成功｜助力值 +{add}")

# ==================== 启动 ====================
if __name__ == "__main__":
    bot.infinity_polling()
