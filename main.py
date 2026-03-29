import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
)

# ===================== 配置 =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN:
    raise Exception("请配置 BOT_TOKEN 环境变量")

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
        ip_status TEXT DEFAULT "none",  # none / pending / approved
        air_drop_time TEXT DEFAULT "",
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

init_db()

# ===================== 数据库工具 =====================
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

# ===================== 主菜单 =====================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("⛏️ IP 节点挖矿", callback_data="mining_panel")],
        [InlineKeyboardButton("🔗 绑定 IP 挖矿", callback_data="bind_ip")],
        [InlineKeyboardButton("🔄 申请回户", callback_data="apply_back")],
        [InlineKeyboardButton("🧧 每日空投", callback_data="daily_air")],
        [InlineKeyboardButton("👤 我的资产", callback_data="my_asset")],
        [InlineKeyboardButton("📜 项目说明", callback_data="proj_info")],
        [InlineKeyboardButton("💬 联系客服", callback_data="contact_service")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===================== /start =====================
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    create_user(user.id, user.username)
    try:
        update.message.reply_text(
            f"👋 欢迎 {user.first_name}，IP 节点挖矿机器人已启动\n请选择功能：",
            reply_markup=main_menu()
        )
    except:
        pass

# ===================== 按钮处理 =====================
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    query.answer()

    user = get_user(user_id)

    if data == "mining_panel":
        panel = """
⛏️ 12 币种挖矿面板
BTC  0.0000
ETH  0.0000
TRX  0.0000
BNB  0.0000
SOL  0.0000
XRP  0.0000
ADA  0.0000
DOGE 0.0000
AVAX 0.0000
DOT  0.0000
LINK 0.0000
LTC  0.0000
        """
        query.edit_message_text(panel.strip(), reply_markup=main_menu())

    elif data == "bind_ip":
        query.edit_message_text("🔗 请直接发送你的 IP 地址，提交后等待管理员审核", reply_markup=main_menu())

    elif data == "my_asset":
        trx = user[2]
        power = user[3]
        ip_st = user[4] if user[4] else "未绑定"
        msg = f"👤 资产总览\nTRX：{trx}\n助力值：{power}\nIP：{ip_st}"
        query.edit_message_text(msg, reply_markup=main_menu())

    elif data == "daily_air":
        query.edit_message_text("🧧 每日空投 12:00 开放，敬请准时领取", reply_markup=main_menu())

    elif data == "apply_back":
        query.edit_message_text("🔄 回户申请已开放，请联系客服办理", reply_markup=main_menu())

    elif data == "proj_info":
        query.edit_message_text("📜 IP 节点挖矿项目：通过贡献节点流量获得稳定收益", reply_markup=main_menu())

    elif data == "contact_service":
        query.edit_message_text("💬 客服：@fcff88", reply_markup=main_menu())

# ===================== 接收 IP =====================
def receive_ip(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if len(text) < 7 or "." not in text:
        update.message.reply_text("❌ 格式不正确，请发送合法 IP 地址")
        return

    conn = sqlite3.connect("ip_mining.db")
    c = conn.cursor()
    c.execute("UPDATE users SET ip=?, ip_status='pending' WHERE user_id=?", (text, user_id))
    conn.commit()
    conn.close()

    update.message.reply_text("✅ IP 已提交，等待管理员审核")

    # 通知管理员
    try:
        context.bot.send_message(ADMIN_ID, f"🆕 用户 {user_id} 提交 IP：{text}")
    except:
        pass

# ===================== 管理员：同意绑定 =====================
def admin_agree(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ 无权限")
        return
    try:
        target_id = int(context.args[0])
        conn = sqlite3.connect("ip_mining.db")
        c = conn.cursor()
        c.execute("UPDATE users SET ip_status='approved' WHERE user_id=?", (target_id,))
        conn.commit()
        conn.close()
        update.message.reply_text(f"✅ 已同意用户 {target_id} 的 IP 绑定")
    except:
        update.message.reply_text("用法：/agree 用户ID")

# ===================== 管理员：加 TRX =====================
def add_trx(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ 无权限")
        return
    try:
        target_id = int(context.args[0])
        amount = float(context.args[1])
        conn = sqlite3.connect("ip_mining.db")
        c = conn.cursor()
        c.execute("UPDATE users SET trx = trx + ? WHERE user_id=?", (amount, target_id))
        conn.commit()
        conn.close()
        update.message.reply_text(f"✅ 已给 {target_id} 增加 {amount} TRX")
    except:
        update.message.reply_text("用法：/add_trx 用户ID 数量")

# ===================== 启动机器人 =====================
def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("agree", admin_agree))
    dp.add_handler(CommandHandler("add_trx", add_trx))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, receive_ip))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
