from telebot.handler_backends import State, StatesGroup

class UserInfoState(StatesGroup):
    '''
    класс содержащий в себе данные о состоянии пользователя:
    city = Город
    local = Локация
    date_checkin = Дата заезда
    date_checkout = Дата выселения
    low_price = Нижний порог цены
    high_price = Верхний порог цены
    '''
    city = State()
    local = State()
    date_checkin = State()
    date_checkout = State()
    low_price = State()
    high_price = State()