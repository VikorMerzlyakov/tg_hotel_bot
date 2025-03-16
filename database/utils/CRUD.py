from typing import Dict, List
from peewee import ModelSelect
from database.common.models import History

def _store_data(data: Dict) -> None:
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

def _retrieve_all_data() -> List[Dict]:
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

class CRUDInterface:
    @staticmethod
    def create():
        return _store_data

    @staticmethod
    def retrieve():
        return _retrieve_all_data