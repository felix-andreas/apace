import collections

def flatten(iterable):
    for element in iterable:
        if isinstance(element, collections.Iterable) and not isinstance(element, (str, bytes)):
            yield from flatten(element)
        else:
            yield element

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self