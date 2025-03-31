from datetime import datetime
from peewee import Model, CharField, IntegerField, DateTimeField, TextField, SqliteDatabase, ForeignKeyField, AutoField
import os

# Определяем корневую директорию проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, '..', 'history.db')  # Поднимаемся на уровень выше

# Создаем единственный экземпляр базы данных
db = SqliteDatabase(DATABASE_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField(primary_key=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    id_tg = IntegerField(unique=True)

    class Meta:
        table_name = 'users'


class History(BaseModel):
    id_his = AutoField(primary_key=True)
    username = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    city = CharField()
    location = CharField()
    check_in_date = CharField()
    check_out_date = CharField()
    low_price = CharField()
    high_price = CharField()
    photo = TextField(null=True)

    user = ForeignKeyField(User, field='id', backref='histories', null=True)

    class Meta:
        table_name = 'history'


class HistorySearch(BaseModel):
    id_his = AutoField(primary_key=True)
    user_tg_id = IntegerField(index=True, null=True)  # Добавляем индекс
    created_at = DateTimeField(default=datetime.now)
    city = CharField()
    booking_url = CharField()
    description = CharField()
    check_in_date = CharField()
    check_out_date = CharField()
    price = CharField()
    photo = TextField()
    latitude = CharField()
    longitude = CharField()

    class Meta:
        table_name = 'history_search'
