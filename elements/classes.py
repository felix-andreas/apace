import weakref  # only tree should contain strong ref
from .utils import WeakList
import numpy as np


class _Base:

    def __init__(self, name, type, comment):
        """
        A base class for elements and cells.
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
        attributes = []
        for key, value in self.__dict__.items():
            if key[0] != '_' and key != "main_cell" and not "flag" in key:
                if isinstance(value, weakref.WeakSet):
                    string = f"{', '.join(e.name for e in value):}"
                else:
                    string = str(value)
                attributes.append(f"{key:12}: {string:}")

        properties = []
        for x in dir(self.__class__):
            x_attr = getattr(self.__class__, x)
            if isinstance(x_attr, property):
                x_attr = x_attr.fget(self)
                if isinstance(x_attr, weakref.WeakSet):
                    string = ', '.join(e.name for e in x_attr)
                else:
                    string = str(x_attr)
                properties.append(f"{x:12}: {string}")
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
        self._nkicks = 10
        self.parent_cells = set() #weakref.WeakSet()
        self.stepsize = self._length / self._nkicks
        self._positions = []
        self.main_cell = None

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value
        self.stepsize = self._length / self._nkicks
        for x in self.parent_cells:
            x.length_flag.has_changed = True

    @property
    def nkicks(self):
        return self._nkicks

    @nkicks.setter
    def nkicks(self, value):
        self._nkicks = value
        self.stepsize = self._length / self._nkicks
        for x in self.parent_cells:
            x.nkicks_flag.has_changed = True

    @property
    def positions(self):
        if self.main_cell and self.main_cell.elements_positon_flag.has_changed:
            self.main_cell.update_element_positions()
        return self._positions

    def value_changed(self):
        self.main_cell.set_changed_element(self)


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


class Quad(_Element):
    def __init__(self, name, length, k1, comment=''):
        super().__init__(name, 'Quad', length, comment)
        self._k1 = k1

    @property
    def k1(self):
        return self._k1

    @k1.setter
    def k1(self, value):
        self._k1 = value
        self.value_changed()


class Sext(_Element):
    def __init__(self, name, length, k2, comment=''):
        super().__init__(name, 'Sext', length, comment)
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
        comment : str, optional
            A brief comment on the cell.

        Attributes
        ----------
        tree : list
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
            Set of all elements.
        cells : set
            Set of all cells.
    """

    def __init__(self, name, tree=None, comment=''):
        super().__init__(name, "Cell", comment)
        # attributes
        self._tree = list()  # has strong links to objects
        self.tree_flag = CachedPropertyFlag(depends_on=None)
        self.child_cells = set() #weakref.WeakSet()
        self.parent_cells = set() #weakref.WeakSet()
        self.main_cell = None
        # tree properties
        self.tree_properties_flag = CachedPropertyFlagCell(self, "tree_properties_flag", depends_on=[self.tree_flag])
        self._lattice = list() #WeakList()  ##TODO: check performance vs list
        self._elements = dict() #weakref.WeakValueDictionary
        self._cells = dict() #weakref.WeakValueDictionary
        # length
        self._length = 0
        self.length_flag = CachedPropertyFlagCell(self, "length_flag", depends_on=[self.tree_flag])
        # nkicks
        self._nkicks = 0
        self.nkicks_flag = CachedPropertyFlagCell(self, "nkicks_flag", depends_on=[self.tree_flag])
        # add objects
        if tree:
            self.tree_add_objects(tree, pos=len(self.tree))

    @property
    def tree(self):
        return self._tree

    # tree setter 1
    def tree_add_objects(self, new_objects_list, pos=None):
        self.tree_properties_flag.has_changed = True
        if pos:
            self._tree[pos:pos] = new_objects_list
        else:
            self._tree.extend(new_objects_list)

        for obj in set(new_objects_list):
            obj.parent_cells.add(self)
            if isinstance(obj, Cell):
                self.child_cells.add(obj)
        self.tree_flag.has_changed = False

    # tree setter 2
    def tree_remove_objects(self, pos, num=1):
        self.tree_properties_flag.has_changed = True
        removed_objects = self.tree[pos:pos + num]
        self._tree[pos:pos + num] = []
        for obj in set(removed_objects):
            if obj not in self._tree:
                if isinstance(obj, Cell):
                    self.child_cells.remove(obj)
                print(obj.name, obj.parent_cells, self.tree)
                obj.parent_cells.remove(self)
        self.tree_flag.has_changed = False

    # class properties
    @property
    def lattice(self):
        if self.tree_properties_flag.has_changed:
            self.update_tree_properties()
        return self._lattice

    @property
    def elements(self):
        if self.tree_properties_flag.has_changed:
            self.update_tree_properties()
        return self._elements

    @property
    def cells(self):
        if self.tree_properties_flag.has_changed:
            self.update_tree_properties()
        return self._cells

    def update_tree_properties(self):
        self._lattice.clear()
        self._elements.clear()
        self._cells.clear()
        self._update_tree_properties(self.tree)
        self.tree_properties_flag.has_changed = False


    def _update_tree_properties(self, tree):
        '''A recursive helper function for update_tree_properties.'''
        for x in tree:
            # x = weakref.proxy(x) # all references should be weak!
            if isinstance(x, Cell):
                if x.name not in self._cells:
                    self._cells[x.name] = x
                self._update_tree_properties(x.tree)
            else:
                self._lattice.append(x)
                if x.name not in self._elements:
                    self._elements[x.name] = x

    @property
    def length(self):
        if self.length_flag.has_changed:
            self.update_length()
            self.length_flag.has_changed = False
        return self._length

    def update_length(self):  # is overwritten in Maincell class
        self._length = sum([x.length for x in self.tree])
        self.length_flag.has_changed = False

    @property
    def nkicks(self):
        if self.nkicks_flag.has_changed:
            self.update_nkicks()
            self.nkicks_flag.has_changed = False
        return self._nkicks

    def update_nkicks(self):  # is overwritten in Maincell class
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

    def _print_tree(self, cell):
        length = len(cell.tree)
        for i, x in enumerate(cell.tree):
            is_last = i == length - 1
            fill = "└───" if is_last else "├───"
            print(f"{self.filler}{fill} {x.name}")
            if is_last and self.depth == 0:
                self.start = "    "
            if isinstance(x, Cell):
                self.depth += 1
                self.filler = self.start * (self.depth > 0) + (self.depth - 1) * ("    " if is_last else "│   ")
                self._print_tree(x)
                self.depth -= 1
                self.filler = self.start * (self.depth > 0) + (self.depth - 1) * ("    " if is_last else "│   ")

    def __del__(self):
        for x in self.child_cells:
            x.parent_cells.discard(self)


class MainCell(Cell):
    def __init__(self, *args, description="", **kwargs):
        self.description = description
        super().__init__(*args, **kwargs)
        self.elements_positon_flag = CachedPropertyFlag(depends_on=[self.tree_properties_flag, self.nkicks_flag])
        # set maincell link to all elements and cells
        for x in self.elements.values():
            x.main_cell = self
        for x in self.cells.values():
            x.main_cell = self
        self._stepsize = None
        self.stepsize_flag = CachedPropertyFlag(depends_on=[self.nkicks_flag, self.length_flag, self.tree_properties_flag])
        self._s = None
        self.s_flag = CachedPropertyFlag(depends_on=[self.stepsize_flag])
        self._changed_elements = set()
        self.changed_elements_flag = CachedPropertyFlag()
        self.methods = []


    @property
    def stepsize(self):
        if self.stepsize_flag.has_changed:
            self._stepsize = np.empty(self.nkicks + 1)
            self._stepsize[0] = 0
            for element in self.elements.values():
                self._stepsize[element.positions] = element.stepsize
            self.stepsize_flag.has_changed = False
        return self._stepsize

    @property
    def s(self):
        if self.s_flag.has_changed:
            self._s = np.add.accumulate(self.stepsize)  # s corresponds to the orbit position
        return self._s

    @Cell.length.setter
    def length(self, new_length):
        ratio = new_length / self._length
        self._length = new_length
        for x in self.elements.values():
            x.length = x.length * ratio

    def update_nkicks(self):
        super().update_nkicks()
        self.elements_positon_flag.has_changed = True

    def update_tree_properties(self):
        super().update_tree_properties()
        self.elements_positon_flag.has_changed = True

    def update_element_positions(self):
        self.elements_positon_flag.has_changed = False
        for element in self.elements.values():  # clear element positons
            element._positions.clear()
        start = 1  # starts with 1 because 0th entry is identity matrix
        for element in self.lattice:
            end = start + element.nkicks
            element._positions.extend(list(range(start, end)))
            start = end

    def set_changed_element(self, element):
        self.changed_elements_flag.set_dependents_flags()
        for method in self.methods:
            method.changed_elements(element)


def change_element_type(element, new_type, *args, **kwargs):
    for key in list(element.__dict__):
        delattr(element, key)
    element.__class__ = new_type
    element.__init__(*args, **kwargs)


class CachedPropertyFlag:
    def __init__(self, depends_on=None, initial_state=True):
        """
        A container class for an attribute, which is only computed if one of the
        objects it depends on changes.
        Args:
            depends_on: list of objects the object depends on
        """
        self._has_changed = initial_state
        self.dependents = set()
        self.depends_on = depends_on

        if depends_on:
            for x in self.depends_on:
                x.dependents.add(self)

    @property
    def has_changed(self):
        return self._has_changed

    @has_changed.setter
    def has_changed(self, value):
        self._has_changed = value
        if value:
            self.set_dependents_flags()

    def set_dependents_flags(self):
        for x in self.dependents:
            x.has_changed = True


class CachedPropertyFlagCell(CachedPropertyFlag): # muss verbessert werden , name sollte nicht ubergeben werden
    def __init__(self, cell, flag_name, depends_on=None):
        super().__init__(depends_on)
        self.cell = cell
        self.flag_name = flag_name

    def set_dependents_flags(self):
        super().set_dependents_flags()
        for x in self.cell.parent_cells:
            getattr(x, self.flag_name).has_changed = True

