class _Element:
    '''
    Basic class from which every other Element inherts.
        Parameters / Attributes
        ----------
        name : str
            Name of the element.
        type : str
            Type of the element.
        l : float
            Length of the element.
        comment : str, optional
            A brief comment on the element.
    '''

    def __init__(self, name, type, l, comment=None):
        self.name = name
        self.type = type
        self.length = l
        self.comment = comment

    def __repr__(self):
        return self.name


class Drift(_Element):
    def __init__(self, name, l):
        super().__init__(name, 'Drift', l)


class Bend(_Element):
    def __init__(self, name, l, angle, e1=0, e2=0):
        super().__init__(name, 'Bend', l)
        self.angle = angle
        self.e1 = e1
        self.e2 = e2
        self.r = l / angle


class Quad(_Element):
    def __init__(self, name, l, k1):
        super().__init__(name, 'Quad', l)
        self.k = k1


class Sext(_Element):
    def __init__(self, name, l, k2):
        super().__init__(name, 'Sext', l)
        self.k2 = k2


class Line:
    """
    Class that defines the order of elements in accelerator. Accepts also Lines as input.
        Parameters
        ----------
        elements : list
            List of elements/lines.
        name : str
            Name of the line.

        Attributes
        ----------
        tree : list
            Nested list of the lines/elements.
        lattice : list
            List that defines the physical order of elements in the magnetic lattice.
            Corresponds to flattened tree attribute.
        elements : set
            Set of all elements.
        lines : set
            Set of all lines.
        children_lines : set
            Set of all children lines.
        parent_lines : set
            Set of all parent lines.
    """

    def __init__(self, name, elements):
        self.name = name
        self.tree = list()
        self.children_lines = set()
        self.parent_lines = set()  # !vll als weakref implementieren
        self.add_elements(elements, pos=-1)

    def update_lattice(self):
        '''Creates a list from tree that defines the physical order of elements in the magnetic lattice.
        Corresponds to flattened tree attribute.'''
        self.lattice = list(self.__class__._update_lattice(self.tree))

    @staticmethod
    def _update_lattice(tree):
        '''A recursive helper function for update_lattice.'''
        for x in tree:
            if isinstance(x, Line):
                yield from Line._update_lattice(x.tree)
            else:
                yield x

    def update_elements(self):
        'Creates a set of all elements within the line.'
        self.elements = set(self.lattice)

    def add_elements(self, elements, pos=-1):
        self.tree[pos:pos] = elements
        for x in elements:
            if isinstance(x, Line):
                self.children_lines.add(x)
                self.lines.add(x.lines)
                x.parent_lines.add(self)

        self.update_all()

    def remove_elements(self, pos, num=1):
        elements = self.tree[pos:pos + num]
        self.tree[pos:pos + num] = []
        for element in elements:
            if isinstance(element, Line) and element not in self.tree:
                self.children_lines.remove(element)
                x.parent_lines.remove(self)

        self.update_all()

    def update_lines(self):
        """Creates a set of all lines within the line."""
        self.lines = set()
        _update_lines(self)

    def _update_lines(self, line):
        '''A recursive helper function for update_lines.'''
        self.lines.add(line)
        for x in line.children_lines:
            if bool(x.lines):  # empty set
                pass
            else:
                self._update_lines(x)

    def update_all(self):
        self.update()
        self.update_all_parents()

    def update(self):
        self.update_lattice()
        self.update_elements()

    def update_all_parents(self):
        '''Updates the lattice and elements attribute of all parent lines.'''
        for x in self.parent_lines:  # update parents
            self.__class__._update_all_parents(x)

    @staticmethod
    def _update_all_parents(line):
        line.update_lattice()
        line.update_elements()
        for x in line.parent_lines:  # update parents
            x.__class__._update_all_parents()

    def __iter__(self):
        return _update_lattice(self.tree)

    def __del__(self):
        for x in self.lines:
            x.parent_lines.remove(self)
        del self

    def __repr__(self):
        return self.name
