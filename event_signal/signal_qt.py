"""
The event module was created to emulate Qt's Signal. It is very convenient to be able to have
multiple functions called from one function call. This class was made for that specific purpose.

The main difference between Qt's Signal and this class is that this class does not call the 
connected callback functions in the main thread. It calls all of the functions in the thread that
called the function (or used CallbackManager().emit()). If you are using this signal in a separate thread to update
a gui item it will fail with a pixmap error.

Example:

    .. code-block:: python

        >>> # ========== Using Signal as a class decorator (Recommended) ==========
        >>> class MyClass:
        >>>     something_happened = Signal(str)
        >>>
        >>>     def process(self):
        >>>         ...
        >>>         self.something_happened.emit("This happened!")
        >>>         # Or self.something_happened.emit("This happened!") # Like Qt except does not call in main thread.
        >>> 
        >>> m = MyClass()
        >>> m.something_happened.connect(print)
        >>> m.something_happened.connect(lambda msg: print("Hello", msg))
        >>> m.something_happened = lambda msg: print("Second method", msg)
        >>> m.process()
        "This happened!"
        "Hello This happened!"
        "Second method This happened!"
        
        >>> # ========== Using Signal as a function ==========
        >>> something_happened = Signal(str)
        >>> something_happened.connect(print)
        >>> something_happened.connect(lambda msg: print("Hello", msg))
        >>> # WARNING! '=' does not work! This will completely replace the something_happened Signal
        >>> # with the new variable
        >>> # something_happened = lambda msg: print("Second method", msg)
        >>> something_happened("This also happened!")
        >>> something_happened.emit("This happened!") # alias for __call__ to emulate Qt Signal
    
How it works:

    Signal is a class decorator that creates and manages CallbackManagers for every class instance.
    
    .. code-block:: python

        my_class = MyClass() # Creates the class instance
        my_class.something_happened  # Creates a CallbackManager for this instance
        my_class.something_happened = function  # Adds the function to the CallbackManager function list
    
    The line of code, `my_class.something_happened`, is a getter that calls the `__get__` method. The
    line of code, `my_class.something_happened = function`, is a setter that calls the `__set__`
    method. The `__get__` and `__set__` methods create a CallbackManager the first time it is called.
    Since Signal is a class decorator, it creates and manages the CallbackManagers for every class
    instance. The `__get__` and `__set__` methods use a CallbackManager instance for every MyClass instance.
    
    .. code-block:: python

        my_class.something_happened.connect(function)
    
    The above like of code first gets a CallbackManager with `my_class.something_happened`. The
    `.connect(function)` is calling the CallbackManager's 'connect' method.  
"""
from .interface import SignalerInstance, SignalerDescriptorInstance


__all__ = ["Signal"]


class CallbackManager(SignalerInstance):
    """The CallbackManager class holds a collection of callback functions. The callback functions are
    called when an emit is called. This class does not need to be used directly, use Signal instead.
    """

    def __init__(self, *args, **kwargs):
        super(CallbackManager, self).__init__()
        self._mp_variables.extend(['args', 'kwargs'])

        self.event_signals["change"] = []
        self.args = args
        self.kwargs = kwargs
    # enc Constructor

    def connect(self, func):
        """Add a callback function to be called when an event happens."""
        return self.on("change", func)
    # end connect

    def disconnect(self, func=None):
        """Disconnect a callback function or all callback functions if None is given."""
        return self.off("change", func)
    # end disconnect

    def block(self, signal_type="change", block=True):
        """Temporarily block the signal from calling the callback methods.

        Args:
            signal_type (str)[None]: Signal name to direct which signal to use or None for all signals
            block (bool)[True]: Block or unblock the signals

        Args Alternative:
            signal_type (bool)[True]: If a bool is given it sets the block argument and the signal_type is assumed
                to be the default "change" signal.
        """
        if signal_type is True or signal_type is False:
            block = signal_type
            signal_type = "change"
        return super(CallbackManager, self).block(signal_type=signal_type, block=block)

    def block_signal(self, block=True):
        """Temporarily block the signal from calling the callback methods.

        Args:
            block (bool)[True]: Block or unblock the signals
        """
        return super(CallbackManager, self).block(signal_type="change", block=block)

    def check_arguments(self, *args, **kwargs):
        """Check the given arguments. DEPRECATED! Found this to be more of a hindrance."""
        for i, arg in enumerate(self.args):
            try:
                given = args[i]
                msg = None
            except IndexError:
                msg = " ".join(("Missing", str(len(self.args)-i), "required positional argument."))
            if msg:
                # Not in exception because of python raising a double exception
                raise TypeError(msg)

            if not isinstance(given, arg):
                raise TypeError("Positional argument "+ repr(i) + " should be of type "+ str(arg))

        for key, value in self.kwargs.items():
            if key not in kwargs:
                kwargs[key] = value

        return args, kwargs
    # end check_arguments
        
    def emit(self, *args, **kwargs):
        """Trigger the event (Call all of the CallbackManager's functions)."""
        return self.fire("change", *args, **kwargs)
    # end emit

    def __call__(self, *args, **kwargs):
        """Trigger the event (Call all of the CallbackManager's functions)."""
        return self.fire("change", *args, **kwargs)
    # end __call__
# end class CallbackManager


class Signal(SignalerDescriptorInstance):
    """The Signal class is the connection between a class and having multiple callback functions.
    
    Example:
        .. code-block:: python
        
            # ========== Using Signal as a class decorator (Recommended) ==========
            class MyClass:
                something_happened = Signal(str)
                
            m = MyClass()
            m.something_happened.connect(print)
            m.something_happened.connect(lambda msg: print("Hello", msg))
            m.something_happened = lambda msg: print("Second method", msg)
            m.something_happened("This also happened!")
            m.something_happened.emit("This something_happened!") # alias for __call__ to emulate Qt Signal
            
            # ========== Using Signal as a function ==========
            something_happened = Signal(str)
    
            something_happened.connect(print)
            something_happened.connect(lambda msg: print("Hello", msg))
    
            # WARNING! '=' does not work! This will completely replace the something_happened Signal
            # with the new variable
            # something_happened = lambda msg: print("Second method", msg)  # This will replace something_happened!
    
            something_happened("This also happened!")
            something_happened.emit("This happened!") # alias for __call__ to emulate Qt Signal
    """

    # __signalers__ = {}  # Need an annoying class global variable for multiprocessing. I don't see any way around this

    def __init__(self, *args):
        super(Signal, self).__init__()
        self.args = args
        self._mp_variables.extend(['args'])
    # end Constructor

    def create_signaler_instance(self, instance=None):
        """Create and return a signaler instance."""
        sig = CallbackManager(*self.args)
        # sig.name = self.name
        return sig

    # ========== Using Signal as a class decorator (Recommended) ==========
    def __set__(self, instance, func):
        """Set decorator for a class.
        
        Example:

            .. code-block:: python
            
                class MyClass:
                    something_happened = Signal(str)
                    
                m = MyClass() # instance of a class
                m.something_happened = print
                #  '=' calls this `__set__` method which adds the given func to the instances
                # CallbackManager callback list 
        """
        cmngr = self.get_signaler_instance(instance)
        cmngr.connect(func)
    # end __set__

    def __get__(self, instance, owner):
        """Get decorator for a class.

        Example:
        
            .. code-block:: python

                class MyClass:
                    something_happened = Signal(str)
                    
                m = MyClass() # instance of a class
                m.something_happened # returns the instance's CallbackManager allowing
                # `m.something_happened()` and `m.something_happened.connect(function)` 
        """
        return self.get_signaler_instance(instance)
    # end __get__
    # ========== END Using Signal as a class decorator (Recommended) ==========

    # ========== Using Signal as a function ==========
    def connect(self, func):
        """Connect a function to this Signal instance."""
        cmngr = self.get_signaler_instance(self)
        return cmngr.connect(func)
    # end connect
    
    def disconnect(self, func):
        """Disconnect a function from this Signal instance."""
        cmngr = self.get_signaler_instance(self)
        return cmngr.disconnect(func)
    # end disconnect

    def block(self, block=True):
        """Temporarily block a signal from calling callback functions."""
        cmngr = self.get_signaler_instance(self)
        return cmngr.block(block=block)
    
    def emit(self, *args, **kwargs):
        """Emit and call this Signal instance event handler functions."""
        return self.__call__(*args, **kwargs)
    # end emit
    
    def __call__(self, *args, **kwargs):
        """Emit and call this Signal instance event handler functions."""
        cmngr = self.get_signaler_instance(self)
        return cmngr(*args, **kwargs)
    # end __call__
    # ========== END Using Signal as a Function ==========
# end class Signal
