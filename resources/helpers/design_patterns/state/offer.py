class OfferState(object):
    name = 'state'
    allowed = []

    def switch(self, state):
        if state.name in self.allowed:
            self.__class__ = state
        else:
            raise Exception('Cannot change from {} to {}'.format(self.name, state.name))


class Active(OfferState):
    name = 'active'
    allowed = ['in_selection', 'deleted', 'finished']


class InSelection(OfferState):
    name = 'in_selection'
    allowed = ['finished', 'deleted', 'active']


class Finished(OfferState):
    name = 'finished'
    allowed = ['deleted']


class Deleted(OfferState):
    name = 'deleted'
    allowed = []


class OfferStateManager(object):
    STATE_DICT = {
        'active': Active,
        'in_selection': InSelection,
        'finished': Finished,
        'deleted': Deleted
    }

    def __init__(self, state):
        self.state = self.STATE_DICT[state]()

    def change(self, state):
        self.state.switch(self.STATE_DICT[state])
