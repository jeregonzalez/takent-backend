from datetime import datetime, date

from dateutil.relativedelta import relativedelta

from database.models.offer import Offer
from database.models.parametric_docs import StateOffer, StatePostulant
from resources.helpers import enterprise_helper


def get_offers_per_month(date_from=None, date_to=None):
    enterprise = enterprise_helper.get_enterprise()

    date_filters = {}
    if date_from:
        date_filters['publication_date__gte'] = datetime.combine(date_from, datetime.min.time())
    if date_to:
        date_filters['publication_date__lte'] = datetime.combine(date_to, datetime.max.time())

    offers = Offer.objects(
        enterprise=enterprise,
        state__nin=['deleted', 'programmed', 'draft'],
        **date_filters
    )

    if not date_from:
        if date_to:
            min_date = date_to - relativedelta(months=11)
        else:
            min_date = date.today() - relativedelta(months=11)
    else:
        min_date = date_from
    max_date = date_to or date.today()
    months = (max_date.year - min_date.year) * 12 + (max_date.month - min_date.month) + 1

    offers_per_month = []
    for i in range(0, months):
        aux_date = min_date + relativedelta(months=i)
        offers_per_month.append({'month': aux_date.strftime('%m/%y'), 'quantity': 0})

    for offer in offers:
        publication_month = offer.publication_date.strftime('%m/%y')
        [stat for stat in offers_per_month if stat.get('month') == publication_month][0]['quantity'] += 1

    return list(offers_per_month)


def get_offers_with_greater_postulants_amount(date_from=None, date_to=None, quantity=5):
    enterprise = enterprise_helper.get_enterprise()

    date_filters = {}
    if date_from:
        date_filters['publication_date__gte'] = datetime.combine(date_from, datetime.min.time())
    if date_to:
        date_filters['publication_date__lte'] = datetime.combine(date_to, datetime.max.time())

    offers = Offer.objects(enterprise=enterprise, state__nin=['draft', 'programmed', 'deleted'], **date_filters)

    result = [{'title': offer.title, 'postulants': len(offer.postulants)} for offer in offers]
    result.sort(key=lambda offer: offer.get('postulants'), reverse=True)
    result = result[:quantity]

    existing_titles = []
    for item in result:
        for existing_title in existing_titles:
            if existing_title[0] == item.get('title'):
                existing_title[1] += 1
                item['title'] += ' (%s)' % existing_title[1]
                break
        else:
            existing_titles.append([item.get('title'), 0])

    return result


def get_offers_by_state(date_from=None, date_to=None):
    enterprise = enterprise_helper.get_enterprise()

    date_filters = {}
    if date_from:
        date_filters['publication_date__gte'] = datetime.combine(date_from, datetime.min.time())
    if date_to:
        date_filters['publication_date__lte'] = datetime.combine(date_to, datetime.max.time())

    offers = Offer.objects(enterprise=enterprise, state__ne='deleted', **date_filters)

    result = [{'state': state.name, 'quantity': 0} for state in StateOffer.objects(name__ne='deleted')]
    for offer in offers:
        [stat for stat in result if stat.get('state') == offer.state.name][0]['quantity'] += 1

    return result


def get_postulants_age(date_from=None, date_to=None, min=18, max=65, interval_length=10):
    enterprise = enterprise_helper.get_enterprise()

    date_filters = {}
    if date_from:
        date_filters['publication_date__gte'] = datetime.combine(date_from, datetime.min.time())
    if date_to:
        date_filters['publication_date__lte'] = datetime.combine(date_to, datetime.max.time())

    offers = Offer.objects(enterprise=enterprise, state__ne='deleted', **date_filters)
    postulant_ages = []
    for offer in offers:
        postulant_ages.extend([__get_age(postulant.postulant.birth_date) for postulant in offer.postulants])

    age_ranges = {'{}-{}'.format(i, i + interval_length - 1) if i + interval_length < max else '+{}'.format(i - 1): (i, i + interval_length - 1)
                  for i in range(min, max, interval_length)}

    result = [{'age': age_range, 'quantity': 0} for age_range in age_ranges.keys()]
    for age in postulant_ages:
        for label, age_range in age_ranges.items():
            if age_range[0] <= age <= age_range[1]:
                [stat for stat in result if stat.get('age') == label][0]['quantity'] += 1
                break
        else:
            [stat for stat in result if stat.get('age') == label][0]['quantity'] += 1

    return result


def __get_age(birth_date):
    days_in_year = 365.2425
    age = int((datetime.now() - birth_date).days / days_in_year)
    return age


def get_postulants_by_state_by_month(date_from=None, date_to=None):
    enterprise = enterprise_helper.get_enterprise()

    date_filters = {}
    if date_from:
        date_filters['publication_date__gte'] = datetime.combine(date_from, datetime.min.time())
    if date_to:
        date_filters['publication_date__lte'] = datetime.combine(date_to, datetime.max.time())

    offers = Offer.objects(
        enterprise=enterprise,
        **date_filters
    )

    if not date_from:
        if date_to:
            min_date = date_to - relativedelta(months=5)
        else:
            min_date = date.today() - relativedelta(months=5)
    else:
        min_date = date_from
    max_date = date_to or date.today()
    months = (max_date.year - min_date.year) * 12 + (max_date.month - min_date.month) + 1
    postulant_states = [state.name for state in StatePostulant.objects]

    result = []
    for i in range(0, months):
        aux_date = min_date + relativedelta(months=i)
        stat = {**{'month': aux_date.strftime('%m/%y')}, **{state: 0 for state in postulant_states}}
        result.append(stat)

    for offer in offers:
        for postulant in offer.postulants:
            publication_month = offer.publication_date.strftime('%m/%y')
            [stat for stat in result if stat.get('month') == publication_month][0][postulant.state.name] += 1

    return result
