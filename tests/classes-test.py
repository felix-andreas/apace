from elements.classes import Bend, Quad, Cell, change_element_type

b1 = Bend('B1', 1, 1, 1)
print(id(b1))
print(b1)

line = Cell("LINE1", [b1, b1, b1], comment="Mainline of the Ring")
change_element_type(b1, Quad, 'Q2', l=0.4, k1=-1.2)
print('\n')
print(line)

def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


# print(todict(line))
