from datetime import datetime

from peewee import Model, CharField, IntegerField, DateTimeField, TextField, SqliteDatabase, ForeignKeyField

db = SqliteDatabase('history.db')  # Имя файла базы данных

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    """
    Класс для хранения данных о пользователе.
    """
    id = IntegerField(primary_key=True)  # Уникальный ID пользователя в базе данных
    first_name = CharField(null=True)   # Имя пользователя
    last_name = CharField(null=True)    # Фамилия пользователя
    id_tg = IntegerField(unique=True)   # Telegram ID пользователя (уникальное значение)

    class Meta:
        table_name = 'users'

class History(BaseModel):
    id_his = IntegerField()
    username = CharField(null=True)  # Имя пользователя
    city = CharField()  # Город
    location = CharField()  # Локация
    photo = TextField(null=True)  # Поле для хранения фото - URL
    created_at = DateTimeField(default=datetime.now)  # Время создания записи
    user = ForeignKeyField(User, field='id', backref='histories', null=True)  # Связь с таблицей User

    class Meta:
        table_name = 'history'
