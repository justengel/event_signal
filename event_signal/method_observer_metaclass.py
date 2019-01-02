from future.utils import with_metaclass

import types
from .signaler import signaler


__all__ = ["MethodObserverMeta", "MethodObserver"]


class MethodObserverMeta(type):
    """Meta class that makes all functions signalers."""
    def __new__(typ, name, bases, attr):
        # Replace each function with a Signalar that can have custom methods connected to it.
        for name, value in attr.items():
            val_type = type(value)
            if not name.startswith("__") and (val_type is types.FunctionType or val_type is types.MethodType):
                attr[name] = signaler(value)

        return super(MethodObserverMeta, typ).__new__(typ, name, bases, attr)


class MethodObserver(with_metaclass(MethodObserverMeta, object)):
    """Class mixin that makes all functions signaler functions that can be connected to."""
    pass
