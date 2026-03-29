import telebot
import sqlite3
import random
from datetime import datetime
from telebot import types

# ==================== 配置區 ====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = 8256055083
CUSTOMER_SERVICE = "@fcff88"

# 全域挖礦開關 (管理員專用)
GLOBAL_MINING_ENABLED = True

# ==================== 資料庫初始化 (全新欄位) ====================
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
        mining_status INTEGER DEFAULT 0,  -- 0未申請 1審核中 2已開通
        mining_paused INTEGER DEFAULT 0,  -- 0正常 1單人暫停
        is_banned INTEGER DEFAULT 0
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

def check_ban(uid):
    u = get_user(uid)
    return u and (u[11] == 1 or u[10] == 1)

# ==================== 豪華交易所風格選單 ====================
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⛏️ 開始IP節點挖礦", callback_data="start_mine"),
        types.InlineKeyboardButton("🚀 申請挖礦權限", callback_data="apply_mining"),
        types.InlineKeyboardButton("🔄 申請回戶作業", callback_data="apply_hu"),
        types.InlineKeyboardButton("🧧 每日空投領取", callback_data="daily_air"),
        types.InlineKeyboardButton("👤 個人資產總覽", callback_data="profile"),
        types.InlineKeyboardButton("📜 項目資格說明書", callback_data="doc_1"),
        types.InlineKeyboardButton("💬 線上客服專區", callback_data="service"),
    )
    return markup

# ==================== 4頁項目資料包 (繁體完整內容) ====================
def get_doc_page(page):
    docs = {
        1: (
            "📜 項目說明書 · 第1頁/共4頁\n\n"
            "⚡️ IP節點挖礦助力機制說明\n\n"
            "在 t.me/IP_Mining_Bot 進行助力，即為區塊鏈網路貢獻設備算力與流量，\n"
            "提升節點驗證效率與網路安全性。\n\n"
            "系統將根據有效驗證行為，以助力值形式發放代幣激勵，\n"
            "助力值與收益直接掛鉤，累計越高回報越豐厚。\n\n"
            "此模式與比特幣挖礦原理同源，以行動裝置替代傳統礦機，\n"
            "大幅降低參與門檻，讓一般用戶便捷共享區塊鏈生態紅利。"
        ),
        2: (
            "📜 項目說明書 · 第2頁/共4頁\n\n"
            "🔰 合法性與資格說明\n\n"
            "買幣、囤幣、挖礦、炒幣均不屬於違法，\n"
            "四大類皆屬於區塊鏈去中心化範疇。\n\n"
            "目前全世界尚無任何一條法律明確規範此類行為違法，\n"
            "因為區塊鏈的核心就是去中心化，不歸任何中心機構管轄。\n\n"
            "各國僅能實施境內監管規範，無法以法律判定挖礦行為犯罪，\n"
            "因此鏈上礦場收益高卻合法穩定。"
        ),
        3: (
            "📜 項目說明書 · 第3頁/共4頁\n\n"
            "🏛 雲鼎資本集團 · 平台資格\n\n"
            "▪ 總部位於杜拜，業務覆蓋全球20餘國\n"
            "▪ 註冊資金逾90億美元\n"
            "▪ 國際專業團隊超過100人，技術專家占比40%\n"
            "▪ 擁有20項技術專利與國際權威資格認證\n"
            "▪ 區塊鏈布局通過美國貨幣監管體系審核\n"
            "▪ 服務TG用戶超過50000+\n\n"
            "集團深耕Web3.0、數位金融、分散式挖礦，生態完整安全。"
        ),
        4: (
            "📜 項目說明書 · 第4頁/共4頁\n\n"
            "📈 產業背景與發展歷程\n\n"
            "近年產業擔保環境波動，多家機構相繼退出，\n"
            "IP節點挖礦堅持穩健營運與安全保障。\n\n"
            "2018年：進駐Telegram平台\n"
            "2021年：完成正規擔保合作（金盾擔保）\n"
            "2022年：助力挖礦模式正式上線\n"
            "2024年：生態成熟，獲得多方資本支持\n"
            "2025年：持續低門檻、低風險、易上手營運\n\n"
            "堅持三低原則：低門檻、低風險、低難度。"
        )
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

# ==================== 回覆按鈕處理 ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handle(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    mid = call.message.message_id
    if check_ban(uid):
        bot.answer_callback_query(call.id, "⚠️ 您已被限制使用", show_alert=True)
        return
    # 返回主選單
    if call.data == "back_main":
        text = "🏧 IP節點挖礦系統｜專業交易所版\n\n請選擇功能項目"
        bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=main_menu(), parse_mode="Markdown")
    # 文件翻頁
    elif call.data.startswith("doc_"):
        page = int(call.data.split("_")[1])
        text = get_doc_page(page)
        bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=doc_nav_markup(page))
    # 客服專區
    elif call.data == "service":
        text = (
            "💬 線上客服專區\n\n"
            "📩 官方唯一客服帳號:\n"
            f"`{CUSTOMER_SERVICE}`\n\n"
            "⚠️ 重要提醒\n"
            "平台僅此唯一客服，請勿相信其他陌生帳號，\n"
            "避免造成資產損失。"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 返回主選單", callback_data="back_main"))
        bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=markup, parse_mode="Markdown")
    # 個人資產
    elif call.data == "profile":
        u = get_user(uid)
        status = "已開通" if u[11] == 2 else "未開通/審核中"
        pause = "已暫停" if u[12] == 1 else "正常"
        info = (
            "👤 個人資產總覽\n\n"
            f"🆔 礦工ID：`{u[2]}`\n"
            f"💰 TRX 餘額：`{u[3]:.2f}`\n"
            f"⚡ 目前助力值：`{u[4]}`\n"
            f"📊 累計助力值：`{u[5]}`\n"
            f"🧧 今日空投：`{u[6]}`\n"
            f"🏆 累計空投：`{u[7]}`\n"
            f"🔁 空投累計回戶：`{u[8]}`\n"
            f"🔁 助力累計回戶：`{u[9]}`\n"
            f"💸 累計消耗TRX：`{u[10]:.2f}`\n"
            f"🔓 挖礦權限：`{status}`\n"
            f"🚦 挖礦狀態：`{pause}`"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 返回主選單", callback_data="back_main"))
        bot.edit_message_text(chat_id=cid, message_id=mid, text=info, reply_markup=markup, parse_mode="Markdown")
    # 申請挖礦權限
    elif call.data == "apply_mining":
        u = get_user(uid)
        if u[11] == 2:
            bot.answer_callback_query(call.id, "✅ 您已擁有挖礦權限", show_alert=True)
            return
        update_user(uid, "mining_status", 1)
        bot.send_message(ADMIN_ID, f"🔔 挖礦權限申請\n礦工ID：{u[2]}\n用戶ID：{uid}\n請回覆：/agree {uid} 或 /refuse {uid}")
        bot.answer_callback_query(call.id, "✅ 申請已提交，等待管理員審核", show_alert=True)
    # 開始挖礦
    elif call.data == "start_mine":
        global GLOBAL_MINING_ENABLED
        u = get_user(uid)
        if not GLOBAL_MINING_ENABLED:
            bot.answer_callback_query(call.id, "🚧 系統維護中，全域挖礦暫停", show_alert=True)
            return
        if u[12] == 1:
            bot.answer_callback_query(call.id, "🛑 您的挖礦權限已被管理員暫停", show_alert=True)
            return
        if u[11] != 2:
            bot.answer_callback_query(call.id, "❌ 請先申請並通過挖礦權限審核", show_alert=True)
            return
        add = random.randint(1, 88)
        new_p = u[4] + add
        total_p = u[5] + add
        update_user(uid, "power", new_p)
        update_user(uid, "total_power", total_p)
        bot.answer_callback_query(call.id, f"✅ 挖礦成功｜助力值 +{add}", show_alert=True)
    # 申請回戶
    elif call.data == "apply_hu":
        u = get_user(uid)
        bot.send_message(ADMIN_ID, f"🔔 回戶申請\n礦工ID：{u[2]}\n用戶ID：{uid}")
        bot.answer_callback_query(call.id, "✅ 回戶申請已提交，等待管理員處理", show_alert=True)
    # 每日空投
    elif call.data == "daily_air":
        u = get_user(uid)
        today = datetime.now().strftime("%Y-%m-%d")
        if u[6] >= 1:
            bot.answer_callback_query(call.id, "✅ 今日空投已領取", show_alert=True)
            return
        add_air = 50
        new_today = u[6] + 1
        new_total = u[7] + add_air
        update_user(uid, "air_today", new_today)
        update_user(uid, "air_total", new_total)
        bot.answer_callback_query(call.id, f"🧧 領取成功 +{add_air} 空投", show_alert=True)

# ==================== 開始指令 ====================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not get_user(uid):
        mid = gen_miner_id()
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, username, miner_id) VALUES (?,?,?)",
                  (uid, message.from_user.username or "", mid))
        conn.commit()
        conn.close()
    welcome = "🏧 IP節點挖礦系統｜專業交易所版\n\n歡迎使用，請以下方按鈕操作"
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu())

# ==================== 管理員指令 ====================
@bot.message_handler(commands=['agree'])
def agree_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        update_user(uid, "mining_status", 2)
        bot.send_message(uid, "✅ 您的挖礦權限申請已通過")
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
        bot.send_message(uid, "❌ 您的挖礦權限申請被駁回")
        bot.reply_to(message, "✅ 已駁回")
    except:
        bot.reply_to(message, "格式：/refuse 用戶ID")

@bot.message_handler(commands=['pause'])
def pause_single(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        update_user(uid, "mining_paused", 1)
        bot.reply_to(message, "✅ 已暫停該用戶挖礦")
    except:
        bot.reply_to(message, "格式：/pause 用戶ID")

@bot.message_handler(commands=['resume'])
def resume_single(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        uid = int(uid)
        update_user(uid, "mining_paused", 0)
        bot.reply_to(message, "✅ 已恢復該用戶挖礦")
    except:
        bot.reply_to(message, "格式：/resume 用戶ID")

@bot.message_handler(commands=['global_on'])
def global_on(message):
    if message.from_user.id != ADMIN_ID:
        return
    global GLOBAL_MINING_ENABLED
    GLOBAL_MINING_ENABLED = True
    bot.reply_to(message, "✅ 全域挖礦已開啟")

@bot.message_handler(commands=['global_off'])
def global_off(message):
    if message.from_user.id != ADMIN_ID:
        return
    global GLOBAL_MINING_ENABLED
    GLOBAL_MINING_ENABLED = False
    bot.reply_to(message, "✅ 全域挖礦已暫停")

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
        info = (
            "👤 用戶完整資料\n"
            f"用戶ID：{u[0]}\n"
            f"礦工ID：{u[2]}\n"
            f"TRX：{u[3]:.2f}\n"
            f"目前助力：{u[4]}\n"
            f"累計助力：{u[5]}\n"
            f"累計空投：{u[7]}\n"
            f"挖礦狀態：{'開通' if u[11]==2 else '未開通'}\n"
            f"單人暫停：{'是' if u[12]==1 else '否'}\n"
            f"封禁狀態：{'是' if u[13]==1 else '否'}"
        )
        bot.reply_to(message, info)
    except:
        bot.reply_to(message, "格式：/info 礦工ID 或 用戶ID")

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
        if not res:
            bot.reply_to(message, "❌ 無此用戶")
            conn.close()
            return
        new_trx = res[1] + num
        c.execute("UPDATE users SET trx=? WHERE user_id=?", (new_trx, res[0]))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ 已增加 {num} TRX")
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
        if not res:
            bot.reply_to(message, "❌ 無此用戶")
            conn.close()
            return
        new_p = res[1] + num
        new_tp = res[2] + num
        c.execute("UPDATE users SET power=?, total_power=? WHERE user_id=?", (new_p, new_tp, res[0]))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ 已增加 {num} 助力值")
    except:
        bot.reply_to(message, "格式：/add_power 礦工ID 數量")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if res:
            c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (res[0],))
            conn.commit()
            bot.reply_to(message, "✅ 已封禁")
        conn.close()
    except:
        bot.reply_to(message, "格式：/ban 礦工ID")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, ident = message.text.split()
        conn = sqlite3.connect("mining_pro.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id=? OR miner_id=?", (ident, ident))
        res = c.fetchone()
        if res:
            c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (res[0],))
            conn.commit()
            bot.reply_to(message, "✅ 已解封")
        conn.close()
    except:
        bot.reply_to(message, "格式：/unban 礦工ID")

# 無效文字導向選單
@bot.message_handler(func=lambda msg: True)
def any_msg(message):
    bot.send_message(message.chat.id, "🔹 請使用按鈕操作，勿直接輸入文字", reply_markup=main_menu())

# ==================== 啟動機器人 ====================
if __name__ == "__main__":
    bot.infinity_polling()
