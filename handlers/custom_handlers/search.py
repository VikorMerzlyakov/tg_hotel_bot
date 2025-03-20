from loader import bot
from database.core import crud  # Импортируем интерфейс CRUD
from database.common.models import db, History, User  # Модели базы данных
from tg_API.core import display_hotel_info  # Импортируем функцию для работы с API
import logging
from datetime import datetime
from logger import logger


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
            logging.warning(f"У пользователя {telegram_id} нет записей в истории.")
            bot.send_message(message.chat.id, "У вас нет записей в истории. Пожалуйста, пройдите опрос о поиске отеля.")
        else:
            logging.info(f"Найдено {len(history_records)} записей в истории для пользователя {telegram_id}.")
            bot.send_message(message.chat.id, "Запись найдена! Вы уже проходили опрос о поиске отеля.")

            # Получение последней записи из истории
            last_record = history_records[0]

            # Извлечение дат из базы данных
            check_in_date_str = last_record['check_in_date']  # Например, "22.03.2025"
            check_out_date_str = last_record['check_out_date']  # Например, "28.03.2025"

            # Преобразование дат в формат гггг-мм-дд
            arrival = datetime.strptime(check_in_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            departure = datetime.strptime(check_out_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")

            # Формирование данных для запроса к API
            city = last_record['city']

            # Отправка запроса в API
            logging.info(f"Отправка запроса в API: город={city}, дата заезда={arrival}, дата выезда={departure}")
            hotels_data = display_hotel_info(city, arrival, departure)
            # Отправка запроса в API
            logging.info(f"Отправка запроса в API: город={city}, дата заезда={arrival}, дата выезда={departure}")
            hotels_data = display_hotel_info(city, arrival, departure)

            if not hotels_data:
                logging.warning(
                    f"API не вернул данных для запроса: город={city}, дата заезда={arrival}, дата выезда={departure}")
                bot.send_message(message.chat.id, "По вашему запросу не найдено отелей.")
                return

            # Формирование и отправка результата пользователю
            logging.info(f"Получено {len(hotels_data)} отелей от API.")
            response = "Результаты поиска:\n\n"
            for hotel in hotels_data:
                # Формируем информацию об отеле
                hotel_info = (
                    f"Название: {hotel['name']}\n"
                    f"Ссылка на бронирование: {hotel['booking_url']}\n"
                    f"Описание: {hotel['description']}\n"
                    f"Цена: {hotel['price']}\n"
                    f"Даты заезда/выезда: {hotel['dates']}\n"
                    f"Координаты: {hotel['coordinates']}\n"
                )

                # Добавляем фотографии, если они есть
                if hotel['photos']:
                    hotel_info += "Фотографии:\n"
                    for photo_url in hotel['photos']:
                        hotel_info += f"{photo_url}\n"
                else:
                    hotel_info += "Фотографии отсутствуют.\n"

                hotel_info += "---\n"

                # Отправляем сообщение пользователю
                bot.send_message(message.chat.id, hotel_info)
                response += hotel_info

            bot.send_message(message.chat.id, response)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса. Пожалуйста, попробуйте позже.")

    finally:
        # Закрытие соединения с базой данных
        if not db.is_closed():
            db.close()
            logging.info("Соединение с базой данных закрыто.")
