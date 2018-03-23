from .signal_funcs import get_signal, on_signal, off_signal, fire_signal, block_signals


__all__ = ["SignalerInstance"]


class SignalerInstance(object):
    """Emulates a function that has signals. This class is returned when signaler is used as a decorator."""

    def __init__(self):
        self.event_signals = {}

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
        return fire_signal(self, signal_type, *args, **kwargs)

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
