from mongoengine import NULLIFY

from database.db import db
from database.models.common import Address, Image
from database.models.offer import Offer
from database.models.parametric_docs import State
from database.models.user import EnterpriseUser


class Enterprise(db.Document):
    fantasy_name = db.StringField(required=True)
    business_name = db.StringField(required=True)
    profile_photo = db.ReferenceField(Image, reverse_delete_rule=NULLIFY)
    contact_phone = db.IntField()
    contact_email = db.EmailField()
    images = db.ListField(db.ReferenceField(Image))
    description = db.StringField()
    web_page = db.StringField()
    available_offers = db.IntField(default=10)
    address = db.EmbeddedDocumentField(Address)
    admin_user = db.ReferenceField(EnterpriseUser, required=True)
    member_users = db.ListField(db.ReferenceField(EnterpriseUser))
    enterprise_type = db.StringField()
    sector = db.StringField()
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='active'))
    offers = db.ListField(db.ReferenceField(Offer))
