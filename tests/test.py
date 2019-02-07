d = {"foo": 1, "bar": 2, "baz": 3}
from collections import OrderedDict
import inspect


class Test:
    def __init__(foo, hallo, bar, baz):
        foo.baz = baz
        foo.bar = bar
        foo.hallo = hallo

    def as_Dict(self):
        return OrderedDict(((key, getattr(self, key)) for key, value in inspect.signature(self.__class__).parameters.items()))

    def __del__(self):
        print('I was deleted!')


test = Test(1, 2, 3)
x = test.as_Dict()
print(x)
print(x.items())
print(type(x.items()))
import json

x = json.dumps(x)
print(x)
