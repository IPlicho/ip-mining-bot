import telebot
import sqlite3
import random
from datetime import datetime
from telebot import types
import os

# ==================== 配置區 ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CUSTOMER_SERVICE = "@fcff88"

# ==================== 資料庫初始化 ====================
def init_db():
    conn = sqlite3.connect("mining_pro.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        miner_id TEXT UNIQUE,
        trx REAL DEFAULT 2.0,
        power INTEGER DEFAULT 0,
        total_power INTEGER DEFAULT 0,
        air_today INTEGER DEFAULT 0,
        air_total INTEGER DEFAULT 0,
        air_hu_total INTEGER DEFAULT 0,
        power_hu_total INTEGER DEFAULT 0,
        trx_consumed_total REAL DEFAULT 0.0,
        mining_status INTEGER DEFAULT 0,
        user_func_enabled INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS apply_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        apply_type TEXT,
        status TEXT DEFAULT 'pending'
    )''')
    conn.commit()
    conn.close()

init_db()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ==================== 工具函式 ====================
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

def is_user_func_enabled(uid):
    u = get_user(uid)
    return u and (u[12] == 1)

# ==================== 選單 ====================
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⛏️ 開始IP節點挖礦", callback_data="start_mine"),
        types.InlineKeyboardButton("🔗 綁定IP挖礦", callback_data="apply_mining"),
        types.InlineKeyboardButton("🔄 申請回戶作業", callback_data="apply_hu"),
        types.InlineKeyboardButton("🧧 每日空投領取", callback_data="daily_air"),
        types.InlineKeyboardButton("👤 個人資產總覽", callback_data="profile"),
        types.InlineKeyboardButton("📜 項目資格說明書", callback_data="doc_1"),
        types.InlineKeyboardButton("💬 線上客服專區", callback_data="service"),
    )
    return markup

def mining_12coin_menu():
    markup = types.InlineKeyboardMarkup(row_width=3)
    coins = [
        ("BTC", "mine_btc"), ("ETH", "mine_eth"), ("TRX", "mine_trx"),
        ("USDT", "mine_usdt"), ("BNB", "mine_bnb"), ("SOL", "mine_sol"),
        ("ADA", "mine_ada"), ("DOGE", "mine_doge"), ("XRP", "mine_xrp"),
        ("DOT", "mine_dot"), ("AVAX", "mine_avax"), ("MATIC", "mine_matic")
    ]
    btns = [types.InlineKeyboardButton(f"🪙 {n}", callback_data=d) for n, d in coins]
    markup.add(*btns)
    markup.add(types.InlineKeyboardButton("🔙 返回主選單", callback_data="back_main"))
    return markup

def get_doc_page(page):
    docs = {
        1: "📜 項目說明書 · 第1頁/共4頁\n\n⚡️ IP節點挖礦助力機制說明\n\n在 t.me/IP_Mining_Bot 進行助力，即為區塊鏈網路貢獻設備算力與流量，提升節點驗證效率與網路安全性。\n\n系統將根據有效驗證行為，以助力值形式發放代幣激勵，助力值與收益直接掛鉤，累計越高回報越豐厚。\n\n此模式與比特幣挖礦原理同源，以行動裝置替代傳統礦機，大幅降低參與門檻，讓一般用戶便捷共享區塊鏈生態紅利。",
        2: "📜 項目說明書 · 第2頁/共4頁\n\n🔰 合法性與資格說明\n\n買幣、囤幣、挖礦、炒幣均不屬於違法，四大類皆屬於區塊鏈去中心化範疇。\n\n目前全世界尚無任何一條法律明確規範此類行為違法，因為區塊鏈的核心就是去中心化，不歸任何中心機構管轄。\n\n各國僅能實施境內監管規範，無法以法律判定挖礦行為犯罪，因此鏈上礦場收益高卻合法穩定。",
        3: "📜 項目說明書 · 第3頁/共4頁\n\n🏛 雲鼎資本集團 · 平台資格\n\n▪ 總部位於杜拜，業務覆蓋全球20餘國\n▪ 註冊資金逾90億美元\n▪ 國際專業團隊超過100人，技術專家占比40%\n▪ 擁有20項技術專利與國際權威資格認證\n▪ 區塊鏈布局通過美國貨幣監管體系審核\n▪ 服務TG用戶超過50000+\n\n集團深耕Web3.0、數位金融、分散式挖礦，生態完整安全。",
        4: "📜 項目說明書 · 第4頁/共4頁\n\n📈 產業背景與發展歷程\n\n近年產業擔保環境波動，多家機構相繼退出，IP節點挖礦堅持穩健營運與安全保障。\n\n2018年：進駐Telegram平台\n2021年：完成正規擔保合作（金盾擔保）\n2022年：助力挖礦模式正式上線\n2024年：生態成熟，獲得多方資本支持\n2025年：持續低門檻、低風險、易上手營運\n\n堅持三低原則：低門檻、低風險、低難度。"
    }
    return docs.get(page, docs[1])

def doc_nav_markup(current):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = []
    if current > 1:
        btns.append(types.InlineKeyboardButton("⬅️ 上一頁", callback_data=f"doc_{current-1}"))
    if current < 4:
        btns.append(types.InlineKeyboardButton("下一頁 ➡️", callback_data=f"doc_{current+1}"))
    markup.add(*btns)
    markup.add(types.InlineKeyboardButton("🔙 返回主選單", callback_data="back_main"))
    return markup

# ==================== 按鈕回調 ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handle(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data
    allowed_always = ["back_main", "apply_mining", "service", "doc_1", "doc_2", "doc_3", "doc_4"]
    func_enabled = is_user_func_enabled(uid)
    if not func_enabled and data not in allowed_always:
        bot.answer_callback_query(call.id, "🔒 功能未開放，請聯繫管理員開通", show_alert=True)
        return
    if data == "back_main":
        bot.edit_message_text(chat_id=cid, message_id=mid, text="🏧 IP節點挖礦系統｜專業交易所版", reply_markup=main_menu())
    elif data.startswith("doc_"):
        page = int(data.split("_")[1])
        bot.edit_message_text(chat_id=cid, message_id=mid, text=get_doc_page(page), reply_markup=doc_nav_markup(page))
    elif data == "service":
        text = f"💬 線上客服專區\n\n📩 官方唯一客服：`{CUSTOMER_SERVICE}`\n⚠️ 請勿相信其他陌生帳號"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 返回主選單", callback_data="back_main"))
        bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=markup, parse_mode="Markdown")
    elif data == "profile":
        u = get_user(uid)
        info = f"👤 個人資產總覽\n\n🆔 礦工ID：`{u[2]}`\n💰 TRX：`{u[3]:.2f}`\n⚡ 助力值：`{u[4]}`\n📊 累計助力：`{u[5]}`\n🧧 累計空投：`{u[7]}`"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 返回主選單", callback_data="back_main"))
        bot.edit_message_text(chat_id=cid, message_id=mid, text=info, reply_markup=markup, parse_mode="Markdown")
    elif data == "apply_mining":
        u = get_user(uid)
        if u[10] == 2:
            bot.answer_callback_query(call.id, "✅ 您已完成IP綁定", show_alert=True)
            return
        update_user(uid, "mining_status", 1)
        bot.answer_callback_query(call.id, f"🆔 您的ID {uid} 已申請綁定IP", show_alert=True)
        bot.send_message(ADMIN_ID, f"🔔 IP綁定申請\n礦工ID：{u[2]}\n用戶ID：{uid}\n指令：/agree {uid} 或 /refuse {uid}")
    elif data == "start_mine":
        u = get_user(uid)
        if u[10] != 2:
            bot.answer_callback_query(call.id, "❌ 請先完成IP綁定", show_alert=True)
            return
        bot.edit_message_text(chat_id=cid, message_id=mid, text="⛏️ 選擇幣種開始挖礦（點擊即挖）", reply_markup=mining_12coin_menu())
    elif data.startswith("mine_"):
        u = get_user(uid)
        add = random.randint(1, 88)
        update_user(uid, "power", u[4] + add)
        update_user(uid, "total_power", u[5] + add)
        bot.answer_callback_query(call.id, f"✅ 挖礦成功｜助力值 +{add}", show_alert=True)
    elif data == "apply_hu":
        u = get_user(uid)
        if u[3] < 2:
            bot.answer_callback_query(call.id, "❌ TRX不足，操作失敗", show_alert=True)
            return
        bot.send_message(ADMIN_ID, f"🔔 回戶申請\n礦工ID：{u[2]}\n用戶ID：{uid}")
        bot.answer_callback_query(call.id, "✅ 回戶申請已提交", show_alert=True)
    elif data == "daily_air":
        u = get_user(uid)
        if u[6] >= 1:
            bot.answer_callback_query(call.id, "✅ 今日空投已領", show_alert=True)
            return
        update_user(uid, "air_today", 1)
        update_user(uid, "air_total", u[7] + 50)
        bot.answer_callback_query(call.id, "🧧 領取成功 +50 空投", show_alert=True)

# ==================== /start ====================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not get_user(uid):
        mid = gen_miner_id()
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, username, miner_id, user_func_enabled) VALUES (?,?,?,0)",
                  (uid, message.from_user.username or "", mid))
        conn.commit()
        conn.close()
    bot.send_message(message.chat.id, "🏧 IP節點挖礦系統｜專業交易所版", reply_markup=main_menu())

# ==================== 管理員指令 ====================
@bot.message_handler(commands=['agree'])
def agree_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        update_user(uid, "mining_status", 2)
        bot.send_message(uid, "✅ 您的IP挖礦綁定已通過審核")
        bot.reply_to(message, "✅ 審核通過")
    except:
        bot.reply_to(message, "格式：/agree 用戶ID")

@bot.message_handler(commands=['refuse'])
def refuse_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        update_user(uid, "mining_status", 0)
        bot.send_message(uid, "❌ 您的IP綁定申請被駁回")
        bot.reply_to(message, "✅ 已駁回")
    except:
        bot.reply_to(message, "格式：/refuse 用戶ID")

@bot.message_handler(commands=['info'])
def user_info(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        u = c.fetchone()
        conn.close()
        if not u:
            bot.reply_to(message, "❌ 查無此用戶")
            return
        info = f"👤 用戶資料\n用戶ID：{u[0]}\n礦工ID：{u[2]}\nTRX：{u[3]:.2f}\n助力：{u[4]}\n累計空投：{u[7]}\n綁定：{'已開通' if u[10]==2 else '未開通'}\n功能：{'全部開放' if u[12]==1 else '僅3按鈕'}"
        bot.reply_to(message, info)
    except:
        bot.reply_to(message, "格式：/info 礦工ID或用戶ID")

@bot.message_handler(commands=['user_func_on'])
def user_func_on(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        update_user(uid, "user_func_enabled", 1)
        bot.send_message(uid, "✅ 您已可以使用全部功能")
        bot.reply_to(message, "✅ 已開放該用戶全部功能")
    except:
        bot.reply_to(message, "格式：/user_func_on 用戶ID")

@bot.message_handler(commands=['user_func_off'])
def user_func_off(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        update_user(uid, "user_func_enabled", 0)
        bot.reply_to(message, "✅ 已恢復僅3按鈕限制")
    except:
        bot.reply_to(message, "格式：/user_func_off 用戶ID")

@bot.message_handler(commands=['add_trx'])
def add_trx(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident, num = message.text.split()
        num = float(num)
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("SELECT user_id, trx FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if res:
            c.execute("UPDATE users SET trx=? WHERE user_id=?", (res[1] + num, res[0]))
            conn.commit()
            bot.reply_to(message, f"✅ 已增加 {num} TRX")
        conn.close()
    except:
        bot.reply_to(message, "格式：/add_trx 礦工ID 數量")

@bot.message_handler(commands=['add_power'])
def add_power(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident, num = message.text.split()
        num = int(num)
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("SELECT user_id, power, total_power FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if res:
            c.execute("UPDATE users SET power=?, total_power=? WHERE user_id=?", (res[1] + num, res[2] + num, res[0]))
            conn.commit()
            bot.reply_to(message, f"✅ 已增加 {num} 助力值")
        conn.close()
    except:
        bot.reply_to(message, "格式：/add_power 礦工ID 數量")

@bot.message_handler(commands=['add_airdrop'])
def add_airdrop(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident, num = message.text.split()
        num = int(num)
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("SELECT user_id, air_total FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if res:
            c.execute("UPDATE users SET air_total=? WHERE user_id=?", (res[1] + num, res[0]))
            conn.commit()
            bot.reply_to(message, f"✅ 已增加 {num} 空投紅包")
        conn.close()
    except:
        bot.reply_to(message, "格式：/add_airdrop 礦工ID 數量")

@bot.message_handler(func=lambda msg: True)
def any_msg(message):
    bot.send_message(message.chat.id, "🔹 請使用按鈕操作", reply_markup=main_menu())

if __name__ == "__main__":
    bot.infinity_polling()
