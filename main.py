import random
import time
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# ==========================================
# 【零配置 + Railway 自动适配】
# ==========================================
# 直接读取 Railway 分配的环境变量，无需手动改
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
# Railway 强制要求监听 0.0.0.0 和动态端口
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_URL = os.getenv("RAILWAY_PUBLIC_DOMAIN") # 自动获取 Webhook 地址

# 基础配置
ADMIN_ID = [6365510771]
PAY_TIMEOUT = 12 * 3600 # 12小时超时（秒）
VIRTUAL_ORDER_AMOUNTS = [50, 50, 50, 100] # 50概率75%，100概率25%

# 极简数据存储
users = {}
orders = {}
user_step = {}

# 工具函数
def gen_uid():
    return str(int(time.time()))[-6:]

def gen_order_id():
    return f"ORD{int(time.time())}{random.randint(100, 999)}"

def is_admin(user_id):
    return user_id in ADMIN_ID

# UI 菜单
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🏠 入驻担保", callback_data="verify")],
        [InlineKeyboardButton("👤 个人中心", callback_data="profile")],
        [InlineKeyboardButton("📥 担保派单", callback_data="assign")],
        [InlineKeyboardButton("🚀 抢单大厅", callback_data="grab")],
        [InlineKeyboardButton("💰 充值提现", callback_data="wallet")],
        [InlineKeyboardButton("📜 担保记录", callback_data="record")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= 核心逻辑 =================
async def start(update: Update, context):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {"uid": gen_uid(), "status": "unverified", "balance": 0.0}
    await update.message.reply_text("🔥 担保交易平台\n请选择功能：", reply_markup=main_menu())

async def callback_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user = users.get(user_id, {"status": "unverified"})

    # 1. 入驻担保
    if data == "verify":
        if user["status"] == "approved":
            await query.edit_message_text("✅ 已通过审核", reply_markup=main_menu())
            return
        user_step[user_id] = "name"
        await query.edit_message_text("请输入真实姓名：")

    # 2. 个人中心
    elif data == "profile":
        text = (
            f"👤 个人中心\n"
            f"UID: {user['uid']}\n"
            f"状态: {user['status']}\n"
            f"余额: {user['balance']:.2f} USDT"
        )
        await query.edit_message_text(text, reply_markup=main_menu())

    # 3. 抢单大厅
    elif data == "grab":
        if user["status"] != "approved":
            await query.edit_message_text("❌ 请先完成入驻审核", reply_markup=main_menu())
            return
        amount = random.choice(VIRTUAL_ORDER_AMOUNTS)
        order_id = gen_order_id()
        orders[order_id] = {"amount": amount, "status": "wait", "user_id": None}
        kb = [[InlineKeyboardButton(f"🚀 抢单 {amount} USDT", callback_data=f"grab_{order_id}")]]
        await query.edit_message_text(f"🎯 随机订单\n金额: {amount} USDT", reply_markup=InlineKeyboardMarkup(kb))

    # 4. 执行抢单
    elif data.startswith("grab_"):
        order_id = data.split("_")[1]
        if order_id not in orders or orders[order_id]["status"] != "wait":
            await query.answer("❌ 订单已被抢", show_alert=True)
            return
        orders[order_id]["user_id"] = user_id
        orders[order_id]["status"] = "paid" # 直接标记为已支付（虚拟单）
        await query.edit_message_text(f"✅ 抢单成功!\n订单: {order_id}\n金额: {amount} USDT", reply_markup=main_menu())

    # 5. 管理员派单
    elif data == "assign":
        if not is_admin(user_id):
            await query.edit_message_text("❌ 无权限", reply_markup=main_menu())
            return
        user_step[user_id] = "assign_uid"
        await query.edit_message_text("输入用户 UID:")

    # 6. 充值提现
    elif data == "wallet":
        await query.edit_message_text("💰 办理业务请联系 @fcff88", reply_markup=main_menu())

    # 7. 担保记录
    elif data == "record":
        user_orders = [f"{k} | {v['amount']} USDT | {v['status']}" for k, v in orders.items() if v["user_id"] == user_id]
        text = "\n".join(user_orders) if user_orders else "📭 暂无记录"
        await query.edit_message_text(f"📜 我的记录\n{text}", reply_markup=main_menu())

    # 返回
    elif data == "back":
        await query.edit_message_text("🏠 返回主菜单", reply_markup=main_menu())

# 表单处理
async def message_handler(update: Update, context):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if user_id not in user_step:
        return

    step = user_step[user_id]

    # 入驻表单
    if step == "name":
        user_step[user_id] = "phone"
        await update.message.reply_text("✅ 姓名已存\n输入电话:")
    elif step == "phone":
        user_step[user_id] = "email"
        await update.message.reply_text("输入邮箱:")
    elif step == "email":
        user_step[user_id] = "addr"
        await update.message.reply_text("输入地址:")
    elif step == "addr":
        user_step[user_id] = "ref"
        await update.message.reply_text("输入推荐人(无填无):")
    elif step == "ref":
        # 审核通过
        users[user_id]["status"] = "approved"
        del user_step[user_id]
        await update.message.reply_text("🎉 入驻审核通过!", reply_markup=main_menu())

    # 派单表单
    elif step == "assign_uid":
        # 简单查找
        target_uid = None
        for uid, u in users.items():
            if u["uid"] == text:
                target_uid = uid
                break
        if not target_uid:
            await update.message.reply_text("❌ 未找到该 UID")
            return
        user_step[user_id] = "assign_amt"
        users[target_uid]["balance"] += 100 # 简单加钱（示例）
        await update.message.reply_text(f"✅ 派单成功! 给用户 {text} 增加 100 USDT")

# ================= 启动 Bot (Railway 适配) =================
def main():
    # 使用 Webhook 模式（Railway 推荐）
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # 关键：Railway 必须使用 Webhook 监听 0.0.0.0
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()
