import sqlite3
import random
import telebot
import os

# 初始化数据库
def init_db():
    conn = sqlite3.connect('ip_mining.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, miner_id TEXT, trx REAL DEFAULT 0.0, coin INTEGER DEFAULT 0, power INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS mining_records
                 (user_id INTEGER, coin TEXT, end_time INTEGER,
                 PRIMARY KEY (user_id, coin))''')
    conn.commit()
    conn.close()

# 获取或创建用户
def get_user(uid, username=None):
    conn = sqlite3.connect('ip_mining.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    user = c.fetchone()
    if not user:
        miner_id = ''.join(random.choices("0123456789abcdef", k=8))
        c.execute('INSERT INTO users (user_id, username, miner_id) VALUES (?, ?, ?)',
                  (uid, username, miner_id))
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
        user = c.fetchone()
    conn.close()
    return user

# 更新用户信息
def update_user(uid, field, value):
    conn = sqlite3.connect('ip_mining.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, uid))
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    u = cursor.fetchone()

    text = f"""
🚀 IP节点挖矿机器人
🆔 矿工ID: {u[2]}
💰 TRX: {u[3]:.1f}
🌍 COIN: {u[4]}
📈 助力值: {u[5]}
"""

    conn.close()
    return text

# 初始化机器人
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# 个人中心命令
@bot.message_handler(commands=['start', 'profile'])
def profile(message):
    u = get_user(message.from_user.id, message.from_user.username)
    text = f"""
👤 个人中心
🆔 矿工ID: {u[2]}
💰 TRX: {u[3]:.1f}
🌍 COIN: {u[4]}
📈 助力值: {u[5]}
"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# 启动
if __name__ == '__main__':
    init_db()
    print("Bot started!")
    bot.polling(none_stop=True)
