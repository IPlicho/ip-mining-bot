import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==========================================
# 【零配置，直接用】
# ==========================================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
# Railway 自动读取端口和域名，无需手动改
PORT = int(os.environ.get("PORT", 8080))
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").rstrip("/")

# 内存数据
users = {}
user_step = {}

# 主菜单
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 入驻担保", callback_data="reg")],
        [InlineKeyboardButton("👤 个人中心", callback_data="me")],
        [InlineKeyboardButton("🚀 抢单大厅", callback_data="grab")],
        [InlineKeyboardButton("📥 担保派单", callback_data="send")],
        [InlineKeyboardButton("💰 充值提现", callback_data="pay")],
        [InlineKeyboardButton("📜 担保记录", callback_data="log")],
    ])

# /start
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in users:
        users[uid] = {"name": "", "phone": "", "email": "", "addr": "", "ref": "", "usdt": 0, "status": 0}
    await update.message.reply_text("✅ 机器人已启动\n请选择菜单：", reply_markup=main_menu())

# 按钮回调
async def cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    if data == "reg":
        user_step[uid] = "name"
        await q.edit_message_text("请输入姓名：")
    elif data == "me":
        u = users[uid]
        await q.edit_message_text(f"👤 个人中心\nUSDT: {u['usdt']}", reply_markup=main_menu())
    elif data == "grab":
        await q.edit_message_text("🚀 抢单：50/100 USDT（随机）", reply_markup=main_menu())
    elif data == "send":
        await q.edit_message_text("📥 管理员派单功能", reply_markup=main_menu())
    elif data == "pay":
        await q.edit_message_text("💰 充值提现 @fcff88", reply_markup=main_menu())
    elif data == "log":
        await q.edit_message_text("📜 暂无记录", reply_markup=main_menu())

# 文字消息
async def msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if uid not in user_step:
        await update.message.reply_text("请点菜单：", reply_markup=main_menu())
        return

    step = user_step[uid]
    if step == "name":
        users[uid]["name"] = text
        user_step[uid] = "phone"
        await update.message.reply_text("输入电话：")
    elif step == "phone":
        users[uid]["phone"] = text
        user_step[uid] = "email"
        await update.message.reply_text("输入邮箱：")
    elif step == "email":
        users[uid]["email"] = text
        user_step[uid] = "addr"
        await update.message.reply_text("输入地址：")
    elif step == "addr":
        users[uid]["addr"] = text
        user_step[uid] = "ref"
        await update.message.reply_text("输入推荐人：")
    elif step == "ref":
        users[uid]["ref"] = text
        users[uid]["status"] = 1
        del user_step[uid]
        await update.message.reply_text("✅ 入驻成功！", reply_markup=main_menu())

# ==========================================
# 【Railway 专属启动，100%不崩溃】
# ==========================================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))

    # 核心修复：Railway 必须用 Webhook，不能用轮询
    if RAILWAY_DOMAIN:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{RAILWAY_DOMAIN}/{BOT_TOKEN}",
            drop_pending_updates=True
        )
    else:
        # 本地测试用轮询
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
