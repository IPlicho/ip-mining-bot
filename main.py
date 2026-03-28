import telebot
import sqlite3
import random
from telebot import types

# ==================== 配置 ====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = 8256055083

# ==================== 数据库（兼容旧数据，不丢失用户） ====================
def init_db():
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        miner_id TEXT UNIQUE,
        power INTEGER DEFAULT 0,
        mining_status TEXT DEFAULT "none"
    )''')
    conn.commit()
    conn.close()

init_db()
bot = telebot.TeleBot(BOT_TOKEN)

# ==================== 兼容旧数据：自动升级旧状态 ====================
def migrate_old_data():
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    try:
        c.execute("SELECT user_id, mining_status FROM users")
        all_users = c.fetchall()
        for uid, val in all_users:
            if isinstance(val, int):
                if val == 0:
                    new_val = "none"
                elif val == 1:
                    new_val = "applied"
                elif val == 2:
                    new_val = "approved"
                else:
                    new_val = "none"
                c.execute("UPDATE users SET mining_status=? WHERE user_id=?", (new_val, uid))
        conn.commit()
    except:
        pass
    conn.close()

migrate_old_data()

# ==================== 用户信息 ====================
def get_user(uid):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(uid):
    if not get_user(uid):
        miner_id = str(random.randint(100000, 999999))
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, miner_id) VALUES (?,?)", (uid, miner_id))
        conn.commit()
        conn.close()
    return get_user(uid)

# ==================== 菜单 ====================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 申请挖矿权限", "⛏️ 开始挖矿", "👤 我的信息")
    return markup

# ==================== 用户逻辑 ====================
@bot.message_handler(commands=['start'])
def start(message):
    create_user(message.from_user.id)
    bot.send_message(message.chat.id, "🏧 IP节点挖矿系统", reply_markup=main_menu())

@bot.message_handler(func=lambda msg: True)
def handle_user(message):
    uid = message.from_user.id
    text = message.text.strip()
    user = create_user(uid)

    if text == "🚀 申请挖矿权限":
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("UPDATE users SET mining_status='applied' WHERE user_id=?", (uid,))
        conn.commit()
        conn.close()
        bot.send_message(uid, "✅ 申请已提交，等待管理员审核")
        bot.send_message(ADMIN_ID, f"🔔 挖矿申请\n用户ID：{uid}\n矿工ID：{user[1]}")

    elif text == "⛏️ 开始挖矿":
        if user[3] != "approved":
            bot.send_message(uid, "❌ 请先申请并等待管理员通过")
            return
        add = random.randint(1, 88)
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("UPDATE users SET power=power+? WHERE user_id=?", (add, uid))
        conn.commit()
        conn.close()
        bot.send_message(uid, f"✅ 挖矿成功｜助力值 +{add}")

    elif text == "👤 我的信息":
        status_map = {"none": "未申请", "applied": "待审核", "approved": "已开通"}
        show_status = status_map.get(user[3], "未知")
        bot.send_message(uid, f"🆔 矿工ID：{user[1]}\n⚡ 助力值：{user[2]}\n✅ 挖矿权限：{show_status}")

# ==================== 管理员：回复 通过 / 不通过 ====================
@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID)
def admin_reply(message):
    txt = message.text.strip()
    if txt not in ["通过", "不通过"]:
        return

    try:
        prev_msg = bot.get_chat_message(ADMIN_ID, message.message_id - 1)
        target_uid = None
        for line in prev_msg.text.split("\n"):
            if "用户ID：" in line:
                target_uid = int(line.replace("用户ID：", "").strip())
                break
        if target_uid is None:
            bot.reply_to(message, "❌ 未找到申请消息")
            return
    except:
        bot.reply_to(message, "❌ 处理失败，请在收到申请后直接回复")
        return

    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    if txt == "通过":
        c.execute("UPDATE users SET mining_status='approved' WHERE user_id=?", (target_uid,))
        bot.reply_to(message, f"✅ 用户{target_uid} 已通过，可直接挖矿")
    else:
        c.execute("UPDATE users SET mining_status='applied' WHERE user_id=?", (target_uid,))
        bot.reply_to(message, f"❌ 用户{target_uid} 已驳回")
    conn.commit()
    conn.close()

# ==================== 启动 ====================
if __name__ == "__main__":
    bot.infinity_polling()
