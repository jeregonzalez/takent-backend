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
    allowed = ['in_course', 'completed']


class InCourse(ServiceRequestState):
    name = 'in_course'
    allowed = ['completed']


class Completed(ServiceRequestState):
    name = 'completed'
    allowed = []


class ServiceRequestStateManager(object):
    STATE_DICT = {
        'pending': Pending,
        'in_course': InCourse,
        'completed': Completed,
    }

    def __init__(self, state):
        self.state = self.STATE_DICT[state]()

    def change(self, state):
        self.state.switch(self.STATE_DICT[state])
