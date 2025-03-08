from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def request_location() -> ReplyKeyboardMarkup:
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboards.add(KeyboardButton("Центр города"))
    keyboards.add(KeyboardButton("Окраина"))
    keyboards.add(KeyboardButton("Аэропорт"))
    return keyboards