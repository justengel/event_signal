"""Multiprocessing manager.

This works by saving a signal with a name. The other process should queue the signal name, signal to be fired,
arguments, and keyword arguments. A thread is spawned in the main process to read this queue and fire the real signal.
"""
import sys
import marshal
import types
import importlib

import threading
import multiprocessing

try:
    from queue import Empty
except ImportError:
    from Queue import Empty


__all__ = ['pickle_module', 'unpickle_module', 'pickle_function', 'unpickle_function', 'MpSignalManager',
           'SignalEvent', 'multiprocessing_support']


def pickle_module(value):
    """Pickle a module."""
    if isinstance(value, types.ModuleType):
        return '{}{};{}{}'.format('__module__.', value.__name__, '__package__.', value.__package__)
    return value


def unpickle_module(value):
    """Pickle a module."""
    if isinstance(value, str) and value.startswith('__module__.'):
        name, package = value.replace('__module__.', '').replace('__package__.', '').split(';')
        value = sys.modules.get(name, None)
        if value is None:
            value = importlib.import_module(name, package)
    return value


def pickle_function(name, func):
    """Pickle and return a dictionary of the decorated function.

    Note:
        Some decorated functions do not pickle correctly. This function aims to correct that.

    Args:
        name (str): Name to pack
    """
    state = {}
    if func:
        state[name + ".__code__"] = marshal.dumps(func.__code__)
        state[name + ".__globals__"] = {key: pickle_module(val) for key, val in func.__globals__.items()}
        try:
            if func.__self__:
                state[name + ".__self__"] = func.__self__
        except AttributeError:
            pass

    return state


def unpickle_function(name, state):
    """Unpickle a decorated function."""
    func = None

    func_code = state.pop(name + '.__code__', None)
    func_globals = {key: unpickle_module(val) for key, val in state.pop(name + '.__globals__', {}).items()}
    func_self = state.pop(name + '.__self__', None)
    if func_code:
        code = marshal.loads(func_code)
        func = types.FunctionType(code, func_globals)
        if func_self:
            func = types.MethodType(func, func_self)

    return func


class MpSignalManager(threading.Thread):
    QUEUE_TIMEOUT = 2

    def __init__(self):
        super(MpSignalManager, self).__init__()

        if not hasattr(self, '_started'):
            self._started = threading.Event()

        # Event to keep the thread alive.
        self.alive = threading.Event()

    def start(self):
        """Start the thread as a non-daemon thread so join is called and can be closed properly."""
        if not self._started.is_set():
            self.daemon = False
            super(MpSignalManager, self).start()
            self._started.set()

    def is_running(self):
        try:
            return self.alive.is_set()
        except AttributeError:
            return False

    def run(self):
        """Run the thread until the program stops."""
        self.alive.set()
        while self.alive.is_set():
            try:
                event = SignalEvent.QUEUE.get(timeout=self.QUEUE_TIMEOUT)
                try:
                    event.exec_()
                except Exception:
                    pass
            except(Empty):
                pass

    def close(self):
        """Close the thread properly."""
        self.alive.clear()

    def join(self, timeout=None):
        try:
            self.close()
        except:
            pass
        super(MpSignalManager, self).join(timeout)


class SignalEvent(object):
    """Event to be run later after being put in a queue."""

    SIGNALS = {}
    QUEUE = None
    MP_MANAGER = None  # Use a multiprocessing.Manager to create a queue that can be passed to another process
    DEFAULT_MANAGER = None  # Set this to anything but None to prevent automatic creation of a thread
    DEFAULT_MANAGER_CLASS = MpSignalManager  # Class(Thread) that will be created and started if DEFAULT_MANAGER is None

    @classmethod
    def multiprocessing_support(cls, queue=None, manager=None, consumer=None, consumer_class=None):
        """Create a consumer thread and make a queue to allow event_signal to work with multiprocessing.

        Args:
            queue (multiprocessing.Queue)[None]: Set a queue or automatically create one
            manager (multiprocessing.Manager)[None]: Manager to use to create the queue automatically.
            consumer (threading.Thread): Thread to consume items off of the signal queue
            consumer_class (class/object): Class to create a new consumer with.
        """
        # Set the Queue used for message passing
        if SignalEvent.QUEUE is None:
            if not queue:
                if not manager:
                    manager = SignalEvent.MP_MANAGER = multiprocessing.Manager()
                queue = manager.Queue()
            SignalEvent.QUEUE = queue

        # Set the thread queue consumer (DEFAULT_MANAGER)
        if SignalEvent.DEFAULT_MANAGER is None:
            if not consumer:
                if not consumer_class:
                    consumer_class = SignalEvent.DEFAULT_MANAGER_CLASS
                consumer = consumer_class()

            SignalEvent.DEFAULT_MANAGER = consumer
            try:
                SignalEvent.DEFAULT_MANAGER.start()
            except Exception:
                pass

    @classmethod
    def fire_signal(cls, name, sig, *args, **kwargs):
        """Add a task to fire a signal in the main process.

        Args:
            name (str)[None]: Name of the signal instance
            sig (str)[None]: Name of the signal in the signal instance to fire.
            *args (tuple): Signal arguments
            QUEUE (Queue)[None]: Queue to put the data on. None if you wan to use the default.
            **kwargs (dict): Signal keyword arguments
        """
        event = SignalEvent(name, sig, args, kwargs)
        SignalEvent.QUEUE.put(event)

    @classmethod
    def run_signal(cls, name, signal_type, *args, **kwargs):
        """Get the signal from the name and fire the signal.

        Args:
            name (str): Unique signal name that is registered.
            signal_type (str): Signal type.
            *args (tuple): Positional arguments to fire the signal with.
            **kwargs (dict): Keyword arguments to fire the signal with.
        """
        # Get the registered signal
        sig_inst = cls.get_signal(name)

        # Check if a valid signal was found
        if sig_inst is not None and signal_type is not None:
            # Fire the signal
            sig_inst.fire(signal_type, *args, **kwargs)

    @classmethod
    def register_signal(cls, name, signal_inst):
        """Register a signaler instance.

        Args:
            name (str): Name to register the signaler instance with.
            signal_inst (event_signal.SignalerInstance/Signaler/Signal): Signaler instance to register
        """
        if name not in SignalEvent.SIGNALS:
            SignalEvent.SIGNALS[name] = signal_inst

    @classmethod
    def get_signal(cls, name):
        """Return the signal instance associated with the given name."""
        return SignalEvent.SIGNALS.get(name, None)

    @classmethod
    def remove_signal(cls, name):
        try:
            del SignalEvent.SIGNALS[name]
        except KeyError:
            pass

    def __init__(self, name, signal_type=None, args=None, kwargs=None):
        if isinstance(name, (list, tuple)):
            name, signal_type, args, kwargs = name
        self.name = name
        self.signal_type = signal_type
        self.args = args or tuple()
        self.kwargs = kwargs or {}

        self.results = None
        self.error = None

    def run(self):
        """Run the actual command that was given and return the results"""
        return self.run_signal(self.name, self.signal_type, *self.args, **self.kwargs)

    def exec_(self):
        """Get the command and run it"""
        self.results = None
        self.error = None

        try:
            self.results = self.run()
        except Exception as err:
            self.error = err


multiprocessing_support = SignalEvent.multiprocessing_support
