import telebot
from telebot import types
import random

TOKEN = '8366715994:AAFf09auAmguMGv_8fPHSaD9L4twOHteAo4'
OWNER_ID = 2106708967
ADMIN_IDS = [OWNER_ID, 7841720739]

bot = telebot.TeleBot(TOKEN)

user_reports = {}
all_reports = {}
report_counter = 0
complaint_data = {}
blocked_users = set()

# Для пранка — список шуток и индекс для каждого пользователя
prank_jokes = [
    "😂 Ты только что удалил интернет. Перезапусти холодильник!",
    "🛑 Вы были временно переведены в бан... Шутка 😜",
    "👻 Сзади тебя... ой, это твоя тень.",
    "🔇 У тебя теперь нет микрофона... в Телеграме.",
    "💣 Бот самоуничтожится через... 3... 2... 1... Шутка!",
    "📵 У тебя заблокирован Telegram. Перезвони в ICQ!",
    "🎯 Ты выиграл... ничего! Поздравляю!",
    "🐒 Обезьяна взломала твой аккаунт. Но не бойся, она добрая.",
    "🎉 Сегодня твой день! Но это был вчера.",
    "🦄 Единорог только что лайкнул твою жалобу.",
    "🚫 Ты больше не можешь использовать кнопки. Или можешь?",
    "🤡 Ты в цирке. Только не забудь выйти!",
    "🎮 Ты случайно активировал режим: 'бесполезная кнопка'.",
    "📦 Упс! Ты заказал ананас в коробке!",
    "😈 Ты только что вызвал баги. Бот уже чинится.",
    "🪐 Ты отправлен на Марс... Жди сигнала.",
    "🥷 Хакер вошел в систему... шутка, это ты.",
    "🔋 Заряд бота на 1%. Помоги лайком!",
    "🧠 Уровень IQ превышен. Перезапуск!",
    "📡 Ты включил WiFi другим пользователям. Благодарим!"
]
user_prank_index = {}

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("📩 Отправить жалобу", callback_data="send_report"),
        types.InlineKeyboardButton("📞 Связь с владельцем", callback_data="contact_owner"),
        types.InlineKeyboardButton("📋 Мои заявки", callback_data="my_reports"),
        types.InlineKeyboardButton("👁 Просмотренные заявки", callback_data="viewed_reports"),
        types.InlineKeyboardButton("ℹ️ Правила бота", callback_data="rules"),
        types.InlineKeyboardButton("🔄 Обновить меню", callback_data="refresh_menu"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
        types.InlineKeyboardButton("🛑 Заблокировать", callback_data="block_user"),
        types.InlineKeyboardButton("✅ Разблокировать", callback_data="unblock_user"),
        types.InlineKeyboardButton("📝 Написать сообщение", callback_data="send_message"),
        types.InlineKeyboardButton("🗑 Очистить мои заявки", callback_data="clear_reports"),
        types.InlineKeyboardButton("⛔ Poslat' nahui", callback_data="poslat_nahui"),
        types.InlineKeyboardButton("🎭 Пранк", callback_data="prank_user")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в службу поддержки 24/7!\n\n"
        "Выбери действие в меню ниже или просто напиши 'жалоба', чтобы сразу начать жалобу.",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text and message.text.lower() == "жалоба")
def start_report_text(message):
    user_id = message.from_user.id
    complaint_data[user_id] = {}
    bot.send_message(message.chat.id, "🔹 Шаг 1/6: Укажи свой юзернейм (или напиши 'без ника'):")
    bot.register_next_step_handler(message, process_username)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    global report_counter

    # Обработка кнопок одобрения/отклонения жалоб админом
    if call.data.startswith("approve_") or call.data.startswith("reject_"):
        action, rid_str = call.data.split("_")
        rid = int(rid_str)
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "❌ У вас нет прав на это действие.", show_alert=True)
            return

        report = all_reports.get(rid)
        if not report:
            bot.answer_callback_query(call.id, "⚠️ Жалоба не найдена.", show_alert=True)
            Return
if report['status'] != 'В ожидании':
            bot.answer_callback_query(call.id, "ℹ️ Эта жалоба уже обработана.", show_alert=True)
            return

        if action == "approve":
            report['status'] = 'Принята'
            bot.send_message(report['user_id'], f"✅ Ваша жалоба №{rid} принята в обработку.")
            bot.answer_callback_query(call.id, "Жалоба принята.")
        elif action == "reject":
            report['status'] = 'Отклонена'
            bot.send_message(report['user_id'], f"❌ Ваша жалоба №{rid} отклонена владельцем.")
            bot.answer_callback_query(call.id, "Жалоба отклонена.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        return

    # Основное меню кнопок
    if call.data == "send_report":
        complaint_data[user_id] = {}
        bot.send_message(call.message.chat.id, "🔹 Шаг 1/6: Укажи свой юзернейм (или напиши 'без ника'):")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_username)

    elif call.data == "contact_owner":
        bot.send_message(call.message.chat.id, "📨 Связаться с владельцем: @WellLoveyou")

    elif call.data == "my_reports":
        reports = user_reports.get(user_id, [])
        if not reports:
            bot.send_message(call.message.chat.id, "📭 У тебя пока нет отправленных жалоб.")
        else:
            text = ""
            for r in reports:
                text += f"🆔 Жалоба #{r['id']}\n⚠️ Причина: {r['reason'][:50]}{'...' if len(r['reason'])>50 else ''}\nСтатус: {r['status']}\n\n"
            bot.send_message(call.message.chat.id, f"📋 Твои жалобы:\n\n{text}")

    elif call.data == "viewed_reports":
        reports = user_reports.get(user_id, [])
        viewed = [r for r in reports if r['status'] != 'В ожидании']
        if not viewed:
            bot.send_message(call.message.chat.id, "👁 Нет обработанных заявок.")
        else:
            text = ""
            for r in viewed:
                text += f"🆔 Жалоба #{r['id']}\n⚠️ Причина: {r['reason'][:50]}{'...' if len(r['reason'])>50 else ''}\nСтатус: {r['status']}\n\n"
            bot.send_message(call.message.chat.id, f"👁 Просмотренные заявки:\n\n{text}")

    elif call.data == "rules":
        bot.send_message(call.message.chat.id, "📜 Правила бота:\n- Пиши только по теме\n- Не используй мат и оскорбления\n- Уважай других\n- Не спамь")

    elif call.data == "refresh_menu":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=main_menu())

    elif call.data == "help":
        bot.send_message(call.message.chat.id,
            "❓ *Помощь по боту:*\n"
            "- Используй кнопки меню для навигации\n"
            "- Отправляй жалобы подробно\n"
            "- Связывайся с владельцем через кнопку\n"
            "- Для возврата в меню напиши /start", parse_mode="Markdown")

    elif call.data == "block_user":
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "❌ У вас нет прав блокировать пользователей.", show_alert=True)
            return
        bot.send_message(call.message.chat.id, "Введите ID пользователя для блокировки:")
        bot.register_next_step_handler(call.message, block_user_step)

    elif call.data == "unblock_user":
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "❌ У вас нет прав разблокировать пользователей.", show_alert=True)
            return
        bot.send_message(call.message.chat.id, "Введите ID пользователя для разблокировки:")
        bot.register_next_step_handler(call.message, unblock_user_step)

    elif call.data == "send_message":
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "❌ У вас нет прав отправлять сообщения пользователям.", show_alert=True)
            return
        bot.send_message(call.message.chat.id, "Введите ID пользователя, которому хотите написать:")
        bot.register_next_step_handler(call.message, send_message_step_user)
elif call.data == "clear_reports":
        user_reports[user_id] = []
        bot.send_message(call.message.chat.id, "🗑 Ваши заявки очищены.")

    elif call.data == "poslat_nahui":
        bot.send_message(call.message.chat.id, "🖕 Ну вот и послал!")

    elif call.data == "prank_user":
        # Пранк — меняем шутку на новую для пользователя, чтобы не было повторов подряд
        idx = user_prank_index.get(user_id, -1)
        next_idx = (idx + 1) % len(prank_jokes)
        user_prank_index[user_id] = next_idx
        bot.send_message(call.message.chat.id, prank_jokes[next_idx])

def block_user_step(message):
    try:
        uid = int(message.text.strip())
        blocked_users.add(uid)
        bot.send_message(message.chat.id, f"🚫 Пользователь с ID {uid} заблокирован.")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка: введите корректный числовой ID.")

def unblock_user_step(message):
    try:
        uid = int(message.text.strip())
        if uid in blocked_users:
            blocked_users.remove(uid)
            bot.send_message(message.chat.id, f"✅ Пользователь с ID {uid} разблокирован.")
        else:
            bot.send_message(message.chat.id, "ℹ️ Этот пользователь не был заблокирован.")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка: введите корректный числовой ID.")

def send_message_step_user(message):
    try:
        uid = int(message.text.strip())
        bot.send_message(message.chat.id, f"Введите сообщение для пользователя с ID {uid}:")
        bot.register_next_step_handler(message, send_message_step_text, uid)
    except:
        bot.send_message(message.chat.id, "❌ Ошибка: введите корректный числовой ID.")

def send_message_step_text(message, uid):
    text = message.text.strip()
    try:
        bot.send_message(uid, f"📩 Сообщение от администрации:\n\n{text}")
        bot.send_message(message.chat.id, "✅ Сообщение отправлено.")
    except:
        bot.send_message(message.chat.id, "❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.")

def process_username(message):
    user_id = message.from_user.id
    if user_id in blocked_users:
        bot.send_message(message.chat.id, "🚫 Вы заблокированы и не можете отправлять жалобы.")
        return
    username = message.text.strip()
    if not username:
        username = "без ника"
    complaint_data[user_id] = {'user_username': username, 'user_id': user_id}
    bot.send_message(message.chat.id, "🔹 Шаг 2/6: Опиши подробно причину жалобы (мин. 10 символов):")
    bot.register_next_step_handler(message, process_reason)

def process_reason(message):
    user_id = message.from_user.id
    if user_id in blocked_users:
        bot.send_message(message.chat.id, "🚫 Вы заблокированы и не можете отправлять жалобы.")
        return
    reason = message.text.strip()
    if len(reason) < 10:
        msg = bot.send_message(message.chat.id, "⚠️ Слишком коротко. Опиши подробнее (мин. 10 символов):")
        bot.register_next_step_handler(msg, process_reason)
        return
    complaint_data[user_id]['reason'] = reason
    bot.send_message(message.chat.id, "🔹 Шаг 3/6: Укажи юзернейм нарушителя (или 'без ника'):")
    bot.register_next_step_handler(message, process_violator_username)

def process_violator_username(message):
    user_id = message.from_user.id
    if user_id in blocked_users:
        bot.send_message(message.chat.id, "🚫 Вы заблокированы и не можете отправлять жалобы.")
        return
    violator_username = message.text.strip()
    if not violator_username:
        violator_username = "без ника"
    complaint_data[user_id]['violator_username'] = violator_username
    bot.send_message(message.chat.id, "🔹 Шаг 4/6: Укажи ID нарушителя (число):")
bot.register_next_step_handler(message, process_violator_id)
def process_violator_id(message):
    user_id = message.from_user.id
    if user_id in blocked_users:
        bot.send_message(message.chat.id, "🚫 Вы заблокированы и не можете отправлять жалобы.")
        return
    if not message.text.strip().isdigit():
        msg = bot.send_message(message.chat.id, "⚠️ ID должен быть числом. Попробуй ещё раз:")
        bot.register_next_step_handler(msg, process_violator_id)
        return
    complaint_data[user_id]['violator_id'] = int(message.text.strip())
    bot.send_message(message.chat.id, "🔹 Шаг 5/6: Есть ли дополнительная информация? Если нет — напиши 'нет':")
    bot.register_next_step_handler(message, process_extra_info)

def process_extra_info(message):
    global report_counter
    user_id = message.from_user.id
    if user_id in blocked_users:
        bot.send_message(message.chat.id, "🚫 Вы заблокированы.")
        return
    extra = message.text.strip()
    if extra.lower() == 'нет':
        extra = "Отсутствует"
    complaint_data[user_id]['extra_info'] = extra

    report_counter += 1
    rid = report_counter
    data = complaint_data[user_id]
    report = {
        'id': rid,
        'user_id': user_id,
        'user_username': data['user_username'],
        'reason': data['reason'],
        'violator_username': data['violator_username'],
        'violator_id': data['violator_id'],
        'extra_info': data['extra_info'],
        'status': 'В ожидании'
    }

    user_reports.setdefault(user_id, []).append(report)
    all_reports[rid] = report

    report_text = (
        f"🚨 *Новая жалоба №{rid}*\n\n"
        f"👤 *Жалобщик:* @{report['user_username']} | ID: {report['user_id']}\n"
        f"⚠️ *Причина:* {report['reason']}\n"
        f"👮 *Нарушитель:* @{report['violator_username']} | ID: {report['violator_id']}\n"
        f"📝 *Дополнительно:* {report['extra_info']}\n\n"
        f"✨ Спасибо за подробную жалобу!"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Принять", callback_data=f"approve_{rid}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{rid}")
    )

    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, report_text, parse_mode="Markdown", reply_markup=markup)

    bot.send_message(message.chat.id, "✅ Жалоба отправлена владельцу. Спасибо!")

@bot.message_handler(commands=['инфо'])
def group_info(message):
    if message.chat.type in ['group', 'supergroup']:
        text = (
            "✉️ Кто хочет подать жалобу — просто напишите в чат: _хочу написать жалобу_\n"
            "📲 Бот поддержки: [@SluzhbaPomoshchiBot](https://t.me/SluzhbaPomoshchiBot)"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.chat.type in ['group', 'supergroup'] and 'хочу написать жалобу' in msg.text.lower())
def want_to_report(message):
    bot.send_message(message.chat.id,
        "📲 Напишите свою жалобу боту в личку: [@SluzhbaPomoshchiBot](https://t.me/SluzhbaPomoshchiBot)",
        parse_mode="Markdown"
    )

print("Бот запущен...")
bot.infinity_polling()
