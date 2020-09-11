class AmbiguousNameError(Exception):
    """Raised if multiple elements or lattices have the same name.

    :param str name: The ambiguous name.
    """

    def __init__(self, name):
        super().__init__(f'The name "{name}" is ambiguous. Names must be unique!')


class UnstableLatticeError(Exception):
    """Raised if no stable solution exists for the lattice."""

    def __init__(self, twiss):
        super().__init__(
            f"The lattice {twiss.lattice.name} is unstable!\n"
            f"    Horizontal plane stability: {twiss.stable_x}\n"
            f"    Vertical plane stability  : {twiss.stable_y}"
        )
