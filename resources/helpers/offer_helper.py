

from database.models.offer import Offer
from database.models.common import State
from flask_restful import abort

from database.models.users import EnterpriseUser


def validate_offer_must_exist(id=None, user=None):
    if not id:
        return
    elif len(id) != 24:
        abort(400, message='Offer not exist')
    if not Offer.objects(id=id, publication_user=EnterpriseUser.objects.get(account=user), state=State.objects.get(name='active')).count():
        abort(400, message='Offer not exist')


def validate_offer_must_not_exist(title):
    if not title:
        abort(400, message='Field title not exist')

    if Offer.objects(title=title).count():
        abort(400, message='Offer {} exist'.format(title))
