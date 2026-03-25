import telebot
import sqlite3
import random
from datetime import datetime, timedelta

# 记录用户挖矿次数，实现递增冷却
user_mining_counts = {}

# ==================== 配置区 ====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = 8256055083
MINING_COOLDOWN = 60

# 12个挖矿币种
COIN_LIST = [
    "BTC", "ETH", "SOL", "BNB", "ADA", "AVAX",
    "DOT", "LINK", "MATIC", "ULT", "LISTA", "TRX"
]

# ==================== 数据库初始化 ====================
def init_db():
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        miner_id TEXT UNIQUE,
        trx REAL DEFAULT 2.0,
        power INTEGER DEFAULT 0,
        air_total INTEGER DEFAULT 0,
        air_day INTEGER DEFAULT 0,
        last_air TEXT DEFAULT "",
        mining_status INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS hu_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        year_month TEXT,
        create_time TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS cooldown (
        user_id INTEGER,
        coin TEXT,
        expire TEXT,
        PRIMARY KEY (user_id, coin)
    )''')

    conn.commit()
    conn.close()

init_db()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# ==================== 工具函数 ====================
def get_user(uid):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    res = c.fetchone()
    conn.close()
    return res

def update_user_field(uid, field, value):
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, uid))
    conn.commit()
    conn.close()

def gen_miner_id():
    return str(random.randint(100000, 999999))

def check_ban(uid):
    user = get_user(uid)
    return user and user[9] == 1

def mining_cooldown(uid, coin):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT expire FROM cooldown WHERE user_id=? AND coin=?", (uid, coin))
    res = c.fetchone()

    mining_count = user_mining_counts.get(uid, 0)
    base_cool = random.randint(3, 30)
    inc_cool = mining_count * 2
    total_cool = min(base_cool + inc_cool, 60)

    if res:
        try:
            exp = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S")
            if datetime.now() < exp:
                remain = int((exp - datetime.now()).total_seconds() // 60) + 1
                conn.close()
                return True, remain
        except:
            pass

    exp_time = (datetime.now() + timedelta(minutes=total_cool)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("REPLACE INTO cooldown (user_id, coin, expire) VALUES (?,?,?)", (uid, coin, exp_time))
    conn.commit()
    conn.close()

    user_mining_counts[uid] = user_mining_counts.get(uid, 0) + 1
    return False, total_cool

# ==================== 用户菜单（只新增申请按钮，其他完全不变） ====================
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton("⛏️ IP节点挖矿"),
        telebot.types.KeyboardButton("🚀 申请算力权限"),  # 仅新增这一个科幻按钮
        telebot.types.KeyboardButton("🔄回户"),
        telebot.types.KeyboardButton("🧧区块链空投"),
        telebot.types.KeyboardButton("👤个人中心")
    )
    return markup

# ==================== 开始/注册（完全原样不动） ====================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    user = get_user(uid)
    if not user:
        mid = gen_miner_id()
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, username, miner_id) VALUES (?,?,?)",
                  (uid, message.from_user.username or "", mid))
        conn.commit()
        conn.close()
    bot.send_message(message.chat.id, "✅ 欢迎使用挖矿机器人", reply_markup=main_menu())

# ==================== 新增：用户点击申请算力权限 ====================
@bot.message_handler(func=lambda m: m.text == "🚀 申请算力权限")
def apply_mining_permission(message):
    uid = message.from_user.id
    if check_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 已被封禁")
        return
    user = get_user(uid)
    miner_id = user[2]
    # 发给管理员的科幻风格申请文案
    bot.send_message(ADMIN_ID,
        f"⚡ 新节点接入申请！\n矿工ID：{miner_id}\n用户ID：{uid}\n回复「通过 {miner_id}」激活算力权限")
    # 用户端科幻提示文案
    bot.send_message(message.chat.id,
        "🚀 算力权限申请已提交！\n你的节点正在排队接入主网...\n请等待管理员审核通过后，即可启动挖矿！")

# ==================== 新增：管理员审批「通过 矿工ID」 ====================
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text.startswith("通过 "))
def admin_approve_mining(message):
    try:
        cmd_part, miner_id = message.text.split(maxsplit=1)
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE miner_id=?", (miner_id,))
        res = c.fetchone()
        if not res:
            bot.send_message(message.chat.id, "❌ 该矿工ID不存在")
            conn.close()
            return
        target_uid = res[0]
        # 开通权限（mining_status=2 为你原有开通标准）
        c.execute("UPDATE users SET mining_status=2 WHERE miner_id=?", (miner_id,))
        conn.commit()
        conn.close()
        # 管理员成功文案
        bot.send_message(message.chat.id, f"✅ 节点 {miner_id} 已接入主网，算力权限激活成功！")
        # 用户通过通知文案
        bot.send_message(target_uid,
            f"✅ 算力权限已激活！\n矿工ID：{miner_id}\n你已成功接入IP节点网络，现在可以启动挖矿，获取算力收益！")
    except:
        bot.send_message(message.chat.id, "❌ 格式错误，请使用：通过 矿工ID")

# ==================== 个人中心（完全原样不动） ====================
@bot.message_handler(func=lambda m: m.text == "👤个人中心")
def profile(message):
    uid = message.from_user.id
    if check_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 已被封禁")
        return
    u = get_user(uid)
    status = "已开通" if u[8] == 2 else "未开通"
    text = (f"👤个人信息\n"
            f"矿工ID：{u[2]}\n"
            f"TRX：{u[3]}\n"
            f"助力值：{u[4]}\n"
            f"累计CNY：{u[5]}\n"
            f"挖矿权限：{status}")
    bot.send_message(message.chat.id, text)

# ==================== 挖矿（完全原样不动） ====================
@bot.message_handler(func=lambda m: m.text == "⛏️ IP节点挖矿")
def mining_page(message):
    uid = message.from_user.id
    if check_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 已被封禁")
        return
    u = get_user(uid)
    if u[8] != 2:
        bot.send_message(message.chat.id, "❌ 请先申请挖矿权限")
        return
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [telebot.types.KeyboardButton(c) for c in COIN_LIST]
    buttons.append(telebot.types.KeyboardButton("🔙 返回主菜单"))
    markup.add(*buttons)
    bot.send_message(message.chat.id, "选择币种挖矿", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔙 返回主菜单")
def back_to_main(message):
    bot.send_message(message.chat.id, "✅ 已返回主菜单", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in COIN_LIST)
def do_mine(message):
    uid = message.from_user.id
    coin = message.text
    if check_ban(uid):
        return
    u = get_user(uid)
    if u[8] != 2:
        bot.send_message(message.chat.id, "❌ 无挖矿权限")
        return
    cd, rem = mining_cooldown(uid, coin)
    if cd:
        bot.send_message(message.chat.id, f"⏳ {coin} 冷却中，剩余{rem}分钟")
        return
    add_p = random.randint(1, 88)
    new_p = u[4] + add_p
    update_user_field(uid, "power", new_p)
    bot.send_message(message.chat.id, f"✅ 挖矿成功\n币种：{coin}\n获得助力值：+{add_p}\n当前：{new_p}\n⏳ 下次可挖：{rem} 分钟后")

# ==================== 回户（完全原样不动） ====================
@bot.message_handler(func=lambda m: m.text == "🔄回户")
def huihu(message):
    uid = message.from_user.id
    if check_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 已被封禁")
        return
    u = get_user(uid)
    if u[3] < 2:
        bot.send_message(message.chat.id, "❌ 回户失败，TRX不足")
        return
    new_trx = u[3] - 2
    update_user_field(uid, "trx", new_trx)
    ym = datetime.now().strftime("%Y-%m")
    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("INSERT INTO hu_records (user_id, amount, year_month, create_time) VALUES (?,?,?,?)",
              (uid, 2.0, ym, ct))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"✅ 回户成功\n剩余TRX：{new_trx}")

# ==================== 空投（完全原样不动） ====================
@bot.message_handler(func=lambda m: m.text == "🧧区块链空投")
def airdrop(message):
    uid = message.from_user.id
    if check_ban(uid):
        bot.send_message(message.chat.id, "⚠️ 已被封禁")
        return
    u = get_user(uid)
    today = datetime.now().strftime("%Y-%m-%d")
    if u[7] == today:
        bot.send_message(message.chat.id, "⏹️ 今日已领取")
        return
    day = u[6] + 1
    add = 50
    if day >= 5:
        add = 2000
        day = 1
    new_total = u[5] + add
    update_user_field(uid, "air_total", new_total)
    update_user_field(uid, "air_day", day)
    update_user_field(uid, "last_air", today)
    bot.send_message(message.chat.id, f"🧧 领取成功 +{add} CNY\n累计：{new_total}")

# ==================== 管理员命令（全部原样不动） ====================
@bot.message_handler(commands=['t200'])
def t200(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id, trx FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if not res:
            bot.send_message(message.chat.id, "❌ 无此用户")
            return
        uid, trx = res
        new_trx = trx + 200
        c.execute("UPDATE users SET trx=? WHERE user_id=?", (new_trx, uid))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ +200 TRX → {ident}")
    except:
        bot.send_message(message.chat.id, "用法：/t200 矿工ID/用户ID")

@bot.message_handler(commands=['p2000'])
def p2000(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id, power FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if not res:
            bot.send_message(message.chat.id, "❌ 无此用户")
            return
        uid, p = res
        if p < 2000:
            bot.send_message(message.chat.id, "❌ 助力不足")
            return
        new_p = p - 2000
        c.execute("UPDATE users SET power=? WHERE user_id=?", (new_p, uid))
        conn.commit()
        conn.close()
        bot.send_message(uid, "✅ 已成功回户")
        bot.send_message(message.chat.id, f"✅ -2000助力 → {ident}")
    except:
        bot.send_message(message.chat.id, "用法：/p2000 矿工ID/用户ID")

@bot.message_handler(commands=['p60'])
def p60(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id, power FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if not res:
            bot.send_message(message.chat.id, "❌ 无此用户")
            return
        uid, p = res
        if p < 60:
            bot.send_message(message.chat.id, "❌ 助力不足")
            return
        new_p = p - 60
        c.execute("UPDATE users SET power=? WHERE user_id=?", (new_p, uid))
        conn.commit()
        conn.close()
        bot.send_message(uid, "✅ 已成功回户")
        bot.send_message(message.chat.id, f"✅ -60助力 → {ident}")
    except:
        bot.send_message(message.chat.id, "用法：/p60 矿工ID/用户ID")

@bot.message_handler(commands=['p'])
def p_any(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident, amount = message.text.split()
        amount = int(amount)
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id, power FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if not res:
            bot.send_message(message.chat.id, "❌ 无此用户")
            conn.close()
            return
        uid, power = res
        if power < amount:
            bot.send_message(message.chat.id, "❌ 助力值不足")
            conn.close()
            return
        new_p = power - amount
        c.execute("UPDATE users SET power=? WHERE user_id=?", (new_p, uid))
        conn.commit()
        conn.close()
        bot.send_message(uid, f"✅ 系统已扣除您 {amount} 点助力值")
        bot.send_message(message.chat.id, f"✅ 成功 -{amount} 助力 → {ident}")
    except:
        bot.send_message(message.chat.id, "用法：/p 矿工ID 扣除数值")

@bot.message_handler(commands=['ban'])
def ban(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if not res:
            bot.send_message(message.chat.id, "❌ 无此用户")
            return
        uid = res[0]
        c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (uid,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ 已封禁 {ident}")
    except:
        bot.send_message(message.chat.id, "用法：/ban 矿工ID/用户ID")

@bot.message_handler(commands=['unban'])
def unban(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if not res:
            bot.send_message(message.chat.id, "❌ 无此用户")
            return
        uid = res[0]
        c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (uid,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ 已解封 {ident}")
    except:
        bot.send_message(message.chat.id, "用法：/unban 矿工ID/用户ID")

@bot.message_handler(commands=['open_mining'])
def open_mining(message):
    if message.from_user.id != 8256055083:
        return
    uid = message.from_user.id
    conn = sqlite3.connect("mining.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    user = c.fetchone()
    if not user:
        mid = str(random.randint(100000, 999999))
        c.execute("INSERT INTO users (user_id, username, miner_id, mining_status) VALUES (?,?,?,2)",
                  (uid, message.from_user.username or "", mid))
    else:
        c.execute("UPDATE users SET mining_status=2 WHERE user_id=?", (uid,))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, "✅ 你的挖矿权限已开通！")

@bot.message_handler(commands=['hu_month'])
def hu_month(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        ym = datetime.now().strftime("%Y-%m")
        conn = sqlite3.connect("mining.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if not res:
            bot.send_message(message.chat.id, "❌ 无此用户")
            return
        uid = res[0]
        c.execute("SELECT SUM(amount) FROM hu_records WHERE user_id=? AND year_month=?", (uid, ym))
        total = c.fetchone()[0] or 0.0
        conn.close()
        bot.send_message(message.chat.id, f"📊 {ident} 本月回户累计：{total} TRX")
    except:
        bot.send_message(message.chat.id, "用法：/hu_month 矿工ID/用户ID")

# ==================== 启动机器人（完全原样不动） ====================
bot.infinity_polling()
