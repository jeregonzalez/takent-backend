from database.db import db


class EducationLevel(db.Document):
    name = db.StringField(required=True)


class LanguageLevel(db.Document):
    name = db.StringField(primary_key=True)


class Language(db.Document):
    code = db.StringField(primary_key=True)
    name = db.StringField()


class State(db.Document):
    name = db.StringField(primary_key=True)
    scope = db.StringField()


class JobType(db.Document):
    name = db.StringField(primary_key=True)


class Sector(db.Document):
    name = db.StringField(primary_key=True)


class EnterpriseType(db.Document):
    name = db.StringField(primary_key=True)


class Profession(db.Document):
    id = db.IntField(primary_key=True)
    name = db.StringField()


class OfferPack(db.Document):
    id = db.StringField(primary_key=True)
    common_name = db.StringField()
    item_template = db.DictField()


class Permission(db.Document):
    name = db.StringField(primary_key=True)
