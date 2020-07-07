from database.db import db


class Permission(db.Document):
    name = db.StringField(primary_key=True)
    description = db.StringField(required=True)


class Role(db.Document):
    name = db.StringField(primary_key=True)
    description = db.StringField(required=True)
    permissions = db.ListField(db.ReferenceField(Permission), required=True)
