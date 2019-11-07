from typing import List, Set, Dict, Union, Type, Iterable

import weakref  # only tree should contain strong ref
from .utils import Signal, AmbiguousNameError


class Object:
    """Abstract base for all element and cell classes.

    :param str name: The name of the object.
    :param description: A brief description of the object.
    :type description: str, optional
    """

    def __init__(self, name, length, description=''):
        self.name: str = name
        """The name of the object."""
        self.description: str = description
        """A brief description of the object"""
        self.parent_cells: Set['Cell'] = set()
        """All cells which contain the object."""
        self._length = length

    @property
    def length(self) -> float:
        """Length of the object (m)."""
        return self._length

    def __repr__(self):
        return self.name

    def __str__(self):  # TODO: update function
        attributes = []
        signals = []
        for name, attr in self.__dict__.items():
            if name[0] == '_':
                continue

            if isinstance(attr, Signal):
                signals.append((name, str(attr)))
            else:
                if isinstance(attr, weakref.WeakSet):
                    string = f'{", ".join(e.name for e in attr):}'
                else:
                    string = str(attr)

                attributes.append((name, string))

        properties = []
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if isinstance(attr, property):
                attr = attr.fget(self)
                if isinstance(attr, weakref.WeakSet):
                    string = ', '.join(e.name for e in attr)
                else:
                    string = str(attr)
                properties.append((name, string))

        return '\n'.join(f'{name:14}: {string}' for name, string in attributes + properties + signals)


class Element(Object):
    """Abstract base for all element classes.

    :param str name: The name of the element.
    :param float length: The length of the element (m).
    :param str description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, description=''):
        super().__init__(name, length, description)
        self._length = length
        self.length_changed: Signal = Signal()
        """Gets emitted when the length changes."""
        self.length_changed.connect(self._on_length_changed)
        self.value_changed: Signal = Signal()
        """Gets emitted when one of the attributes changes."""
        self.value_changed.connect(self._on_value_changed)

    @property
    def length(self) -> float:
        """Length of the element (m)."""
        return self._length

    @length.setter
    def length(self, value):
        self._length = value
        self.length_changed()

    def _on_length_changed(self):
        for cell in self.parent_cells:
            cell.length_changed()
            cell.element_changed(self)

    def _on_value_changed(self):
        for cell in self.parent_cells:
            cell.element_changed(self)


class Drift(Element):
    """A drift space element.

    :param str name: The name of the element.
    :param float length: The length of the element (m).
    :param str description: A brief description of the element.
    :type description: str, optional
    """
    pass


class Bend(Element):
    """A dipole element.

    :param str name: Name of the element.
    :param float length: Length of the element (m).
    :param float angle: Deflection angle in rad.
    :param e1: Entrance angle in rad.
    :type e1: float, optional
    :param e2: Exit angle in rad.
    :type e2: float, optional
    :param description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, angle, e1=0, e2=0, description=''):
        super().__init__(name, length, description)
        self._angle = angle
        self._e1 = e1
        self._e2 = e2

    @property
    def angle(self) -> float:
        """Deflection angle (rad)."""
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.value_changed()

    @property
    def e1(self) -> float:
        """Entrance angle (rad)."""
        return self._e1

    @e1.setter
    def e1(self, value):
        self._e1 = value
        self.value_changed()

    @property
    def e2(self) -> float:
        """Exit angle (rad)."""
        return self._e2

    @e2.setter
    def e2(self, value):
        self._e2 = value
        self.value_changed()

    @property
    def radius(self) -> float:
        """Radius of curvature (m)."""
        return self.length / self.angle

    @radius.setter
    def radius(self, value):
        self.angle = value


class Quad(Element):
    """A quadrupole element.

    :param str name: Name of the element.
    :param float length: Length of the element (m).
    :param float k1: Geometric quadrupole strength (m^-2).
    :param description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, k1, description=''):
        super().__init__(name, length, description)
        self._k1 = k1

    @property
    def k1(self) -> float:
        """Geometric quadrupole strength (m^-2)."""
        return self._k1

    @k1.setter
    def k1(self, value):
        self._k1 = value
        self.value_changed()


class Sext(Element):
    """A sextupole element.

    :param str name: Name of the element.
    :param float length: Length of the element (m).
    :param float k1: Geometric quadrupole strength (m^-3).
    :param description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, k2, description=''):
        super().__init__(name, length, description)
        self._k2 = k2

    @property
    def k2(self) -> float:
        """Geometric sextupole strength (m^-1)."""
        return self._k2

    @k2.setter
    def k2(self, value):
        self._k2 = value
        self.value_changed()


class Octu(Element):
    """An octupole element.

    :param str name: Name of the element.
    :param float length: Length of the element (m).
    :param float k1: Geometric quadrupole strength (m^-4).
    :param description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, k2, description=''):
        super().__init__(name, length, description)
        self._k2 = k2

    @property
    def k2(self) -> float:
        """Geometric sextupole strength (m^-1)."""
        return self._k2

    @k2.setter
    def k2(self, value):
        self._k2 = value
        self.value_changed()


class Cell(Object):
    """Defines the order of elements in the accelerator.

    :param str name: Name of the cell.
    :param List[Union[Type[Element], Cell]] tree: Nested tree of elements and cells.
    :param str description: A brief description of the element.
    """

    def __init__(self, name, tree=None, description=None):
        super().__init__(name, description)
        self._tree = list()  # has strong links to objects
        self.tree_changed: Signal = Signal()
        """Gets emitted when the tree of element and cells changes."""
        if tree:
            self.add(tree, pos=len(self.tree))

        # tree properties: # TODO: tree properties should be weak reference
        self._lattice = []
        self._elements = {}
        self._cells = {}
        self._tree_properties_needs_update = True
        self.tree_properties_changed: Signal = Signal(self.tree_changed)
        """Gets emitted when one of the attributes lattice, element or cells changes."""
        self.tree_properties_changed.connect(self._on_tree_properties_changed)

        self._length = 0
        self._length_needs_update = True
        self.length_changed: Signal = Signal(self.tree_changed)
        """Gets emitted when the length of cell changes."""
        self.length_changed.connect(self._on_length_changed)

        self.element_changed: Signal = Signal()
        """Gets emitted when an attribute of an element within this cell changes."""
        self.element_changed.connect(self._on_element_changed)

    def __getitem__(self, key):
        if isinstance(key, str):
            try:
                return self.elements[key]
            except KeyError:
                return self.cells[key]

        else:
            return self.lattice[key]

    def __del__(self):
        for obj in self.tree:
            obj.parent_cells.discard(self)

    @property
    def length(self) -> float:
        """Length of the cell."""
        if self._length_needs_update:
            self.update_length()
        return self._length

    def update_length(self):
        """Manually update the Length of the cell (m)."""
        self._length = sum(obj.length for obj in self.tree)
        self._length_needs_update = False

    def _on_length_changed(self):
        self._length_needs_update = True
        for cell in self.parent_cells:
            cell.length_changed()

    def _on_element_changed(self, element):
        for cell in self.parent_cells:
            cell.element_changed(element)

    @property
    def tree(self) -> List[Type[Object]]:  # do not set tree manually
        """The tree of objeccts defines the physical order of elements withing this cell."""

        return self._tree

    def add(self, new_objects, pos=None):
        """Add objects to the object tree of the cell.

        :param new_objects: Objects which get added to the :attr:`tree`.
        :type new_objects: Object or Iterable[Object]
        :param pos: The position within the :attr:`tree` at which the new objects are inserted.
                    If pos is None, objects are appended to the end of the cell.
        :type pos: int, optional
        """
        if isinstance(new_objects, Object):
            new_objects = [new_objects]

        if pos is not None:
            self._tree[pos:pos] = new_objects
        else:
            self._tree.extend(new_objects)

        for obj in set(new_objects):
            obj.parent_cells.add(self)

        self.tree_changed()

    def remove(self, pos, num=1):
        """Remove objects from the objects tree of the cell.

        :param int pos: Position from which the objects are removed.
        :param num: Number of objects to remove.
        :type num: int, optional
        """
        if pos < 0:
            end = len(self._tree) + pos + num
        else:
            end = pos + num

        removed_objects = self.tree[pos:end]
        self._tree[pos:end] = []
        for obj in set(removed_objects):
            if obj not in self._tree:
                obj.parent_cells.remove(self)

        self.tree_changed()

    @property
    def lattice(self) -> List[Type[Element]]:
        """Defines the physical order of elements. Corresponds to flattened tree."""
        if self._tree_properties_needs_update:
            self.update_tree_properties()

        return self._lattice

    @property
    def elements(self) -> Dict[str, Type[Element]]:
        """Contains all elements within this cell."""
        if self._tree_properties_needs_update:
            self.update_tree_properties()

        return self._elements

    @property
    def cells(self) -> Dict[str, 'Cell']:
        """Contains all cells within this cell."""
        if self._tree_properties_needs_update:
            self.update_tree_properties()

        return self._cells

    def update_tree_properties(self):
        """Manually update the lattice, elements and cell properties."""
        self._lattice.clear()
        self._elements.clear()
        self._cells.clear()
        self._update_tree_properties(self.tree)
        self._tree_properties_needs_update = False

    def _update_tree_properties(self, tree):
        """A recursive helper function for update_tree_properties."""
        lattice = self._lattice
        elements = self._elements
        cells = self._cells
        for obj in tree:
            # TODO: obj = weakref.proxy(x) # all references should be weak!
            if isinstance(obj, Cell):
                value = cells.get(obj.name)
                if value is None:
                    cells[obj.name] = obj
                elif obj is not value:
                    raise AmbiguousNameError(obj.name)

                self._update_tree_properties(obj.tree)
            else:
                lattice.append(obj)
                value = elements.get(obj.name)
                if value is None:
                    elements[obj.name] = obj
                elif obj is not value:
                    raise AmbiguousNameError(obj.name)

    def _on_tree_properties_changed(self):
        self._tree_properties_needs_update = True
        for cell in self.parent_cells:
            cell.tree_properties_changed()

    def print_tree(self):
        """Print the tree of objects."""
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
