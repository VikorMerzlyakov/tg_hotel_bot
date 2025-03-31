from handlers.custom_handlers.common import searchWithFilter
import logging
from loader import bot


# Команда /bestdeal
@bot.message_handler(commands=['bestdeal'])
def bestdeal(message):
    """
    Обработчик команды /bestdeal.
    Добавляет фильтр для сортировки отелей по расстоянию ("sort_by": "distance").
    """
    try:
        logging.info("Получена команда /bestdeal.")

        # Устанавливаем фильтр для сортировки по расстоянию
        sort_by = "distance"

        # Вызываем обработчик команды /search, передавая дополнительный параметр
        searchWithFilter(message, sort_by=sort_by)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса. Пожалуйста, попробуйте позже.")
