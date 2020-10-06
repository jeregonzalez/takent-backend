from bson import ObjectId

from database.db import db


class UserEducation(db.EmbeddedDocument):
    id = db.ObjectIdField(default=ObjectId)
    title = db.StringField()
    institution = db.StringField()
    description = db.StringField()
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    level = db.StringField()


class UserExperience(db.EmbeddedDocument):
    id = db.ObjectIdField(default=ObjectId)
    position = db.StringField(required=True)
    company = db.StringField(required=True)
    description = db.StringField()
    reference = db.DictField()
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField()
    profession = db.StringField()


class UserSkill(db.EmbeddedDocument):
    id = db.ObjectIdField(default=ObjectId)
    name = db.StringField(required=True)
    description = db.StringField()


class UserCurriculumVitae(db.Document):
    name = db.StringField()
    base64 = db.StringField(required=True)


class UserLanguage(db.EmbeddedDocument):
    id = db.ObjectIdField(default=ObjectId)
    language = db.StringField(required=True)
    writing_level = db.StringField(required=True)
    communication_level = db.StringField(required=True)
    certificate = db.BooleanField(default=False)
    description = db.StringField(max_length=300)
