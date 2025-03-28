from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def dynamic_keyboard(options: list) -> ReplyKeyboardMarkup:
    """
    Создает динамическую клавиатуру на основе переданных опций.

    :param options: Список строк (названия кнопок).
    :return: Клавиатура с динамическими кнопками.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for option in options:
        keyboard.add(KeyboardButton(option))
    return keyboard

def create_date_keyboard(dates):
    """
    Создает инлайн-клавиатуру с уникальными датами для выбора.

    :param dates: Список уникальных дат (например, ['2025-03-23', '2025-03-24']).
    :return: Объект InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(date, callback_data=f"history_date:{date}") for date in dates]
    keyboard.add(*buttons)
    return keyboard