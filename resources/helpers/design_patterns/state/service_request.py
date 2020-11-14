class ServiceRequestState(object):
    name = 'state'
    allowed = []

    def switch(self, state):
        if state.name in self.allowed:
            self.__class__ = state
        else:
            raise Exception('Cannot change from {} to {}'.format(self.name, state.name))


class Pending(ServiceRequestState):
    name = 'pending'
    allowed = ['completed', 'canceled']


class Completed(ServiceRequestState):
    name = 'completed'
    allowed = []


class Canceled(ServiceRequestState):
    name = 'canceled'
    allowed = []


class ServiceRequestStateManager(object):
    STATE_DICT = {
        'pending': Pending,
        'completed': Completed,
        'canceled': Canceled
    }

    def __init__(self, state):
        self.state = self.STATE_DICT[state]()

    def change(self, state):
        self.state.switch(self.STATE_DICT[state])
