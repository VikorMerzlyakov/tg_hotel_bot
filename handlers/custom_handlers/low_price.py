from handlers.custom_handlers.common import searchWithFilter
import logging
from loader import bot


# Команда /low_price
@bot.message_handler(commands=['low_price'])
def low_price(message):
    """
    Обработчик команды /low_price.
    Добавляет фильтр для сортировки отелей по цене ("sort_by": "price").
    """
    try:
        logging.info("Получена команда /low_price.")

        # Устанавливаем фильтр для сортировки по цене
        sort_by = "price"

        # Вызываем обработчик команды /search, передавая дополнительный параметр
        searchWithFilter(message, sort_by=sort_by)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса. Пожалуйста, попробуйте позже.")
