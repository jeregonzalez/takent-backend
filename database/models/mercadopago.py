from database.db import db


class OfferPack(db.Document):
    id = db.StringField(primary_key=True)
    common_name = db.StringField()
    item_template = db.DictField()
