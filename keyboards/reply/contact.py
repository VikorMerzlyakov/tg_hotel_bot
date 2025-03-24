from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def request_location() -> ReplyKeyboardMarkup:
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboards.add(KeyboardButton("Центр города"))
    keyboards.add(KeyboardButton("Окраина"))
    keyboards.add(KeyboardButton("Аэропорт"))
    return keyboards




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