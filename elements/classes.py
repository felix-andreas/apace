import numpy as np


class _Element:
    def __init__(self, name, type, length):
        self.name = name
        self.type = type
        self.length = length

    def __repr__(self):
        return self.name


class Drift(_Element):
    def __init__(self, name, length):
        super().__init__(name, 'Drift', length)

    def computematrix(self, distance):
        self.matrix = np.matrix(((1, distance, 0, 0, 0), (0, 1, 0, 0, 0), (0, 0, 1, distance, 0), (0, 0, 0, 1, 0), (0, 0, 0, 0, 1)))


class Bend(_Element):
    def __init__(self, name, length, angle, e1=0, e2=0):
        super().__init__(name, 'Bend', length)
        self.angle = angle
        self.e1 = e1
        self.e2 = e2

    def computematrix(self):
        if self.R == 0:
            self.matrix = [np.matrix(((1, self.ss, 0, 0, 0), (0, 1, 0, 0, 0), (0, 0, 1, self.ss, 0), (0, 0, 0, 1, 0), (0, 0, 0, 0, 1)))] * self.n_kicks
        else:
            sin = np.sin(self.ss / self.R)
            cos = np.cos(self.ss / self.R)
            self.matrix = [np.matrix((
                (cos, self.R * sin, 0, 0, self.R * (1 - cos)), (-1 / self.R * sin, cos, 0, 0, sin),
                (0, 0, 1, self.ss, 0), (0, 0, 0, 1, 0), (0, 0, 0, 0, 1)))] * BEND.n_kicks
            if self.e1:
                tanR1 = np.tan(self.e1) / self.R
                MEB1 = np.matrix(np.identity(5), copy=False)
                MEB1[1, 0], MEB1[3, 2] = tanR1, -tanR1
                self.matrix[0] = self.matrix[0] * MEB1
            if self.e2:
                tanR2 = np.tan(self.e2) / self.R
                MEB2 = np.matrix(np.identity(5), copy=False)
                MEB2[1, 0], MEB2[3, 2] = tanR2, -tanR2
                self.matrix[-1] = MEB2 * self.matrix[-1]


class Quad(_Element):
    def __init__(self, name, length):
        super().__init__(name, 'Quad', length)


class Sext(Drift):
    pass


def _update_lattice(elements):
    for x in elements:
        if isinstance(x, Line):
            yield from _update_lattice(x.lattice)
        else:
            yield x


class Line(_Element):
    def __init__(self, name, elements):
        super().__init__(name, 'Line', length=0)
        self.elements = list()
        self.lines = set()
        self.parent_lines = set()
        self.add_elements(elements, pos=-1)

    def update_lattice(self):
        self.lattice = list(_update_lattice(self.elements))

    def update_lattice_set(self):
        self.lattice_set = set(self.lattice)

    def update_all(self):
        self.update_lattice()
        self.update_lattice_set()
        for x in self.parent_lines:  # update parents
            x.update_all()

    def add_elements(self, elements, pos=-1):
        self.elements[pos:pos] = elements
        for x in elements:
            if isinstance(x, Line):
                self.lines.add(x)
                x.parent_lines.add(self)

        self.update_all()

    def remove_element(self, pos):
        element = self.elements[pos]
        self.elements.pop(pos)
        if isinstance(element, Line) and element not in self.elements:
            self.lines.remove(element)
            x.parent_lines.remove(self)

        self.update_all()

    def __iter__(self):
        return _update_lattice(self.elements)

    def __del__(self):
        for x in self.lines:
            x.parent_lines.remove(self)
        del self

    def __repr__(self):
        return self.name
