from dateutil import parser
from flask_restful import abort
from mongoengine import ReferenceField, EmbeddedDocumentListField, StringField, DateTimeField, ObjectIdField, \
    EmbeddedDocumentField, ListField

from database.models.common import City
from database.models.offer import Offer


def offer_exists(_id=None):
    return bool(Offer.objects(id=_id).count())


def validate_offer_must_not_exist(title):
    if not title:
        abort(400, message='Field title not exist')

    if Offer.objects(title=title).count():
        abort(400, message='Offer {} exist'.format(title))


def get_fields():
    return Offer._fields.keys()


def get_field_type(field):
    return Offer._fields.get(field)


def filter_offers(filters):
    """
    Filter offers given multiple filters
    :param filters: list of filters
    :type filters: list
    :return: list of offers filtered
    """
    mongo_query_params = []
    for key, value in filters:
        field_type = get_field_type(key)
        query_param = []
        values = value.split(',')
        if type(field_type) == ObjectIdField:
            if len(values[0]) != 24:
                return []
            query_param.append(('pk__in', values))
        elif type(field_type) == ReferenceField:
            reference_obj = field_type.document_type_obj
            filter_references = reference_obj.objects(pk__in=values)
            query_param.append(('{}__in'.format(key), filter_references))
        elif type(field_type) == EmbeddedDocumentField:
            for x in range(0, len(values)):
                cities = City.objects(name__icontains=values[x])
                if cities.count():
                    values = cities
                    query_param.append(('{}__{}__in'.format(key, 'city'), values))
                else:
                    return []
        elif type(field_type) == ListField:
            query_param.append(('{}__in'.format(key), values))
        elif type(field_type) == EmbeddedDocumentListField:
            query_param.append(('{}__{}__in'.format(key, 'name'), values))
        elif type(field_type) == StringField:
            query_param.append(('{}__icontains'.format(key), value))
        elif type(field_type) == DateTimeField:
            try:
                start_date = parser.parse(values[0])
            except Exception:
                start_date = None
            try:
                end_date = parser.parse(values[1])
            except Exception:
                end_date = None
            if start_date:
                query_param.append(('{}__gte'.format(key), start_date))
            if end_date:
                query_param.append(('{}__lte'.format(key), end_date))
        mongo_query_params.extend(query_param)
    mongo_query_params = dict(mongo_query_params)
    return Offer.objects(**mongo_query_params).order_by('-publication_date')
