import logging
from loader import bot
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from database.core import crud  # Импортируем CRUD для работы с базой данных
from keyboards.reply.contact import create_date_keyboard  # Импортируем клавиатуру


# Команда /history для просмотра истории запросов
@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """
    Обрабатывает команду /history для просмотра истории запросов пользователя.
    """
    try:
        logging.info(f"Получена команда /history от пользователя {message.from_user.id}")

        # Получаем Telegram ID пользователя
        telegram_id = message.from_user.id
        logging.debug(f"Получен Telegram ID пользователя: {telegram_id}")

        # Получаем историю запросов пользователя через CRUD
        logging.info(f"Запрос истории запросов для пользователя {telegram_id}")
        history_data = crud.retrieve_search_history(telegram_id)

        if not history_data:
            # Если история пуста или пользователь не зарегистрирован, уведомляем пользователя
            logging.warning(f"История запросов пуста для пользователя {telegram_id}")
            bot.send_message(
                message.chat.id,
                "История запросов пуста. Начните поиск отелей, чтобы создать историю."
            )
            return

        logging.info(f"История запросов успешно получена для пользователя {telegram_id}")

        # Извлекаем уникальные даты из истории
        unique_dates = sorted(set(entry['created_at'].split(" ")[0] for entry in history_data), reverse=True)

        if not unique_dates:
            bot.send_message(message.chat.id, "В истории нет записей с датами.")
            return

        # Отправляем клавиатуру с датами
        bot.send_message(
            message.chat.id,
            "Выберите дату для просмотра истории запросов:",
            reply_markup=create_date_keyboard(unique_dates)
        )

    except Exception as e:
        logging.error(f"Произошла ошибка при обработке команды /history: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
        )


# Обработчик нажатий на кнопки дат
@bot.callback_query_handler(func=lambda call: call.data.startswith("history_date:"))
def handle_date_selection(call: CallbackQuery):
    """
    Обрабатывает выбор даты из клавиатуры.

    :param call: CallbackQuery с выбранной датой.
    """
    try:
        selected_date = call.data.split(":")[1]  # Извлекаем выбранную дату
        telegram_id = call.from_user.id

        logging.info(f"Пользователь {telegram_id} выбрал дату: {selected_date}")

        # Получаем историю запросов за выбранную дату
        history_data = crud.retrieve_search_history_by_date(telegram_id, selected_date)

        if not history_data:
            bot.send_message(call.message.chat.id, f"За дату {selected_date} записей не найдено.")
            return

        logging.info(f"История запросов успешно получена для пользователя {telegram_id} за дату {selected_date}")

        # Отправляем каждую запись из истории
        for entry in history_data:
            formatted_entry = format_single_entry(entry)

            # Извлекаем фотографии из записи
            photos = entry.get("photo", [])

            # Если photos — строка, преобразуем её в список
            if isinstance(photos, str):
                photos = photos.split(", ")

            # Если есть фотографии, отправляем их как альбом
            if photos and photos[0]:
                media_group = []
                for i, photo_url in enumerate(photos[:10]):  # Максимум 10 фото в альбоме
                    if i == 0:
                        # Для первой фотографии добавляем описание
                        media_group.append(InputMediaPhoto(photo_url, caption=formatted_entry))
                    else:
                        media_group.append(InputMediaPhoto(photo_url))

                bot.send_media_group(call.message.chat.id, media_group)
            else:
                # Если фотографий нет, отправляем только текстовое сообщение
                bot.send_message(call.message.chat.id, formatted_entry)

    except Exception as e:
        logging.error(f"Произошла ошибка при обработке выбора даты: {e}")
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
        )


def format_single_entry(entry: dict) -> str:
    """
    Форматирует одну запись из истории запросов для удобочитаемого вывода.

    :param entry: Словарь с данными о запросе.
    :return: Отформатированная строка с информацией об отеле.
    """
    return (
        f"Название отеля: {entry['city']}\n"
        f"Ссылка на бронирование: {entry['booking_url']}\n"
        f"Описание: {entry['description']}\n"
        f"Дата заезда: {entry['check_in_date']}\n"
        f"Дата выезда: {entry['check_out_date']}\n"
        f"Цена: {entry['price']}\n"
        f"Координаты: Широта - {entry['latitude']}, Долгота - {entry['longitude']}\n"
        f"Дата запроса: {entry['created_at']}\n"
        f"---\n"
    )