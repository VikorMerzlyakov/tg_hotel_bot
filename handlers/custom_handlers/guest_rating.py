from handlers.custom_handlers.common import searchWithFilter
import logging
from loader import bot


# Команда /guest_rating
@bot.message_handler(commands=['guest_rating'])
def guest_rating(message):
    """
    Обработчик команды /guest_rating.
    Добавляет фильтр по рейтингу гостей (reviewscorebuckets::80) и переадресует запрос в search.py.
    """
    try:
        logging.info("Получена команда /guest_rating.")

        # Устанавливаем фильтр для рейтинга гостей
        categories_filter = "reviewscorebuckets::80"

        # Вызываем обработчик команды /search, передавая дополнительный параметр
        searchWithFilter(message, categories_filter=categories_filter)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса. Пожалуйста, попробуйте позже.")
