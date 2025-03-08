from telebot.handler_backends import State, StatesGroup
# 1. Имя
# 2. Возраст
# 3. Страна
# 4. Город
# 5. Номер телефона
class UserInfoState(StatesGroup):
    name = State()
    age = State()
    country = State()
    city = State()
    phone_number = State()