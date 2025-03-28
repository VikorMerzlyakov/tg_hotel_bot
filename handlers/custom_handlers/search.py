from loader import bot
from database.core import crud  # Импортируем интерфейс CRUD
from database.common.models import db, History, User  # Модели базы данных
from tg_API.core import display_hotel_info  # Импортируем функцию для работы с API
import logging
from datetime import datetime
from telebot.types import InputMediaPhoto  # Для создания медиа-группы
from logger import logging


# Команда /search
@bot.message_handler(commands=['search'])
def search(message):
    """
    Обработчик команды /search.
    Проверяет наличие записей в истории запросов пользователя.
    Если записи найдены, отправляет запрос в API и выводит результат в чат.
    """
    try:
        # Получаем Telegram ID пользователя
        telegram_id = message.from_user.id

        # Подключение к базе данных
        if not db.is_closed():
            logging.info("Соединение с базой данных уже открыто.")
        else:
            db.connect()
            logging.info("Подключение к базе данных установлено.")

        # Проверка существования таблиц
        if not db.table_exists(User):
            logging.warning("Таблица 'users' не существует. Создание таблиц...")
            db.create_tables([User, History], safe=True)
            logging.info("Таблицы успешно созданы.")

        # Проверка наличия пользователя в таблице users
        users = crud.retrieve_users()()
        user = next((u for u in users if u['id_tg'] == telegram_id), None)

        if not user:
            logging.warning(f"Пользователь с Telegram ID {telegram_id} не зарегистрирован.")
            bot.send_message(message.chat.id, "Вы не зарегистрированы. Пожалуйста, пройдите регистрацию.")
            return

        logging.info(f"Пользователь с Telegram ID {telegram_id} найден.")

        # Получение истории запросов для пользователя
        history_records = crud.retrieve_history_by_tg_id()(telegram_id)

        if not history_records:
            bot.send_message(message.chat.id, "У вас нет записей в истории. Пожалуйста, пройдите опрос о поиске отеля.")
        else:
            bot.send_message(message.chat.id, "Запись найдена! Ожидайте ответа от сайта.")

            # Получение последней записи из истории
            last_record = history_records[0]

            # Извлечение дат из базы данных
            check_in_date_str = last_record['check_in_date']  # Например, "22.03.2025"
            check_out_date_str = last_record['check_out_date']  # Например, "28.03.2025"

            # Преобразование дат в формат гггг-мм-дд
            arrival = datetime.strptime(check_in_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            departure = datetime.strptime(check_out_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")

            price_min = last_record['low_price']
            price_max= last_record['high_price']
            # Формирование данных для запроса к API
            city = last_record['city']
            local = last_record['location']

            # Отправка запроса в API
            logging.info(f"Отправка запроса в API: город={city}, дата заезда={arrival}, дата выезда={departure}")
            hotels_data = display_hotel_info(city, local, arrival, departure, price_min, price_max)


            # Сохраняем данные в БД перед отправкой сообщений
            crud.save_hotel_info_to_db(telegram_id, hotels_data)

            if not hotels_data:
                logging.warning(
                    f"API не вернул данных для запроса: город={city}, дата заезда={arrival}, дата выезда={departure}")
                bot.send_message(message.chat.id, "По вашему запросу не найдено отелей.")
                return

            # Формирование и отправка результата пользователю
            logging.info(f"Получено {len(hotels_data)} отелей от API.")
            for hotel in hotels_data:
                # Формируем информацию об отеле
                hotel_info = (
                    f"Название: {hotel['name']}\n"
                    f"Описание: {hotel['description']}\n"
                    f"Цена: {hotel['price']}\n"
                    f"Даты заезда/выезда: {hotel['dates']}\n"
                    f"Координаты: {hotel['coordinates']}\n"
                )

                # Отправляем текстовое сообщение с информацией об отеле
                #bot.send_message(message.chat.id, hotel_info)

                if hotel['photos']:
                    media_group = []
                    for i, photo_url in enumerate(hotel['photos']):
                        # Добавляем уникальный параметр к URL
                        unique_photo_url = f"{photo_url}&cache_buster={i}"

                        # Добавляем подпись только к первой фотографии
                        caption = hotel_info if i == 0 else None
                        media_group.append(InputMediaPhoto(media=unique_photo_url, caption=caption))

                        # Если достигнут лимит в 10 фото, отправляем альбом
                        if len(media_group) == 10 or i == len(hotel['photos']) - 1:
                            bot.send_media_group(message.chat.id, media_group)
                            media_group = []  # Очищаем альбом для следующей группы фото
                else:
                    bot.send_message(message.chat.id, "Фотографии отсутствуют.\n")

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса. Пожалуйста, попробуйте позже.")

    finally:
        # Закрытие соединения с базой данных
        if not db.is_closed():
            db.close()
            logging.info("Соединение с базой данных закрыто.")