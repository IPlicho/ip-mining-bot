import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import os
from datetime import datetime
import traceback
import time

# ====================== 核心配置 ======================
ADMIN_IDS = [8401979801, 8781082053]
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ====================== 多语言文案 ======================
LANG = {
    "zh_tw": {
        "welcome": "👋 歡迎使用 TrustEscrow 擔保平台！\n我們提供專業的第三方擔保服務，保障您的交易安全。",
        "select_lang": "請選擇語言 / Please select language",
        "lang_set": "✅ 語言已設定為繁體中文",
        "lang_set_en": "✅ Language set to English",
        "back": "🔙 返回首頁",
        "contact_admin": "📞 聯繫管理員",
        "no_permission": "❌ 您無權使用此功能",
        "invalid_cmd": "❌ 無效指令",
        "success": "✅ 操作成功",
        "loading": "⏳ 載入中...",

        "inline": {
            "home": "🏠 首頁",
            "service": "📌 擔保項目",
            "create": "🚀 發起擔保",
            "level": "📊 合夥人制度",
            "lang": "🌐 切換語言"
        },
        "keyboard": {
            "my_order": "📜 我的擔保",
            "income": "💰 收益中心",
            "detail": "🧾 資金明細",
            "apply": "🛡️ 擔保入駐",
            "order_mgmt": "📦 訂單管理"
        },
        "home_title": "🏠 TrustEscrow 擔保平台",
        "home_desc": "安全 · 高效 · 可信 · 全程擔保\n所有擔保人經過嚴格審核，訂單可查、過程可控、售後可追溯。",
        "service_title": "📌 擔保項目",
        "service_list": """
我們支持以下正規擔保交易：
• USDT 轉帳擔保
• 線上交易擔保
• 線下交易擔保
• 合約履約擔保
• 多人交易擔保

擔保流程：
1. 用戶發起擔保 → 2. 資金託管 → 3. 履約確認 → 4. 放行結算
""",
        "level_title": "📊 合夥人制度",
        "level_desc": "等級越高，收益越高，最高可拿 50% 收益",
        "level_list": """
Lv1 見習擔保人｜搶單 5%｜派單 15%
Lv2 正式擔保人｜搶單 7%｜派單 20%
Lv3 資深擔保人｜搶單 10%｜派單 25%
Lv4 核心擔保人｜搶單 15%｜派單 35%
Lv5 合夥人｜搶單 25%｜派單 50%
""",
        "apply_title": "🛡️ 擔保入駐",
        "apply_desc": "成為擔保人即可接單賺取收益。",
        "admin_announce": "✅ 公告已更新",
        "admin_grab_on": "✅ 搶單大廳已開啟",
        "admin_grab_off": "✅ 搶單大廳已關閉",
    },
    "en": {
        "welcome": "👋 Welcome to TrustEscrow Guarantee Platform!\nSecure transactions with professional escrow service.",
        "select_lang": "Please select language",
        "lang_set": "✅ Language set to Traditional Chinese",
        "lang_set_en": "✅ Language set to English",
        "back": "🔙 Back",
        "contact_admin": "📞 Contact Admin",
        "no_permission": "❌ No permission",
        "invalid_cmd": "❌ Invalid command",
        "success": "✅ Success",
        "loading": "⏳ Loading...",

        "inline": {
            "home": "🏠 Home",
            "service": "📌 Services",
            "create": "🚀 Create Guarantee",
            "level": "📊 Partner Program",
            "lang": "🌐 Language"
        },
        "keyboard": {
            "my_order": "📜 My Orders",
            "income": "💰 Income",
            "detail": "🧾 History",
            "apply": "🛡️ Apply",
            "order_mgmt": "📦 Orders"
        },
        "home_title": "🏠 TrustEscrow",
        "home_desc": "Secure · Efficient · Trusted",
        "service_title": "📌 Services",
        "service_list": """
We support:
• USDT Transfer Escrow
• Online Transaction Escrow
• Offline Transaction Escrow
• Contract Performance Escrow
• Multi-party Escrow
""",
        "level_title": "📊 Partner Program",
        "level_desc": "Higher level, higher income up to 50%.",
        "level_list": """
Lv1 Trainee｜Grab 5%｜Assign 15%
Lv2 Official｜Grab 7%｜Assign 20%
Lv3 Senior｜Grab 10%｜Assign 25%
Lv4 Core｜Grab 15%｜Assign 35%
Lv5 Partner｜Grab 25%｜Assign 50%
""",
        "apply_title": "🛡️ Become a Guarantor",
        "apply_desc": "Start earning today.",
        "admin_announce": "✅ Announcement updated",
        "admin_grab_on": "✅ Grab enabled",
        "admin_grab_off": "✅ Grab disabled",
    }
}

# ====================== 数据存储 ======================
DATA_FILE = "bot_data.json"

def init_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "users": {},
            "orders": {},
            "withdraws": {},
            "announcement": {
                "zh_tw": "🏠 擔保服務平台\n安全 · 高效 · 可信",
                "en": "🏠 TrustEscrow\nSecure · Efficient · Trusted"
            },
            "grab_enabled": True,
            "order_counter": 1
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====================== 工具 ======================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_user_lang(user_id, data):
    return data["users"].get(str(user_id), {}).get("lang", "zh_tw")

def t(user_id, key, data):
    lang = get_user_lang(user_id, data)
    keys = key.split(".")
    res = LANG[lang]
    for k in keys:
        res = res[k]
    return res

# ====================== 按钮 ======================
def lang_menu():
    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton("繁體中文", callback_data="lang_zh_tw"),
        InlineKeyboardButton("English", callback_data="lang_en")
    )
    return m

def user_inline(user_id, data):
    lang = get_user_lang(user_id, data)
    m = InlineKeyboardMarkup()
    i = LANG[lang]["inline"]
    m.row(InlineKeyboardButton(i["home"], callback_data="in_home"))
    m.row(
        InlineKeyboardButton(i["service"], callback_data="in_service"),
        InlineKeyboardButton(i["create"], callback_data="in_create")
    )
    m.row(
        InlineKeyboardButton(i["level"], callback_data="in_level"),
        InlineKeyboardButton(i["lang"], callback_data="in_lang")
    )
    return m

def user_kb(user_id, data):
    lang = get_user_lang(user_id, data)
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    k = LANG[lang]["keyboard"]
    m.add(KeyboardButton(k["my_order"]))
    return m

def guarantor_inline(user_id, data):
    return user_inline(user_id, data)

def guarantor_kb(user_id, data):
    lang = get_user_lang(user_id, data)
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    k = LANG[lang]["keyboard"]
    m.add(
        KeyboardButton(k["order_mgmt"]),
        KeyboardButton(k["income"]),
        KeyboardButton(k["detail"]),
        KeyboardButton(k["apply"])
    )
    return m

# ====================== 语言设置（修复卡死） ======================
@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def cb_lang(c):
    try:
        data = init_data()
        user_id = c.from_user.id
        lang = c.data.split("_")[1]
        if str(user_id) not in data["users"]:
            data["users"][str(user_id)] = {
                "username": c.from_user.username,
                "first_name": c.from_user.first_name,
                "is_guarantor": False,
                "guarantor_status": "unapplied",
                "level": 1,
                "balance": 0.0,
                "lang": lang,
                "join_time": str(datetime.now())
            }
        else:
            data["users"][str(user_id)]["lang"] = lang
        save_data(data)

        msg = t(user_id, "lang_set_en" if lang == "en" else "lang_set", data)
        bot.answer_callback_query(c.id, msg)

        bot.edit_message_text(
            t(user_id, "welcome", data),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=user_inline(user_id, data)
        )
        bot.send_message(
            c.message.chat.id,
            "✅ Menu ready",
            reply_markup=user_kb(user_id, data)
        )
    except:
        bot.answer_callback_query(c.id, "❌ Error")

# ====================== start ======================
@bot.message_handler(commands=["start"])
def cmd_start(m):
    data = init_data()
    user_id = m.from_user.id
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {
            "username": m.from_user.username,
            "first_name": m.from_user.first_name,
            "is_guarantor": False,
            "guarantor_status": "unapplied",
            "level": 1,
            "balance": 0.0,
            "lang": "zh_tw",
            "join_time": str(datetime.now())
        }
        save_data(data)
    bot.send_message(m.chat.id, t(user_id, "select_lang", data), reply_markup=lang_menu())

# ====================== 内联回调 ======================
@bot.callback_query_handler(func=lambda c: c.data.startswith("in_"))
def cb_inline(c):
    try:
        data = init_data()
        user_id = c.from_user.id
        act = c.data[3:]
        if act == "home":
            txt = data["announcement"][get_user_lang(user_id, data)]
            bot.edit_message_text(txt, c.message.chat.id, c.message.id, reply_markup=user_inline(user_id, data))
        elif act == "service":
            txt = t(user_id, "service_title", data) + "\n" + t(user_id, "service_list", data)
            bot.edit_message_text(txt, c.message.chat.id, c.message.id, reply_markup=user_inline(user_id, data))
        elif act == "level":
            txt = t(user_id, "level_title", data) + "\n" + t(user_id, "level_list", data)
            bot.edit_message_text(txt, c.message.chat.id, c.message.id, reply_markup=user_inline(user_id, data))
        elif act == "lang":
            bot.edit_message_text(t(user_id, "select_lang", data), c.message.chat.id, c.message.id, reply_markup=lang_menu())
        elif act == "create":
            bot.answer_callback_query(c.id, "🚀 Coming soon")
        bot.answer_callback_query(c.id)
    except:
        bot.answer_callback_query(c.id, "❌ Error")

# ====================== 键盘消息 ======================
@bot.message_handler(func=lambda x: True)
def all_msgs(m):
    try:
        data = init_data()
        user_id = m.from_user.id
        lang = get_user_lang(user_id, data)
        u = data["users"][str(user_id)]
        txt = m.text

        if txt == t(user_id, "keyboard.my_order", data):
            bot.send_message(m.chat.id, "📜 My Orders", reply_markup=user_kb(user_id, data))
        elif txt == t(user_id, "keyboard.order_mgmt", data):
            bot.send_message(m.chat.id, "📦 Order Management", reply_markup=guarantor_kb(user_id, data))
        elif txt == t(user_id, "keyboard.income", data):
            bot.send_message(m.chat.id, "💰 Income Center", reply_markup=guarantor_kb(user_id, data))
        elif txt == t(user_id, "keyboard.detail", data):
            bot.send_message(m.chat.id, "🧾 Transaction History", reply_markup=guarantor_kb(user_id, data))
        elif txt == t(user_id, "keyboard.apply", data):
            bot.send_message(m.chat.id, t(user_id, "apply_title", data) + "\n" + t(user_id, "apply_desc", data), reply_markup=guarantor_kb(user_id, data))
        else:
            bot.send_message(m.chat.id, t(user_id, "invalid_cmd", data))
    except:
        bot.send_message(m.chat.id, "❌ System error")

# ====================== 管理员命令 ======================
@bot.message_handler(commands=["公告", "announce"])
def admin_announce(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, t(m.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    parts = m.text.split(" ", 1)
    if len(parts) < 2:
        bot.reply_to(m, "❌ Usage: /公告 内容")
        return
    data["announcement"]["zh_tw"] = parts[1]
    data["announcement"]["en"] = parts[1]
    save_data(data)
    bot.reply_to(m, t(m.from_user.id, "admin_announce", data))

@bot.message_handler(commands=["開啟搶單", "enable_grab"])
def admin_grab_on(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, t(m.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    data["grab_enabled"] = True
    save_data(data)
    bot.reply_to(m, t(m.from_user.id, "admin_grab_on", data))

@bot.message_handler(commands=["關閉搶單", "disable_grab"])
def admin_grab_off(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, t(m.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    data["grab_enabled"] = False
    save_data(data)
    bot.reply_to(m, t(m.from_user.id, "admin_grab_off", data))

# ====================== 启动 ======================
if __name__ == "__main__":
    print("✅ Bot started (stable, no functions deleted)")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except:
            time.sleep(3)
