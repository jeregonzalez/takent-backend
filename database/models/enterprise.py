from database.db import db
from database.models.common import Address, State
from database.models.users import EnterpriseUser


# TODO Investigar como guardar imagenes en la base de datos
class Enterprise(db.Document):
    fantasy_name = db.StringField(required=True)
    business_name = db.StringField(required=True)
    address = db.EmbeddedDocumentField(Address)
    phone = db.IntField()
    email = db.EmailField(required=True)
    location = db.StringField()
    profile_photo = db.ImageField()
    photos = db.ListField(db.ImageField())
    description = db.StringField()
    admin_user = db.ReferenceField(EnterpriseUser, required=True)
    member_users = db.ListField(db.ReferenceField(EnterpriseUser))
    state = db.ReferenceField(State)
