from telebot.handler_backends import State, StatesGroup
# 1. Имя
# 2. Возраст
# 3. Страна
# 4. Город
# 5. Номер телефона
class UserInfoState(StatesGroup):
    city = State()
    local = State()
    date_checkin = State()
    date_checkout = State()
    low_price = State()
    high_price = State()