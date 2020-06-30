from database.db import db


class City(db.Document):
    code = db.IntField(unique=True)
    name = db.StringField(required=True)
    province_id = db.IntField(required=True)


class Province(db.EmbeddedDocument):
    code = db.IntField(unique=True)
    name = db.StringField(required=True)
    cities = db.ListField(db.ReferenceField(City))


class Country(db.Document):
    code = db.IntField(unique=True)
    name = db.StringField(required=True)
    provinces = db.EmbeddedDocumentListField(Province)


class Address(db.EmbeddedDocument):
    district = db.StringField()
    street = db.StringField()
    number = db.IntField()
    apartment = db.StringField()
    floor = db.IntField()
    postal_code = db.IntField()
    city = db.ReferenceField(City)


class EducationLevel(db.Document):
    name = db.StringField(unique=True, required=True)


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
