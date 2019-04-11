from future.utils import raise_from


__all__ = ['SignalError', "get_signal", "on_signal", "off_signal", "fire_signal", "block_signals", "add_signal",
           "copy_signals", "copy_signals_as_bound", 'SignalerInstance', 'SignalerDescriptorInstance']


class SignalError(ValueError):
    pass


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
        err = SignalError("Invalid 'signal_type' given ({:s}). Cannot connect a function to this "
                          "signal.".format(repr(signal_type)))
        raise_from(err, error)
        # raise err from error


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
            try:
                sig.clear()
            except AttributeError:
                del sig[:]  # Python 2.7
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
        err = SignalError("Invalid 'signal_type' given ({:s}). Cannot connect a function to this "
                          "signal.".format(repr(signal_type)))
        raise_from(err, error)
        # raise err from error

    for func in sig:
        func(*args, **kwargs)


def init_signals(obj):
    # Make sure the event signals are initialized
    if not hasattr(obj, '__signalerinstances__'):
        obj.__signalerinstances__ = [name for name in dir(obj)
                                     if isinstance(getattr(obj.__class__, name, None), SignalerInstance) or
                                        isinstance(getattr(obj, name, None), SignalerInstance)]


def block_signals(obj, signal_type=None, block=True):
    """Temporarily block signals from being called."""
    # Make sure the event signals are initialized
    init_signals(obj)

    # Check the signal type
    if signal_type is None:
        # Block all SignalerInstance
        for name in obj.__signalerinstances__:
            try:
                getattr(obj, name, None).block(block=block)
            except (AttributeError, Exception):
                pass
        try:
            signal_type = list(obj.event_signals.keys())
        except AttributeError:
            signal_type = []

    elif not isinstance(signal_type, (list, tuple)):
        signal_type = [signal_type]

    # Block all of the signal types for this object
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


class SignalerInstance(object):
    """Emulates a function that has signals. This class is returned when signaler is used as a decorator."""

    def __init__(self):
        self.event_signals = {}
        self.name = str(id(self))

    # ========== Callbacks ==========
    get_signal = get_signal

    def on(self, signal_type, func=None):
        """Connect a callback function to a signal. If a function is not given then a decorator function is returned.

        Example:

            .. code-block:: python

                class MyClass:
                    @signaler
                    def set_x(self, value):
                        self._x = value

                    @set_x.on("change")
                    def notify_change(self, value):
                        print("x was changed")

                m = MyClass()
                m.set_x(1)
                # "x was changed"
                m.set_x.on("change", print)
                m.set_x(2)
                # "x was changed"
                # 2

        Args:
            signal_type (str): Signal name to direct which signal to use
            func (callable)[None]: Callback function

        Returns:
            func (callable): The callable function that was given or a decorator to decorate a function.
        """
        if func is None:
            def decorator(func):
                self.on(signal_type, func)
                return func
            return decorator

        on_signal(self, signal_type, func)
        return func

    def off(self, signal_type, func=None):
        """Disconnect a callback function from a signal.

        Example:

            .. code-block:: python

                class MyClass:
                    @signaler
                    def set_x(self, value):
                        self._x = value

                    @set_x.on("change")
                    def notify_change(self, value):
                        print("x was changed")

                m = MyClass()
                m.set_x(1)
                # "x was changed"
                m.set_x.off("change", m.notify_change)
                p.set_x(2)

        Args:
            signal_type (str): Signal name to direct which signal to use
            func (callable)[None]: Callback function

        Returns:
            existed (bool): True if the given function was attached to the signal. Also True if the given func argument
                was None and there was at least 1 function attached to the signal.
        """
        return off_signal(self, signal_type, func)

    def fire(self, signal_type, *args, **kwargs):
        """Call all of the callback functions that are associated with a signal.

        Example:

            .. code-block:: python

                class MyClass:
                    @signaler
                    def set_x(self, value):
                        self._x = value

                    @set_x.on("change")
                    def notify_change(self, value):
                        print("x was changed", value)

                m = MyClass()
                m.set_x.fire("change", 1)
                # "x was changed 1"

        Args:
            signal_type (str): Signal name to direct which signal to use
            *args: Arguments to pass to the callback functions
            **kwargs: Named arguments to pass to the callback functions
        """
        # Main process fire a normal signal
        fire_signal(self, signal_type, *args, **kwargs)

    def block(self, signal_type=None, block=True):
        """Temporarily block a specific signal or all signals from calling their callback functions.

        Example:

            .. code-block:: python

                class MyClass:
                    @signaler
                    def set_x(self, value):
                        self._x = value

                    @set_x.on("before_change")
                    def notify_before_change(self, value):
                        print("x is changing", value)

                    @set_x.on("change")
                    def notify_change(self, value):
                        print("x was changed", value)

                m = MyClass()
                m.set_x(1)
                # "x is changing 1"
                # "x was changed 1"

                m.set_x.block()
                m.set_x(2)

                m.set_x.block(block=False)
                m.set_x(3)
                # "x is changing 2"
                # "x was changed 3"

                m.set_x.block("before_change", True)
                m.set_x(4)
                # "x was changed 4"

                m.set_x.block("before_change", False)
                m.set_x(5)
                # "x is changing 5"
                # "x was changed 5"

        Args:
            signal_type (str)[None]: Signal name to direct which signal to block or None to block or unblock all signals
            block (bool)[True]: Block or unblock the signals
        """
        return block_signals(self, signal_type=signal_type, block=block)


class SignalerDescriptorInstance(SignalerInstance):
    """Class that can easily be used as a class descriptor"""
    def get_signaler_instance(self, instance=None):
        """Return (maybe create) the instance CallbackManager."""
        if instance is None:
            return self

        # Make sure the instance keeps track of all it's signalers
        if not hasattr(instance, '__signalers__'):
            instance.__signalers__ = {}

        # Get the signaler
        try:
            return instance.__signalers__[self]  # return an event handler object for the instance
        except KeyError:
            # Create the signaler instance
            sig = self.create_signaler_instance(instance)
            instance.__signalers__[self] = sig
            return sig

    def create_signaler_instance(self, instance=None):
        """Create and return a signaler instance."""
        raise NotImplementedError
