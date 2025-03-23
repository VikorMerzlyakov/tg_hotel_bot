from database.utils.CRUD import CRUDInterface
from database.common.models import db, History, User, History_search

db.connect()
db.create_tables([User, History, History_search], safe=True)

crud = CRUDInterface()
