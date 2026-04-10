import telebot

# 中间人端专属Token（直接用你从@BotFather复制的）
BOT_TOKEN = "8747559514:AAE_N9M9CallB4rYV0lbyny_0tGJnz3hLYU"
# 这里先填一个临时数字，你本地运行时再换成自己的真实ID，Railway部署先保证不崩溃
ADMIN_ID = 123456789
bot = telebot.TeleBot(BOT_TOKEN)

# 中间人端主菜单
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("📋 待接单列表")
    btn2 = telebot.types.KeyboardButton("✅ 已派单订单")
    btn3 = telebot.types.KeyboardButton("ℹ️ 管理员说明")
    markup.add(btn1, btn2, btn3)
    return markup

# /start触发菜单
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

# 菜单按钮响应
@bot.message_handler(func=lambda msg: True)
def handle_menu(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ 您无权限使用此系统！")
        return
    
    if message.text == "📋 待接单列表":
        bot.send_message(message.chat.id, "📋 待接单订单列表")
    elif message.text == "✅ 已派单订单":
        bot.send_message(message.chat.id, "✅ 已派单订单列表")
    elif message.text == "ℹ️ 管理员说明":
        bot.send_message(message.chat.id, "ℹ️ 中间人端仅管理员可操作，用于接单/派单")
    else:
        bot.send_message(message.chat.id, f"收到：{message.text}")

# 运行入口
if __name__ == "__main__":
    bot.polling(none_stop=True)
