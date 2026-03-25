import telebot
import sqlite3
import random
from datetime import datetime, timedelta
import threading
import time
import osma

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 8256055083))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

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
        mining_apply INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cooldown (
        user_id INTEGER, coin TEXT, end_time TEXT,
        PRIMARY KEY (user_id, coin)
    )''')
    conn.commit()
    conn.close()

def get_user(uid, username=None):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    user = c.fetchone()
    if not user:
        miner_id = ''.join(random.choices("0123456789", k=8))
        c.execute('INSERT INTO users (user_id, username, miner_id) VALUES (?,?,?)',
                  (uid, username, miner_id))
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        user = c.fetchone()
    conn.close()
    return user

def update_user(uid, field, value):
    conn = sqlite3.connect('ip_mining.db')
cursor = conn.cursor()
    text = f"""
  🚀 IP节点挖矿机器人
🆔 矿工ID：{u[2]}
💰 TRX：{u[3]:.1f}
🪙 COIN：{u[4]}
📈 助力值：{u[5]}
"""
bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "👤个人中心")
def profile(message):
u = get_user(message.from_user.id)
text = f"""
👤 个人中心
矿工ID：{u[2]}
TRX：{u[3]:.1f}
COIN：{u[4]}
助力值：{u[5]}
"""
bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📝申请挖矿权限")
def apply(message):
uid = message.from_user.id
u = get_user(uid)
if u[9] == 2:
bot.send_message(message.chat.id, "✅ 已拥有挖矿权限")
return
if u[9] == 1:
bot.send_message(message.chat.id, "⏳ 已提交申请，等待审核")
return
update_user(uid, "mining_apply", 1)
bot.send_message(message.chat.id, "📤 申请已提交")
bot.send_message(ADMIN_ID, f"🔔 新挖矿申请\n用户ID：{uid}\n用户名：{u[1]}")

@bot.message_handler(commands=['allow'])
def allow_cmd(message):
if message.from_user.id != ADMIN_ID:
return
try:
uid = int(message.text.split()[1])
update_user(uid, "mining_apply", 2)
bot.send_message(ADMIN_ID, "✅ 已通过挖矿权限")
bot.send_message(uid, "🎉 你的挖矿申请已通过")
except:
bot.send_message(ADMIN_ID, "❌ 格式：/allow 用户ID")

@bot.message_handler(func=lambda m: m.text == "⛏ IP节点挖矿")
def mining(message):
u = get_user(message.from_user.id)
if u[9] != 2:
bot.send_message(message.chat.id, "❌ 请先申请并通过审核")
return
bot.send_message(message.chat.id, "✅ 挖矿功能已解锁，可以正常使用")

def run_bot():
while True:
try:
bot.infinity_polling(timeout=30, long_polling_timeout=10)
except Exception as e:
print("重启中..", e)
time.sleep(5)

if __name__ == "__main__":
init_db()
print("✅ 机器人启动成功")
run_bot()
