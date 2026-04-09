import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict

# 担保机器人 Token（你刚刚给我的）
TRUST_BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
trust_bot = telebot.TeleBot(TRUST_BOT_TOKEN)

# 管理员
ADMIN_IDS = [8256055083, 8279854167]

# 订单数据
orders = defaultdict(dict)
order_id_counter = 1

# 中间人数据
middlemen = defaultdict(lambda: {
    "is_active": False,
    "balance": 0.0,
    "total_earn": 0.0
})

# ───────────────────────────────
# 主菜单
# ───────────────────────────────
@trust_bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(
        InlineKeyboardButton("✅ 申请成为中间人", callback_data="apply_middleman"),
        InlineKeyboardButton("📦 创建担保订单", callback_data="create_order"),
        InlineKeyboardButton("📋 我的订单", callback_data="my_orders"),
        InlineKeyboardButton("👛 中间人钱包", callback_data="middleman_wallet"),
        InlineKeyboardButton("📜 帮助说明", callback_data="help_info")
    )
    trust_bot.send_message(
        msg.chat.id,
        "🛡️ TrustEscrow 担保机器人\n安全交易 · 全程托管",
        reply_markup=mk
    )

# ───────────────────────────────
# 申请中间人
# ───────────────────────────────
@trust_bot.callback_query_handler(lambda c: c.data == "apply_middleman")
def apply_middleman(call):
    uid = call.from_user.id
    if middlemen[uid]["is_active"]:
        trust_bot.answer_callback_query(call.id, "✅ 你已经是中间人", show_alert=True)
        return
    middlemen[uid]["is_active"] = True
    trust_bot.send_message(call.message.chat.id, "✅ 你已成功成为中间人，可接单担保")
    trust_bot.answer_callback_query(call.id)

# ───────────────────────────────
# 创建订单（简化版）
# ───────────────────────────────
@trust_bot.callback_query_handler(lambda c: c.data == "create_order")
def create_order(call):
    global order_id_counter
    uid = call.from_user.id
    oid = order_id_counter
    order_id_counter += 1
    orders[oid] = {
        "buyer": uid,
        "seller": 0,
        "middleman": 0,
        "amount": 0.0,
        "status": "waiting_seller"
    }
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton("👤 卖家点击加入", callback_data=f"join_seller_{oid}"))
    trust_bot.send_message(
        call.message.chat.id,
        f"📦 订单 #{oid}\n等待卖家加入…",
        reply_markup=mk
    )
    trust_bot.answer_callback_query(call.id)

# ───────────────────────────────
# 卖家加入订单
# ───────────────────────────────
@trust_bot.callback_query_handler(lambda c: c.data.startswith("join_seller_"))
def join_seller(call):
    uid = call.from_user.id
    oid = int(call.data.split("_")[-1])
    if orders[oid]["seller"] != 0:
        trust_bot.answer_callback_query(call.id, "❌ 已有卖家", show_alert=True)
        return
    orders[oid]["seller"] = uid
    trust_bot.send_message(
        call.message.chat.id,
        f"✅ 订单 #{oid}\n卖家已加入\n请输入担保金额："
    )
    trust_bot.answer_callback_query(call.id)

# ───────────────────────────────
# 帮助
# ───────────────────────────────
@trust_bot.callback_query_handler(lambda c: c.data == "help_info")
def help_info(call):
    trust_bot.send_message(
        call.message.chat.id,
        "📜 使用说明\n\n1. 买家创建订单\n2. 卖家加入\n3. 设置金额\n4. 中间人担保\n5. 确认放款"
    )
    trust_bot.answer_callback_query(call.id)

# ───────────────────────────────
# 启动机器人
# ───────────────────────────────
if __name__ == "__main__":
    print("✅ 担保机器人已启动")
    trust_bot.infinity_polling()
