from flask_bcrypt import generate_password_hash, check_password_hash

from .db import db


class User(db.Document):
    account = db.StringField(required=True, unique=True)
    password = db.StringField(required=True, min_length=6)
    name = db.StringField(required=True)
    surname = db.StringField(required=True)
    dni = db.IntField(required=True)
    birth_date = db.DateTimeField()

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password, password)
