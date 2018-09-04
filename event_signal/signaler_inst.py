from .signal_funcs import SignalError, get_signal, on_signal, off_signal, fire_signal, block_signals
from .mp_manager import SignalEvent, MpSignalManager


__all__ = ["SignalerInstance", 'SignalerDescriptorInstance']


class SignalerInstance(object):
    """Emulates a function that has signals. This class is returned when signaler is used as a decorator."""

    def __init__(self):
        self.event_signals = {}
        self.name = str(id(self))

        # Multiprocessing variables to save
        self._mp_variables = ['name']

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

    def fire_queue(self, signal_type, *args, **kwargs):
        """Fire the signal by putting the data on a queue to be called in the main process."""
        SignalEvent.fire_signal(self.name, signal_type, *args, **kwargs)
        try:
            fire_signal(self, signal_type, *args, **kwargs)
        except SignalError:
            pass

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
    # ========== END Callbacks ==========

    # ========== Multiprocessing Support ==========
    def __getstate__(self):
        """Return the state for multiprocessing.

        Note:
            The main process should connect to signals with the 'on' method. The multiprocessing should emit signals
            with the 'fire' method.
        """
        # Get the variables to share with the other process
        state = {key: getattr(self, key, None) for key in self._mp_variables}
        state['_mp_variables'] = self._mp_variables
        state['event_signals'] = list(self.event_signals.keys())

        # Register the signal, so the appropriate signal can be called.
        SignalEvent.register_signal(self.name, self)

        # Share SignalEvent queues
        state['SignalEvent.QUEUE'] = SignalEvent.QUEUE

        # Change the fire function
        state['fire'] = self.fire_queue

        return state

    def __setstate__(self, state):
        """Recreate the object after unpickling."""
        # Default variables
        SignalEvent.QUEUE = state.pop('SignalEvent.QUEUE', SignalEvent.QUEUE)
        self.is_separate_process = state.pop('is_separate_process', True)
        self.event_signals = {key: [] for key in state.pop('event_signals')}

        for key, value in state.items():
            try:
                setattr(self, key, value)
            except:
                pass


class SignalerDescriptorInstance(SignalerInstance):
    """Class that can easily be used as a class descriptor"""
    def __init__(self):
        super().__init__()
        self.name_searched = False
        self.__signalers__ = {}
        self._mp_variables.extend(['__signalers__', 'name_searched'])

    def _find_name(self, owner):
        """Find the variable name for this signal from the owner.

        This is required to allow multiprocessing to keep in sync. Multiprocessing does not pickle class variables, so
        this object id may be different in a separate process.
        """
        if not self.name_searched:
            try:
                for key, val in owner.__dict__.items():
                    if val == self:
                        self.name = owner.__name__ + '.' + key
                        break
            except (ValueError, TypeError):
                pass

            self.name_searched = True

    def get_signaler_instance(self, instance=None):
        """Return (maybe create) the instance CallbackManager."""
        if instance is None:
            return self

        # Check to find the correct name
        self._find_name(instance.__class__)

        # Make sure the instance keeps track of all it's signalers
        if not hasattr(instance, '__signalers__'):
            instance.__signalers__ = {}

        # Get the signaler
        try:
            return instance.__signalers__[self.name]  # return an event handler object for the instance
        except KeyError:
            # Create the signaler instance
            sig = self.create_signaler_instance(instance)
            sig.name_searched = True
            sig.name = self.name + '-' + repr(instance)

            instance.__signalers__[self.name] = sig
            return sig

    def create_signaler_instance(self, instance=None):
        """Create and return a signaler instance."""
        raise NotImplementedError
