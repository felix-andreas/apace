import collections
import cProfile, pstats, io

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

class Structure:
    pass

def profile(fun, num=1):

    """A decorator that uses CProfile to profile matrix_array function."""

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        for _ in range(num):
            retval = fun(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner