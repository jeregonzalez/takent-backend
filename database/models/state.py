from database.db import db


class Scope(db.Document):
    name = db.StringField(primary_key=True)
    description = db.StringField()


class State(db.Document):
    name = db.StringField(primary_key=True)
    description = db.StringField(required=True)
    scope = db.ReferenceField(Scope)
