from enum import Enum, auto


class Signal:
    """A callable signal class to which callbacks can be registered.

    When ever the signal is emitted all registered functions are called.

    :param signals: Signals which this signal gets registered to.
    :type signals: Signal, optional
    """

    def __init__(self, *signals):
        self.callbacks = set()
        """Functions called when the signal is emitted."""
        for signal in signals:
            signal.connect(self)

    def __call__(self, *args, **kwargs):
        """Emit signal and call registered functions."""
        for callback in self.callbacks:
            callback(*args, **kwargs)

    def __str__(self):
        return "Signal"

    __repr__ = __str__

    def connect(self, callback):
        """Connect a callback to this signal.

        :param function callback: Function which gets called when the signal is emitted.
        """
        self.callbacks.add(callback)


class Flag:
    def __init__(self, initial_value, signals=None):
        self.value = initial_value
        for signal in signals:
            signal.connect(self.set_value(True))

    def __bool__(self):
        return self.value

    def set_value(self, value):
        self.value = value


class Attribute(Enum):
    LENGTH = auto()
    ANGLE = auto()
    K1 = auto()
    K2 = auto()
    K3 = auto()
    E1 = auto()
    E2 = auto()


class AmbiguousNameError(Exception):
    """Raised if multiple elements or lattices have the same name.

    :param str name: The ambiguous name.
    """

    def __init__(self, name):
        super().__init__(f'The name "{name}" is ambiguous. Names must be unique!')
