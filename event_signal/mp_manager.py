"""Multiprocessing manager.

This works by saving a signal with a name. The other process should queue the signal name, signal to be fired,
arguments, and keyword arguments. A thread is spawned in the main process to read this queue and fire the real signal.
"""
import marshal
import types
import importlib

import threading
import multiprocessing


__all__ = ['pickle_module', 'unpickle_module', 'pickle_function', 'unpickle_function', 'MpSignalManager']


def pickle_module(value):
    """Pickle a module."""
    if isinstance(value, types.ModuleType):
        return '{}{};{}{}'.format('__module__.', value.__name__, '__package__.', value.__package__)
    return value


def unpickle_module(value):
    """Pickle a module."""
    if isinstance(value, str) and value.startswith('__module__.'):
        name, package = value.replace('__module__.', '').replace('__package__.', '').split(';')
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


class ClosableThread(threading.Thread):
    def __init__(self, target=None, name=None, args=None, kwargs=None, daemon=None):
        args = args or tuple()
        kwargs = kwargs or {}
        super(ClosableThread, self).__init__(target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)

        # Should be created by __init__ (parent method).
        if not hasattr(self, '_args'):
            self._args = args
        if not hasattr(self, '_kwargs'):
            self._kwargs = kwargs.copy()
        if not hasattr(self, '_started'):
            self._started = threading.Event()

    def start(self):
        """Start the thread as a non-daemon thread so join is called and can be closed properly."""
        if not self._started.is_set():
            self.daemon = False
            super(ClosableThread, self).start()
            self._started.set()

    def join(self, timeout=None):
        try:
            self.close()
        except:
            pass
        super(ClosableThread, self).join(timeout)

    def close(self):
        """Override to close a thread properly."""
        pass


class MpSignalManager(object):
    QUEUE = multiprocessing.Queue()
    SIGNALS = {}
    DEFAULT_MANAGER = None

    @classmethod
    def fire_signal(cls, name, sig, *args, **kwargs):
        """Add a task to fire a signal in the main process.

        Args:
            name (str)[None]: Name of the signal instance
            sig (str)[None]: Name of the signal in the signal instance to fire.
            *args (tuple): Signal arguments
            **kwargs (dict): Signal keyword arguments
        """
        cls.QUEUE.put([name, sig, args, kwargs])

    @classmethod
    def register_signal(cls, name, signal_inst):
        """Register a signaler instance.

        Args:
            name (str): Name to register the signaler instance with.
            signal_inst (event_signal.SignalerInstance/Signaler/Signal): Signaler instance to register
        """
        if name not in cls.SIGNALS:
            cls.SIGNALS[name] = signal_inst

    @classmethod
    def get_signal(cls, name):
        """Return the signal instance associated with the given name."""
        return cls.SIGNALS.get(name, None)

    @classmethod
    def remove_signal(cls, name):
        try:
            del cls.SIGNALS[name]
        except KeyError:
            pass

    def __init__(self):
        # Thread to process events from the other process
        self.alive = threading.Event()
        self.thread = ClosableThread(target=self.run)
        self.thread.close = self.close

    def is_running(self):
        try:
            return self.alive.is_set()
        except AttributeError:
            return False

    def start(self):
        self.thread.start()

    def run(self):
        """Run the thread until the program stops."""
        self.alive.set()
        while self.alive.is_set():
            name, sig, args, kwargs = MpSignalManager.QUEUE.get()
            sig_inst = self.get_signal(name)

            # Check if a valid signal was found
            if sig_inst is not None and sig is not None:
                # Fire the signal
                sig_inst.fire(sig, *args, **kwargs)

    def close(self):
        """Close the thread properly."""
        self.alive.clear()
        self.fire_signal(None, None)  # Pump the queue

    def __getstate__(self):
        """Return the pickling state."""
        return {}

    def __setstate__(self, state):
        # Set the variables
        self.alive = None
        self.thread = None
