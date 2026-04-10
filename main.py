import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 你的机器人TOKEN
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"

# 超简单菜单
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("我是按钮1", callback_data="1")],
        [InlineKeyboardButton("我是按钮2", callback_data="2")],
    ])

# 启动命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 机器人已上线", reply_markup=menu())

# 按钮回调
async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("✅ 按钮正常工作", reply_markup=menu())

# 启动（极简、稳定）
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb))

    # Railway 必须要的端口（极简写法，不会错）
    port = int(os.environ.get("PORT", 8080))
    app.run_webhook(listen="0.0.0.0", port=port, url_path="/", webhook_url="https://"+os.environ["RAILWAY_PUBLIC_DOMAIN"])

if __name__ == "__main__":
    main()
