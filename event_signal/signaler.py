from .signal_funcs import fire_signal
from .signaler_inst import SignalerInstance
from .signaler_prop import signaler_property


class SignalerDecoratorInstance(SignalerInstance):
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

        self.event_signals = {"before_change": [], "change": []}

    def __call__(self, *args, **kwargs):
        fire_signal(self, "before_change", *args, **kwargs)
        ret = self.func(*args, **kwargs)
        fire_signal(self, "change", *args, **kwargs)
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
            if self.func:
                func = self.func.__get__(instance, instance.__class__)

            # Create the new signaler for the instance with bound methods.
            sig = SignalerDecoratorInstance(func)
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
