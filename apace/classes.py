import weakref  # only tree should contain strong ref

from .utils import Signal


class _Base:
    def __init__(self, name, description):
        """
        A base class for elements and cells.
        Args:
            name: name of object
            description: description of the object
        """
        self.name = name
        self.description = description
        self.parent_cells = set()  # weakref.WeakSet()

    def __repr__(self):
        return self.name

    def __str__(self):
        attributes = []
        for key, value in self.__dict__.items():
            if key[0] != '_':
                if isinstance(value, weakref.WeakSet):
                    string = f'{", ".join(e.name for e in value):}'
                else:
                    string = str(value)
                attributes.append(f'{key:12}: {string:}')

        properties = []
        for x in dir(self.__class__):
            x_attr = getattr(self.__class__, x)
            if isinstance(x_attr, property):
                x_attr = x_attr.fget(self)
                if isinstance(x_attr, weakref.WeakSet):
                    string = ', '.join(e.name for e in x_attr)
                else:
                    string = str(x_attr)
                properties.append(f'{x:12}: {string}')
        return '\n'.join(attributes + properties)


class _Element(_Base):
    """
    Basic element class from which every other element-class inherits.
        Parameters / Attributes
        ----------
        name : str
            Name of the element.
        length : float
            Length of the element.
        comment : str, optional
            A brief comment on the element.
    """

    def __init__(self, name, length, description):
        super().__init__(name, description)
        self._length = length
        self.length_changed = Signal()
        self.length_changed.register(self._on_length_changed)
        self.value_changed = Signal()
        self.value_changed.register(self._on_value_changed)

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value
        self.length_changed()

    def _on_length_changed(self):
        for cell in self.parent_cells:
            cell.length_changed(self)

    def _on_value_changed(self):
        for cell in self.parent_cells:
            cell.element_changed(self)


class Drift(_Element):
    """
    The Drift element.
    Args:
        name: name of the element
        length: length of the element
        description: comment on the element.
    """

    def __init__(self, name, length, description=''):
        super().__init__(name, length, description)


class Bend(_Element):
    def __init__(self, name, length, angle, e1=0, e2=0, description=''):
        super().__init__(name, length, description)
        self._angle = angle
        self._e1 = e1
        self._e2 = e2

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.value_changed()

    @property
    def e1(self):
        return self._e1

    @e1.setter
    def e1(self, value):
        self._e1 = value
        self.value_changed()

    @property
    def e2(self):
        return self._e2

    @e2.setter
    def e2(self, value):
        self._e2 = value
        self.value_changed()

    @property
    def radius(self):
        return self.length / self.angle

    @radius.setter
    def radius(self, value):
        self.angle = value


class Quad(_Element):
    def __init__(self, name, length, k1, description=''):
        super().__init__(name, length, description)
        self._k1 = k1

    @property
    def k1(self):
        return self._k1

    @k1.setter
    def k1(self, value):
        self._k1 = value
        self.value_changed()


class Sext(_Element):
    def __init__(self, name, length, k2, description=''):
        super().__init__(name, length, description)
        self._k2 = k2

    @property
    def k2(self):
        return self._k2

    @k2.setter
    def k2(self, value):
        self._k2 = value
        self.value_changed()


class Cell(_Base):
    """
    Class that defines the order of elements in accelerator. Accepts also cells as input.
        Parameters
        ----------
        name : str
            Name of the cell.
        tree : list
            (Nested) list of elements/cells.
        description : str, optional
            A brief comment on the cell.

        Attributes
        ----------
        tree : list, tuple
            (Nested) list of the cells/elements.
        child_cells : set
            Set of all children cells.
        parent_cells : set
            Set of all parent cells.

        Properties
        ----------
        lattice : list
            List that defines the physical order of elements in the magnetic lattice.
            Corresponds to flattened tree attribute.
        elements : set
            Set of all apace.
        cells : set
            Set of all cells.
    """

    def __init__(self, name, tree=None, description=''):
        super().__init__(name, description)
        self._tree = list()  # has strong links to objects
        self.tree_changed = Signal()
        self.child_cells = set()
        self.main_cell = None

        # tree properties: # TODO: tree properties should be weak reference
        self._lattice = list()
        self._elements = dict()
        self._cells = dict()
        self._tree_properties_needs_update = True
        self.tree_properties_changed = Signal()
        self.tree_changed.register(self._on_tree_changed)

        self._length = 0
        self._length_needs_update = True
        self.length_changed = Signal()
        self.length_changed.register(self._on_length_changed)

        self.element_changed = Signal()
        self.element_changed.register(self._on_element_changed)

        if tree:
            self.tree_add_objects(tree, pos=len(self.tree))

    def __getitem__(self, key):
        if isinstance(key, str):
            try:
                return self.elements[key]
            except KeyError:
                return self.cells[key]

        else:
            return self.lattice[key]

    def __del__(self):
        for cell in self.child_cells:
            cell.parent_cells.discard(self)

    @property
    def tree(self):  # do not allow to set tree manually
        return self._tree

    def tree_add_objects(self, new_objects_list, pos=None):
        if pos:
            self._tree[pos:pos] = new_objects_list
        else:
            self._tree.extend(new_objects_list)

        for obj in set(new_objects_list):
            obj.parent_cells.add(self)
            if isinstance(obj, Cell):
                self.child_cells.add(obj)

        self.tree_changed()

    def tree_remove_objects(self, pos, num=1):
        removed_objects = self.tree[pos:pos + num]
        self._tree[pos:pos + num] = []
        for obj in set(removed_objects):
            if obj not in self._tree:
                if isinstance(obj, Cell):
                    self.child_cells.remove(obj)
                print(obj.name, obj.parent_cells, self.tree)
                obj.parent_cells.remove(self)

        self.tree_changed()

    @property
    def lattice(self):
        if self._tree_properties_needs_update:
            self.update_tree_properties()
        return self._lattice

    @property
    def elements(self):
        if self._tree_properties_needs_update:
            self.update_tree_properties()
        return self._elements

    @property
    def cells(self):
        if self._tree_properties_needs_update:
            self.update_tree_properties()
        return self._cells

    def _on_tree_changed(self):
        self._tree_properties_needs_update = True
        for cell in self.parent_cells:
            cell.tree_properties_changed()

    def update_tree_properties(self):
        self._lattice.clear()
        self._elements.clear()
        self._cells.clear()
        self._update_tree_properties(self.tree)
        self._tree_properties_needs_update = False

    def _update_tree_properties(self, tree):
        """A recursive helper function for update_tree_properties."""
        elements = self._elements
        cells = self._cells
        for x in tree:
            # TODO: x = weakref.proxy(x) # all references should be weak!
            if isinstance(x, Cell):
                value = cells.get(x.name)
                if value is None:
                    cells[x.name] = x
                elif x is not value:
                    raise Exception('Cells must have unique names!')

                self._update_tree_properties(x.tree)
            else:
                self._lattice.append(x)
                value = elements.get(x.name)
                if value is None:
                    elements[x.name] = x
                elif x is not value:
                    raise Exception('Elements must have unique names!')

    @property
    def length(self):
        if self._length_needs_update:
            self.update_length()
        return self._length

    def update_length(self):
        self._length = sum(obj.length for obj in self.tree)
        self._length_needs_update = False

    def _on_length_changed(self, element):
        self._length_needs_update = True
        for cell in self.parent_cells:
            cell.length_changed(element)

    def _on_element_changed(self, element):
        for cell in self.parent_cells:
            cell.element_changed(element)

    def print_tree(self):
        self.depth = 0
        self.filler = ''
        self.start = '│   '
        print(f'{self.name}')
        self._print_tree(self)
        del self.depth
        del self.filler
        del self.start

    def _print_tree(self, cell):
        length = len(cell.tree)
        for i, x in enumerate(cell.tree):
            is_last = i == length - 1
            fill = '└───' if is_last else '├───'
            print(f'{self.filler}{fill} {x.name}')
            if is_last and self.depth == 0:
                self.start = '    '
            if isinstance(x, Cell):
                self.depth += 1
                self.filler = self.start * (self.depth > 0) + (self.depth - 1) * ('    ' if is_last else '│   ')
                self._print_tree(x)
                self.depth -= 1
                self.filler = self.start * (self.depth > 0) + (self.depth - 1) * ('    ' if is_last else '│   ')
