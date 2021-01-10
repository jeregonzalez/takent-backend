from datetime import datetime

from dateutil.relativedelta import relativedelta

from database.models.offer import Offer
from database.models.parametric_docs import StateOffer, StatePostulant
from resources.helpers import enterprise_helper


def get_offers_per_month(months=12):
    enterprise = enterprise_helper.get_enterprise()

    min_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - \
               relativedelta(months=months)
    offers = Offer.objects(enterprise=enterprise, state__nin=['deleted', 'programmed'],
                           publication_date__gte=min_date)

    offers_per_month = []
    for i in range(1, months + 1):
        date = min_date + relativedelta(months=i)
        offers_per_month.append({'month': date.strftime('%m/%Y'), 'quantity': 0})

    for offer in offers:
        publication_month = offer.publication_date.strftime('%m/%Y')
        [stat for stat in offers_per_month if stat.get('month') == publication_month][0]['quantity'] += 1

    return list(offers_per_month)


def get_offers_with_greater_postulants_amount(quantity=10):
    enterprise = enterprise_helper.get_enterprise()

    offers = Offer.objects(enterprise=enterprise)

    result = [{'title': offer.title, 'postulants': len(offer.postulants)} for offer in offers]
    result.sort(key=lambda offer: offer.get('postulants'), reverse=True)
    result = result[:quantity]

    return result


def get_offers_by_state():
    enterprise = enterprise_helper.get_enterprise()

    offers = Offer.objects(enterprise=enterprise, state__ne='deleted')

    result = [{'state': state.name, 'quantity': 0} for state in StateOffer.objects(name__ne='deleted')]
    for offer in offers:
        [stat for stat in result if stat.get('state') == offer.state.name][0]['quantity'] += 1

    return result


def get_postulants_age(min=18, max=65, interval_length=10):
    enterprise = enterprise_helper.get_enterprise()

    offers = Offer.objects(enterprise=enterprise, state__ne='deleted')
    postulant_ages = []
    for offer in offers:
        postulant_ages.extend([__get_age(postulant.postulant.birth_date) for postulant in offer.postulants])

    age_ranges = {'{}-{}'.format(i, i + interval_length - 1): (i, i + interval_length - 1)
                  for i in range(min, max, interval_length)}

    result = [{'age': age_range, 'quantity': 0} for age_range in age_ranges.keys()]
    for age in postulant_ages:
        for label, age_range in age_ranges.items():
            if age_range[0] <= age <= age_range[1]:
                [stat for stat in result if stat.get('age') == label][0]['quantity'] += 1
                break

    return result


def __get_age(birth_date):
    days_in_year = 365.2425
    age = int((datetime.now() - birth_date).days / days_in_year)
    return age


def get_postulants_by_state_by_month(months=6):
    enterprise = enterprise_helper.get_enterprise()

    min_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - \
               relativedelta(months=months)
    offers = Offer.objects(enterprise=enterprise)
    postulant_states = [state.name for state in StatePostulant.objects]

    result = []
    for i in range(1, months + 1):
        date = min_date + relativedelta(months=i)
        stat = {**{'month': date.strftime('%m/%Y')}, **{state: 0 for state in postulant_states}}
        result.append(stat)

    for offer in offers:
        for postulant in offer.postulants:
            publication_month = offer.publication_date.strftime('%m/%Y')
            [stat for stat in result if stat.get('month') == publication_month][0][postulant.state.name] += 1

    return result
