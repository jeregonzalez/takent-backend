from flask_restful import abort
from database.models.common import State


def validate_state_exist(name_state):
    if not State.objects(name=name_state).count():
        abort(400, message='State {} not exists'.format(name_state))
