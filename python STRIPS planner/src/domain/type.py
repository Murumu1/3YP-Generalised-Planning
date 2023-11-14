class Type:
    def __init__(self, name, parent):

        self._name = name
        self._type = parent

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

