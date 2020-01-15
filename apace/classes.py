import inspect
import sys
from typing import List, Set, Dict, List, Iterable
from .utils import Signal, AmbiguousNameError


class Base:
    """Abstract base for all element and lattice classes.

    :param str name: The name of the object.
    :param description: A brief description of the object.
    :type description: str, optional
    """

    def __init__(self, name, length, description=""):
        self.name: str = name
        """The name of the object."""
        self.description: str = description
        """A brief description of the object"""
        self.parent_lattices: Set["Lattice"] = set()
        """All lattices which contain the object."""
        self._length = length

    @property
    def length(self) -> float:
        """Length of the object (m)."""
        return self._length

    def __repr__(self):
        return self.name

    def __str__(self):
        attributes = [("type", self.__class__.__name__)]
        properties = []
        signals = []
        for key in dir(self):
            if key.startswith("_"):
                continue

            obj = getattr(self, key)
            if isinstance(obj, property):
                properties.append(key, str(obj))
            elif isinstance(obj, Signal):
                signals.append((key, str(obj)))
            else:
                attributes.append((key, str(obj)))

        return "\n".join(
            f"{name:16}: {string}" for name, string in attributes + properties + signals
        )


class Element(Base):
    """Abstract base for all element classes.

    :param str name: The name of the element.
    :param float length: The length of the element (m).
    :param str description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, description=""):
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
        for lattice in self.parent_lattices:
            lattice.length_changed()
            lattice.element_changed(self)

    def _on_value_changed(self):
        for lattice in self.parent_lattices:
            lattice.element_changed(self)


class Drift(Element):
    """A drift space element.

    :param str name: The name of the element.
    :param float length: The length of the element (m).
    :param str description: A brief description of the element.
    :type description: str, optional
    """

    pass


class Dipole(Element):
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

    def __init__(self, name, length, angle, e1=0, e2=0, description=""):
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


class Quadrupole(Element):
    """A quadrupole element.

    :param str name: Name of the element.
    :param float length: Length of the element (m).
    :param float k1: Geometric quadrupole strength (m^-2).
    :param description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, k1, description=""):
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


class Sextupole(Element):
    """A sextupole element.

    :param str name: Name of the element.
    :param float length: Length of the element (m).
    :param float k1: Geometric quadrupole strength (m^-3).
    :param description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, k2, description=""):
        super().__init__(name, length, description)
        self._k2 = k2

    @property
    def k2(self) -> float:
        """Geometric sextupole strength (m^-3)."""
        return self._k2

    @k2.setter
    def k2(self, value):
        self._k2 = value
        self.value_changed()


class Octupole(Element):
    """An octupole element.

    :param str name: Name of the element.
    :param float length: Length of the element (m).
    :param float k3: Geometric quadrupole strength (m^-4).
    :param description: A brief description of the element.
    :type description: str, optional
    """

    def __init__(self, name, length, k3, description=""):
        super().__init__(name, length, description)
        self._k3 = k3

    @property
    def k3(self) -> float:
        """Geometric sextupole strength (m^-1)."""
        return self._k3

    @k3.setter
    def k3(self, value):
        self._k3 = value
        self.value_changed()


class Lattice(Base):
    """Defines the order of elements in the accelerator.

    :param str name: Name of the lattice.
    :param Tuple[Union[Element, Lattice] tree: Nested tree of elements and lattices.
    :param str description: A brief description of the element.
    """

    def __init__(self, name, tree, description=None):
        super().__init__(name, description)
        self._tree = tree
        for obj in set(tree):
            obj.parent_lattices.add(self)

        # arrangement, positions, elements & sub_lattices are infered from self.tree
        self._arrangement = []  # TODO: is an np.array better here?
        self._indices = {}
        self._elements = {}
        self._sub_lattices = {}
        self._update_tree_properties()

        self._length = 0
        self._length_needs_update = True
        self.length_changed: Signal = Signal()
        """Gets emitted when the length of lattice changes."""
        self.length_changed.connect(self._on_length_changed)

        self.element_changed: Signal = Signal()
        """Gets emitted when an attribute of an element within this lattice changes."""
        self.element_changed.connect(self._on_element_changed)

    def __getitem__(self, key):
        if isinstance(key, str):
            try:
                return self.elements[key]
            except KeyError:
                return self.sub_lattices[key]
        else:
            return self.arrangement[key]

    def __del__(self):
        for obj in self.tree:
            obj.parent_lattices.discard(self)

    @property
    def length(self) -> float:
        """Length of the lattice."""
        if self._length_needs_update:
            self.update_length()
        return self._length

    def update_length(self):
        """Manually update the Length of the lattice (m)."""
        self._length = sum(obj.length for obj in self.tree)
        self._length_needs_update = False

    # TODO: move to base class
    def _on_length_changed(self):
        self._length_needs_update = True
        for lattice in self.parent_lattices:
            lattice.length_changed()

    def _on_element_changed(self, element):
        for lattice in self.parent_lattices:
            lattice.element_changed(element)

    @property
    def tree(self) -> List[Base]:  # do not set tree manually
        """The tree of objects defines the physical order of elements withing this lattice."""
        return self._tree

    @property
    def arrangement(self) -> List[Element]:
        """Defines the physical order of elements. Corresponds to flattened tree."""
        return self._arrangement

    @property
    def indices(self) -> Dict[Element, List[float]]:
        """A dict which contains the a `List` of indices for each element.
           Can be thought of as inverse of arrangment."""
        return self._indices

    @property
    def elements(self) -> Dict[str, Element]:
        """Contains all elements within this lattice."""
        return self._elements

    @property
    def sub_lattices(self) -> Dict[str, "Lattice"]:  # TODO: Python 3.7 change type hint
        """Contains all lattices within this lattice."""
        return self._sub_lattices

    def _update_tree_properties(self, tree=None, idx=0):
        """A recursive helper function to update the tree properties."""
        if tree is None:
            tree = self._tree

        arrangement = self._arrangement
        indices = self._indices
        elements = self._elements
        sub_lattices = self._sub_lattices
        for obj in tree:
            if isinstance(obj, Lattice):
                value = sub_lattices.get(obj.name)
                if value is None:
                    sub_lattices[obj.name] = obj
                elif obj is not value:
                    raise AmbiguousNameError(obj.name)

                idx = self._update_tree_properties(obj.tree, idx)
            else:
                arrangement.append(obj)
                try:
                    indices[obj].append(idx)
                except KeyError:
                    indices[obj] = [idx]

                idx += 1

                value = elements.get(obj.name)
                if value is None:
                    elements[obj.name] = obj
                elif obj is not value:
                    raise AmbiguousNameError(obj.name)
        return idx

    def print_tree(self):
        """Print the lattice as tree of objects. (Similar to unix tree command)"""
        print(self._tree_as_string(self))

    @staticmethod
    def _tree_as_string(obj, prefix=""):
        string = obj.name + "\n"
        if isinstance(obj, Lattice):
            for node in obj.tree[:-1]:
                string += f"{prefix}├─── "
                string += Lattice._tree_as_string(node, prefix + "│   ")

            string += f"{prefix}└─── "
            string += Lattice._tree_as_string(obj.tree[-1], prefix + "    ")
        return string

    @classmethod
    def from_dict(cls, data):
        """Creates a new `Lattice` object from a latticeJSON compliant dictionary."""

        objects = {}  # dictionary for all objects (elements + lattices)
        for name, attributes in data["elements"].items():
            type_ = attributes.pop("type")

            class_ = getattr(sys.modules[__name__], type_)
            objects[name] = class_(name=name, **attributes)

        # TODO: make sure sub_lattices are loaded in correct order
        sub_lattices = data["sub_lattices"]
        for name, tree_names in sub_lattices.items():
            tree = [objects[name] for name in tree_names]
            objects[name] = Lattice(name, tree)

        return Lattice(
            name=data["name"],
            tree=[objects[name] for name in data["lattice"]],
            description=data.get("description", ""),
        )

    def as_dict(self):
        """Serializes the `Lattice` object into a latticeJSON compliant dictionary."""
        elements_dict = {}
        for element in self.elements.values():
            attributes = {
                key: getattr(element, key)
                for (key, value) in inspect.signature(
                    element.__class__
                ).parameters.items()
            }
            attributes.pop("name")
            elements_dict[element.name] = attributes
            elements_dict[element.name]["type"] = element.__class__.__name__

        sub_lattices_dict = {
            lattice.name: [obj.name for obj in lattice.tree]
            for lattice in self.sub_lattices.values()
        }

        return dict(
            name=self.name,
            description=self.description,
            lattice=[obj.name for obj in self.tree],
            elements=elements_dict,
            sub_lattices=sub_lattices_dict,
        )
