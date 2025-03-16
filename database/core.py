from database.utils.CRUD import CRUDInterface
from database.common.models import db, History, User

db.connect()
db.create_tables([User, History], safe=True)

crud = CRUDInterface()