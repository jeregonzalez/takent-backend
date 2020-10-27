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
    allowed = ['inactive', 'finished']


class Inactive(ServiceState):
    name = 'inactive'
    allowed = ['active', 'finished']


class Finished(ServiceState):
    name = 'finished'
    allowed = []


class ServiceStateManager(object):
    STATE_DICT = {
        'active': Active,
        'inactive': Inactive,
        'finished': Finished
    }

    def __init__(self, state):
        self.state = self.STATE_DICT[state]()

    def change(self, state):
        self.state.switch(self.STATE_DICT[state])
