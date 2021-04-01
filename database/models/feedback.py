from database.db import db


class Feedback(db.Document):
    email = db.EmailField(required=True)
    text = db.StringField(required=True)
