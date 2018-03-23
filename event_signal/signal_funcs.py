

__all__ = ["get_signal", "on_signal", "off_signal", "fire_signal", "block_signals", "add_signal",
           "copy_signals", "copy_signals_as_bound"]


def get_signal(obj, signal_type):
    """Return a list of callback functions that are connected to the signal."""
    try:
        # Get the blocked functions not the temporary fake signal type used when blocked
        if "blocked-" + signal_type in obj.event_signals:
            sig = obj.event_signals["blocked-" + signal_type]
        else:
            sig = obj.event_signals[signal_type]
        return [func for func in sig]
    except (KeyError, AttributeError) as error:
        raise ValueError("Invalid 'signal_type' given ({:s}). Cannot connect a function to this "
                         "signal.".format(repr(signal_type))) from error


def on_signal(obj, signal_type, func):
    """Connect a callback function to a signal."""
    try:
        # Connect to the blocked functions not the temporary fake signal type used when blocked
        if "blocked-" + signal_type in obj.event_signals:
            sig = obj.event_signals["blocked-" + signal_type]
        else:
            sig = obj.event_signals[signal_type]
        if func not in sig:
            sig.append(func)
    except (KeyError, AttributeError):
        if not hasattr(obj, "event_signals"):
            obj.event_signals = {}
        obj.event_signals[signal_type] = [func]


def off_signal(obj, signal_type, func):
    """Disconnect a callback function from a signal."""
    try:
        # Disconnect from blocked functions not the temporary fake signal type used when blocked
        if "blocked-" + signal_type in obj.event_signals:
            sig = obj.event_signals["blocked-" + signal_type]
        else:
            sig = obj.event_signals[signal_type]
        if func is None:
            existed = len(sig) > 0
            sig.clear()
        else:
            existed = func in sig
            try:
                sig.remove(func)
            except:
                pass
        return existed
    except (KeyError, AttributeError):
        return False


def fire_signal(obj, signal_type, *args, **kwargs):
    """Call all fo the callback functions for a signal."""
    try:
        sig = obj.event_signals[signal_type]
    except (KeyError, AttributeError) as error:
        sig = []
        raise ValueError("Invalid 'signal_type' given ({:s}). Cannot connect a function to this "
                         "signal.".format(repr(signal_type))) from error

    for func in sig:
        func(*args, **kwargs)


def block_signals(obj, signal_type=None, block=True):
    """Temporarily block signals from being called."""
    if signal_type is None:
        signal_type = list(obj.event_signals.keys())
    if not isinstance(signal_type, (list, tuple)):
        signal_type = [signal_type]

    for signal in signal_type:
        if block:
            if "blocked-" + signal not in obj.event_signals:
                try:
                    sigs = obj.event_signals[signal]
                    if sigs:
                        obj.event_signals[signal] = []
                        obj.event_signals["blocked-" + signal] = sigs
                except KeyError:
                    pass
        else:
            try:
                obj.event_signals[signal] = obj.event_signals["blocked-" + signal]
                del obj.event_signals["blocked-" + signal]
            except KeyError:
                pass


def add_signal(obj, signal_type, assign_signal_functions=True):
    """Add a 'signal_type' to an object.

    Warning:
        If a class is given the signal will be added as a class variable. All instances will share the signals.

    Example:

        ..code-block:: python

            >>> # Decorator example
            >>> item = MyClass()
            >>> add_signal(item, "custom_notifier")
            >>> item.on("custom_notifier", lambda *args: print(*args))
            >>> item.fire("custom_notifier", "Hello World!")

    Args:
        signal_type(str): String signal name.
        obj (object)[None]: Object that will have the signal items added to it.
            If an object is not given this function works as a decorator.
        assign_signal_functions (bool)[True]: Add methods 'get_signal', 'on', 'off', and 'fire'.
    """
    # Add normal signal methods
    if assign_signal_functions:
        if not hasattr(obj, "get_signal"):
            obj.get_signal = get_signal.__get__(obj, obj.__class__)
        if not hasattr(obj, "on"):
            obj.on = on_signal.__get__(obj, obj.__class__)
        if not hasattr(obj, "off"):
            obj.off = off_signal.__get__(obj, obj.__class__)
        if not hasattr(obj, "fire"):
            obj.fire = fire_signal.__get__(obj, obj.__class__)

    # Add signal dictionary
    if not hasattr(obj, "event_signals"):
        obj.event_signals = {}
    if signal_type not in obj.event_signals:
        obj.event_signals[signal_type] = []

    return obj


def copy_signals(old_sig, sig):
    """Copy the event_signals over to the new sig.

    Args:
        old_sig: Copy event_signals from this object.
        sig: Add event_signals to this object
    """
    if not hasattr(sig, "event_signals"):
        sig.event_signals = {}

    # Map all of the connected callbacks as bound methods to the instance
    for key, funcs in old_sig.event_signals.items():
        if key not in sig.event_signals:
            sig.event_signals[key] = []

        # Bind the methods and add them to the signals
        bound_funcs = [func for func in funcs if func not in sig.event_signals[key]]
        sig.event_signals[key] = sig.event_signals[key] + bound_funcs


def copy_signals_as_bound(old_sig, sig, instance):
    """Copy the event_signals over to the new sig as bound methods.

    Args:
        old_sig: Copy event_signals from this object.
        sig: Add event_signals to this object
        instance (object): Instance object to bind methods to.
    """
    if not hasattr(sig, "event_signals"):
        sig.event_signals = {}

    # Map all of the connected callbacks as bound methods to the instance
    for key, funcs in old_sig.event_signals.items():
        if key not in sig.event_signals:
            sig.event_signals[key] = []

        # Bind the methods and add them to the signals
        bound_funcs = [func.__get__(instance, instance.__class__) for func in funcs]
        sig.event_signals[key] = sig.event_signals[key] + bound_funcs
