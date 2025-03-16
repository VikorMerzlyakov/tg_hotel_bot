from typing import Dict, List
from peewee import ModelSelect
from database.common.models import History, User

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

# Создаем экземпляр интерфейса
crud = CRUDInterface()