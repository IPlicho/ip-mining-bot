import telebot

# 【你的中间人机器人专属Token，直接用】
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
# 【管理员ID】填你自己的Telegram用户ID（用@UserInfo机器人查，只有你能操作）
ADMIN_ID = 123456789  # 这里替换成你的真实ID
bot = telebot.TeleBot(BOT_TOKEN)

# 【中间人端主菜单】和用户端同风格，带接单/派单入口
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("📋 待接单列表")
    btn2 = telebot.types.KeyboardButton("✅ 已派单订单")
    btn3 = telebot.types.KeyboardButton("ℹ️ 管理员说明")
    markup.add(btn1, btn2, btn3)
    return markup

# 【/start 触发菜单，仅管理员可进入】
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "✅ 中间人端管理员已登录！欢迎使用接单/派单系统👇",
            reply_markup=main_menu()
        )
    else:
        bot.send_message(message.chat.id, "❌ 您无权限使用此系统！")

# 【菜单按钮响应逻辑】
@bot.message_handler(func=lambda msg: True)
def handle_menu(message):
    # 权限校验，非管理员直接拦截
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ 您无权限使用此系统！")
        return
    
    # 菜单功能响应
    if message.text == "📋 待接单列表":
        bot.send_message(message.chat.id, "📋 这里是所有待接单的担保订单，可查看详情、接单")
    elif message.text == "✅ 已派单订单":
        bot.send_message(message.chat.id, "✅ 这里是已派单的订单，可跟进进度、完成订单")
    elif message.text == "ℹ️ 管理员说明":
        bot.send_message(message.chat.id, "ℹ️ 中间人端仅管理员可操作，用于担保订单的接单、派单、管理，保障交易安全")
    else:
        # 通用消息回复
        bot.send_message(message.chat.id, f"收到指令：{message.text}")

# 【运行入口，和用户端完全一致】
if __name__ == "__main__":
    bot.polling(none_stop=True)
