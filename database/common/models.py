from datetime import datetime
from peewee import Model, CharField, IntegerField, DateTimeField, TextField, SqliteDatabase, ForeignKeyField, AutoField

db = SqliteDatabase('history.db')  # Имя файла базы данных

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
    city = CharField()
    location = CharField()
    check_in_date = CharField()
    check_out_date = CharField()
    low_price = CharField()
    high_price = CharField()
    photo = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    user = ForeignKeyField(User, field='id', backref='histories', null=True)

    class Meta:
        table_name = 'history'