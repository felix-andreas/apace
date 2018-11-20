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
        self._positions = []
        self.mainline = None

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value
        self.stepsize = self._length / self._nkicks
        for x in self.parent_lines:
            x.length_trigger.changed = True

    @property
    def nkicks(self):
        return self._nkicks

    @nkicks.setter
    def nkicks(self, value):
        self._nkicks = value
        self.stepsize = self._length / self._nkicks
        for x in self.parent_lines:
            x.nkicks_trigger.changed = True

    @property
    def positions(self):
        if self.mainline and self.mainline.elements_positon_trigger.changed:
            self.mainline.update_element_positions()
        return self._positions



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
        self.tree_trigger = PropertyTrigger()
        self.mainline = None
        # tree properties
        self.tree_properties_trigger = PropertyTriggerLine(self, "tree_properties_trigger", depends_on=self.tree_trigger)
        self._lattice = None
        self._elements = None
        self._all_lines = None
        # length
        self._length = None
        self.length_trigger = PropertyTriggerLine(self, "length_trigger", depends_on=self.tree_trigger)
        # nkicks
        self._nkicks = None
        self.nkicks_trigger = PropertyTriggerLine(self, "nkicks_trigger", depends_on=self.tree_trigger)
        # add objects
        self.add_objects(tree, pos=-1)

    # change tree
    def add_objects(self, elements, pos):
        self.tree[pos:pos] = elements
        for x in elements:
            x.parent_lines.add(self)
            if isinstance(x, Line):
                self.child_lines.add(x)
        self.tree_trigger.trigger_dependents()

    def remove_objects(self, pos, num=1):
        elements = self.tree[pos:pos + num]
        self.tree[pos:pos + num] = []
        for x in elements:
            if isinstance(x, Line):
                self.child_lines.remove(x)
            if x not in self.tree:
                x.parent_lines.remove(self)
        self.tree_trigger.trigger_dependents()


    # class properties
    @property
    def lattice(self):
        if self.tree_properties_trigger.changed:
            self.update_lattice_properties()
        return self._lattice

    @property
    def elements(self):
        if self.tree_properties_trigger.changed:
            self.update_lattice_properties()
        return self._elements

    @property
    def all_lines(self):
        if self.tree_properties_trigger.changed:
            self.update_lattice_properties()
        return self._all_lines

    def update_lattice_properties(self):
        self._lattice = list()  ## should be weakref
        self._elements = weakref.WeakSet()
        self._all_lines = weakref.WeakSet()
        self._update_lattice_properties(self.tree)
        self.tree_properties_trigger.changed = False

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
        if self.length_trigger.changed:
            self.update_length()
            self.length_trigger.changed = False
        return self._length

    def update_length(self):  # is overwritten in Mainline class
        self._length = sum([x.length for x in self.tree])
        self.length_trigger.changed = False
        print(self.name, "length update")

    @property
    def nkicks(self):
        if self.nkicks_trigger.changed:
            self.update_nkicks()
            self.nkicks_trigger.changed = False
        return self._nkicks

    def update_nkicks(self):  # is overwritten in Mainline class
        self._nkicks = sum([x.nkicks for x in self.tree])


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
        # elements positon
        self.elements_positon_trigger = PropertyTrigger(depends_on=[self.tree_trigger, self.nkicks_trigger])
        # set mainline link to all elements and lines
        for x in self.elements | self.all_lines:
            x.mainline = self
        # stepsize
        self._stepsize = None
        self.stepsize_trigger = PropertyTrigger(depends_on=[self.nkicks_trigger, self.length_trigger, self.tree_trigger])
        # orbit coordinate s
        self._s = None
        self.s_trigger = PropertyTrigger(depends_on=self.stepsize_trigger)


    @property
    def stepsize(self):
        if self.stepsize_trigger.changed:
            self._stepsize = np.empty(self.nkicks + 1)
            self._stepsize[0] = 0
            for element in self.elements:
                self._stepsize[element.positions] = element.stepsize
            self.stepsize_trigger.changed = False
        return self._stepsize

    @property
    def s(self):
        if self.s_trigger.changed:
            self._s = np.add.accumulate(self.stepsize)  # s corresponds to the orbit position
        return self._s

    @Line.length.setter
    def length(self, new_length):
        ratio = new_length / self._length
        self._length = new_length
        for x in self.elements:
            x.length = x.length * ratio

    def update_nkicks(self):
        super().update_nkicks()
        self.elements_positon_trigger.changed = True

    def update_lattice_properties(self):
        super().update_lattice_properties()
        self.elements_positon_trigger.changed = True


    def update_element_positions(self):
        self.elements_positon_trigger.changed = False
        for element in self.elements:  # clear element positons
            element._positions.clear()
        start = 1  # starts with 1 because 0th entry is identity matrix
        for element in self.lattice:
            end = start + element.nkicks
            element._positions.extend(list(range(start, end)))
            start = end


def change_element_type(element, new_type, *args, **kwargs):
    for key in list(element.__dict__):
        delattr(element, key)
    element.__class__ = new_type
    element.__init__(*args, **kwargs)


class PropertyTrigger: # muss verbessert werden , name sollte nicht ubergeben werden
    def __init__(self, depends_on=None, initial_state=True):
        """
        A container class for an attribute, which is only computed if one of the
        objects it depends on changes.
        Args:
            depends_on: list of objects the object depends on
        """
        self._changed = initial_state
        self.dependents = set()
        # convert depends_on to list
        tmp = depends_on or [] #check if None
        self.depends_on = tmp if isinstance(tmp, list) else [tmp]
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
    def __init__(self, line, triggername, depends_on=None):
        super().__init__(depends_on)
        self.line = line
        self.triggername = triggername

    def trigger_dependents(self):
        super().trigger_dependents()
        for x in self.line.parent_lines:
            getattr(x, self.triggername).changed = True


class Method:

    def __init__(self, mainline):
        self.mainline = mainline
        self.mainline.methods.add(self)
