import logging
from loader import bot
from telebot.types import Message, InputMediaPhoto
from database.core import crud  # Импортируем CRUD для работы с базой данных


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

                bot.send_media_group(message.chat.id, media_group)
            else:
                # Если фотографий нет, отправляем только текстовое сообщение
                bot.send_message(message.chat.id, formatted_entry)

        logging.info(f"История запросов отправлена пользователю {telegram_id}")

    except Exception as e:
        logging.error(f"Произошла ошибка при обработке команды /history: {e}")
        bot.send_message(
            message.chat.id,
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