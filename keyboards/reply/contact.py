from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def request_contact() -> ReplyKeyboardMarkup:
    keyboards = ReplyKeyboardMarkup(True, True)
    keyboards.add(KeyboardButton('Отправить контакт', request_contact=True))
    return keyboards