from database.utils.CRUD import CRUDInterface
from database.common.models import db, History, User, HistorySearch

db.connect()
db.create_tables([User, History, HistorySearch], safe=True)

crud = CRUDInterface()
