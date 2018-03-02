import functools
from .signal_funcs import get_signal, on_signal, off_signal, emit_signal


class signaler_instance(object):
    """Fake function that allows connecting to before_change and change signals."""
    SIGNALS = ["before_change", "change"]

    def __init__(self, func):
        super().__init__()

        self.func = func
        try:
            self.__name__ = self.func.__name__
        except AttributeError:
            pass
        try:
            self.__doc__ = self.func.__doc__
        except AttributeError:
            pass

        self._before_change_funcs = []
        self._change_funcs = []

    def __call__(self, *args, **kwargs):
        self.emit_before_change(*args, **kwargs)
        ret = self.func(*args, **kwargs)
        self.emit_change(*args, **kwargs)
        return ret

    # ========== Callbacks ==========
    def get(self, signal_type):
        """Return a list of callback methods that are connected with the given signal."""
        return get_signal(self, signal_type)

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
        """
        if func is None:
            def wrapper(func):
                self.on(signal_type, func)
                return func
            return wrapper

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
        """
        off_signal(self, signal_type, func)

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
        emit_signal(self, signal_type, *args, **kwargs)

    # ===== Pre Change =====
    def connect_before_change(self, func):
        if func not in self._before_change_funcs:
            self._before_change_funcs.append(func)

    def disconnect_before_change(self, func=None):
        if func is None:
            self._before_change_funcs = []
        else:
            try:
                self._before_change_funcs.remove(func)
            except:
                pass

    def emit_before_change(self, *args, **kwargs):
        for func in self._before_change_funcs:
            func(*args, **kwargs)

    # ===== Normal Post Change signal =====
    def connect_change(self, func):
        if func not in self._change_funcs:
            self._change_funcs.append(func)

    def disconnect_change(self, func=None):
        if func is None:
            self._change_funcs = []
        else:
            try:
                self._change_funcs.remove(func)
            except:
                pass

    def emit_change(self, *args, **kwargs):
        for func in self._change_funcs:
            func(*args, **kwargs)

    connect = connect_change
    disconnect = disconnect_change
    emit = emit_change
    # ========== END Callbacks ==========


class signaler(signaler_instance):
    """Signaler used with binded methods and instances. Does not allow using as a decorator."""

    def get_signaler_instance(self, instance=None):
        """Return (maybe create as well) the instance CallbackManager.

        Args:
            instance (object)[None]: Instance object that has observables.
        """
        if instance is None:
            instance = self
        if not hasattr(instance, "__signalers__"):
            instance.__signalers__ = {}
        if self not in instance.__signalers__:
            func = None
            if self.func:
                func = self.func.__get__(instance, instance.__class__)
            instance.__signalers__[self] = signaler_instance(func)
            instance.__signalers__[self]._before_change_funcs = [func.__get__(instance, instance.__class__)
                                                              for func in self._before_change_funcs]
            instance.__signalers__[self]._change_funcs = [func.__get__(instance, instance.__class__)
                                                          for func in self._change_funcs]

        return instance.__signalers__[self]  # return an event handler object for the instance
    # end get_callback

    def __get__(self, instance, owner):
        """Return the signaler with a binded method callback."""
        return self.get_signaler_instance(instance)
