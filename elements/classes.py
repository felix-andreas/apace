import weakref

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
        self.l = l
        self.comment = comment
        self.nkicks = 20
        self.stepsize = l / self.nkicks

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
        name : str
            Name of the line.
        tree : list
            (Nested) list of elements/lines.
        comment : str, optional
            A brief comment on the line.

        Attributes
        ----------
        tree : list
            (Nested) list of the lines/elements.
        lattice : list
            List that defines the physical order of elements in the magnetic lattice.
            Corresponds to flattened tree attribute.
        elements : set
            Set of all elements.
        lines : set
            Set of all lines.
        child_lines : set
            Set of all children lines.
        parent_lines : set
            Set of all parent lines.
    """

    def __init__(self, name, tree, comment=None):
        self.name = name
        self.tree = list()
        self.comment = comment
        self.child_lines = set()
        self.parent_lines = set()
        self.add_elements(tree, pos=-1)

    def add_elements(self, elements, pos=-1):
        self.tree[pos:pos] = elements
        for x in elements:
            if isinstance(x, Line):
                self.child_lines.add(x)
                x.parent_lines.add(weakref.ref(self))

    def remove_elements(self, pos, num=1):
        elements = self.tree[pos:pos + num]
        self.tree[pos:pos + num] = []
        for element in elements:
            if isinstance(element, Line) and element not in self.tree:
                self.child_lines.remove(element)
                x.parent_lines.remove(weakref.ref(self))

    # def update_all_parents(self):
    #     '''Updates the lattice and elements attribute of all parent lines.'''
    #     for x in self.parent_lines:  # update parents
    #         self.__class__._update_all_parents(x)
    #
    # @staticmethod
    # def _update_all_parents(line):
    #     line.update_lattice()
    #     line.update_elements()
    #     for x in line.parent_lines:  # update parents
    #         x.__class__._update_all_parents()

    def __del__(self):
        # print('delete {}'.format(self.name))
        for x in self.child_lines:
            x.parent_lines.discard(self)
        del self

    def __repr__(self):
        return self.name


flatten2 = lambda n: (e for a in n
                      for e in (flatten2(a.tree) if isinstance(a, Line) else (a,)))


class Mainline(Line):
    def __init__(self, name, tree, comment=None):
        super().__init__(name, tree, comment=comment)
        self.update()

    def update(self):
        '''Creates matrix_array list from tree that defines the physical order of elements in the magnetic lattice.
        Corresponds to flattened tree attribute.'''
        self.lattice = list(self.__class__._update_lattice(self.tree))
        self.elements = set(self.lattice)

    @staticmethod
    def _update_lattice(tree):
        '''A recursive helper function for update_lattice.'''
        for x in tree:
            if isinstance(x, Line):
                yield from Mainline._update_lattice(x.tree)
            else:
                yield x

    def update_lines(self):
        """Creates matrix_array set of all lines within the line."""
        self.lines = set()
        _update_lines(self)

    def _update_lines(self, line):
        '''A recursive helper function for update_lines.'''
        self.lines.add(line)
        for x in line.children_lines:
            if not bool(x.children_lines):  # not empty set
                self._update_lines(x)

    def __iter__(self):
        return _update_lattice(self.tree)
