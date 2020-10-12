from database.db import db


class EducationLevel(db.Document):
    name = db.StringField(required=True)


class LanguageLevel(db.Document):
    name = db.StringField(primary_key=True)


class Language(db.Document):
    code = db.StringField(primary_key=True)
    name = db.StringField()


class StateUser(db.Document):
    name = db.StringField(primary_key=True)


class StateOffer(db.Document):
    name = db.StringField(primary_key=True)


class StatePostulant(db.Document):
    name = db.StringField(primary_key=True)


class StateService(db.Document):
    name = db.StringField(primary_key=True)


class StateServiceRequest(db.Document):
    name = db.StringField(primary_key=True)


class ContractType(db.Document):
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


class ExperienceLevel(db.Document):
    name = db.StringField(primary_key=True)
