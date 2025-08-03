import telebot

TOKEN = 'твой_токен_бота_сюда'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот работает!")

bot.polling(non_stop=True)
