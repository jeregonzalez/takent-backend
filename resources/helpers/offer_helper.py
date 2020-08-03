from database.models.offer import Offer
from database.models.common import State
from flask_restful import abort

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
