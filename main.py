# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import datetime

# ====================== 配置 ======================
ADMIN_IDS = [8401979801, 8781082053]
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
bot = telebot.TeleBot(BOT_TOKEN)

# ====================== 繁體文案（你給的全套） ======================
TEXT = {
    "home": """🏠 担保服务平台
安全 · 高效 · 可信 · 全程担保

本平台提供第三方中立担保服务，保障交易双方资金与权益安全。
所有担保人经过严格审核，订单可查、过程可控、售后可追溯。""",

    "service": """📌 担保项目

我们支持以下正规担保交易：

• USDT 转账担保
双方交易前由平台托管资金，确认无误后放行。

• 线上交易担保
商品/服务/账号/虚拟资产交易安全担保。

• 线下交易担保
当面交易资金托管，避免欺诈。

• 合约履约担保
按约定条件完成后才释放资金。

• 多人交易担保
支持多方参与的复杂交易担保。

担保流程
1. 用户发起担保 → 2. 资金托管 → 3. 履约确认 → 4. 放行结算""",

    "apply": """🛡️ 担保入驻

成为担保人即可接单赚取收益。

入驻要求
• 同意平台规则
• 提供基本资料审核
• 无违规记录

申请流程
1. 提交资料 → 2. 管理员审核 → 3. 开通权限 → 4. 开始接单

注意
• 违规将被永久封锁权限""",

    "create": """🚀 发起担保

下单流程：
1. 选择担保类型
2. 填写金额、备注
3. 提交订单 → 等待担保人接单
4. 托管资金 → 履约完成 → 确认放行""",

    "help": """📖 帮助中心
• 担保项目：查看支持的交易类型
• 担保入驻：申请成为担保人
• 发起担保：创建新订单
• 我的订单：查看历史记录""",

    "applied": "✅ 你已提交过申请",
    "apply_success": "✅ 申请已提交，等待管理员审核",
    "btn_back": "« 返回首页"
}

# ====================== 數據 ======================
def load_data():
    try:
        with open("data.json","r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users":{},"apps":{},"orders":{}}

def save_data(data):
    with open("data.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

# ====================== 按鈕選單 ======================
def main_menu():
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton("📌 担保项目", callback_data="service"),
        InlineKeyboardButton("🛡️ 担保入驻", callback_data="apply"),
        InlineKeyboardButton("🚀 发起担保", callback_data="create"),
        InlineKeyboardButton("📖 帮助中心", callback_data="help")
    )
    return m

def back_menu():
    m = InlineKeyboardMarkup(row_width=1)
    m.add(InlineKeyboardButton(TEXT["btn_back"], callback_data="home"))
    return m

# ====================== 啟動 ======================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, TEXT["home"], reply_markup=main_menu())

# ====================== 頁面切換 ======================
@bot.callback_query_handler(func=lambda c:True)
def cb(c):
    data = c.data
    mid = c.message.id
    cid = c.message.chat.id
    uid = c.from_user.id
    d = load_data()

    if data == "home":
        bot.edit_message_text(TEXT["home"], cid, mid, reply_markup=main_menu())

    elif data == "service":
        bot.edit_message_text(TEXT["service"], cid, mid, reply_markup=back_menu())

    elif data == "apply":
        bot.edit_message_text(TEXT["apply"], cid, mid, reply_markup=back_menu())

    elif data == "create":
        bot.edit_message_text(TEXT["create"], cid, mid, reply_markup=back_menu())

    elif data == "help":
        bot.edit_message_text(TEXT["help"], cid, mid, reply_markup=back_menu())

    bot.answer_callback_query(c.id)

# ====================== 管理員指令 ======================
@bot.message_handler(commands=["审核","拒绝","封锁","解除","等级","派单","完成","通过提现","拒绝提现","公告","开启抢单","关闭抢单","用户信息","订单信息"])
def admin_cmd(msg):
    if msg.from_user.id not in ADMIN_IDS:
        msg.reply("❌ 無權限")
        return
    msg.reply("🔐 管理員指令已接收")

# ====================== 運行 ======================
if __name__ == "__main__":
    print("✅ 担保机器人 - 正式上線版")
    bot.infinity_polling()
