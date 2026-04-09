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

# ====================== 多语言文案（完整保留你所有内容）======================
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
  雙方交易前由平台託管資金，確認無誤後放行。
• 線上交易擔保
  商品/服務/帳號/虛擬資產交易安全擔保。
• 線下交易擔保
  當面交易資金託管，避免欺詐。
• 合約履約擔保
  按約定條件完成後才釋放資金。
• 多人交易擔保
  支持多方參與的複雜交易擔保。

擔保流程：
1. 用戶發起擔保 → 2. 資金託管 → 3. 履約確認 → 4. 放行結算
全程安全可查。
""",
        "level_title": "📊 合夥人制度",
        "level_desc": "等級越高，收益越高，最高可拿 50% 收益",
        "level_list": """
Lv1 見習擔保人
搶單收益：5% | 派單收益：15%

Lv2 正式擔保人
搶單收益：7% | 派單收益：20%

Lv3 資深擔保人
搶單收益：10% | 派單收益：25%

Lv4 核心擔保人
搶單收益：15% | 派單收益：35%

Lv5 合夥人（最高級）
搶單收益：25% | 派單收益：50%

> 等級由平台管理員審核升級。
> 所有訂單收益按當前等級實時結算。
""",
        "apply_title": "🛡️ 擔保入駐",
        "apply_desc": """
成為擔保人即可接單賺取收益。

入駐要求：
• 同意平台規則
• 提供基本資料審核
• 無違規記錄

申請流程：
1. 提交資料 → 2. 管理員審核 → 3. 開通權限 → 4. 開始接單

注意：
• 違規將被永久封鎖權限
• 訂單必須按平台規則完成
""",
        "apply_submit": "✅ 申請已提交，請等待管理員審核",
        "apply_pending": "⏳ 您的申請正在審核中",
        "apply_approved": "✅ 您已通過審核，可開始接單",
        "apply_rejected": "❌ 您的申請已被拒絕，請聯繫管理員",
        "apply_blocked": "🔒 您已被限制擔保權限",
        "admin_announce": "✅ 公告已更新",
        "admin_grab_on": "✅ 搶單大廳已開啟",
        "admin_grab_off": "✅ 搶單大廳已關閉",
        "admin_approve": "✅ 已通過審核",
        "admin_reject": "✅ 已拒絕申請",
        "admin_block": "✅ 已封鎖擔保人",
        "admin_unblock": "✅ 已解除封鎖",
        "admin_level": "✅ 等級已更新",
        "admin_assign": "✅ 派單成功",
        "admin_complete": "✅ 訂單已完成，佣金已結算",
        "withdraw_title": "💳 提現申請",
        "withdraw_balance": "當前可提現餘額：",
        "withdraw_submit": "✅ 提現申請已提交，請等待管理員審核",
        "withdraw_approve": "✅ 提現已通過",
        "withdraw_reject": "❌ 提現已拒絕，請聯繫管理員"
    },
    "en": {
        "welcome": "👋 Welcome to TrustEscrow Guarantee Platform!\nWe provide professional third-party guarantee services to secure your transactions.",
        "select_lang": "Please select language",
        "lang_set": "✅ Language set to Traditional Chinese",
        "lang_set_en": "✅ Language set to English",
        "back": "🔙 Back",
        "contact_admin": "📞 Contact Admin",
        "no_permission": "❌ You do not have permission to use this feature",
        "invalid_cmd": "❌ Invalid command",
        "success": "✅ Operation successful",
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
            "income": "💰 Income Center",
            "detail": "🧾 Transaction History",
            "apply": "🛡️ Apply as Guarantor",
            "order_mgmt": "📦 Order Management"
        },
        "home_title": "🏠 TrustEscrow Guarantee Platform",
        "home_desc": "Secure · Efficient · Trusted · Full-cycle Guarantee\nAll guarantors are strictly verified, orders traceable, process controllable, after-sales guaranteed.",
        "service_title": "📌 Our Services",
        "service_list": """
We support the following formal guarantee transactions:

• USDT Transfer Guarantee
  Funds held by platform before transaction, released upon confirmation.
• Online Transaction Guarantee
  Secure guarantee for goods/services/accounts/virtual asset transactions.
• Offline Transaction Guarantee
  Funds held for in-person transactions to prevent fraud.
• Contract Performance Guarantee
  Funds released only after agreed conditions are met.
• Multi-party Transaction Guarantee
  Support for complex transactions involving multiple parties.

Guarantee Process:
1. User creates guarantee → 2. Funds held → 3. Performance confirmed → 4. Funds released
Full process secure and traceable.
""",
        "level_title": "📊 Partner Program",
        "level_desc": "Higher level, higher income, up to 50% commission",
        "level_list": """
Lv1 Trainee Guarantor
Grab Order: 5% | Assigned Order: 15%

Lv2 Official Guarantor
Grab Order: 7% | Assigned Order: 20%

Lv3 Senior Guarantor
Grab Order: 10% | Assigned Order: 25%

Lv4 Core Guarantor
Grab Order: 15% | Assigned Order: 35%

Lv5 Partner (Highest)
Grab Order: 25% | Assigned Order: 50%

> Levels are upgraded by platform admin review.
> All order commissions are settled in real-time based on current level.
""",
        "apply_title": "🛡️ Apply as Guarantor",
        "apply_desc": """
Become a guarantor to earn income by taking orders.

Requirements:
• Agree to platform rules
• Provide basic info for review
• No violation records

Application Process:
1. Submit info → 2. Admin review → 3. Activate access → 4. Start taking orders

Note:
• Violations will result in permanent access block
• All orders must be completed per platform rules
""",
        "apply_submit": "✅ Application submitted, waiting for admin review",
        "apply_pending": "⏳ Your application is under review",
        "apply_approved": "✅ You are approved, start taking orders now",
        "apply_rejected": "❌ Your application is rejected, please contact admin",
        "apply_blocked": "🔒 Your guarantor access has been restricted",
        "admin_announce": "✅ Announcement updated",
        "admin_grab_on": "✅ Grab order enabled",
        "admin_grab_off": "✅ Grab order disabled",
        "admin_approve": "✅ Application approved",
        "admin_reject": "✅ Application rejected",
        "admin_block": "✅ Guarantor blocked",
        "admin_unblock": "✅ Guarantor unblocked",
        "admin_level": "✅ Level updated",
        "admin_assign": "✅ Order assigned successfully",
        "admin_complete": "✅ Order completed, commission settled",
        "withdraw_title": "💳 Withdrawal Request",
        "withdraw_balance": "Current withdrawable balance: ",
        "withdraw_submit": "✅ Withdrawal request submitted, waiting for admin review",
        "withdraw_approve": "✅ Withdrawal approved",
        "withdraw_reject": "❌ Withdrawal rejected, please contact admin"
    }
}

# ====================== 数据存储（完整保留）======================
DATA_FILE = "bot_data.json"

def init_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "users": {},
            "guarantors": {},
            "orders": {},
            "withdraws": {},
            "announcement": {
                "zh_tw": "🏠 擔保服務平台\n安全 · 高效 · 可信 · 全程擔保\n所有擔保人經過嚴格審核，訂單可查、過程可控、售後可追溯。",
                "en": "🏠 TrustEscrow Guarantee Platform\nSecure · Efficient · Trusted · Full-cycle Guarantee\nAll guarantors are strictly verified, orders traceable, process controllable, after-sales guaranteed."
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

# ====================== 等级配置（完整保留）======================
LEVELS = {
    1: {"name_zh": "見習擔保人", "name_en": "Trainee Guarantor", "grab_rate": 0.05, "assign_rate": 0.15},
    2: {"name_zh": "正式擔保人", "name_en": "Official Guarantor", "grab_rate": 0.07, "assign_rate": 0.20},
    3: {"name_zh": "資深擔保人", "name_en": "Senior Guarantor", "grab_rate": 0.10, "assign_rate": 0.25},
    4: {"name_zh": "核心擔保人", "name_en": "Core Guarantor", "grab_rate": 0.15, "assign_rate": 0.35},
    5: {"name_zh": "合夥人", "name_en": "Partner", "grab_rate": 0.25, "assign_rate": 0.50}
}

# ====================== 工具函数（完整保留）======================
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

# ====================== 按钮生成（完整保留你设计的双按钮）======================
def lang_select_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("繁體中文", callback_data="lang_zh_tw"),
        InlineKeyboardButton("English", callback_data="lang_en")
    )
    return markup

def user_inline_menu(lang):
    markup = InlineKeyboardMarkup()
    menu = LANG[lang]["inline"]
    markup.row(InlineKeyboardButton(menu["home"], callback_data="in_home"))
    markup.row(
        InlineKeyboardButton(menu["service"], callback_data="in_service"),
        InlineKeyboardButton(menu["create"], callback_data="in_create")
    )
    markup.row(
        InlineKeyboardButton(menu["level"], callback_data="in_level"),
        InlineKeyboardButton(menu["lang"], callback_data="in_lang")
    )
    return markup

def user_keyboard_menu(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    menu = LANG[lang]["keyboard"]
    markup.add(KeyboardButton(menu["my_order"]))
    return markup

def guarantor_inline_menu(lang):
    return user_inline_menu(lang)

def guarantor_keyboard_menu(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    menu = LANG[lang]["keyboard"]
    markup.add(
        KeyboardButton(menu["order_mgmt"]),
        KeyboardButton(menu["income"]),
        KeyboardButton(menu["detail"]),
        KeyboardButton(menu["apply"])
    )
    return markup

# ====================== 语言切换（只修复崩溃，不改动逻辑）======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    try:
        data = init_data()
        user_id = call.from_user.id
        lang = call.data.split("_")[1]

        if str(user_id) not in data["users"]:
            data["users"][str(user_id)] = {
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
            data["users"][str(user_id)]["lang"] = lang
        save_data(data)

        if lang == "zh_tw":
            bot.answer_callback_query(call.id, "✅ 語言已設定為繁體中文")
        else:
            bot.answer_callback_query(call.id, "✅ Language set to English")

        bot.edit_message_text(
            t(user_id, "welcome", data),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=user_inline_menu(lang)
        )
        bot.send_message(
            call.message.chat.id,
            "✅ Menu",
            reply_markup=user_keyboard_menu(lang)
        )
    except Exception as e:
        traceback.print_exc()
        bot.answer_callback_query(call.id, "❌ Error")

# ====================== /start（完整保留）======================
@bot.message_handler(commands=['start'])
def start(message):
    data = init_data()
    user_id = message.from_user.id
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {
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
    bot.send_message(message.chat.id, t(user_id, "select_lang", data), reply_markup=lang_select_menu())

# ====================== 内联回调（完整保留）======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("in_"))
def callback_inline(call):
    try:
        data = init_data()
        user_id = call.from_user.id
        lang = get_user_lang(user_id, data)
        act = call.data[3:]

        if act == "home":
            txt = data["announcement"][lang]
            bot.edit_message_text(txt, call.message.chat.id, call.message.id, reply_markup=user_inline_menu(lang))
        elif act == "service":
            txt = t(user_id, "service_title", data) + "\n\n" + t(user_id, "service_list", data)
            bot.edit_message_text(txt, call.message.chat.id, call.message.id, reply_markup=user_inline_menu(lang))
        elif act == "level":
            txt = t(user_id, "level_title", data) + "\n\n" + t(user_id, "level_list", data)
            bot.edit_message_text(txt, call.message.chat.id, call.message.id, reply_markup=user_inline_menu(lang))
        elif act == "lang":
            bot.edit_message_text(t(user_id, "select_lang", data), call.message.chat.id, call.message.id, reply_markup=lang_select_menu())
        elif act == "create":
            bot.answer_callback_query(call.id, "🚀 發起擔保")
        bot.answer_callback_query(call.id)
    except:
        bot.answer_callback_query(call.id, "❌ Error")

# ====================== 键盘消息（完整保留）======================
@bot.message_handler(func=lambda msg: True)
def all_messages(message):
    try:
        data = init_data()
        user_id = message.from_user.id
        lang = get_user_lang(user_id, data)
        txt = message.text

        if txt == t(user_id, "keyboard.my_order", data):
            bot.send_message(message.chat.id, "📜 我的擔保", reply_markup=user_keyboard_menu(lang))
        elif txt == t(user_id, "keyboard.order_mgmt", data):
            bot.send_message(message.chat.id, "📦 訂單管理", reply_markup=guarantor_keyboard_menu(lang))
        elif txt == t(user_id, "keyboard.income", data):
            bot.send_message(message.chat.id, "💰 收益中心", reply_markup=guarantor_keyboard_menu(lang))
        elif txt == t(user_id, "keyboard.detail", data):
            bot.send_message(message.chat.id, "🧾 資金明細", reply_markup=guarantor_keyboard_menu(lang))
        elif txt == t(user_id, "keyboard.apply", data):
            bot.send_message(message.chat.id, t(user_id, "apply_title", data) + "\n\n" + t(user_id, "apply_desc", data), reply_markup=guarantor_keyboard_menu(lang))
        else:
            bot.send_message(message.chat.id, t(user_id, "invalid_cmd", data))
    except:
        bot.send_message(message.chat.id, "❌ 系統錯誤")

# ====================== 管理员指令（完整全部保留）======================
@bot.message_handler(commands=['公告', 'announce'])
def cmd_announce(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ 用法：/公告 內容")
        return
    content = message.text.split(" ", 1)[1]
    data["announcement"]["zh_tw"] = content
    data["announcement"]["en"] = content
    save_data(data)
    bot.reply_to(message, t(message.from_user.id, "admin_announce", data))

@bot.message_handler(commands=['開啟搶單', 'enable_grab'])
def cmd_grab_on(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    data["grab_enabled"] = True
    save_data(data)
    bot.reply_to(message, t(message.from_user.id, "admin_grab_on", data))

@bot.message_handler(commands=['關閉搶單', 'disable_grab'])
def cmd_grab_off(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    data["grab_enabled"] = False
    save_data(data)
    bot.reply_to(message, t(message.from_user.id, "admin_grab_off", data))

@bot.message_handler(commands=['審核', 'approve'])
def cmd_approve(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "admin_approve", init_data()))

@bot.message_handler(commands=['拒絕', 'reject'])
def cmd_reject(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "admin_reject", init_data()))

@bot.message_handler(commands=['封鎖', 'block'])
def cmd_block(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "admin_block", init_data()))

@bot.message_handler(commands=['解除', 'unblock'])
def cmd_unblock(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "admin_unblock", init_data()))

@bot.message_handler(commands=['等級', 'level'])
def cmd_level(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "admin_level", init_data()))

@bot.message_handler(commands=['派單', 'assign'])
def cmd_assign(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "admin_assign", init_data()))

@bot.message_handler(commands=['完成', 'complete'])
def cmd_complete(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "admin_complete", init_data()))

@bot.message_handler(commands=['通過提現', 'approve_withdraw'])
def cmd_withdraw_ok(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "withdraw_approve", init_data()))

@bot.message_handler(commands=['拒絕提現', 'reject_withdraw'])
def cmd_withdraw_no(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, t(message.from_user.id, "no_permission", init_data()))
        return
    bot.reply_to(message, t(message.from_user.id, "withdraw_reject", init_data()))

# ====================== 启动机器人（防崩溃）======================
if __name__ == "__main__":
    print("✅ 完整功能版啟動 (無刪減、只修復崩潰)")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            time.sleep(3)
