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

    def format_response(self):
        response = super(Address, self).to_mongo()
        if response.get('city'):
            city = City.objects.get(code=response['city'])
            province = list(filter(lambda obj: obj.code == city.province_id,
                                   Country.objects.get(code=1).provinces))[0]
            response['province'] = {'code': province.code, 'name': province.name}
            response['city'] = {'code': city.code, 'name': city.name}
        return response


class EducationLevel(db.Document):
    name = db.StringField(required=True)


class Education(db.EmbeddedDocument):
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    institution = db.StringField()
    name = db.StringField()
    level = db.StringField()
    description = db.StringField()


class Experience(db.EmbeddedDocument):
    company = db.StringField(required=True)
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField()
    position = db.StringField(required=True)
    description = db.StringField()
    reference = db.DictField()


class Skill(db.EmbeddedDocument):
    name = db.StringField(required=True)
    description = db.StringField()


class UserLanguage(db.EmbeddedDocument):
    name = db.StringField(required=True)
    writing_level = db.StringField(required=True)
    reading_level = db.StringField(required=True)


class LanguageLevel(db.Document):
    name = db.StringField(primary_key=True)


class Language(db.Document):
    code = db.StringField(primary_key=True)
    name = db.StringField()


class Scope(db.Document):
    name = db.StringField(primary_key=True)
    description = db.StringField()


class State(db.Document):
    name = db.StringField(primary_key=True)
    description = db.StringField()
    scope = db.ReferenceField(Scope)


class Image(db.Document):
    base64 = db.StringField()
