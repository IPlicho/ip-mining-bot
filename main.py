import telebot
import time
from datetime import datetime, timedelta
import os
import threading

# ====================== 你的机器人配置（已填好新Token，仅改ADMIN_ID）======================
BOT_TOKEN = "8747559514:AAFJdsZ3tlCVPIW6vL60hTuBc_Eo5FP4kU"
ADMIN_ID = 123456789  # 🔥 这里改成你自己的 Telegram ID 🔥

bot = telebot.TeleBot(BOT_TOKEN)

# 内存数据（测试用，重启会清空，正式用可换数据库）
user_balance = {}
orders = {}
order_id = 1

# ====================== 主菜单 ======================
def main_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("📝 担保申请/派单")
    btn2 = telebot.types.KeyboardButton("📜 我的担保订单")
    btn3 = telebot.types.KeyboardButton("💰 我的钱包")
    markup.add(btn1, btn2, btn3)

    if user_id == ADMIN_ID:
        markup.add(telebot.types.KeyboardButton("📊 管理员后台"))
    return markup

# ====================== /start 入口 ======================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    bal = user_balance.get(user_id, 0.0)
    text = (
        "✅ 担保系统已启动\n\n"
        f"👤 你的ID：{user_id}\n"
        f"💰 余额：{bal} USDT\n"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu(user_id))

# ====================== 菜单按钮处理 ======================
@bot.message_handler(func=lambda msg: True)
def handle_menu(message):
    global order_id
    user_id = message.from_user.id
    text = message.text.strip()
    bal = user_balance.get(user_id, 0.0)

    # 用户菜单：发起派单
    if text == "📝 担保申请/派单":
        bot.send_message(user_id, (
            "📝 发起担保派单\n\n"
            "请按格式发送：\n"
            "/order 对方ID 金额\n\n"
            "例：/order 987654321 50\n"
            "⚠️ 余额不足将无法派单"
        ))

    # 用户菜单：我的订单
    elif text == "📜 我的担保订单":
        if not orders:
            bot.send_message(user_id, "📭 暂无担保订单")
            return

        msg = "📜 我的担保订单\n\n"
        for oid, o in orders.items():
            if o["from_id"] == user_id or o["to_id"] == user_id:
                status = o["status"]
                expire = o["expire"].strftime("%m-%d %H:%M")
                msg += (
                    f"🔖 订单：{oid}\n"
                    f"👤 发起：{o['from_id']}\n"
                    f"👤 对方：{o['to_id']}\n"
                    f"💰 金额：{o['amount']} USDT\n"
                    f"⏳ 12小时处理：{expire}\n"
                    f"📌 状态：{status}\n\n"
                )
        bot.send_message(user_id, msg)

    # 用户菜单：我的钱包
    elif text == "💰 我的钱包":
        bot.send_message(user_id, (
            f"💰 我的钱包\n\n"
            f"👤 ID：{user_id}\n"
            f"💵 余额：{bal} USDT\n\n"
            "充值请联系管理员"
        ))

    # 管理员后台
    elif text == "📊 管理员后台" and user_id == ADMIN_ID:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📋 待接单列表", "💰 手动加余额", "🔙 返回主菜单")
        bot.send_message(user_id, "📊 管理员后台", reply_markup=markup)

    # 待接单列表（仅管理员）
    elif text == "📋 待接单列表" and user_id == ADMIN_ID:
        wait = [o for o in orders.values() if o["status"] == "待接单"]
        if not wait:
            bot.send_message(user_id, "📭 暂无待接单")
            return

        for o in wait:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("✅ 接单", callback_data=f"accept_{o['order_id']}"))
            bot.send_message(user_id, (
                f"📋 待接单 {o['order_id']}\n"
                f"发起：{o['from_id']}\n"
                f"对方：{o['to_id']}\n"
                f"金额：{o['amount']} USDT\n"
                f"12小时处理：{o['expire'].strftime('%m-%d %H:%M')}"
            ), reply_markup=markup)

    # 手动加余额（仅管理员）
    elif text == "💰 手动加余额" and user_id == ADMIN_ID:
        bot.send_message(user_id, "发送：/add 用户ID 金额\n例：/add 123456789 100")

    # 返回主菜单
    elif text == "🔙 返回主菜单":
        bot.send_message(user_id, "🔙 已返回", reply_markup=main_menu(user_id))

    # 派单指令
    elif text.startswith("/order"):
        parts = text.split()
        if len(parts) != 3:
            bot.send_message(user_id, "❌ 格式：/order 对方ID 金额")
            return
        try:
            to_id = int(parts[1])
            amt = float(parts[2])
        except:
            bot.send_message(user_id, "❌ ID或金额错误")
            return

        if bal < amt:
            bot.send_message(user_id, "❌ 余额不足")
            return

        # 冻结金额
        user_balance[user_id] = bal - amt

        oid = order_id
        order_id += 1
        orders[oid] = {
            "order_id": oid,
            "from_id": user_id,
            "to_id": to_id,
            "amount": amt,
            "status": "待接单",
            "expire": datetime.now() + timedelta(hours=12)
        }

        bot.send_message(user_id, (
            f"✅ 派单成功！订单 {oid}\n"
            f"💰 已冻结：{amt} USDT\n"
            f"⏳ 12小时内处理"
        ))
        # 通知管理员
        bot.send_message(ADMIN_ID, f"🔔 新派单 {oid}\n用户{user_id} → {to_id}，{amt} USDT")

    # 管理员加钱指令
    elif text.startswith("/add") and user_id == ADMIN_ID:
        parts = text.split()
        if len(parts) != 3:
            bot.send_message(user_id, "❌ 格式：/add 用户ID 金额")
            return
        try:
            uid = int(parts[1])
            amt = float(parts[2])
        except:
            bot.send_message(user_id, "❌ 错误")
            return
        user_balance[uid] = user_balance.get(uid, 0.0) + amt
        bot.send_message(user_id, f"✅ 已给 {uid} 加 {amt} USDT")
        bot.send_message(uid, f"💰 管理员充值到账：+{amt} USDT")

# ====================== 管理员接单 ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_order(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ 无权限")
        return
    oid = int(call.data.split("_")[1])
    if oid not in orders:
        bot.edit_message_text("❌ 订单不存在", call.message.chat.id, call.message.message_id)
        return
    o = orders[oid]
    o["status"] = "已接单"
    bot.edit_message_text(f"✅ 订单 {oid} 已接单", call.message.chat.id, call.message.message_id)
    bot.send_message(o["from_id"], f"📢 你的订单 {oid} 已接单，处理中！\n💰 已扣除：{o['amount']} USDT")

# ====================== 长轮询启动 ======================
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # 启动长轮询，彻底告别Webhook 401问题
    threading.Thread(target=run_bot, daemon=True).start()
    # 保持进程运行
    while True:
        time.sleep(3600)
