from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from keyboards.reply.contact import request_location
from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message, CallbackQuery
from datetime import datetime, timedelta
from database.core import crud  # Импортируем CRUD для работы с базой данных


# Команда /survey для начала опроса
@bot.message_handler(commands=['survey'])
def survey(message: Message) -> None:
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    users = crud.retrieve_users()()
    user = next((u for u in users if u['id_tg'] == telegram_id), None)

    if not user:
        # Если пользователь не зарегистрирован, предлагаем пройти регистрацию
        bot.send_message(
            message.chat.id,
            "Вы не зарегистрированы. Пожалуйста, пройдите регистрацию, используя команду /register."
        )
        return  # Останавливаем обработку команды

    # Если пользователь зарегистрирован, продолжаем обработку
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.username}, введи город (латинскими буквами) для поиска отеля')


# Обработчик для получения города
@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(
            message.from_user.id,
            'Спасибо, записал. Теперь уточните локацию.',
            reply_markup=request_location()
        )
        bot.set_state(message.from_user.id, UserInfoState.local, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Название города может содержать только буквы.')


@bot.message_handler(content_types=['text'], state=UserInfoState.local)
def get_local(message: Message) -> None:
    if message.text in ["Центр города", "Окраина", "Аэропорт"]:
        bot.send_message(
            message.from_user.id,
            'Спасибо, записал. Теперь выберите дату заезда.'
        )
        bot.set_state(message.from_user.id, UserInfoState.date_checkin, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['local'] = message.text

        # Отправляем календарь для выбора даты заезда
        calendar, step = DetailedTelegramCalendar(min_date=datetime.now().date()).build()
        bot.send_message(
            message.chat.id,
            f"Выберите дату заезда: {LSTEP[step]}",
            reply_markup=calendar
        )
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, выберите локацию из предложенных вариантов.')


# Обработка callback-запроса для даты заезда
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(), state=UserInfoState.date_checkin)
def process_date_checkin(call: CallbackQuery):
    result, key, step = DetailedTelegramCalendar(min_date=datetime.now().date()).process(call.data)

    if not result and key:
        bot.edit_message_text(
            f"Выберите дату заезда: {LSTEP[step]}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=key
        )
    elif result:
        bot.edit_message_text(
            f"Вы выбрали дату заезда: {result.strftime('%d.%m.%Y')}",
            call.message.chat.id,
            call.message.message_id
        )

        bot.send_message(
            call.message.chat.id,
            'Теперь выберите дату выселения.'
        )

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['date_checkin'] = result.strftime("%d.%m.%Y")

        bot.set_state(call.from_user.id, UserInfoState.date_checkout, call.message.chat.id)

        # Отправляем календарь для выбора даты выселения
        check_in_date = result  # result уже datetime.date
        calendar, step = DetailedTelegramCalendar(min_date=check_in_date + timedelta(days=1)).build()
        bot.send_message(
            call.message.chat.id,
            'Выберите дату выселения.',
            reply_markup=calendar
        )


# Обработка callback-запроса для даты выселения
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(), state=UserInfoState.date_checkout)
def process_date_checkout(call: CallbackQuery):
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        check_in_date = datetime.strptime(data['date_checkin'], "%d.%m.%Y").date()

    result, key, step = DetailedTelegramCalendar(min_date=check_in_date + timedelta(days=1)).process(call.data)

    if not result and key:
        bot.edit_message_text(
            f"Выберите дату выселения: {LSTEP[step]}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=key
        )
    elif result:
        bot.edit_message_text(
            f"Вы выбрали дату выселения: {result.strftime('%d.%m.%Y')}",
            call.message.chat.id,
            call.message.message_id
        )

        bot.send_message(
            call.message.chat.id,
            'Спасибо, записал. Теперь введите минимальную цену(USD).'
        )

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['date_checkout'] = result.strftime("%d.%m.%Y")

        bot.set_state(call.from_user.id, UserInfoState.low_price, call.message.chat.id)


@bot.message_handler(state=UserInfoState.low_price)
def get_low_price(message: Message) -> None:
    if message.text.isdigit():
        low_price = int(message.text)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['low_price'] = low_price

        bot.send_message(message.from_user.id, 'Спасибо, записал. Теперь введите максимальную цену.')
        bot.set_state(message.from_user.id, UserInfoState.high_price, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Ошибка: минимальная цена должна быть числом. Попробуйте снова.')


@bot.message_handler(state=UserInfoState.high_price)
def get_high_price(message: Message) -> None:
    if message.text.isdigit():
        high_price = int(message.text)

        #with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
         #   data['low_price'] = low_price


        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            low_price = data['low_price']

            if high_price > low_price:
                data['high_price'] = high_price

                text = (
                    f'Спасибо за предоставленную Вами информацию:\n'
                    f'Город: {data["city"]}\n'
                    f'Локация: {data["local"]}\n'
                    f'Дата заезда: {data["date_checkin"]}\n'
                    f'Дата выселения: {data["date_checkout"]}\n'
                    f'Минимальная цена: {data["low_price"]}\n'
                    f'Максимальная цена: {data["high_price"]}'
                )
                bot.send_message(message.from_user.id, text)

                # Сохраняем данные в базу данных
                from database.utils.CRUD import CRUDInterface
                crud = CRUDInterface()
                store_data = crud.create()

                store_data({
                    'user_id': message.from_user.id,
                    'username': message.from_user.username,
                    'city': data['city'],
                    'location': data['local'],
                    'check_in_date': data['date_checkin'],
                    'check_out_date': data['date_checkout'],
                    'low_price': data['low_price'],
                    'high_price': data['high_price']
                })


                # Предлагаем пользователю продолжить взаимодействие
                bot.send_message(
                    message.from_user.id,
                    'Опрос завершен! Вы можете использовать команду поиска - /search.'
                )



            else:
                bot.send_message(
                    message.from_user.id,
                    'Ошибка: максимальная цена должна быть больше минимальной. Попробуйте снова.'
                )
        # Сбрасываем состояние после завершения опроса
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Ошибка: максимальная цена должна быть числом. Попробуйте снова.')
