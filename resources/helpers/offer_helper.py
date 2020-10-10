import random

from dateutil import parser
from mongoengine import ReferenceField, EmbeddedDocumentListField, StringField, DateTimeField, ObjectIdField, \
    EmbeddedDocumentField, ListField, InvalidQueryError, LookUpError

from database.models.common import City
from database.models.offer import Offer
from database.models.place import Province, Country
from resources.utils.exceptions import GetException

FILTER_OPTIONS = ['strict', 'sort']


def offer_exists(_id=None):
    return bool(Offer.objects(id=_id).count())


def get_fields():
    return list(Offer._fields.keys())


def get_field_type(field):
    return Offer._fields.get(field)


def validate_filter_keys(keys):
    filter_keys = get_fields() + FILTER_OPTIONS
    bad_keys = [key for key in keys if key.split('.')[0] not in filter_keys]
    return not bool(bad_keys), bad_keys


def filter_offers(filters):
    """
    Filter offers given multiple filters
    :param filters: list of filters
    :type filters: list
    :return: list of offers filtered
    """
    mongo_query_params = []
    strict = any(key == 'strict' and value.lower() == 'true' for key, value in filters)
    for key, value in filters:
        field_type = get_field_type(key)
        query_param = []
        values = value.split(',')
        if type(field_type) == ObjectIdField:
            query_param.append(('pk__in', values))
        elif type(field_type) == ReferenceField:
            reference_obj = field_type.document_type_obj
            filter_references = reference_obj.objects(pk__in=values)
            query_param.append(('{}__in'.format(key), filter_references))
        elif type(field_type) == ListField:
            query_param.append(('{}__in'.format(key), values))
        elif type(field_type) == EmbeddedDocumentListField:
            query_param.append(('{}__{}__in'.format(key, 'name'), values))
        elif type(field_type) == StringField:
            operator = 'iexact' if strict else 'icontains'
            query_param.append(('{}__{}'.format(key, operator), value))
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
        elif key.startswith('language'):
            keys = '__'.join(key.split('.'))
            if 'certificate' in keys:
                values = [True if value == 'true' else False for value in values]
            query_param.append(('{}__in'.format(keys), values))
        elif key.startswith('address'):
            keys = key.split('.')
            if keys[1] == 'province':
                province_codes = [province.code for province in Country.objects.get(code=1).provinces
                                  if province.name in values]
                city_codes = [city.code for city in City.objects(province_id__in=province_codes)]
            else:
                city_codes = [city.code for city in City.objects(name__in=values)]
            query_param.append(('address__city__in', city_codes))
        mongo_query_params.extend(query_param)
    mongo_query_params = dict(mongo_query_params)
    sort = [filter_sort for filter_sort in filters if filter_sort[0] == 'sort']
    if sort:
        sort = sort[0][1]
        if sort == 'desc':
            get_offers = lambda: Offer.objects(**mongo_query_params).order_by('-publication_date')
        elif sort == 'random':
            def get_offers():
                list_offers = [offer for offer in Offer.objects(**mongo_query_params)]
                random.shuffle(list_offers)
                return list_offers
        else:
            get_offers = lambda: Offer.objects(**mongo_query_params).order_by('+publication_date')
    else:
        get_offers = lambda: Offer.objects(**mongo_query_params).order_by('+publication_date')
    try:
        offers = get_offers()
    except (InvalidQueryError, LookUpError) as e:
        raise GetException(e)
    return offers
