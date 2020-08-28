from mongoengine import InvalidQueryError

from database.models.offer import Offer
from database.models.common import State
from flask_restful import abort, request

from database.models.user import EnterpriseUser


def validate_offer_id_state_must_exist(id=None, state=None, user=None):
    if not id and not state:
        return

    if id:
        if len(id) != 24:
            abort(400, message='Offer not exist')
        else:
            if not Offer.objects(id=id, publication_user=EnterpriseUser.objects.get(account=user),
                                 state=State.objects.get(name='active')).count():
                abort(400, message='Offer not exist')


def validate_offer_must_exist(id=None, user=None):
    if not id:
        return
    elif len(id) != 24:
        abort(400, message='Offer not exist')
    if not Offer.objects(id=id, publication_user=EnterpriseUser.objects.get(account=user)).count():
        abort(400, message='Offer not exist')


def validate_offer_must_not_exist(title):
    if not title:
        abort(400, message='Field title not exist')

    if Offer.objects(title=title).count():
        abort(400, message='Offer {} exist'.format(title))


def validate_attributes_exist(account, attr):
    aux = []
    states = {}
    if not attr.get('publication_user'):
        attr['publication_user'] = account

    if attr.get('state'):
        aux = attr['state'].split(',')
        states = {'1': 'active', '2': 'inactive', '3': 'in_selection', '4': 'finished', '5': 'deleted'}
        for state in aux:
            if State.objects(name=states.get(state)).count():
                states[state] = State.objects.get(name=states.get(state))
            else:
                abort(400, message='State not exist')

    if attr.get('language'):
        language = attr['language']
        attr['language__match'] = attr.pop('language')
        attr['language__match'] = {"name__icontains": language}

    try:
        if attr.get('state'):
            for state in aux:
                attr['state'] = states[state]
                Offer.objects(**attr).count()

        Offer.objects(**attr).count()
    except InvalidQueryError:
        abort(400, message='Field not exist')
