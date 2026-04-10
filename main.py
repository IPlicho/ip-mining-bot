import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 你的Bot Token，直接用
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"

# 极简菜单
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 测试按钮", callback_data="test")]
    ])

# /start 命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 机器人正常运行！", reply_markup=main_menu())

# 按钮回调
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ 按钮点击成功！", reply_markup=main_menu())

# 启动（Railway专属Webhook，零错误写法）
def main():
    # 构建应用，v20.7专属写法
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 注册处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback))
    
    # Railway强制端口配置，自动读取环境变量
    port = int(os.environ.get("PORT", 8080))
    webhook_url = f"https://{os.environ['RAILWAY_PUBLIC_DOMAIN']}"
    
    # 启动Webhook，v20.7正确写法，彻底解决Updater错误
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=f"{webhook_url}/{BOT_TOKEN}",
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
