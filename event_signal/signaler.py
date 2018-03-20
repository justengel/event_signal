from .signal_funcs import fire_signal
from .signaler_inst import SignalerInstance
from .signaler_prop import signaler_property


__all__ = ["signaler", "SignalerDecoratorInstance"]


class SignalerDecoratorInstance(SignalerInstance):
    def __init__(self, func=None, getter=None):
        """Decorate a function to emit signals.

        Args:
            func (callable)[None]: Callable function that you want to decorate.
            getter (callable)[None]: Takes no arguments and returns a single argument that is used when firing
                the change signal.
        """
        super().__init__()

        self.func = func
        self.getter = getter
        self.event_signals = {"before_change": [], "change": []}

        try:
            self.__name__ = self.func.__name__
        except AttributeError:
            pass
        try:
            self.__doc__ = self.func.__doc__
        except AttributeError:
            pass

    def __call__(self, *args, **kwargs):
        if self.func is None and callable(args[0]):
            # Decorating a function
            self.func = args[0]
            try:
                self.__name__ = self.func.__name__
            except AttributeError:
                pass
            try:
                self.__doc__ = self.func.__doc__
            except AttributeError:
                pass
            return self
        else:
            # Calling this class
            fire_signal(self, "before_change", *args, **kwargs)
            ret = self.func(*args, **kwargs)

            if self.getter is None:
                fire_signal(self, "change", *args, **kwargs)
            else:
                fire_signal(self, "change", self.getter())
            return ret


class signaler(SignalerDecoratorInstance):
    """Signaler used with binded methods and instances. Does not allow using as a decorator."""

    property = signaler_property

    def get_signaler_instance(self, instance=None):
        """Return (maybe create as well) the signals mapped to the instance.

        Args:
            instance (object)[None]: Instance object that has signals.
        """
        if instance is None:
            instance = self
        if not hasattr(instance, "__signalers__"):
            instance.__signalers__ = {}
        if self not in instance.__signalers__:
            func = None
            getter = None
            if self.func:
                func = self.func.__get__(instance, instance.__class__)
            if self.getter:
                getter = self.getter.__get__(instance, instance.__class__)

            # Create the new signaler for the instance with bound methods.
            sig = SignalerDecoratorInstance(func, getter=getter)
            instance.__signalers__[self] = sig

            # Map all of the connected callbacks as bound methods to the instance
            for key, funcs in self.event_signals.items():
                if key not in sig.event_signals:
                    sig.event_signals[key] = []

                # Bind the methods and add them to the signals
                bound_funcs = [func.__get__(instance, instance.__class__) for func in funcs]
                sig.event_signals[key] = sig.event_signals[key] + bound_funcs

        return instance.__signalers__[self]  # return an event handler object for the instance
    # end get_signaler_instance

    def __get__(self, instance, owner):
        """Return the signaler with a binded method callback."""
        return self.get_signaler_instance(instance)
