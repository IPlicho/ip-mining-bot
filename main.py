import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import os
from datetime import datetime
import traceback
import time

# ====================== 核心配置（双管理员） ======================
ADMIN_IDS = [8401979801, 8781082053]  # 两个管理员ID
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ====================== 多语言文案（完全修复）======================
LANG = {
    "zh_tw": {
        # 通用
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
        
        # 內聯按鈕（高級懸浮，不佔鍵盤）
        "inline": {
            "home": "🏠 首頁",
            "service": "📌 擔保項目",
            "create": "🚀 發起擔保",
            "level": "📊 合夥人制度",
            "lang": "🌐 切換語言"
        },
        
        # 鍵盤按鈕（個人功能，固定在鍵盤）
        "keyboard": {
            "my_order": "📜 我的擔保",
            "income": "💰 收益中心",
            "detail": "🧾 資金明細",
            "apply": "🛡️ 擔保入駐",
            "order_mgmt": "📦 訂單管理"
        },
        
        # 首頁
        "home_title": "🏠 TrustEscrow 擔保平台",
        "home_desc": "安全 · 高效 · 可信 · 全程擔保\n所有擔保人經過嚴格審核，訂單可查、過程可控、售後可追溯。",
        
        # 擔保項目
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
        
        # 合夥人制度
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
        
        # 入駐申請
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
        
        # 管理員指令提示
        "admin_announce": "✅ 公告已更新",
        "admin_grab_on": "✅ 搶單大廳已開啟",
        "admin_grab_off": "✅ 搶單大廳已關閉",
        "admin_approve": "✅ 已通過審核",
        "admin_reject": "✅ 已拒絕申請",
        "admin_block": "✅ 已封鎖擔保人",
        "admin_unblock": "✅ 已解除封鎖",
        "admin_level": "✅ 等級已更新",
        "admin_assign": "✅ 派單成功",
        "admin_complete": "✅ 訂單已完成，佣金已結算"
    },
    "en": {
        # General
        "welcome": "👋 Welcome to TrustEscrow Guarantee Platform!\nWe provide professional third-party guarantee services to secure your transactions.",
        "select_lang": "請選擇語言 / Please select language",
        "lang_set": "✅ Language set to Traditional Chinese",
        "lang_set_en": "✅ Language set to English",
        "back": "🔙 Back to Home",
        "contact_admin": "📞 Contact Admin",
        "no_permission": "❌ You do not have permission to use this feature",
        "invalid_cmd": "❌ Invalid command",
        "success": "✅ Operation successful",
        "loading": "⏳ Loading...",
        
        # Inline Buttons (Premium Floating)
        "inline": {
            "home": "🏠 Home",
            "service": "📌 Services",
            "create": "🚀 Create Guarantee",
            "level": "📊 Partner Program",
            "lang": "🌐 Switch Language"
        },
        
        # Keyboard Buttons (Personal Functions)
        "keyboard": {
            "my_order": "📜 My Guarantees",
            "income": "💰 Income Center",
            "detail": "🧾 Transaction History",
            "apply": "🛡️ Apply as Guarantor",
            "order_mgmt": "📦 Order Management"
        },
        
        # Home
        "home_title": "🏠 TrustEscrow Guarantee Platform",
        "home_desc": "Secure · Efficient · Trusted · Full-cycle Guarantee\nAll guarantors are strictly verified, orders traceable, process controllable, after-sales guaranteed.",
        
        # Services
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
        
        # Partner Program
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
        
        # Apply
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
        
        # Admin Commands
        "admin_announce": "✅ Announcement updated",
        "admin_grab_on": "✅ Grab order enabled",
        "admin_grab_off": "✅ Grab order disabled",
        "admin_approve": "✅ Application approved",
        "admin_reject": "✅ Application rejected",
        "admin_block": "✅ Guarantor blocked",
        "admin_unblock": "✅ Guarantor unblocked",
        "admin_level": "✅ Level updated",
        "admin_assign": "✅ Order assigned successfully",
        "admin_complete": "✅ Order completed, commission settled"
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

# ====================== 等級配置 ======================
LEVELS = {
    1: {"name_zh": "見習擔保人", "name_en": "Trainee Guarantor", "grab_rate": 0.05, "assign_rate": 0.15},
    2: {"name_zh": "正式擔保人", "name_en": "Official Guarantor", "grab_rate": 0.07, "assign_rate": 0.20},
    3: {"name_zh": "資深擔保人", "name_en": "Senior Guarantor", "grab_rate": 0.10, "assign_rate": 0.25},
    4: {"name_zh": "核心擔保人", "name_en": "Core Guarantor", "grab_rate": 0.15, "assign_rate": 0.35},
    5: {"name_zh": "合夥人", "name_en": "Partner", "grab_rate": 0.25, "assign_rate": 0.50}
}

# ====================== 工具函數 ======================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_user_lang(user_id, data):
    return data["users"].get(str(user_id), {}).get("lang", "zh_tw")

def t(user_id, key, data, **kwargs):
    lang = get_user_lang(user_id, data)
    # 處理嵌套字典
    if "." in key:
        parts = key.split(".")
        text = LANG[lang]
        for part in parts:
            text = text[part]
    else:
        text = LANG[lang][key]
    if isinstance(text, dict):
        return text
    return text.format(**kwargs)

# ====================== 鍵盤生成 ======================
def lang_select_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("繁體中文", callback_data="lang_zh_tw"),
        InlineKeyboardButton("English", callback_data="lang_en")
    )
    return markup

# 普通用戶內聯按鈕（高級懸浮）
def user_inline_menu(lang):
    markup = InlineKeyboardMarkup()
    menu = LANG[lang]["inline"]
    markup.row(
        InlineKeyboardButton(menu["home"], callback_data="menu_home"),
        InlineKeyboardButton(menu["service"], callback_data="menu_service")
    )
    markup.row(
        InlineKeyboardButton(menu["create"], callback_data="menu_create"),
        InlineKeyboardButton(menu["level"], callback_data="menu_level")
    )
    markup.row(
        InlineKeyboardButton(menu["lang"], callback_data="menu_lang")
    )
    return markup

# 普通用戶鍵盤按鈕（個人功能）
def user_keyboard_menu(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    menu = LANG[lang]["keyboard"]
    markup.add(
        KeyboardButton(menu["my_order"])
    )
    return markup

# 擔保人內聯按鈕（高級懸浮）
def guarantor_inline_menu(lang):
    markup = InlineKeyboardMarkup()
    menu = LANG[lang]["inline"]
    markup.row(
        InlineKeyboardButton(menu["home"], callback_data="menu_home"),
        InlineKeyboardButton(menu["service"], callback_data="menu_service")
    )
    markup.row(
        InlineKeyboardButton(menu["create"], callback_data="menu_create"),
        InlineKeyboardButton(menu["level"], callback_data="menu_level")
    )
    markup.row(
        InlineKeyboardButton(menu["lang"], callback_data="menu_lang")
    )
    return markup

# 擔保人鍵盤按鈕（個人功能）
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

# ====================== 語言切換處理（修復點擊無反應）======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    try:
        data = init_data()
        user_id = call.from_user.id
        lang = call.data.split("_")[1]
        
        # 初始化用戶數據
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
        
        # 回調響應
        if lang == "zh_tw":
            bot.answer_callback_query(call.id, t(user_id, "lang_set", data))
            # 發送歡迎語+雙按鈕菜單
            bot.send_message(
                call.message.chat.id,
                t(user_id, "welcome", data),
                reply_markup=user_inline_menu("zh_tw")
            )
            bot.send_message(
                call.message.chat.id,
                "✅ 菜單已加載",
                reply_markup=user_keyboard_menu("zh_tw")
            )
        else:
            bot.answer_callback_query(call.id, t(user_id, "lang_set_en", data))
            bot.send_message(
                call.message.chat.id,
                t(user_id, "welcome", data),
                reply_markup=user_inline_menu("en")
            )
            bot.send_message(
                call.message.chat.id,
                "✅ Menu loaded",
                reply_markup=user_keyboard_menu("en")
            )
    except Exception as e:
        traceback.print_exc()
        bot.answer_callback_query(call.id, "❌ Error, please try again")

# ====================== 啟動處理 ======================
@bot.message_handler(commands=['start'])
def start(message):
    try:
        data = init_data()
        user_id = message.from_user.id
        
        # 初始化用戶數據
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
        
        # 彈出語言選擇
        bot.send_message(
            message.chat.id,
            t(user_id, "select_lang", data),
            reply_markup=lang_select_menu()
        )
    except Exception as e:
        traceback.print_exc()
        bot.send_message(message.chat.id, "❌ System error, please try again later")

# ====================== 內聯菜單回調處理 ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def menu_callback(call):
    try:
        data = init_data()
        user_id = call.from_user.id
        lang = get_user_lang(user_id, data)
        action = call.data.split("_")[1]
        
        if action == "home":
            # 首頁
            announcement = data["announcement"][lang]
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=announcement,
                reply_markup=user_inline_menu(lang) if not data["users"][str(user_id)]["is_guarantor"] else guarantor_inline_menu(lang)
            )
            bot.answer_callback_query(call.id)
        elif action == "service":
            # 擔保項目
            title = t(user_id, "service_title", data)
            content = t(user_id, "service_list", data)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{title}\n{content}",
                reply_markup=user_inline_menu(lang) if not data["users"][str(user_id)]["is_guarantor"] else guarantor_inline_menu(lang)
            )
            bot.answer_callback_query(call.id)
        elif action == "level":
            # 合夥人制度
            title = t(user_id, "level_title", data)
            desc = t(user_id, "level_desc", data)
            content = t(user_id, "level_list", data)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{title}\n{desc}\n{content}",
                reply_markup=user_inline_menu(lang) if not data["users"][str(user_id)]["is_guarantor"] else guarantor_inline_menu(lang)
            )
            bot.answer_callback_query(call.id)
        elif action == "lang":
            # 切換語言
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=t(user_id, "select_lang", data),
                reply_markup=lang_select_menu()
            )
            bot.answer_callback_query(call.id)
        elif action == "create":
            # 發起擔保（後續補全功能）
            bot.answer_callback_query(call.id, "⏳ Feature coming soon")
    except Exception as e:
        traceback.print_exc()
        bot.answer_callback_query(call.id, "❌ Error, please try again")

# ====================== 管理員指令（雙管理員通用）======================
@bot.message_handler(commands=['公告', 'announce'])
def set_announcement(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, t(message.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    text = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    data["announcement"]["zh_tw"] = text
    data["announcement"]["en"] = text
    save_data(data)
    bot.send_message(message.chat.id, t(message.from_user.id, "admin_announce", data))

@bot.message_handler(commands=['開啟搶單', 'enable_grab'])
def enable_grab(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, t(message.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    data["grab_enabled"] = True
    save_data(data)
    bot.send_message(message.chat.id, t(message.from_user.id, "admin_grab_on", data))

@bot.message_handler(commands=['關閉搶單', 'disable_grab'])
def disable_grab(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, t(message.from_user.id, "no_permission", init_data()))
        return
    data = init_data()
    data["grab_enabled"] = False
    save_data(data)
    bot.send_message(message.chat.id, t(message.from_user.id, "admin_grab_off", data))

# ====================== 異常捕獲與防崩潰 ======================
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        data = init_data()
        user_id = message.from_user.id
        lang = get_user_lang(user_id, data)
        
        # 處理鍵盤按鈕
        if message.text == t(user_id, "keyboard.my_order", data):
            bot.send_message(message.chat.id, "⏳ My Guarantees coming soon", reply_markup=user_keyboard_menu(lang))
        elif message.text == t(user_id, "keyboard.order_mgmt", data):
            bot.send_message(message.chat.id, "⏳ Order Management coming soon", reply_markup=guarantor_keyboard_menu(lang))
        elif message.text == t(user_id, "keyboard.income", data):
            bot.send_message(message.chat.id, "⏳ Income Center coming soon", reply_markup=guarantor_keyboard_menu(lang))
        elif message.text == t(user_id, "keyboard.detail", data):
            bot.send_message(message.chat.id, "⏳ Transaction History coming soon", reply_markup=guarantor_keyboard_menu(lang))
        elif message.text == t(user_id, "keyboard.apply", data):
            title = t(user_id, "apply_title", data)
            content = t(user_id, "apply_desc", data)
            bot.send_message(message.chat.id, f"{title}\n{content}", reply_markup=guarantor_keyboard_menu(lang))
        else:
            bot.send_message(message.chat.id, t(user_id, "invalid_cmd", data))
    except Exception as e:
        traceback.print_exc()
        bot.send_message(message.chat.id, "❌ System error, please try again later")

# ====================== 啟動機器人 ======================
if __name__ == "__main__":
    print("🤖 TrustEscrow 雙管理員雙按鈕雙語穩定版啟動中...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            traceback.print_exc()
            time.sleep(5)
            print("🔄 機器人崩潰，5秒後重啟...")
