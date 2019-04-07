

class Attribute(object):
    element = None
    name = None
    value = None

    def __init__(self, element, name, value):
        self.element = element
        self.name = name
        self.value = value

    def set(self):
        self.element.set(
            self.name,
            self.value
        )


class DataAttribute(Attribute):

    def __init__(self, element, name, data, key, parent=None):
        if isinstance(data, dict):
            if parent:
                p_data = data.get(parent)
                value = p_data.get(key)
            else:
                value = data.get(key)

            super(DataAttribute, self).__init__(element, name, value)
        else:
            raise TypeError('Data should be dict type')
