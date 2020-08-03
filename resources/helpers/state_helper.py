from flask_restful import abort
from database.models.common import State


def validate_state_must_exist(state):
    if not State.objects(name=state).count():
        abort(400, message='State {} not exists'.format(state))
