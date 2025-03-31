from datetime import datetime
from telebot.types import InputMediaPhoto
from loader import bot
from tg_API.core import displayHotelInfo  # Импортируем функцию для работы с API
import logging
from database.core import crud


def searchWithFilter(message, sort_by=None, categories_filter=None):
    """
    Переадресация запроса в search.py с добавлением фильтра.
    Может отправлять либо sort_by, либо categories_filter.
    """
    try:
        # Получаем Telegram ID пользователя
        telegram_id = message.from_user.id

        # Подключение к базе данных и проверка истории запросов
        history_records = retrieveHistoryForRating(telegram_id)

        if not history_records:
            bot.send_message(message.chat.id, "У вас нет записей в истории. Пожалуйста, пройдите опрос о поиске отеля.")
            return
        else:
            bot.send_message(message.chat.id, "Запись найдена! Ожидайте ответа от сайта.")

        # Получение последней записи из истории
        last_record = history_records[0]

        # Извлечение дат из базы данных
        check_in_date_str = last_record['check_in_date']  # Например, "22.03.2025"
        check_out_date_str = last_record['check_out_date']  # Например, "28.03.2025"

        arrival = datetime.strptime(check_in_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        departure = datetime.strptime(check_out_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")

        # Формирование данных для запроса к API
        city = last_record['city']
        local = last_record['location']

        # Добавляем фильтр в запрос
        hotels_data = displayHotelInfo(
            city_name=city,
            local=local,
            arrival_date=arrival,
            departure_date=departure,
            sort_by=sort_by,
            categories_filter=categories_filter
        )

        # Сохраняем данные в БД и отправляем результат пользователю
        handleHotelResults(message, hotels_data, telegram_id)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса. Пожалуйста, попробуйте позже.")


def retrieveHistoryForRating(telegram_id):
    """
    Получение истории запросов для команды.
    """
    return crud.retrieveHistoryByTgId()(telegram_id)


def handleHotelResults(message, hotels_data, telegram_id):
    """
    Обработка результатов запроса и отправка их пользователю.
    Результаты отправляются в виде альбома с 10 фотографиями и подписью к первой фотографии.
    """
    if not hotels_data:
        logging.warning("API не вернул данных для запроса.")
        bot.send_message(message.chat.id, "По вашему запросу не найдено отелей.")
        return

    # Сохраняем данные в БД

    crud.saveHotelInfoToDb(telegram_id, hotels_data)

    # Отправляем результаты пользователю
    for hotel in hotels_data:
        # Формируем текстовое описание отеля
        hotel_info = (
            f"Название: {hotel['name']}\n"
            f"Описание: {hotel['description']}\n"
            f"Цена: {hotel['price']}\n"
            f"Даты заезда/выезда: {hotel['dates']}\n"
            f"Координаты: {hotel['coordinates']}\n"
        )

        # Получаем список URL фотографий (максимум 10)
        photos = hotel.get("photos", [])[:10]

        if photos:
            # Создаем медиа-группу
            media_group = []

            for i, photo_url in enumerate(photos):
                # Добавляем уникальный параметр к URL, чтобы избежать кэширования
                unique_photo_url = f"{photo_url}&cache_buster={i}"

                # Добавляем подпись только к первой фотографии
                caption = hotel_info if i == 0 else None
                media_group.append(InputMediaPhoto(media=unique_photo_url, caption=caption))

            # Отправляем альбом с фотографиями
            try:
                bot.send_media_group(message.chat.id, media_group)
            except Exception as e:
                logging.error(f"Ошибка при отправке альбома: {e}")
                bot.send_message(message.chat.id, "Произошла ошибка при отправке фотографий.")
        else:
            # Если фотографий нет, отправляем только текстовое описание
            bot.send_message(message.chat.id, hotel_info)
