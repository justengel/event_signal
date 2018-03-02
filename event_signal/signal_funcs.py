

__all__ = ["get_signal", "on_signal", "off_signal", "emit_signal", "add_signal"]


def get_signal(manager, signal_type):
    """Return a list of callback functions that are connected to the signal."""
    funcs_sig = getattr(manager, "_"+signal_type+"_funcs", None)
    if funcs_sig is None:
        raise ValueError("Invalid 'signal_type' given ({:s}). Cannot connect a function to this "
                         "signal.".format(repr(signal_type)))
    return [func for func in funcs_sig]


def on_signal(manager, signal_type, func):
    """Connect a callback function to a signal."""
    connect_sig = getattr(manager, "connect_"+signal_type, None)
    if connect_sig is None:
        raise ValueError("Invalid 'signal_type' given ({:s}). Cannot connect a function to this "
                         "signal.".format(repr(signal_type)))
    connect_sig(func)


def off_signal(manager, signal_type, func):
    """Disconnect a callback function from a signal."""
    disconnect_sig = getattr(manager, "disconnect_"+signal_type, None)
    if disconnect_sig is None:
        raise ValueError("Invalid 'signal_type' given ({:s}). Cannot disconnect a function from this "
                         "signal.".format(repr(signal_type)))
    disconnect_sig(func)


def emit_signal(manager, signal_type, *args, **kwargs):
    """Call all fo the callback functions for a signal."""
    emit_sig = getattr(manager, "emit_"+signal_type, None)
    if emit_sig is None:
        raise ValueError("Invalid 'signal_type' given ({:s}). Cannot emit and call callback functions from this "
                         "signal.".format(repr(signal_type)))
    emit_sig(*args, **kwargs)


def add_signal(signal_type, cls=None):
    """Add a 'signal_type' to a class."""
    # ===== Decorator =====
    if cls is None:
        def wrapper(cls):
            return add_signal(signal_type, cls)
        return wrapper

    # ===== Make Class =====
    if not hasattr(cls, "SIGNALS"):
        cls.SIGNALS = []

    if signal_type in cls.SIGNALS:
        raise ValueError("Class " + repr(cls) + " already has the signal_type "+repr(signal_type))

    funcs_var = "_"+signal_type+"_funcs"

    class NewClass(cls):
        SIGNALS = [sig for sig in cls.SIGNALS] + [signal_type]

        def __init__(self, *args, **kwargs):
            setattr(self, funcs_var, [])
            super(NewClass, self).__init__(*args, **kwargs)

    def connect_func(self, func):
        funcs = getattr(self, funcs_var)
        if func not in funcs:
            funcs.append(func)

    def disconnect_func(self, func=None):
        funcs = getattr(self, funcs_var)
        if func is None:
            funcs.clear()
        else:
            try:
                funcs.remove(func)
            except:
                pass

    def emit_func(self, *args, **kwargs):
        for func in getattr(self, funcs_var):
            func(*args, **kwargs)

    setattr(NewClass, "connect_"+signal_type, connect_func)
    setattr(NewClass, "disconnect_"+signal_type, disconnect_func)
    setattr(NewClass, "emit_"+signal_type, emit_func)

    try:
        NewClass.__name__ = cls.__name__
    except AttributeError:
        pass

    return NewClass
