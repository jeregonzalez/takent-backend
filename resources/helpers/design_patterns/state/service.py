class ServiceState(object):
    name = 'state'
    allowed = []

    def switch(self, state):
        if state.name in self.allowed:
            self.__class__ = state
        else:
            raise Exception('Cannot change from {} to {}'.format(self.name, state.name))


class Active(ServiceState):
    name = 'active'
    allowed = ['inactive', 'deleted']


class Inactive(ServiceState):
    name = 'inactive'
    allowed = ['active', 'deleted']


class Deleted(ServiceState):
    name = 'deleted'
    allowed = []


class ServiceStateManager(object):
    STATE_DICT = {
        'active': Active,
        'inactive': Inactive,
        'deleted': Deleted
    }

    def __init__(self, state):
        self.state = self.STATE_DICT[state]()

    def change(self, state):
        self.state.switch(self.STATE_DICT[state])
