import logging
from datetime import datetime
from typing import Dict, List
from peewee import ModelSelect, OperationalError
from database.common.models import History, User, History_search
from typing import List, Dict
from database.common.models import History


def _store_data(data: Dict) -> None:
    """
    Сохраняет данные в таблицу History.
    :param data: Словарь с данными для записи.
    """
    History.create(
        user=data['user_id'],
        username=data.get('username'),
        city=data['city'],
        location=data['location'],
        check_in_date=data['check_in_date'],
        check_out_date=data['check_out_date'],
        low_price=data['low_price'],
        high_price=data['high_price']
    )


def _store_user_data(data: Dict) -> None:
    """
    Сохраняет данные в таблицу User.
    :param data: Словарь с данными для записи.
    """
    User.create(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        id_tg=data['id_tg']  # Telegram ID пользователя
    )


def _retrieve_all_data() -> List[Dict]:
    """
    Извлекает все записи из таблицы History.
    :return: Список словарей с данными.
    """
    query = History.select()
    return [
        {
            'user_id': record.user_id,
            'username': record.username,
            'city': record.city,
            'location': record.location,
            'check_in_date': record.check_in_date,
            'check_out_date': record.check_out_date,
            'low_price': record.low_price,
            'high_price': record.high_price,
            'created_at': record.created_at
        }
        for record in query
    ]


def _retrieve_all_users() -> List[Dict]:
    """
    Извлекает все записи из таблицы User.
    :return: Список словарей с данными.
    """
    query = User.select()
    return [
        {
            'id': record.id,
            'first_name': record.first_name,
            'last_name': record.last_name,
            'id_tg': record.id_tg
        }
        for record in query
    ]


def _retrieve_history_by_tg_id(tg_id: int) -> List[Dict]:
    """
    Извлекает записи из таблицы History для пользователя с указанным Telegram ID.
    :param tg_id: Telegram ID пользователя.
    :return: Список словарей с данными.
    """
    # Запрос к таблице history, где user_id равен tg_id
    query = (
        History
        .select()
        .where(History.user == tg_id)  # Фильтруем по user_id
        .order_by(History.created_at.desc())  # Сортируем по дате создания (последние записи первыми)
    )

    # Преобразуем результаты в список словарей
    return [
        {
            'user_id': record.user_id,
            'username': record.username,
            'city': record.city,
            'location': record.location,
            'check_in_date': record.check_in_date,
            'check_out_date': record.check_out_date,
            'low_price': record.low_price,
            'high_price': record.high_price,
            'created_at': record.created_at
        }
        for record in query
    ]




def _retrieve_user_history(user_id: int) -> List[Dict]:
    """
    Извлекает историю запросов для конкретного пользователя.
    :param user_id: ID пользователя в Telegram.
    :return: Список словарей с данными.
    """

    query = History.select().where(History.user == user_id)

    # Форматирование данных
    history_data = [
        {
            'username': record.username,
            'city': record.city,
            'location': record.location,
            'check_in_date': record.check_in_date,
            'check_out_date': record.check_out_date,
            'low_price': record.low_price,
            'high_price': record.high_price,
            'created_at': record.created_at
        }
        for record in query
    ]

    return history_data


def _retrieve_search_history(user_tg_id: int) -> List[Dict]:
    """
    Извлекает историю запросов для конкретного пользователя.
    :param user_tg_id: Telegram ID пользователя.
    :return: Список словарей с данными.
    """
    try:
        # Запрос к таблице history_search
        query = History_search.select().where(History_search.user_tg_id == user_tg_id)

        # Форматирование данных
        history_data = [
            {
                'id_his': record.id_his,
                'user_tg_id': record.user_tg_id,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'city': record.city,
                'booking_url': record.booking_url,
                'description': record.description,
                'check_in_date': record.check_in_date,
                'check_out_date': record.check_out_date,
                'price': record.price,
                'photo': record.photo.split(", ") if record.photo else [],
                'latitude': record.latitude,
                'longitude': record.longitude
            }
            for record in query
        ]

        return history_data

    except Exception as e:
        print(f"Произошла ошибка при извлечении данных из БД: {e}")
        return []


def _save_hotel_info_to_db(user_tg_id: int, hotels_list: list):
    """
    Сохраняет данные об отелях в таблицу History_search.

    :param user_tg_id: Telegram ID пользователя.
    :param hotels_list: Список словарей с данными об отелях.
    """
    try:
        for hotel in hotels_list:
            # Создаем запись в таблице History_search
            History_search.create(
                user_tg_id=user_tg_id,
                created_at=datetime.now(),
                city=hotel.get("name", "Unknown City"),
                booking_url=hotel.get("booking_url", ""),
                description=hotel.get("description", ""),
                check_in_date=hotel.get("dates", "").split(" - ")[0],
                check_out_date=hotel.get("dates", "").split(" - ")[1] if " - " in hotel.get("dates", "") else "",
                price=hotel.get("price", ""),
                photo=", ".join(hotel.get("photos", [])),  # Преобразуем список фото в строку
                latitude=hotel.get("coordinates", {}).get("latitude", ""),  # Добавляем широту
                longitude=hotel.get("coordinates", {}).get("longitude", "")  # Добавляем долготу
            )
        print(f"Данные успешно сохранены для пользователя с tg_id={user_tg_id}")
    except Exception as e:
        print(f"Произошла ошибка при сохранении данных в БД: {e}")

class CRUDInterface:
    @staticmethod
    def create():
        return _store_data

    @staticmethod
    def create_user():
        return _store_user_data

    @staticmethod
    def retrieve():
        return _retrieve_all_data

    @staticmethod
    def retrieve_users():
        return _retrieve_all_users

    @staticmethod
    def retrieve_history_by_tg_id():
        return _retrieve_history_by_tg_id

    @staticmethod
    def retrieve_user_history():
        return _retrieve_user_history

    @staticmethod
    def save_hotel_info_to_db(user_tg_id: int, hotels_list: list):
        return _save_hotel_info_to_db(user_tg_id, hotels_list)

    @staticmethod
    def retrieve_search_history(user_tg_id: int):
        return _retrieve_search_history(user_tg_id)



# Создаем экземпляр интерфейса
#crud = CRUDInterface()
if __name__ == "__main__":
    # Тестовый tg_id пользователя
    test_user_tg_id = 123456789

    # Вызов функции для получения истории запросов
    history_data = _retrieve_search_history(test_user_tg_id)

    # Вывод результата
    if history_data:
        print("История запросов пользователя:")
        for entry in history_data:
            print(f"""
            ID записи: {entry['id_his']}
            Город: {entry['city']}
            Ссылка на бронирование: {entry['booking_url']}
            Описание: {entry['description']}
            Дата заезда: {entry['check_in_date']}
            Дата выезда: {entry['check_out_date']}
            Цена: {entry['price']}
            Фотографии: {entry['photo']}
            Координаты: Широта - {entry['latitude']}, Долгота - {entry['longitude']}
            Дата запроса: {entry['created_at']}
            ---""")
    else:
        print("История запросов пуста или произошла ошибка.")