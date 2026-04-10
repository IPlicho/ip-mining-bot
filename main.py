# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

# ===================== 你自己的TOKEN =====================
BOT_TOKEN = "8727191543:AAF0rax78kPycp0MqahZgpjqdrrtJQbjj_I"
ADMIN_ID = 6365510771
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== 數據 =====================
user_step = {}
user_balance = {}
orders = {}

# ===================== 菜單 =====================
def main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🏠 入驻担保", callback_data="reg"),
        InlineKeyboardButton("👤 个人中心", callback_data="me"),
        InlineKeyboardButton("📥 担保派单", callback_data="send"),
        InlineKeyboardButton("🚀 抢单大厅", callback_data="grab"),
        InlineKeyboardButton("💰 充值提现", callback_data="pay"),
        InlineKeyboardButton("📜 担保记录", callback_data="log"),
    )
    return m

def back_menu():
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🏠 返回主菜单", callback_data="home"))
    return m

# ===================== /start =====================
@bot.message_handler(commands=['start'])
def start(msg):
    u = msg.from_user.id
    user_step[u] = None
    user_balance.setdefault(u, 0.0)
    bot.send_message(msg.chat.id, "🔥 担保交易系统已启动", reply_markup=main_menu())

# ===================== 按钮 =====================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    u = c.from_user.id
    mid = c.message.message_id
    cid = c.message.chat.id

    if c.data == "home":
        user_step[u] = None
        bot.edit_message_text("🔥 担保交易系统", cid, mid, reply_markup=main_menu())

    elif c.data == "reg":
        user_step[u] = "name"
        bot.edit_message_text("请输入你的姓名：", cid, mid, reply_markup=back_menu())

    elif c.data == "me":
        bot.edit_message_text(f"👤 个人中心\nID：{u}\n余额：{user_balance.get(u,0.0)} USDT", cid, mid, reply_markup=back_menu())

    elif c.data == "grab":
        amt = random.choice([50,50,50,100])
        user_balance[u] = user_balance.get(u,0.0) + amt
        bot.edit_message_text(f"✅ 抢单成功！获得 {amt} USDT", cid, mid, reply_markup=main_menu())

    elif c.data == "send":
        if u != ADMIN_ID:
            bot.answer_callback_query(c.id, "❌ 无权限")
            return
        user_step[u] = "assign"
        bot.edit_message_text("输入用户UID：", cid, mid, reply_markup=back_menu())

    elif c.data == "pay":
        bot.edit_message_text("💰 业务办理请联系 @fcff88", cid, mid, reply_markup=back_menu())

    elif c.data == "log":
        bot.edit_message_text("📜 暂无记录", cid, mid, reply_markup=back_menu())

    bot.answer_callback_query(c.id)

# ===================== 消息處理 =====================
@bot.message_handler(func=lambda m: True)
def msg(msg):
    u = msg.from_user.id
    cid = msg.chat.id
    txt = msg.text.strip()
    user_balance.setdefault(u, 0.0)

    # 管理員加錢
    if u == ADMIN_ID and txt.startswith("/add"):
        try:
            _, uid, amt = txt.split()
            uid = int(uid)
            amt = float(amt)
            user_balance[uid] = user_balance.get(uid,0.0) + amt
            bot.send_message(cid, f"✅ 成功给 {uid} 加 {amt} USDT")
        except:
            bot.send_message(cid, "格式：/add 123456 100")
        return

    if user_step.get(u) == "name":
        user_step[u] = "phone"
        bot.send_message(cid, "请输入电话：")

    elif user_step.get(u) == "phone":
        user_step[u] = None
        bot.send_message(cid, "✅ 入驻成功！", reply_markup=main_menu())

    elif user_step.get(u) == "assign":
        try:
            target = int(txt)
            user_step[u] = ("assign_amt", target)
            bot.send_message(cid, "输入金额 USDT：")
        except:
            bot.send_message(cid, "❌ 输入正确UID")

    elif type(user_step.get(u)) == tuple and user_step[u][0] == "assign_amt":
        target = user_step[u][1]
        try:
            amt = float(txt)
            user_balance[target] = user_balance.get(target,0.0) + amt
            bot.send_message(cid, f"✅ 派单成功：{amt} USDT")
            bot.send_message(target, f"📥 管理员派给你 {amt} USDT")
            user_step[u] = None
        except:
            bot.send_message(cid, "输入数字")

# ===================== 啟動 =====================
if __name__ == "__main__":
    print("✅ 机器人启动成功")
    bot.infinity_polling()
