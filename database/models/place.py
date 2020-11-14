from database.db import db


class City(db.Document):
    code = db.IntField(primary_key=True)
    name = db.StringField(required=True)
    province_id = db.IntField(required=True)


class Province(db.EmbeddedDocument):
    code = db.IntField(primary_key=True)
    name = db.StringField(required=True)
    cities = db.ListField(db.ReferenceField(City))


class Country(db.Document):
    code = db.IntField(primary_key=True)
    name = db.StringField(required=True)
    provinces = db.SortedListField(db.EmbeddedDocumentField(Province), ordering='_id')
