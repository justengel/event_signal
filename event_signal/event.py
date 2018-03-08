"""
event
SeaLandAire Technologies
@author: jengel

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


__all__ = ["Signal", "signal_change"]


class CallbackManager:
    """The CallbackManager class holds a collection of callback functions. The callback functions are
    called when an emit is called. This class does not need to be used directly, use Signal instead.
    """

    def __init__(self, *args, **kwargs):
        self.event_signals = {"change": []}
        self.args = args
        self.kwargs = kwargs
    # enc Constructor

    def connect(self, func):
        """Add a callback function to be called when an event happens."""
        if func not in self.event_signals["change"]:
            self.event_signals["change"].append(func)
    # end connect

    def disconnect(self, func=None):
        """Disconnect a callback function or all callback functions if None is given."""
        if func is None:
            self.event_signals["change"] = []
        else:
            try:
                self.event_signals["change"].remove(func)
            except:
                pass
    # end disconnect

    def check_arguments(self, *args, **kwargs):
        """Check the given arguments. DEPRECATED!"""
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
        self.__call__(*args, **kwargs)
    # end emit

    def __call__(self, *args, **kwargs):
        """Trigger the event (Call all of the CallbackManager's functions)."""
        # self.check_arguments(*args, **kwargs)
        for func in self.event_signals["change"]:
            func(*args, **kwargs)
    # end __call__
# end class CallbackManager


class Signal:
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
    def __init__(self, *args):
        self.args = args
        self.__signals__ = {}
    # end Constructor

    def get_callbackmanager(self, instance=None):
        """Return (maybe create) the instance CallbackManager."""
        if instance is None:
            instance = self
        if not hasattr(instance, "__signals__"):
            instance.__signals__ = {}
        if self not in instance.__signals__:
            instance.__signals__[self] = CallbackManager(*self.args)
        return instance.__signals__[self]  # return an event handler object for the instance
    # end get_callbackmanager

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
        cmngr = self.get_callbackmanager(instance)
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
        return self.get_callbackmanager(instance)
    # end __get__
    # ========== END Using Signal as a class decorator (Recommended) ==========

    # ========== Using Signal as a function ==========
    def connect(self, func):
        """Connect a function to this Signal instance."""
        cmngr = self.get_callbackmanager(self)
        cmngr.connect(func)
    # end connect
    
    def disconnect(self, func):
        """Disconnect a function from this Signal instance."""
        cmngr = self.get_callbackmanager(self)
        cmngr.disconnect(func)
    # end disconnect
    
    def emit(self, *args, **kwargs):
        """Emit and call this Signal instance event handler functions."""
        self.__call__(*args, **kwargs)
    # end emit
    
    def __call__(self, *args, **kwargs):
        """Emit and call this Signal instance event handler functions."""
        cmngr = self.get_callbackmanager(self)
        cmngr(*args, **kwargs)
    # end __call__
    # ========== END Using Signal as a Function ==========
# end class Signal


class signal_change(Signal):
    """Decorator that signals when a function is called.

    Example:

            .. code-block:: python

                >>> class MyClass(object):
                >>>     def __init__(self, x=0):
                >>>         self._x = x
                >>>
                >>>     def get_x(self):
                >>>         return self._x
                >>>
                >>>     @signal_change
                >>>     def set_x(self, x):
                >>>         self._x = x
                >>>
                >>> m = MyClass(0)
                >>> m.set_x.connect(lambda: print(m.get_x()))
                >>> m.set_x(1)
    """
    def __init__(self, func):
        self.myfunc = func
        self.__doc__ = self.myfunc.__doc__
        super().__init__()

    def get_callbackmanager(self, instance=None):
        """Return (maybe create as well) the instance CallbackManager."""
        if instance is None:
            instance = self
        if not hasattr(instance, "__signals__"):
            instance.__signals__ = {}
        if self not in instance.__signals__:
            instance.__signals__[self] = CallbackManager(*self.args)
            instance.__signals__[self].connect(self.myfunc.__get__(instance, instance.__class__))  # Bounded method
        return instance.__signals__[self]  # return an event handler object for the instance
    # end get_callbackmanager


if __name__ == "__main__":
    class Test:
        mysig = Signal(str)

    t = Test()

    def hello_world(name="World"):
        print("Hello", name+"!")
#     t.mysig.connect(hello_world)
    t.mysig = hello_world
    t.mysig = lambda name="World": print("here", name)
    t.mysig.emit()
    t.mysig.emit("jack")
    t.mysig()

    print()
    print("Using Signal as a function")
    test_sig = Signal(str)
    test_sig.connect(hello_world)
    # test_sig = lambda name="World": print("here", name) # This does not work!
    test_sig.connect(lambda name="World": print("here", name))
    test_sig("hello")
    test_sig.emit("hi")

    # ========== Test SignalChange ==========
    class MyClass(object):
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        @signal_change
        def set_x(self, x):
            self._x = x

    m = MyClass(0)
    m.set_x.connect(print)  # Run after the normal set_x has been called.
    m.set_x.connect(lambda x: print("set_x called with a value of", repr(x)))
    m.set_x(1)
