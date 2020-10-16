from database.models.parametric_docs import StatePostulant


class PostulantState(object):
    name = 'state'
    allowed = []

    def switch(self, state):
        if state.name in self.allowed:
            self.__class__ = state
        else:
            raise Exception('Cannot change from {} to {}'.format(self.name, state.name))


class Pending(PostulantState):
    name = 'pending'
    allowed = ['pre_selected', 'discarded']


class PreSelected(PostulantState):
    name = 'pre_selected'
    allowed = ['contacted', 'discarded']


class Contacted(PostulantState):
    name = 'contacted'
    allowed = ['discarded']


class Discarded(PostulantState):
    name = 'discarded'
    allowed = []


class PostulantStateManager(object):
    STATE_DICT = {
        'pending': Pending,
        'pre_selected': PreSelected,
        'contacted': Contacted,
        'discarded': Discarded
    }

    def __init__(self, postulant, enterprise):
        self.postulant = postulant
        self.enterprise = enterprise
        self.state = self.STATE_DICT[postulant.state.name]()

    def change(self, state):
        self.state.switch(self.STATE_DICT[state])
        self.postulant.update(state=StatePostulant.objects.get(name=self.state.name))
