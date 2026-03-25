import telebot
import sqlite3
import random
from datetime import datetime, timedelta

# ==================== 配置 ====================
BOT_TOKEN = "8727191543:AAEwOkZC8OMxIVEY7In8NQaOoXdGFQL551Q"
ADMIN_ID = 8256055083
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# 管理员临时选中的用户
admin_current_uid = {}

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
        mining_apply INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cooldown (
        user_id INTEGER, coin TEXT, end_time TEXT,
        PRIMARY KEY (user_id, coin)
    )''')
    conn.commit()
    conn.close()

# ==================== 工具函数 ====================
def check_ban_and_reply(message):
    uid = message.from_user.id
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT is_banned FROM users WHERE user_id=?", (uid,))
    res = c.fetchone()
    conn.close()
    if res and res[0] == 1:
        bot.send_message(message.chat.id, "⚠️ 出错请联系客服")
        return True
    return False

def gen_miner_id():
    return ''.join(random.choices("0123456789", k=8))

def get_user(uid, username=None):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    user = c.fetchone()
    if not user:
        mid = gen_miner_id()
        c.execute('''INSERT INTO users 
            (user_id, username, miner_id) VALUES (?,?,?)''',
            (uid, username, mid))
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        user = c.fetchone()
    conn.close()
    return user

def update_user(uid, field, value):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, uid))
    conn.commit()
    conn.close()

def add_user_data(uid, field, value):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field}={field}+? WHERE user_id=?", (value, uid))
    conn.commit()
    conn.close()

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
def start(message):
    if check_ban_and_reply(message):
        return
    uid = message.from_user.id
    uname = message.from_user.username
    u = get_user(uid, uname)
    text = f"""
<b>🚀 IP节点挖矿机器人</b>
🆔 矿工ID：<code>{u[2]}</code>
💰 TRX：{u[3]:.1f}
🪙 COIN：{u[4]}
📈 助力值：{u[5]}
"""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "👤个人中心")
def profile(message):
    if check_ban_and_reply(message):
        return
    uid = message.from_user.id
    u = get_user(uid)
    text = f"""
<b>👤 个人中心</b>
矿工ID：<code>{u[2]}</code>
昵称：{u[1] or '无'}
TRX：{u[3]:.1f}
COIN：{u[4]}
助力值：{u[5]}
累计空投：{u[8]} CNY
"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🔄回户")
def huihu(message):
    if check_ban_and_reply(message):
        return
    uid = message.from_user.id
    u = get_user(uid)
    if u[3] < 2:
        bot.send_message(message.chat.id, "❌ 回户失败，请联系客服")
        return
    add_user_data(uid, "trx", -2)
    u2 = get_user(uid)
    bot.send_message(message.chat.id, f"✅ 回户成功\n剩余TRX：{u2[3]:.1f}")

@bot.message_handler(func=lambda m: m.text == "🧧区块链空投")
def airdrop(message):
    if check_ban_and_reply(message):
        return
    uid = message.from_user.id
    u = get_user(uid)
    today = datetime.now().strftime("%Y-%m-%d")
    if u[6] == today:
        bot.send_message(message.chat.id, "❌ 今日已领取空投")
        return
    day = u[7] + 1
    if day == 5:
        amount = 2000
    else:
        amount = random.randint(20, 300)
    update_user(uid, "last_airdrop", today)
    update_user(uid, "air_day", day)
    add_user_data(uid, "air_total", amount)
    text = f"""
🧧 区块链空投
已领取：{amount} CNY
每日限领一次
"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📝申请挖矿权限")
def apply_mining(message):
    if check_ban_and_reply(message):
        return
    uid = message.from_user.id
    u = get_user(uid)
    if u[9] == 2:
        bot.send_message(message.chat.id, "✅ 已拥有挖矿权限")
        return
    if u[9] == 1:
        bot.send_message(message.chat.id, "⏳ 申请已提交，等待管理员审核")
        return
    update_user(uid, "mining_apply", 1)
    bot.send_message(message.chat.id, "📤 申请已提交")
    bot.send_message(ADMIN_ID, f"🔔 新挖矿申请\n用户ID：{uid}\n用户名：{u[1]}")

@bot.message_handler(func=lambda m: m.text == "⛏ IP节点挖矿")
def mining_info(message):
    if check_ban_and_reply(message):
        return
    uid = message.from_user.id
    u = get_user(uid)
    if u[9] == 0:
        bot.send_message(message.chat.id, "❌ 请先申请挖矿权限")
    elif u[9] == 1:
        bot.send_message(message.chat.id, "⏳ 审核中，请等待管理员通过")
    elif u[9] == 2:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🚀 开始辅助")
        bot.send_message(message.chat.id, "<b>🔍 节点挖矿</b>\n算力越强，奖励越多。", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 开始辅助")
def show_coins(message):
    if check_ban_and_reply(message):
        return
    uid = message.from_user.id
    u = get_user(uid)
    if u[9] != 2:
        bot.send_message(message.chat.id, "❌ 无挖矿权限")
        return
    coins = ["LISTA","ULT","MATHER","NEXG","PEW","PARAM",
             "JENNER","TREMP","ALU","MON","NIM","MAGA"]
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for c in coins:
        markup.add(c)
    bot.send_message(message.chat.id, "⚡ 选择币种", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["LISTA","ULT","MATHER","NEXG","PEW","PARAM",
                                               "JENNER","TREMP","ALU","MON","NIM","MAGA"])
def do_help(message):
    if check_ban_and_reply(message):
        return
    uid = message.from_user.id
    coin = message.text
    now = datetime.now()
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT end_time FROM cooldown WHERE user_id=? AND coin=?", (uid, coin))
    res = c.fetchone()
    if res:
        end = datetime.fromisoformat(res[0])
        if now < end:
            sec = int((end - now).total_seconds())
            m = sec // 60
            s = sec % 60
            bot.send_message(message.chat.id, f"⏳ 冷却中：{m}分{s}秒")
            conn.close()
            return
    add = random.randint(1, 88)
    add_user_data(uid, "power", add)
    end_t = (now + timedelta(minutes=random.randint(1,5))).isoformat()
    c.execute("REPLACE INTO cooldown (user_id, coin, end_time) VALUES (?,?,?)",
              (uid, coin, end_t))
    conn.commit()
    conn.close()
    u = get_user(uid)
    text = f"""
✅ 辅助成功
获得助力值：+{add}
当前总助力值：{u[5]}
"""
    bot.send_message(message.chat.id, text)

# ==================== 链接按钮 ====================
@bot.message_handler(func=lambda m: m.text == "📌ip挖矿频道")
def link1(message):
    bot.send_message(message.chat.id, "https://t.me/+8eM4xNGNMlgwNjRh")
@bot.message_handler(func=lambda m: m.text == "📋集团介绍")
def link2(message):
    bot.send_message(message.chat.id, "https://t.me/+8eM4xNGNMlgwNjRh")
@bot.message_handler(func=lambda m: m.text == "📊结算记录")
def link3(message):
    bot.send_message(message.chat.id, "https://t.me/+9tgv3ibhiw40NDdh")
@bot.message_handler(func=lambda m: m.text == "📢回户播报")
def link4(message):
    bot.send_message(message.chat.id, "https://t.me/+9tgv3ibhiw40NDdh")

# ==================== 用户指令 ====================
@bot.message_handler(func=lambda m: m.text == "8238")
def cmd8238(message):
    if check_ban_and_reply(message): return
    add_user_data(message.from_user.id, "trx", 100)
    u = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"✅ 获得100 TRX\n当前：{u[3]:.1f}")

@bot.message_handler(func=lambda m: m.text == "823823")
def cmd823823(message):
    if check_ban_and_reply(message): return
    u = get_user(message.from_user.id)
    if u[5] < 100:
        bot.send_message(message.chat.id, "❌ 助力不足")
        return
    add_user_data(message.from_user.id, "power", -100)
    bot.send_message(message.chat.id, "✅ 扣除100助力")

@bot.message_handler(func=lambda m: m.text == "668")
def cmd668(message):
    if check_ban_and_reply(message): return
    u = get_user(message.from_user.id)
    if u[5] < 50:
        bot.send_message(message.chat.id, "❌ 助力不足")
        return
    add_user_data(message.from_user.id, "power", -50)
    bot.send_message(message.chat.id, "✅ 扣除50助力")

# ==================== 管理员后台 ====================
def admin_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "👥 所有用户", "📄 选择操作用户",
        "💰 +50 TRX", "💰 +100 TRX", "💰 +200 TRX",
        "💰 -50 TRX", "💰 -100 TRX", "💰 -200 TRX",
        "⚡ +500 助力", "⚡ +1000 助力",
        "⚡ -500 助力", "⚡ -1000 助力",
        "🚫 封禁该用户", "✅ 解封该用户",
        "🔁 重置该用户", "📋 挖矿审核",
        "🔙 返回主菜单"
    )
    return markup

@bot.message_handler(commands=['admin'])
def open_admin(message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_current_uid[ADMIN_ID] = None
    bot.send_message(message.chat.id, "🔧 管理员后台", reply_markup=admin_menu())

def set_current_user(message):
    try:
        uid = int(message.text)
        admin_current_uid[ADMIN_ID] = uid
        bot.send_message(ADMIN_ID, f"✅ 已选择用户：{uid}")
    except:
        bot.send_message(ADMIN_ID, "❌ ID错误")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_action(message):
    t = message.text
    aid = ADMIN_ID
    cuid = admin_current_uid.get(aid)

    if t == "👥 所有用户":
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id,username,trx,power,is_banned FROM users")
        users = c.fetchall()
        conn.close()
        if not users:
            bot.send_message(aid, "暂无用户")
            return
        txt = "📋 用户列表\n"
        for u in users:
            ban = "❌封禁" if u[4]==1 else "✅正常"
            txt += f"\nID:{u[0]} | {u[1] or '无'} | TRX:{u[2]:.1f} | 助力:{u[3]} | {ban}\n"
        bot.send_message(aid, txt)

    elif t == "📄 选择操作用户":
        msg = bot.send_message(aid, "输入用户ID：")
        bot.register_next_step_handler(msg, set_current_user)

    elif t == "💰 +50 TRX":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"trx",50)
        bot.send_message(aid,"✅ +50 TRX")
    elif t == "💰 +100 TRX":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"trx",100)
        bot.send_message(aid,"✅ +100 TRX")
    elif t == "💰 +200 TRX":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"trx",200)
        bot.send_message(aid,"✅ +200 TRX")
    elif t == "💰 -50 TRX":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"trx",-50)
        bot.send_message(aid,"✅ -50 TRX")
    elif t == "💰 -100 TRX":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"trx",-100)
        bot.send_message(aid,"✅ -100 TRX")
    elif t == "💰 -200 TRX":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"trx",-200)
        bot.send_message(aid,"✅ -200 TRX")

    elif t == "⚡ +500 助力":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"power",500)
        bot.send_message(aid,"✅ +500 助力")
    elif t == "⚡ +1000 助力":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"power",1000)
        bot.send_message(aid,"✅ +1000 助力")
    elif t == "⚡ -500 助力":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"power",-500)
        bot.send_message(aid,"✅ -500 助力")
    elif t == "⚡ -1000 助力":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        add_user_data(cuid,"power",-1000)
        bot.send_message(aid,"✅ -1000 助力")

    elif t == "🚫 封禁该用户":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        update_user(cuid,"is_banned",1)
        bot.send_message(aid,"🚫 已封禁")
    elif t == "✅ 解封该用户":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        update_user(cuid,"is_banned",0)
        bot.send_message(aid,"✅ 已解封")

    elif t == "🔁 重置该用户":
        if not cuid: bot.send_message(aid,"❌先选用户");return
        update_user(cuid,"trx",2.0)
        update_user(cuid,"coin",0)
        update_user(cuid,"power",0)
        update_user(cuid,"mining_apply",0)
        update_user(cuid,"is_banned",0)
        bot.send_message(aid,"🔁 已重置")

    elif t == "📋 挖矿审核":
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id,username FROM users WHERE mining_apply=1")
        apps = c.fetchall()
        conn.close()
        if not apps:
            bot.send_message(aid,"✅ 暂无申请")
            return
        txt = "🔍 待审核：\n"
        for a in apps:
            txt += f"ID:{a[0]} | {a[1] or '无'}\n"
        txt += "\n通过：/allow 用户ID"
        bot.send_message(aid, txt)

    elif t == "🔙 返回主菜单":
        bot.send_message(aid, "✅ 返回主菜单", reply_markup=main_menu())

@bot.message_handler(commands=['allow'])
def allow_mining(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(message.text.split()[1])
        update_user(uid,"mining_apply",2)
        bot.send_message(ADMIN_ID,"✅ 已通过")
        bot.send_message(uid,"🎉 你的挖矿申请已通过")
    except:
        bot.send_message(ADMIN_ID,"格式：/allow 用户ID")

# ==================== 启动 ====================
if __name__ == "__main__":
    init_db()
    print("✅ 机器人已启动")
    bot.infinity_polling()
