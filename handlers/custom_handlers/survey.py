from keyboards.reply.contact import request_location
from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message
from datetime import datetime

#city = State()
#local = State()
#date_checkin = State()
#date_checkout = State()
#low_price = State()
#high_price = State()


@bot.message_handler(commands=['survey'])
def survey(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.username}, введи город для поиска отеля')

@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Спасибо, записал. Теперь уточните локацию.',
                     reply_markup=request_location())
        bot.set_state(message.from_user.id, UserInfoState.local, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Название города может содержать только буквы')



@bot.message_handler(content_types=['text'], state=UserInfoState.local)
def get_local(message: Message) -> None:
    if message.text in ["Центр города", "Окраина", "Аэропорт"]:
        bot.send_message(
            message.from_user.id,
            'Спасибо, записал. Теперь введите дату заселения в формате ДД.ММ.ГГГГ.'
        )
        bot.set_state(message.from_user.id, UserInfoState.date_checkin, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['local'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, выберите локацию из предложенных вариантов.')

@bot.message_handler(state=UserInfoState.date_checkin)
def get_date_checkin(message: Message) -> None:
    try:
        # Проверяем формат даты
        check_in_date = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        if check_in_date < datetime.now():
            raise ValueError("Дата заезда не может быть в прошлом.")

        bot.send_message(
            message.from_user.id,
            'Спасибо, записал. Теперь введите дату выселения в формате ДД.ММ.ГГГГ.'
        )
        bot.set_state(message.from_user.id, UserInfoState.date_checkout, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['date_checkin'] = check_in_date.strftime("%d.%m.%Y")  # Сохраняем в удобном формате
    except ValueError:
        bot.send_message(
            message.from_user.id,
            'Неверный формат даты или дата в прошлом. Введите дату заезда в формате ДД.ММ.ГГГГ.'
        )

@bot.message_handler(state=UserInfoState.date_checkout)
def get_date_checkout(message: Message) -> None:
    try:
        # Проверяем формат даты
        check_out_date = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            check_in_date = datetime.strptime(data['date_checkin'], "%d.%m.%Y")

        if check_out_date <= check_in_date:
            raise ValueError("Дата выселения должна быть позже даты заезда.")

        bot.send_message(message.from_user.id, 'Спасибо, записал. Теперь введите минимальную цену.')
        bot.set_state(message.from_user.id, UserInfoState.low_price, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['date_checkout'] = check_out_date.strftime("%d.%m.%Y")  # Сохраняем в удобном формате
    except ValueError as e:
        bot.send_message(
            message.from_user.id,
            f'Ошибка: {e}. Введите дату выселения в формате ДД.ММ.ГГГГ.'
        )


@bot.message_handler(state=UserInfoState.low_price)
def get_low_price(message: Message) -> None:
    # Проверяем, что введено число
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
    # Проверяем, что введено число
    if message.text.isdigit():
        high_price = int(message.text)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            low_price = data.get('low_price')

            # Проверяем, что максимальная цена больше минимальной
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
                bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
            else:
                bot.send_message(
                    message.from_user.id,
                    'Ошибка: максимальная цена должна быть больше минимальной. Попробуйте снова.'
                )
    else:
        bot.send_message(message.from_user.id, 'Ошибка: максимальная цена должна быть числом. Попробуйте снова.')