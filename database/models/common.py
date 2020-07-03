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


class Address(db.EmbeddedDocument):
    district = db.StringField()
    street = db.StringField()
    number = db.IntField()
    apartment = db.StringField()
    floor = db.IntField()
    postal_code = db.IntField()
    city = db.ReferenceField(City)


class EducationLevel(db.Document):
    name = db.StringField(required=True)


class Education(db.EmbeddedDocument):
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    name = db.StringField()
    level = db.StringField()
    description = db.StringField()


class Experience(db.EmbeddedDocument):
    company = db.StringField(required=True)
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=True)
    position = db.StringField()
    description = db.StringField()


class Skill(db.EmbeddedDocument):
    name = db.StringField(required=True)
    description = db.StringField()


class UserLanguage(db.EmbeddedDocument):
    name = db.StringField()
    level = db.StringField()


class LanguageLevel(db.Document):
    name = db.StringField(unique=True)


class Language(db.Document):
    name = db.StringField(required=True)


class Scope(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField()


class State(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField()
    scope = db.ReferenceField(Scope)
