"""
Create an observable property. Observable properties allow users to set multiple callback functions to be called
before a value is changed with "before_change", after a value is changed with "change", before a property is deleted
with "before_delete", and after a property is deleted with "delete".

Example:
    .. code-block:: python

        class Point:
            def __init__(self, x=0, y=0):
                self._x = x
                self._y = y

            @observe_property
            def x(self):
                return self._x

            @x.setter
            def x(self, x):
                self._x = x

            @x.deleter
            def x(self):
                del self._x

            @observe_property
            def y(self):
                return self._y

            @y.setter
            def y(self, y):
                self._y = y

            @y.deleter
            def y(self):
                del self._y

            @x.on("before_change")
            @y.on("before_change")
            def moving(self, *args):
                print("Moving")

            @x.on("change")
            @y.on("change")
            def moving(self, *args):
                print("Moved point", repr(self))

            @x.on("before_delete")
            @y.on("before_delete")
            def deleting(self)
                print("Deleting value")

            @x.on("before_delete")
            @y.on("before_delete")
            def deleted(self)
                print("Deleted value")

            def __repr__(self):
                return self.__class__.__name__ + "(%d, %d)" % (self.x, self.y)


        p = Point() # instance of a class
        p.x = 1
        # Moving
        # Moved point Point(1, 0)
        p.y = 2
        # Moving
        # Moved point Point(1, 2)

        del p.x
        # Deleting value
        # Deleted value

        Point.x.on(p, "change", lambda value: print("Changing p's x value to ", repr(value)))  # Instance specific callback
        p.x = 2
        # Moving
        # Moved point Point(2, 2)
        # Changing p's x value to 2

        Point.x.off(p, "change")  # Remove all callbacks from change

"""
from .signal_funcs import get_signal, on_signal, off_signal, fire_signal
from .signaler_inst import SignalerInstance


__all__ = ["signaler_property"]


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


class SignalerPropertyInstance(SignalerInstance):
    """Replaces a property with this class that uses callback functions for before and after a value changes.

    Signals (Callbacks):

        * 'before_delete' - function should take no arguments
        * 'delete' - function should take no arguments
        * 'before_change' - function should take a single value argument
        * 'change' - function should take a single value argument
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, check_change=True):
        """Initialize like a property

        Args:
            fget (function/method)[None]: Getter method for the property
            fset (function/method)[None]: Setter method for the property
            fdel (function/method)[None]: Deleter method for the property
            doc (str)[None]: Documentation for the property
            check_change (bool)[True]: If True before the setter is called check if the value is different (uses getter)
        """
        super(SignalerPropertyInstance, self).__init__()

        self.check_change = check_change
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

        self.event_signals["before_delete"] = []
        self.event_signals["delete"] = []
        self.event_signals["before_change"] = []
        self.event_signals["change"] = []

    # ===== Property methods =====
    def get_value(self):
        """Return the property value with the getter function."""
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget()

    def set_value(self, value):
        """Set the property value with the setter function."""
        if self.fset is None:
            raise AttributeError("can't set attribute")

        # Check if the new value is different from the current value
        if self.check_change and self.fget:
            val = self.get_value()
            if val == value:
                return

        # Set the value
        self.fire("before_change", value)
        ret = self.fset(value)

        # Get the new value from the getter if possible
        new_val = value
        if self.fget:
            new_val = self.get_value()
        self.fire("change", new_val)

        return ret  # None usually

    def del_value(self):
        """Delete the property value with the deleter function."""
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fire("before_delete")
        ret = self.fdel()
        self.fire("delete")
        return ret  # None usually


class signaler_property(property, SignalerInstance):
    """Property that is observable through callback functions.

    Add a callback to function to be called when a before a property changes or after a property changes. Callbacks
    can be added for 'before_change', 'change', 'before_delete', and 'delete'.

    Signals (Callbacks):

        * 'before_delete' - function should take no arguments
        * 'delete' - function should take no arguments
        * 'before_change' - function should take a single value argument
        * 'change' - function should take a single value argument

    Exammple:

        .. code-block:: python

            class MyClass:
                # Just like a normal property
                @signaler_property
                def x(self):
                    return self._x

                @x.setter
                def x(self, value):
                    self._x = value

                @x.deleter
                def x(self):
                    del self._x

                # Connect callback methods to observe what happens to the property
                @x.on("before_change")
                def about_to_change_x(self, *args):
                    print("x is about to change")

                @x.on("change")
                def x_changed(self, value):
                    print("x changed")

                @x.on("before_delete")
                def x_about_to_be_deleted(self):
                    print("x is going to go away now")

                @x.on("delete")
                def x_deleted(self)
                    print("x has been removed")

            m = MyClass()
            m.x = 1
            def print_value(value):
                print("x changed to", value)
            MyClass.x.on("change", print_value)
            m.x = 2
            print(m.x)
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, check_change=True):
        """Initialize like a property

        Args:
            fget (function/method)[None]: Getter method for the property
            fset (function/method)[None]: Setter method for the property
            fdel (function/method)[None]: Deleter method for the property
            doc (str)[None]: Documentation for the property
            check_change (bool)[True]: If True before the setter is called check if the value is different (uses getter)
        """
        super(signaler_property, self).__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)
        self.event_signals = {"before_delete": [], "delete": [], "before_change": [], "change": []}
        self.check_change = check_change

        try:
            self.__name__ = self.fget.__name__
        except AttributeError:
            pass
    # end Constructor

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
            fget = None
            fset = None
            fdel = None
            doc = self.__doc__

            # Bind the get, set, and del methods with the given instance before creating the observable property
            if self.fget:
                fget = self.fget.__get__(instance, instance.__class__)
            if self.fset:
                fset = self.fset.__get__(instance, instance.__class__)
            if self.fdel:
                fdel = self.fdel.__get__(instance, instance.__class__)

            # Create the new signaler for the instance with bound methods.
            sig = SignalerPropertyInstance(fget=fget, fset=fset, fdel=fdel, doc=doc, check_change=self.check_change)
            instance.__signalers__[self] = sig

            # Map all of the connected callbacks as bound methods to the instance
            copy_signals_as_bound(self, sig, instance)

        return instance.__signalers__[self]  # return an event handler object for the instance
    # end get_callback_manager

    # ========== class decorator ==========
    def __set__(self, instance, obj):
        """Class decorator that is called for `obj.x = 1`."""
        sig = self.get_signaler_instance(instance)
        return sig.set_value(obj)
    # end __set__

    def __get__(self, *args, **kwargs):
        """Class decorator that is called for `print(obj.x)`."""
        if len(args) == 0 or args[0] is None:
            return self
        instance = args[0]
        sig = self.get_signaler_instance(instance)
        return sig.get_value()
    # end __get__

    def __delete__(self, instance):
        """Class decorator that is called for `del obj.x`."""
        sig = self.get_signaler_instance(instance)
        return sig.del_value()

    # ===== Decorators =====
    def getter(self, fget):
        """Decorator to add a getter method. Works just like @property.getter."""
        obj = super(signaler_property, self).getter(fget)
        obj.check_change = self.check_change
        copy_signals(self, obj)
        try:
            obj.__name__ = obj.fget.__name__
        except AttributeError:
            pass
        return obj

    def setter(self, fset):
        """Decorator to add a setter method. Works just like @property.setter."""
        obj = super(signaler_property, self).setter(fset)
        obj.check_change = self.check_change
        copy_signals(self, obj)
        return obj

    def deleter(self, fdel):
        """Decorator to add a deleter method. Works just like @property.deleter."""
        obj = super(signaler_property, self).deleter(fdel)
        obj.check_change = self.check_change
        copy_signals(self, obj)
        return obj

    # ========== Connect Callback functions ==========
    def get_signal(self, instance, signal_type=None):
        """Return a list of callback methods.

        Options:

            If user gives 'signal_type' and (optional) 'func' arguments.

            .. code-block:: python

                class MyClass:
                    @signaler_property
                    def x(self):
                        return self._x

                    @x.setter
                    def x(self, value):
                        self._x = value

                    @x.on("before_change")
                    def about_to_change_x(*args):
                        print("x is about to change")

                print(MyClass.x.get_signal("before_change"))

            If user gives 'instance', 'signal_type', and (optional) 'func' arguments.

            .. code-block:: python

                class MyClass:
                    @signaler_property
                    def x(self):
                        return self._x

                    @x.setter
                    def x(self, value):
                        self._x = value

                    @x.on("before_change")
                    def about_to_change_x(*args):
                        print("x is about to change")

                obj = MyClass()
                print(MyClass.x.get_signal(obj, "before_change"))

        Args:
            signal_type (str): Signal name to direct which signal to use

        Args Alternative:
            instance (object): Object to connec the signal with.
            signal_type (str): Signal name to direct which signal to use
        """
        if signal_type is None:
            signal_type = instance
            instance = None

        if not isinstance(signal_type, str):
            raise TypeError("Invalid 'signal type' given.")

        if instance is None:
            instance = self

        return get_signal(instance, signal_type)

    def on(self, *args):
        """Connect callback methods.

        Options:

            If user gives 'signal_type' and (optional) 'func' arguments.

            .. code-block:: python

                class MyClass:
                    @signaler_property
                    def x(self):
                        return self._x

                    @x.setter
                    def x(self, value):
                        self._x = value

                    @x.on("before_change")
                    def about_to_change_x(*args):
                        print("x is about to change")

            If user gives 'instance', 'signal_type', and (optional) 'func' arguments.

            .. code-block:: python

                class MyClass:
                    @signaler_property
                    def x(self):
                        return self._x

                    @x.setter
                    def x(self, value):
                        self._x = value

                obj = MyClass()
                MyClass.x.on(obj, "before_change", lambda *args: print("x is about to change"))

        Args:
            signal_type (str): Signal name to direct which signal to use
            func (callable): Callback function

        Args Alternative:
            instance (object): Object to connec the signal with.
            signal_type (str): Signal name to direct which signal to use
            func (callable): Callback function
        """
        length = len(args)
        if length > 3 or length == 0:
            raise ValueError("Invalid number of arguments given! Give either 'instance', 'signal_type', and 'function' "
                             "or just a 'signal_type' and 'function'.\n"
                             "The 'function argument is optional if you are using this as a function decorator.'")

        first = args[0]
        if length != 3 and isinstance(first, str) and not hasattr(first, "__signalers__"):
            # Method decorator
            return self._on_method_decorator(first, *args[1:])
        else:
            return self._on_instance(first, *args[1:])

    def _on_method_decorator(self, signal_type, func=None):
        """Connect the signal with the given callback function."""
        if func is None:
            def wrapper(func):
                self.on(signal_type, func)
                return func
            return wrapper

        on_signal(self, signal_type, func)
        return func

    def _on_instance(self, instance, signal_type, func=None):
        """Connect the signal with the given callback function for the instance."""
        callback = self.get_signaler_instance(instance)
        if func is None:
            def wrapper(func):
                callback.on(signal_type, func)
                return func
            return wrapper

        return callback.on(signal_type, func)

    def off(self, *args):
        """Disconnect from a signal.

        Options:

            If user gives 'signal_type' and (optional) 'func' arguments.

            .. code-block:: python

                class MyClass:
                    @signaler_property
                    def x(self):
                        return self._x

                    @x.setter
                    def x(self, value):
                        self._x = value

                    @x.on("before_change")
                    def notify_x_about_to_change(value):
                        print("x is about to change to ", value)

                    x.off("before_change", notify_x_about_to_change)   # Disconnect the callback method

            If user give 'instance', 'signal_type', and (optional) 'func' arguments.

            .. code-block:: python

                class MyClass:
                    @signaler_property
                    def x(self):
                        return self._x

                    @x.setter
                    def x(self, value):
                        self._x = value

                    @x.on("before_change")
                    def notify_x_about_to_change(value):
                        print("x is about to change to ", value)

                obj = MyClass()
                MyClass.x.off(obj, "before_change", obj.notify_x_about_to_change)

        Args:
            signal_type (str): Signal name to direct which signal to use
            func (callable)[None]: Callback function

        Args Alternative:
            instance (object): Object to connect the signal with.
            signal_type (str): Signal name to direct which signal to use
            func (callable)[None]: Callback function
        """
        length = len(args)
        if length > 3 or length == 0:
            raise ValueError("Invalid number of arguments given! Give either 'instance', 'signal_type', and 'function' "
                             "or just a 'signal_type' and 'function'.\n"
                             "The 'function argument is optional if you are using this as a function decorator.'")

        first = args[0]
        if length != 3 and isinstance(first, str) and not hasattr(first, "__signalers__"):
            # Method decorator
            return self._off_method_decorator(first, *args[1:])
        else:
            return self._off_instance(first, *args[1:])

    def _off_method_decorator(self, signal_type, func=None):
        """Disconnect the signal from the given callback function (or all if None was given)."""
        off_signal(self, signal_type, func)
        return func

    def _off_instance(self, instance, signal_type, func=None):
        """Disconnect the signal from the given callback function (or all if None was given) for the instance."""
        callback = self.get_signaler_instance(instance)
        return callback.off(signal_type, func)

    def fire(self, *args, **kwargs):
        """Trigger the callback functions connected to the signal.

        Args:
            instance (object): Object to connect the signal with.
            signal_type (str): Signal name to direct which signal to use
            *args, **kwargs: Callback function arguments

        Args Alternative:
            signal_type (str): Signal name to direct which signal to use
            *args, **kwargs: Callback function arguments
        """
        length = len(args)
        if length == 0:
            raise ValueError("Invalid number of arguments given! Give either 'instance', 'signal_type', and '*args' "
                             "or just a 'signal_type' and '*args'.")

        instance = args[0]
        if isinstance(instance, str):
            signal_type = instance
            instance = self
            args = args[1:]
        elif len(args) > 1:
            instance = self.get_signaler_instance(instance)
            signal_type = args[1]
            args = args[2:]
        else:
            raise ValueError("Invalid number of arguments given! Give either 'instance', 'signal_type', and '*args' "
                             "or just a 'signal_type' and '*args'.")

        return fire_signal(instance, signal_type, *args, **kwargs)
