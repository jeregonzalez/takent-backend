from database.db import db
from database.models.place import City, Country


class Address(db.EmbeddedDocument):
    city = db.ReferenceField(City)
    district = db.StringField()
    street = db.StringField()
    number = db.IntField()
    tower = db.StringField()
    apartment = db.StringField()
    floor = db.IntField()
    postal_code = db.IntField()
    location = db.DictField()

    def format_response(self):
        response = super(Address, self).to_mongo()
        if response.get('city'):
            city = City.objects.get(code=response['city'])
            province = list(filter(lambda obj: obj.code == city.province_id,
                                   Country.objects.get(code=1).provinces))[0]
            response['province'] = {'code': province.code, 'name': province.name}
            response['city'] = {'code': city.code, 'name': city.name}
        return response


class Image(db.Document):
    name = db.StringField()
    base64 = db.StringField()
