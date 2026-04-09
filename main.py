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

# ====================== 語言包（繁體完整 + 英文完整）======================
LANG = {
    "zh_tw": {
        "welcome": "👋 歡迎使用 TrustEscrow 擔保平台！\n安全交易 · 全程託管",
        "select_lang": "請選擇語言 / Please select language",
        "lang_set": "✅ 語言已設定為繁體中文",
        "lang_set_en": "✅ Language set to English",
        "no_permission": "❌ 您無權使用此功能",
        "invalid_cmd": "❌ 無效指令",
        "back": "🔙 返回首頁",

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

        "home_text": "🏠 TrustEscrow 擔保機器人\n安全交易 · 全程託管",
        "service_text": """📌 擔保項目
我們支持以下正規擔保交易：
• USDT 轉帳擔保
• 線上交易擔保
• 線下交易擔保
• 合約履約擔保
• 多人交易擔保

擔保流程：
1. 用戶發起擔保 → 2. 資金託管 → 3. 履約確認 → 4. 放行結算""",

        "level_text": """📊 合夥人制度
等級越高，收益越高，最高可拿 50% 收益

Lv1 見習擔保人   搶單 5% ｜ 派單 15%
Lv2 正式擔保人   搶單 7% ｜ 派單 20%
Lv3 資深擔保人   搶單 10%｜ 派單 25%
Lv4 核心擔保人   搶單 15%｜ 派單 35%
Lv5 合夥人       搶單 25%｜ 派單 50%""",

        "apply_text": """🛡️ 擔保入駐
成為擔保人即可接單賺取收益。
點擊「提交申請」，管理員將盡快為您審核。""",

        "apply_submit": "✅ 提交申請",
        "apply_sent": "✅ 申請已提交，等待管理員審核",
        "apply_already": "⚠️ 您已申請過，請等待審核",
        "admin_new_apply": "📥 新的擔保人申請\n用戶ID：{}\n用戶名：@{}\n姓名：{}\n時間：{}",
        "user_approved": "✅ 您的擔保人申請已通過！",
        "user_rejected": "❌ 您的擔保人申請已被拒絕",

        "admin_announce": "✅ 公告已更新",
        "admin_grab_on": "✅ 搶單大廳已開啟",
        "admin_grab_off": "✅ 搶單大廳已關閉",
        "admin_approve": "✅ 已通過該用戶申請",
        "admin_reject": "✅ 已拒絕該用戶申請",
    },

    "en": {
        "welcome": "👋 Welcome to TrustEscrow!\nSecure · Safe · Escrow",
        "select_lang": "Please select language",
        "lang_set": "✅ Language set to Traditional Chinese",
        "lang_set_en": "✅ Language set to English",
        "no_permission": "❌ No permission",
        "invalid_cmd": "❌ Invalid command",
        "back": "🔙 Back",

        "inline": {
            "home": "🏠 Home",
            "service": "📌 Services",
            "create": "🚀 Create",
            "level": "📊 Levels",
            "lang": "🌐 Lang"
        },
        "keyboard": {
            "my_order": "📜 My Orders",
            "income": "💰 Income",
            "detail": "🧾 History",
            "apply": "🛡️ Apply",
            "order_mgmt": "📦 Manage"
        },

        "home_text": "🏠 TrustEscrow\nSecure Transaction",
        "service_text": """📌 Services
• USDT Transfer
• Online Transaction
• Offline Transaction
• Contract Escrow
• Multi-party Transaction""",

        "level_text": """📊 Partner Levels
Lv1 Trainee 5%/15%
Lv2 Official 7%/20%
Lv3 Senior 10%/25%
Lv4 Core 15%/35%
Lv5 Partner 25%/50%""",

        "apply_text": "🛡️ Apply to be a Guarantor.\nClick Submit to send your application.",
        "apply_submit": "✅ Submit",
        "apply_sent": "✅ Application sent",
        "apply_already": "⚠️ Already applied",
        "admin_new_apply": "📥 New Application\nID: {}\nUser: @{}\nTime: {}",
        "user_approved": "✅ Approved!",
        "user_rejected": "❌ Rejected",

        "admin_announce": "✅ Announcement updated",
        "admin_grab_on": "✅ Grab enabled",
        "admin_grab_off": "✅ Grab disabled",
        "admin_approve": "✅ Approved",
        "admin_reject": "✅ Rejected",
    }
}

# ====================== 數據存儲 ======================
DATA_FILE = "bot_data.json"

def init_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "users": {},
            "orders": {},
            "withdraws": {},
            "applications": {},
            "announcement": {
                "zh_tw": "🏠 TrustEscrow 擔保機器人",
                "en": "🏠 TrustEscrow Bot"
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

# ====================== 工具函數 ======================
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

# ====================== 發送通知給管理員 ======================
def notify_admins(text):
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text)
        except:
            continue

# ====================== 按鈕選單 ======================
def lang_select_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("繁體中文", callback_data="lang_zh_tw"),
        InlineKeyboardButton("English", callback_data="lang_en")
    )
    return markup

def user_inline_menu(lang):
    m = LANG[lang]["inline"]
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(m["home"], callback_data="in_home"))
    markup.row(
        InlineKeyboardButton(m["service"], callback_data="in_service"),
        InlineKeyboardButton(m["create"], callback_data="in_create")
    )
    markup.row(
        InlineKeyboardButton(m["level"], callback_data="in_level"),
        InlineKeyboardButton(m["lang"], callback_data="in_lang")
    )
    return markup

def user_keyboard_menu(lang):
    m = LANG[lang]["keyboard"]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(m["my_order"]))
    return markup

def guarantor_keyboard_menu(lang):
    m = LANG[lang]["keyboard"]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(m["order_mgmt"]),
        KeyboardButton(m["income"]),
        KeyboardButton(m["detail"]),
        KeyboardButton(m["apply"])
    )
    return markup

def apply_button_menu(lang):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        LANG[lang]["apply_submit"],
        callback_data="submit_apply"
    ))
    return markup

# ====================== 語言切換 ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    try:
        data = init_data()
        user_id = call.from_user.id
        lang = call.data.split("_")[1]
        uid = str(user_id)

        if uid not in data["users"]:
            data["users"][uid] = {
                "username": call.from_user.username,
                "first_name": call.from_user.first_name,
                "is_guarantor": False,
                "guarantor_status": "unapplied",
                "level": 1,
                "balance": 0.0,
                "lang": lang,
                "join_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            data["users"][uid]["lang"] = lang
        save_data(data)

        if lang == "zh_tw":
            bot.answer_callback_query(call.id, "✅ 語言已設定為繁體中文")
        else:
            bot.answer_callback_query(call.id, "✅ Language set to English")

        bot.edit_message_text(
            LANG[lang]["welcome"],
            call.message.chat.id, call.message.message_id,
            reply_markup=user_inline_menu(lang)
        )
        bot.send_message(
            call.message.chat.id,
            "✅ 選單已載入" if lang == "zh_tw" else "✅ Menu loaded",
            reply_markup=user_keyboard_menu(lang)
        )
    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Error")

# ====================== /start ======================
@bot.message_handler(commands=['start'])
def start(message):
    data = init_data()
    user_id = message.from_user.id
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "is_guarantor": False,
            "guarantor_status": "unapplied",
            "level": 1,
            "balance": 0.0,
            "lang": "zh_tw",
            "join_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_data(data)
    bot.send_message(
        message.chat.id,
        t(user_id, "select_lang", data),
        reply_markup=lang_select_menu()
    )

# ====================== 內聯按鈕 ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("in_"))
def callback_inline(call):
    data = init_data()
    user_id = call.from_user.id
    lang = get_user_lang(user_id, data)
    act = call.data[3:]

    if act == "home":
        bot.edit_message_text(
            data["announcement"][lang],
            call.message.chat.id, call.message.id,
            reply_markup=user_inline_menu(lang)
        )
    elif act == "service":
        bot.edit_message_text(
            t(user_id, "service_text", data),
            call.message.chat.id, call.message.id,
            reply_markup=user_inline_menu(lang)
        )
    elif act == "level":
        bot.edit_message_text(
            t(user_id, "level_text", data),
            call.message.chat.id, call.message.id,
            reply_markup=user_inline_menu(lang)
        )
    elif act == "lang":
        bot.edit_message_text(
            t(user_id, "select_lang", data),
            call.message.chat.id, call.message.id,
            reply_markup=lang_select_menu()
        )
    elif act == "create":
        bot.answer_callback_query(call.id, "🚀 發起擔保")
    bot.answer_callback_query(call.id)

# ====================== 提交擔保人申請 ======================
@bot.callback_query_handler(func=lambda call: call.data == "submit_apply")
def submit_apply(call):
    data = init_data()
    user_id = call.from_user.id
    uid = str(user_id)
    lang = get_user_lang(user_id, data)
    user = data["users"][uid]

    if user["guarantor_status"] == "pending":
        bot.answer_callback_query(call.id, t(user_id, "apply_already", data))
        return

    user["guarantor_status"] = "pending"
    apply_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["applications"][uid] = {
        "user_id": user_id,
        "username": user.get("username", ""),
        "first_name": user.get("first_name", ""),
        "time": apply_time,
        "status": "pending"
    }
    save_data(data)

    bot.edit_message_text(
        t(user_id, "apply_sent", data),
        call.message.chat.id, call.message.message_id
    )

    # ====================== 這裡就是發送給管理員 ======================
    notify_admins(
        t(user_id, "admin_new_apply", data).format(
            user_id,
            user.get("username", "-"),
            user.get("first_name", "-"),
            apply_time
        )
    )

# ====================== 訊息處理 ======================
@bot.message_handler(func=lambda msg: True)
def handle_messages(msg):
    data = init_data()
    user_id = msg.from_user.id
    lang = get_user_lang(user_id, data)
    user = data["users"][str(user_id)]
    text = msg.text

    if text == t(user_id, "keyboard.my_order", data):
        bot.send_message(msg.chat.id, "📜 我的擔保", reply_markup=user_keyboard_menu(lang))

    elif text == t(user_id, "keyboard.apply", data):
        bot.send_message(
            msg.chat.id,
            t(user_id, "apply_text", data),
            reply_markup=apply_button_menu(lang)
        )

    elif text == t(user_id, "keyboard.order_mgmt", data):
        bot.send_message(msg.chat.id, "📦 訂單管理", reply_markup=guarantor_keyboard_menu(lang))
    elif text == t(user_id, "keyboard.income", data):
        bot.send_message(msg.chat.id, "💰 收益中心", reply_markup=guarantor_keyboard_menu(lang))
    elif text == t(user_id, "keyboard.detail", data):
        bot.send_message(msg.chat.id, "🧾 資金明細", reply_markup=guarantor_keyboard_menu(lang))

    else:
        bot.send_message(msg.chat.id, t(user_id, "invalid_cmd", data))

# ====================== 管理員指令 ======================
@bot.message_handler(commands=['公告'])
def cmd_announce(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ 您無權使用此功能")
        return
    data = init_data()
    if len(msg.text.split()) < 2:
        bot.reply_to(msg, "❌ 用法：/公告 內容")
        return
    content = msg.text.split(" ", 1)[1]
    data["announcement"]["zh_tw"] = content
    data["announcement"]["en"] = content
    save_data(data)
    bot.reply_to(msg, "✅ 公告已更新")

@bot.message_handler(commands=['審核'])
def cmd_approve(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ 您無權使用此功能")
        return
    data = init_data()
    args = msg.text.split()
    if len(args) < 2:
        bot.reply_to(msg, "❌ 用法：/審核 用戶ID")
        return
    target_uid = args[1]
    if target_uid not in data["users"]:
        bot.reply_to(msg, "❌ 用戶不存在")
        return

    data["users"][target_uid]["is_guarantor"] = True
    data["users"][target_uid]["guarantor_status"] = "approved"
    save_data(data)

    bot.reply_to(msg, "✅ 已通過該用戶申請")
    try:
        bot.send_message(int(target_uid), "✅ 您的擔保人申請已通過！")
    except:
        pass

@bot.message_handler(commands=['拒絕'])
def cmd_reject(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ 您無權使用此功能")
        return
    data = init_data()
    args = msg.text.split()
    if len(args) < 2:
        bot.reply_to(msg, "❌ 用法：/拒絕 用戶ID")
        return
    target_uid = args[1]
    if target_uid not in data["users"]:
        bot.reply_to(msg, "❌ 用戶不存在")
        return

    data["users"][target_uid]["guarantor_status"] = "rejected"
    save_data(data)

    bot.reply_to(msg, "✅ 已拒絕該用戶申請")
    try:
        bot.send_message(int(target_uid), "❌ 您的擔保人申請已被拒絕")
    except:
        pass

@bot.message_handler(commands=['開啟搶單'])
def cmd_grab_on(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ 您無權使用此功能")
        return
    data = init_data()
    data["grab_enabled"] = True
    save_data(data)
    bot.reply_to(msg, "✅ 搶單大廳已開啟")

@bot.message_handler(commands=['關閉搶單'])
def cmd_grab_off(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ 您無權使用此功能")
        return
    data = init_data()
    data["grab_enabled"] = False
    save_data(data)
    bot.reply_to(msg, "✅ 搶單大廳已關閉")

# ====================== 啟動機器人 ======================
if __name__ == "__main__":
    print("✅ 繁體完整 + 管理員通知 修復完成")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except:
            time.sleep(3)
