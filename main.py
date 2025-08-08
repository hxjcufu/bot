import telebot
from telebot import types

TOKEN = 'YOUR_BOT_TOKEN_HERE'
OWNER_ID = 2106708967
ADMIN_IDS = [OWNER_ID, 7841720739]

bot = telebot.TeleBot(TOKEN)

# Состояния пользователей для формы жалобы
user_states = {}
complaints = {}
complaint_id_counter = 1

# Главное меню с кнопками в квадрате (4 кнопки в ряд)
def main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    buttons = [
        types.InlineKeyboardButton("📢 Отправить жалобу", callback_data="complaint_start"),
        types.InlineKeyboardButton("📋 Мои заявки", callback_data="my_complaints"),
        types.InlineKeyboardButton("👀 Просмотренные заявки", callback_data="viewed_complaints"),
        types.InlineKeyboardButton("📞 Позвать админа", callback_data="call_admin"),
    ]
    keyboard.add(*buttons)
    return keyboard

# Админское меню (тоже в квадратах)
def admin_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    buttons = [
        types.InlineKeyboardButton("📩 Все жалобы", callback_data="all_complaints"),
        types.InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_complaint"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data="reject_complaint"),
        types.InlineKeyboardButton("🗑 Очистить заявки", callback_data="clear_complaints"),
        types.InlineKeyboardButton("🔕 Тихий админ", callback_data="silent_admin"),
        types.InlineKeyboardButton("🔔 Напомнить", callback_data="remind_admin"),
        types.InlineKeyboardButton("🔎 Статистика", callback_data="stats"),
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "Пользователь"
    text = f"Привет, {name}! 👋\nЭто служба поддержки.\nВыбери действие в меню 👇"
    if user_id in ADMIN_IDS:
        bot.send_message(user_id, text, reply_markup=admin_menu_keyboard())
    else:
        bot.send_message(user_id, text, reply_markup=main_menu_keyboard())

# Обработка нажатий по кнопкам
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "complaint_start":
        user_states[user_id] = {"step": 1, "data": {}}
        bot.send_message(user_id, "✍️ Введите свой никнейм (или ID):")
        bot.answer_callback_query(call.id)
        return

    if user_id in user_states:
        state = user_states[user_id]
        if state["step"] == 1:
            state["data"]["complainant"] = call.message.text if call.message else ""
        # Не обрабатываем в callback — ждём в сообщениях
        bot.answer_callback_query(call.id)
        return

    if data == "my_complaints":
        # TODO: показать жалобы пользователя (сейчас пусто)
        bot.send_message(user_id, "📋 Ваших жалоб пока нет.")
        bot.answer_callback_query(call.id)
        return

    if data == "viewed_complaints":
        # TODO: показать просмотренные жалобы (пусто)
        bot.send_message(user_id, "👀 Просмотренных жалоб нет.")
        bot.answer_callback_query(call.id)
        return

    if data == "call_admin":
        # Отправляем уведомление админу
        for admin_id in ADMIN_IDS:
            bot.send_message(admin_id, f"📞 Пользователь @{call.from_user.username} просит админа.")
        bot.send_message(user_id, "✅ Админа вызвали, ждите ответа.")
        bot.answer_callback_query(call.id)
        return

    if user_id in ADMIN_IDS:
        if data == "all_complaints":
            bot.send_message(user_id, "📩 Все жалобы (пока пусто).")
            bot.answer_callback_query(call.id)
            return
        elif data == "confirm_complaint":
            bot.send_message(user_id, "✅ Жалоба подтверждена (функция в разработке).")
bot.answer_callback_query(call.id)
            return
        elif data == "reject_complaint":
            bot.send_message(user_id, "❌ Жалоба отклонена (функция в разработке).")
            bot.answer_callback_query(call.id)
            return
        elif data == "clear_complaints":
            bot.send_message(user_id, "🗑 Заявки очищены (функция в разработке).")
            bot.answer_callback_query(call.id)
            return
        elif data == "silent_admin":
            bot.send_message(user_id, "🔕 Режим тихого админа включён (функция в разработке).")
            bot.answer_callback_query(call.id)
            return
        elif data == "remind_admin":
            bot.send_message(user_id, "🔔 Напоминание отправлено (функция в разработке).")
            bot.answer_callback_query(call.id)
            return
        elif data == "stats":
            bot.send_message(user_id, "📊 Статистика (функция в разработке).")
            bot.answer_callback_query(call.id)
            return

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip()
    if user_id in user_states:
        state = user_states[user_id]
        step = state["step"]

        if step == 1:
            state["data"]["complainant"] = text
            state["step"] = 2
            bot.send_message(user_id, "🔢 Введите ID нарушителя:")
            return
        elif step == 2:
            state["data"]["violator_id"] = text
            state["step"] = 3
            bot.send_message(user_id, "📄 Опишите проблему подробно:")
            return
        elif step == 3:
            state["data"]["problem_desc"] = text
            state["step"] = 4
            bot.send_message(user_id, "❗ Подтвердите отправку жалобы (да/нет):")
            return
        elif step == 4:
            if text.lower() == "да":
                global complaint_id_counter
                complaint_id = complaint_id_counter
                complaint_id_counter += 1

                complaints[complaint_id] = state["data"]
                bot.send_message(user_id, f"✅ Жалоба #{complaint_id} отправлена! Спасибо.")
                # Можно уведомить админов
                for admin_id in ADMIN_IDS:
                    bot.send_message(admin_id,
                                     f"Новая жалоба #{complaint_id}:\n"
                                     f"Жалобщик: {state['data']['complainant']}\n"
                                     f"Нарушитель ID: {state['data']['violator_id']}\n"
                                     f"Проблема: {state['data']['problem_desc']}")
                user_states.pop(user_id)
            else:
                bot.send_message(user_id, "❌ Жалоба отменена.")
                user_states.pop(user_id)
            return
    else:
        bot.send_message(user_id, "⚠️ Используйте кнопки меню для взаимодействия.")

bot.infinity_polling()# --- Часть 2: Админские функции и обработка жалоб ---

from telebot import types

# Здесь complaints, user_states, ADMIN_IDS и complaint_id_counter — из первой части (импортируй, если делишь по файлам)

def get_complaint_summary(complaint_id, data):
    return (f"🔔 Жалоба #{complaint_id}:\n"
            f"Жалобщик: {data['complainant']}\n"
            f"Нарушитель ID: {data['violator_id']}\n"
            f"Проблема: {data['problem_desc']}")

# Показываем все жалобы админу
def show_all_complaints(chat_id):
    if not complaints:
        bot.send_message(chat_id, "📭 Жалоб пока нет.")
        return
    for cid, data in complaints.items():
        text = get_complaint_summary(cid, data)
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{cid}"),
            types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{cid}"),
        )
        bot.send_message(chat_id, text, reply_markup=keyboard)
# Очистка жалоб
def clear_complaints(chat_id):
    complaints.clear()
    bot.send_message(chat_id, "🗑 Все жалобы очищены.")

# Обработка callback для подтверждения и отклонения
@bot.callback_query_handler(func=lambda call: call.from_user.id in ADMIN_IDS and call.data.startswith(("confirm_", "reject_")))
def admin_handle_complaint_decision(call):
    action, cid_str = call.data.split("_")
    cid = int(cid_str)

    if cid not in complaints:
        bot.answer_callback_query(call.id, "⚠️ Жалоба уже обработана или не найдена.", show_alert=True)
        return

    if action == "confirm":
        bot.send_message(call.from_user.id, f"✅ Жалоба #{cid} подтверждена.")
        # Здесь можно добавить логику по блокировкам и т.д.
        del complaints[cid]
    elif action == "reject":
        bot.send_message(call.from_user.id, f"❌ Жалоба #{cid} отклонена.")
        del complaints[cid]

    bot.answer_callback_query(call.id)
    # Обновим список жалоб после действия
    show_all_complaints(call.from_user.id)

# Напоминание админам о новых жалобах (простой пример)
def remind_admins():
    if complaints:
        for admin_id in ADMIN_IDS:
            bot.send_message(admin_id, f"🔔 У вас {len(complaints)} необработанных жалоб!")

# Статистика по жалобам
def send_stats(chat_id):
    total = len(complaints)
    bot.send_message(chat_id, f"📊 Статистика:\nОбщее количество жалоб: {total}")

# Пример кнопок для админского меню с учетом изменений
def admin_menu_keyboard_v2():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton("📩 Все жалобы", callback_data="all_complaints"),
        types.InlineKeyboardButton("🗑 Очистить жалобы", callback_data="clear_complaints"),
        types.InlineKeyboardButton("🔔 Напомнить админам", callback_data="remind_admin"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats"),
    ]
    keyboard.add(*buttons)
    return keyboard

# Обработка остальных callback админских кнопок
@bot.callback_query_handler(func=lambda call: call.from_user.id in ADMIN_IDS)
def admin_callback_handler(call):
    data = call.data
    user_id = call.from_user.id

    if data == "all_complaints":
        show_all_complaints(user_id)
    elif data == "clear_complaints":
        clear_complaints(user_id)
    elif data == "remind_admin":
        remind_admins()
        bot.send_message(user_id, "🔔 Напоминание отправлено.")
    elif data == "stats":
        send_stats(user_id)
    else:
        bot.answer_callback_query(call.id, "⚠️ Неизвестная команда.")
    bot.answer_callback_query(call.id)# --- Часть 3: Обработка жалоб пользователями (многоступенчатая) и меню пользователя ---

# Стейты пользователя для многошаговой подачи жалобы
user_states = {}  # user_id : {"step": int, "data": dict}

# Запуск подачи жалобы
@bot.message_handler(commands=['sendcomplaint'])
def start_complaint(message):
    user_id = message.from_user.id
    user_states[user_id] = {"step": 1, "data": {}}
    bot.send_message(user_id, "📝 Шаг 1/10: Введите ваш никнейм или имя:")

@bot.message_handler(func=lambda m: m.from_user.id in user_states)
def complaint_steps(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if not state:
        return

    step = state["step"]
    text = message.text.strip()

    if step == 1:
        state["data"]["complainant"] = text
        state["step"] = 2
        bot.send_message(user_id, "📝 Шаг 2/10: Введите ваш ID:")
    elif step == 2:
        state["data"]["complainant_id"] = text
        state["step"] = 3
        bot.send_message(user_id, "📝 Шаг 3/10: Введите ник нарушителя:")
    elif step == 3:
        state["data"]["violator"] = text
        state["step"] = 4
        bot.send_message(user_id, "📝 Шаг 4/10: Введите ID нарушителя:")
elif step == 4:
        state["data"]["violator_id"] = text
        state["step"] = 5
        bot.send_message(user_id, "📝 Шаг 5/10: Опишите проблему (кратко):")
    elif step == 5:
        state["data"]["problem_desc"] = text
        state["step"] = 6
        bot.send_message(user_id, "📝 Шаг 6/10: Укажите дату нарушения (дд.мм.гггг):")
    elif step == 6:
        state["data"]["violation_date"] = text
        state["step"] = 7
        bot.send_message(user_id, "📝 Шаг 7/10: Добавьте дополнительные детали (если есть):")
    elif step == 7:
        state["data"]["additional_info"] = text
        state["step"] = 8
        bot.send_message(user_id, "📝 Шаг 8/10: Введите ссылку на доказательства (если есть):")
    elif step == 8:
        state["data"]["evidence_link"] = text
        state["step"] = 9
        bot.send_message(user_id, "📝 Шаг 9/10: Подтвердите, что информация верна (да/нет):")
    elif step == 9:
        if text.lower() == "да":
            state["step"] = 10
            bot.send_message(user_id, "✅ Ваша жалоба готова к отправке. Отправляем...")
            save_complaint(user_id, state["data"])
            user_states.pop(user_id)
        elif text.lower() == "нет":
            bot.send_message(user_id, "⚠️ Жалоба отменена. Если хотите начать заново — используйте /sendcomplaint")
            user_states.pop(user_id)
        else:
            bot.send_message(user_id, "Пожалуйста, ответьте 'да' или 'нет'.")
    else:
        bot.send_message(user_id, "Что-то пошло не так. Попробуйте снова /sendcomplaint")
        user_states.pop(user_id)

def save_complaint(user_id, data):
    global complaint_id_counter
    complaint_id_counter += 1
    complaints[complaint_id_counter] = data
    bot.send_message(user_id, f"🆗 Жалоба №{complaint_id_counter} успешно отправлена! Спасибо за сообщение.")
    # Уведомим админов
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, f"🔔 Новая жалоба №{complaint_id_counter} от {data['complainant']}")

# Пользовательское меню (кнопки)
def user_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton("📨 Отправить жалобу", callback_data="user_send_complaint"),
        types.InlineKeyboardButton("📋 Мои заявки", callback_data="user_my_complaints"),
        types.InlineKeyboardButton("🔍 Просмотренные заявки", callback_data="user_viewed_complaints"),
        types.InlineKeyboardButton("🆘 Позвать админа", callback_data="user_call_admin"),
        types.InlineKeyboardButton("📄 Помощь", callback_data="user_help"),
    ]
    keyboard.add(*buttons)
    return keyboard

# Обработка пользовательских callback
@bot.callback_query_handler(func=lambda call: call.data.startswith("user_"))
def user_callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "user_send_complaint":
        bot.send_message(user_id, "📝 Чтобы начать жалобу, напишите команду /sendcomplaint")
    elif data == "user_my_complaints":
        # Пример простой заглушки
        bot.send_message(user_id, "📋 Ваши заявки пока не реализованы.")
    elif data == "user_viewed_complaints":
        bot.send_message(user_id, "🔍 Просмотренные заявки пока не реализованы.")
    elif data == "user_call_admin":
        for admin_id in ADMIN_IDS:
            bot.send_message(admin_id, f"🆘 Пользователь @{call.from_user.username} попросил помощь!")
        bot.send_message(user_id, "🆘 Админ уведомлен.")
    elif data == "user_help":
        bot.send_message(user_id, "ℹ️ Используйте меню для действий. Чтобы отправить жалобу, нажмите 'Отправить жалобу' или введите /sendcomplaint")
    else:
        bot.send_message(user_id, "❗ Неизвестная команда.")

    bot.answer_callback_query(call.id)# --- Часть 4: Админские функции и меню админа ---
# Админское меню с 14+ кнопками
def admin_panel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton("📋 Все жалобы", callback_data="admin_all_complaints"),
        types.InlineKeyboardButton("✅ Подтвердить жалобу", callback_data="admin_confirm_complaint"),
        types.InlineKeyboardButton("❌ Отклонить жалобу", callback_data="admin_reject_complaint"),
        types.InlineKeyboardButton("🔒 Блокировать пользователя", callback_data="admin_block_user"),
        types.InlineKeyboardButton("🔓 Разблокировать пользователя", callback_data="admin_unblock_user"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("🧹 Очистить все заявки", callback_data="admin_clear_all"),
        types.InlineKeyboardButton("🔔 Уведомления", callback_data="admin_notifications"),
        types.InlineKeyboardButton("🛠️ Тихий режим", callback_data="admin_silent_mode"),
        types.InlineKeyboardButton("👥 Список заблокированных", callback_data="admin_blocked_list"),
        types.InlineKeyboardButton("👨‍💻 Пользователи", callback_data="admin_users_list"),
        types.InlineKeyboardButton("📨 Отправить сообщение", callback_data="admin_send_message"),
        types.InlineKeyboardButton("🕵️‍♂️ Просмотр жалобы", callback_data="admin_view_complaint"),
        types.InlineKeyboardButton("↩️ Назад", callback_data="admin_back"),
    ]
    keyboard.add(*buttons)
    return keyboard

# Админ callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "❗ Доступ запрещён")
        return

    data = call.data

    if data == "admin_all_complaints":
        if not complaints:
            bot.send_message(user_id, "📭 Жалоб пока нет.")
        else:
            text = "📋 Все жалобы:\n"
            for cid, comp in complaints.items():
                text += f"#{cid} от {comp['complainant']} — {comp['problem_desc']}\n"
            bot.send_message(user_id, text)

    elif data == "admin_confirm_complaint":
        bot.send_message(user_id, "✅ Введите ID жалобы для подтверждения:")
        # Ожидание следующего сообщения — допиши если нужно

    elif data == "admin_reject_complaint":
        bot.send_message(user_id, "❌ Введите ID жалобы для отклонения:")
        # Ожидание следующего сообщения — допиши если нужно

    elif data == "admin_block_user":
        bot.send_message(user_id, "🔒 Введите ID пользователя для блокировки:")

    elif data == "admin_unblock_user":
        bot.send_message(user_id, "🔓 Введите ID пользователя для разблокировки:")

    elif data == "admin_stats":
        total = len(complaints)
        blocked = len(blocked_users)
        bot.send_message(user_id, f"📊 Статистика:\nВсего жалоб: {total}\nЗаблокировано пользователей: {blocked}")

    elif data == "admin_clear_all":
        complaints.clear()
        bot.send_message(user_id, "🧹 Все жалобы очищены.")

    elif data == "admin_notifications":
        bot.send_message(user_id, "🔔 Включить или выключить уведомления (функция в разработке).")

    elif data == "admin_silent_mode":
        bot.send_message(user_id, "🛠️ Режим 'Тихий админ' активирован (функция в разработке).")

    elif data == "admin_blocked_list":
        if not blocked_users:
            bot.send_message(user_id, "👥 Нет заблокированных пользователей.")
        else:
            text = "👥 Заблокированные пользователи:\n" + "\n".join(str(uid) for uid in blocked_users)
            bot.send_message(user_id, text)

    elif data == "admin_users_list":
        bot.send_message(user_id, "👨‍💻 Функция списка пользователей в разработке.")

    elif data == "admin_send_message":
        bot.send_message(user_id, "📨 Введите ID пользователя и сообщение через пробел:")

    elif data == "admin_view_complaint":
        bot.send_message(user_id, "🕵️‍♂️ Введите ID жалобы для просмотра:")
elif data == "admin_back":
        bot.send_message(user_id, "↩️ Возврат в главное меню.", reply_markup=admin_panel_keyboard())

    else:
        bot.send_message(user_id, "❗ Неизвестная команда.")

    bot.answer_callback_query(call.id)# === Часть 5 ===

from telebot import types

# Функция для пользовательского меню (квадратные кнопки)
def user_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton("📢 Отправить жалобу", callback_data="send_report"),
        types.InlineKeyboardButton("📋 Мои заявки", callback_data="my_reports"),
        types.InlineKeyboardButton("👀 Просмотренные заявки", callback_data="viewed_reports"),
        types.InlineKeyboardButton("📞 Позвать админа", callback_data="call_admin"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"),
        # Добавь сюда любые другие кнопки для пользователя
    ]
    keyboard.add(*buttons)
    return keyboard

# Обработчик callback для пользовательского меню
@bot.callback_query_handler(func=lambda call: call.data in ["send_report", "my_reports", "viewed_reports", "call_admin", "main_menu"])
def handle_user_menu(call):
    user_id = call.from_user.id
    if call.data == "send_report":
        bot.send_message(user_id, "✍️ Начинаем оформление жалобы. Напишите ID нарушителя:")
        user_states[user_id] = {"step": 1, "complaint": {}}
    elif call.data == "my_reports":
        reports = user_reports.get(user_id, [])
        if not reports:
            bot.send_message(user_id, "У вас пока нет заявок.")
        else:
            text = "Ваши заявки:\n" + "\n".join([f"#{i+1} - {r['status']}" for i, r in enumerate(reports)])
            bot.send_message(user_id, text)
    elif call.data == "viewed_reports":
        bot.send_message(user_id, "Просмотренные заявки пока недоступны.")
    elif call.data == "call_admin":
        bot.send_message(user_id, "Админ уже в пути! 🏃‍♂️")
        bot.send_message(OWNER_ID, f"Пользователь @{call.from_user.username} ({user_id}) позвал админа.")
    elif call.data == "main_menu":
        bot.send_message(user_id, "Возвращаемся в главное меню.", reply_markup=user_menu_keyboard())
    bot.answer_callback_query(call.id)

# Обработка сообщений для жалобы по 10 шагам
@bot.message_handler(func=lambda m: m.from_user.id in user_states)
def handle_complaint_steps(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    step = state["step"]
    complaint = state["complaint"]

    if step == 1:
        complaint["нарушитель_ID"] = message.text.strip()
        bot.send_message(user_id, "Напишите никнейм нарушителя:")
        state["step"] = 2
    elif step == 2:
        complaint["нарушитель_ник"] = message.text.strip()
        bot.send_message(user_id, "Опишите проблему подробно:")
        state["step"] = 3
    elif step == 3:
        complaint["причина"] = message.text.strip()
        bot.send_message(user_id, "Укажите ваш ID:")
        state["step"] = 4
    elif step == 4:
        complaint["жалобщик_ID"] = message.text.strip()
        bot.send_message(user_id, "Ваш никнейм:")
        state["step"] = 5
    elif step == 5:
        complaint["жалобщик_ник"] = message.text.strip()
        bot.send_message(user_id, "Вы можете прикрепить скриншоты или написать 'пропустить':")
        state["step"] = 6
    elif step == 6:
        if message.text and message.text.lower() == "пропустить":
            complaint["скриншоты"] = None
            bot.send_message(user_id, "Подтвердите отправку жалобы (да/нет):")
            state["step"] = 10
        elif message.photo:
            complaint["скриншоты"] = message.photo[-1].file_id
            bot.send_message(user_id, "Фото получено. Подтвердите отправку жалобы (да/нет):")
            state["step"] = 10
else:
            bot.send_message(user_id, "Пожалуйста, отправьте фото или напишите 'пропустить'.")
    elif step == 10:
        answer = message.text.lower()
        if answer == "да":
            # Сохраняем жалобу
            user_reports.setdefault(user_id, []).append({**complaint, "status": "Отправлена"})
            bot.send_message(user_id, "✅ Ваша жалоба отправлена администраторам.")
            # Отправляем админам
            admin_text = (
                f"Новая жалоба от {complaint['жалобщик_ник']} (ID: {complaint['жалобщик_ID']})\n"
                f"Нарушитель: {complaint['нарушитель_ник']} (ID: {complaint['нарушитель_ID']})\n"
                f"Причина: {complaint['причина']}"
            )
            bot.send_message(OWNER_ID, admin_text)
            if complaint["скриншоты"]:
                bot.send_photo(OWNER_ID, complaint["скриншоты"])
            del user_states[user_id]
        elif answer == "нет":
            bot.send_message(user_id, "❌ Жалоба отменена.")
            del user_states[user_id]
        else:
            bot.send_message(user_id, "Пожалуйста, ответьте 'да' или 'нет'.")
    else:
        bot.send_message(user_id, "Что-то пошло не так. Попробуйте ещё раз.")
        del user_states[user_id]

# Запуск бота
bot.infinity_polling()
