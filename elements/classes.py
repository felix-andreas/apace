import weakref  # only tree should contain strong ref
import numpy as np


class _Base:

    def __init__(self, name, type, comment):
        """
        A base class for elements and lines.
        Args:
            name: name of object
            type: type of object
            comment: description of the object
        """
        self.name = name
        self.comment = comment
        self.type = type

    def __repr__(self):
        return self.name

    def __str__(self):
        attributes = [f"{key:}: {value:}" for key, value in self.__dict__.items() if key[0] != '_']
        properties = [f"{x}: {getattr(self.__class__,x).fget(self)}" for x in dir(self.__class__) if
                      isinstance(getattr(self.__class__, x), property)]
        return "\n".join(attributes + properties)


class _Element(_Base):
    '''
    Basic element class from which every other element-class inherits.
        Parameters / Attributes
        ----------
        name : str
            Name of the element.
        type : str
            Type of the element.
        length : float
            Length of the element.
        comment : str, optional
            A brief comment on the element.
    '''

    def __init__(self, name, type, length, comment):
        super().__init__(name, type, comment)
        self._length = length
        self._nkicks = 100
        self.parent_lines = set()
        self.stepsize = self._length / self._nkicks
        self._positons = []
        self.mainline = None

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value
        self.stepsize = self._length / self._nkicks
        for x in self.parent_lines:
            x.length_changed = True

    @property
    def nkicks(self):
        return self._nkicks

    @nkicks.setter
    def nkicks(self, value):
        self._nkicks = value
        self.stepsize = self._length / self._nkicks
        for x in self.parent_lines:
            x.nicks_changed = True

    @property
    def positions(self):
        if self.mainline and self.mainline.lattice_changed:
            self.mainline.update_element_positions()
        return self._positons


class Drift(_Element):
    def __init__(self, name, length, comment=''):
        """
        The Drift element.
        Args:
            name: name of the element
            length: length of the element
            comment: comment on the element.
        """
        super().__init__(name, 'Drift', length, comment)


class Bend(_Element):
    def __init__(self, name, length, angle, e1=0, e2=0, comment=''):
        super().__init__(name, 'Bend', length, comment)
        self.angle = angle
        self.e1 = e1
        self.e2 = e2

    @property
    def radius(self):
        return self.length / self.angle


class Quad(_Element):
    def __init__(self, name, length, k1, comment=''):
        super().__init__(name, 'Quad', length, comment)
        self.k = k1


class Sext(_Element):
    def __init__(self, name, length, k2, comment=''):
        super().__init__(name, 'Sext', length, comment)
        self.k2 = k2


class Line(_Base):
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
        all_lines : set
            Set of all lines.
        child_lines : set
            Set of all children lines.
        parent_lines : set
            Set of all parent lines.
    """

    def __init__(self, name, tree, comment=''):
        super().__init__(name, "Line", comment)
        # attributes
        self.tree = list()  # has strong links to objects
        self.child_lines = weakref.WeakSet()
        self.parent_lines = weakref.WeakSet()
        self.mainline = None
        # properties
        self._lattice = None
        self._elements = None
        self._all_lines = None
        self._length = None
        self._nkicks = None
        self.tree_trigger = self.trigger_property()
        self.lattice_changed = PropertyTriggerLine(self, "lattice_changed")
        self.length_changed = PropertyTriggerLine(self, "length_changed")
        self.nkicks_changed = PropertyTriggerLine(self, "nkicks_changed")
        # call methods
        self.add_objects(tree, pos=-1)

    # change tree
    def add_objects(self, elements, pos):
        self.tree[pos:pos] = elements
        for x in elements:
            x.parent_lines.add(self)
            if isinstance(x, Line):
                self.child_lines.add(x)
        self.trigger_change_tree()


    def remove_objects(self, pos, num=1):
        elements = self.tree[pos:pos + num]
        self.tree[pos:pos + num] = []
        for x in elements:
            if isinstance(x, Line):
                self.child_lines.remove(x)
            if x not in self.tree:
                x.parent_lines.remove(self)
        self.trigger_change_tree()


    def trigger_change_tree(self):
        self.lattice_changed = True
        self.nkicks_changed = True
        self.length_changed = True

    # class properties
    @property
    def lattice(self):
        if self.lattice_changed:
            self.update_lattice_properties()
        return self._lattice

    @property
    def elements(self):
        if self.lattice_changed:
            self.update_lattice_properties()
        return self._elements

    @property
    def all_lines(self):
        if self.lattice_changed:
            self.update_lattice_properties()
        return self._all_lines

    def update_lattice_properties(self):
        self._lattice = list()  ## should be weakref
        self._elements = weakref.WeakSet()
        self._all_lines = weakref.WeakSet()
        self._update_lattice_properties(self.tree)
        self.lattice_changed = False

    def _update_lattice_properties(self, tree):
        '''A recursive helper function for update_lattice_properties.'''
        for x in tree:
            if isinstance(x, Line):
                self._all_lines.add(x)
                self._update_lattice_properties(x.tree)
            else:
                self._lattice.append(x)
                self._elements.add(x)

    @property
    def length(self):
        if self.length_changed:
            self.update_length()
        return self._length

    def update_length(self):  # is overwritten in Mainline class
        self._length = sum([x.length for x in self.tree])
        self.length_changed = False

    @property
    def nkicks(self):
        if self.nkicks_changed:
            self.update_nkicks()
        return self._nkicks

    def update_nkicks(self):  # is overwritten in Mainline class
        self._nkicks = sum([x.nkicks for x in self.tree])
        self.nkicks_changed = False

    def trigger_property(self, name):
        private_name = "_" + name

        @property
        def prop(self):
            return getattr(self, private_name)

        @prop.setter
        def prop(self, value):
            setattr(self, private_name, value)
            if value:  # change parentlines only if true
                for x in self.parent_lines:
                    setattr(x, name, value)

        return prop


    def print_tree(self):
        self.depth = 0
        self.filler = ""
        self.start = "│   "
        print(f"{self.name}")
        self._print_tree(self)
        del self.depth
        del self.filler
        del self.start

    def _print_tree(self, line):
        length = len(line.tree)
        for i, x in enumerate(line.tree):
            is_last = i == length - 1
            fill = "└───" if is_last else "├───"
            print(f"{self.filler}{fill} {x.name}")
            if is_last and self.depth == 0:
                self.start = "    "
            if isinstance(x, Line):
                self.depth += 1
                self.filler = self.start * (self.depth > 0) + (self.depth - 1) * ("    " if is_last else "│   ")
                self._print_tree(x)
                self.depth -= 1
                self.filler = self.start * (self.depth > 0) + (self.depth - 1) * ("    " if is_last else "│   ")

    def __del__(self):
        # print('delete {}'.format(self.name))
        for x in self.child_lines:
            x.parent_lines.discard(self)


class Mainline(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # attriutes
        methods = set()

        # properties
        self._stepsize = PropertyTrigger()
        self._s = PropertyTrigger(depends_on=[self._stepsize])
        self.elements_positon_changed = PropertyTrigger()
        # set mainline link to all elements and lines
        for x in self.elements | self.all_lines:
            x.mainline = self

    @property
    def stepsize(self):
        if self._stepsize.changed:
            self._stepsize.data = np.empty(self.nkicks + 1)
            self._stepsize.data[0] = 0
            for element in self.elements:
                self._stepsize.data[element.positions] = element.stepsize
            self._stepsize.changed = False
        return self._stepsize.data

    @property
    def s(self):
        if self._s.changed:
            self._s.data = np.add.accumulate(self._stepsize.data)  # s corresponds to the orbit position
        return self._s

    @Line.length.setter
    def length(self, new_length):
        ratio = new_length / self._length
        self._length = new_length
        for x in self.elements:
            x.length = x.length * ratio

    def update_nkicks(self):
        super().update_nkicks()
        self.elements_positon_changed = True
        self.stepsize_changed = True

    def update_lattice_properties(self):
        super().update_lattice_properties()
        self.elements_positon_changed = True

    def update_element_positions(self):
        for element in self.elements:  # clear element positons
            element._positions = []
        start = 1  # starts with 1 because 0th entry is identity matrix
        for element in self.lattice:
            end = start + element.nkicks
            element._positions.extend(list(range(start, end)))
            start = end
        self.elements_positon_changed = False
        self.stepsize_changed = True

    def update_stepsize(self):
        self._stepsize = np.empty(self.nkicks + 1)
        self._stepsize[0] = 0
        for element in self.elements:
            self._stepsize[element.positions] = element.stepsize
        self._s = np.add.accumulate(self._stepsize)  # s corresponds to the orbit position
        self.stepsize_changed = False
        self.method_nkicks_changed = True

def change_element_type(element, new_type, *args, **kwargs):
    for key in list(element.__dict__):
        delattr(element, key)
    element.__class__ = new_type
    element.__init__(*args, **kwargs)



class PropertyTrigger:
    def __init__(self, depends_on=None):
        """
        A container class for an attribute, which is only computed if one of the
        objects it depends on changes.
        Args:
            depends_on: list of objects the object depends on
        """
        self._changed = True
        self.dependents = set()
        self.depends_on = depends_on or []
        for x in self.depends_on:
            x.dependents.add(self)

    @property
    def changed(self):
        return self._changed

    @changed.setter
    def changed(self, value):
        self._changed = value
        if value:
            self.trigger_dependents()

    def trigger_dependents(self):
        for x in self.dependents:
            x.changed = True


class PropertyTriggerLine(PropertyTrigger):
    def __init__(self, line, triggername, dependes_on=None):
        super().__init__(dependes_on)
        self.line = line
        self.triggername = triggername

    def trigger_dependents(self):
        super().trigger_dependents()
        for x in self.line.parent_lines:
            setattr(x, self.triggername, value)

class Method:

    def __init__(self, mainline):
        self.mainline = mainline
        self.mainline.methods.add(self)
