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
from .signal_funcs import get_signal, on_signal, off_signal, emit_signal


__all__ = ["signaler_property"]


class signaler_property(property):
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
    SIGNALS = ["before_delete", "delete", "before_change", "change"]

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, check_change=True):
        """Initialize like a property

        Args:
            fget (function/method)[None]: Getter method for the property
            fset (function/method)[None]: Setter method for the property
            fdel (function/method)[None]: Deleter method for the property
            doc (str)[None]: Documentation for the property
            check_change (bool)[True]: If True before the setter is called check if the value is different (uses getter)
        """
        self._before_delete_funcs = []
        self._delete_funcs = []
        self._before_change_funcs = []
        self._change_funcs = []

        self.check_change = check_change

        super(signaler_property, self).__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)
        try:
            self.__name__ = self.fget.__name__
        except AttributeError:
            pass
    # end Constructor

    def get_callback_manager(self, instance=None):
        """Return (maybe create) the instance ObservableCallbackManager.

        Args:
            instance (object)[None]: Instance object that has observables.
        """
        if instance is None:
            instance = self
        if not hasattr(instance, "__observables__"):
            instance.__observables__ = {}
        if self not in instance.__observables__:
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
            instance.__observables__[self] = ObservableCallbackManager(fget=fget, fset=fset, fdel=fdel,
                                                                doc=doc, check_change=self.check_change)
            instance.__observables__[self]._before_delete_funcs = [func.__get__(instance, instance.__class__)
                                                                for func in self._before_delete_funcs]
            instance.__observables__[self]._delete_funcs = [func.__get__(instance, instance.__class__)
                                                            for func in self._delete_funcs]
            instance.__observables__[self]._before_change_funcs = [func.__get__(instance, instance.__class__)
                                                                for func in self._before_change_funcs]
            instance.__observables__[self]._change_funcs = [func.__get__(instance, instance.__class__)
                                                            for func in self._change_funcs]

        return instance.__observables__[self]  # return an event handler object for the instance
    # end get_callback_manager

    # ========== class decorator ==========
    def __set__(self, instance, obj):
        """Class decorator that is called for `obj.x = 1`."""
        observ = self.get_callback_manager(instance)
        return observ.set_value(obj)
    # end __set__

    def __get__(self, *args, **kwargs):
        """Class decorator that is called for `print(obj.x)`."""
        if len(args) == 0 or args[0] is None:
            return self
        instance = args[0]
        observ = self.get_callback_manager(instance)
        return observ.get_value()
    # end __get__

    def __delete__(self, instance):
        """Class decorator that is called for `del obj.x`."""
        observ = self.get_callback_manager(instance)
        return observ.del_value()

    # ===== Decorators =====
    def getter(self, fget):
        """Decorator to add a getter method. Works just like @property.getter."""
        obj = super(signaler_property, self).getter(fget)
        obj._before_delete_funcs = self._before_delete_funcs
        obj._delete_funcs = self._delete_funcs
        obj._before_change_funcs = self._before_change_funcs
        obj._change_funcs = self._change_funcs
        obj.check_change = self.check_change
        try:
            obj.__name__ = obj.fget.__name__
        except AttributeError:
            pass
        return obj

    def setter(self, fset):
        """Decorator to add a setter method. Works just like @property.setter."""
        obj = super(signaler_property, self).setter(fset)
        obj._before_delete_funcs = self._before_delete_funcs
        obj._delete_funcs = self._delete_funcs
        obj._before_change_funcs = self._before_change_funcs
        obj._change_funcs = self._change_funcs
        obj.check_change = self.check_change
        return obj

    def deleter(self, fdel):
        """Decorator to add a deleter method. Works just like @property.deleter."""
        obj = super(signaler_property, self).deleter(fdel)
        obj._before_delete_funcs = self._before_delete_funcs
        obj._delete_funcs = self._delete_funcs
        obj._before_change_funcs = self._before_change_funcs
        obj._change_funcs = self._change_funcs
        obj.check_change = self.check_change
        return obj

    # ========== Connect Callback functions ==========
    def get(self, instance, signal_type=None):
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

                print(MyClass.x.get("before_change"))

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
                print(MyClass.x.get(obj, "before_change"))

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
        if length != 3 and isinstance(first, str) and not hasattr(first, "__observables__"):
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
        callback = self.get_callback_manager(instance)
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
        if length != 3 and isinstance(first, str) and not hasattr(first, "__observables__"):
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
        callback = self.get_callback_manager(instance)
        return callback.off(signal_type, func)

    # ===== Pre Delete =====
    def connect_before_delete(self, func):
        """Connect a callback function to the before_delete signal."""
        if func not in self._before_delete_funcs:
            self._before_delete_funcs.append(func)

    def disconnect_before_delete(self, func=None):
        """Disconnect from the before_delete signal.

        Args:
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        if func is None:
            self._before_delete_funcs = []
        else:
            try:
                self._before_delete_funcs.remove(func)
            except:
                pass

    # ===== Delete =====
    def connect_delete(self, func):
        """Connect a callback function to the delete signal."""
        if func not in self._delete_funcs:
            self._delete_funcs.append(func)

    def disconnect_delete(self, func=None):
        """Disconnect from the delete signal.

        Args:
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        if func is None:
            self._delete_funcs = []
        else:
            try:
                self._delete_funcs.remove(func)
            except:
                pass

    # ===== Pre Change =====
    def connect_before_change(self, func):
        """Connect a callback function to the before_change signal."""
        if func not in self._before_change_funcs:
            self._before_change_funcs.append(func)

    def disconnect_before_change(self, func=None):
        """Disconnect from the before_change signal.

        Args:
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        if func is None:
            self._before_change_funcs = []
        else:
            try:
                self._before_change_funcs.remove(func)
            except:
                pass

    # ===== Normal Post Change signal =====
    def connect_change(self, func):
        """Connect a callback function to the change signal."""
        if func not in self._change_funcs:
            self._change_funcs.append(func)

    def disconnect_change(self, func=None):
        """Disconnect from the change signal.

        Args:
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        if func is None:
            self._change_funcs = []
        else:
            try:
                self._change_funcs.remove(func)
            except:
                pass

    connect = connect_change
    disconnect = disconnect_change


class ObservableCallbackManager(object):
    """Replaces a property with this class that uses callback functions for before and after a value changes.

    Signals (Callbacks):

        * 'before_delete' - function should take no arguments
        * 'delete' - function should take no arguments
        * 'before_change' - function should take a single value argument
        * 'change' - function should take a single value argument
    """
    SIGNALS = ["before_delete", "delete", "before_change", "change"]

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, check_change=True):
        """Initialize like a property

        Args:
            fget (function/method)[None]: Getter method for the property
            fset (function/method)[None]: Setter method for the property
            fdel (function/method)[None]: Deleter method for the property
            doc (str)[None]: Documentation for the property
            check_change (bool)[True]: If True before the setter is called check if the value is different (uses getter)
        """
        self.check_change = check_change
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

        self._before_delete_funcs = []
        self._delete_funcs = []
        self._before_change_funcs = []
        self._change_funcs = []

        super(ObservableCallbackManager, self).__init__()

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
        self.emit_before_change(value)
        ret = self.fset(value)

        # Get the new value from the getter if possible
        new_val = value
        if self.fget:
            new_val = self.get_value()
        self.emit_change(new_val)

        return ret  # None usually

    def del_value(self):
        """Delete the property value with the deleter function."""
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.emit_before_delete()
        ret = self.fdel()
        self.emit_delete()
        return ret  # None usually

    # ========== Connect Callback functions ==========
    def get(self, signal_type):
        """Return the callback methods for the given signal_type."""
        return get_signal(self, signal_type)

    def on(self, signal_type, func):
        """Connect a callback function to a signal.

        Args:
            signal_type(str): Name of the signal. "before_delete", "delete", "before_change", or "change"
            func (function/method): Callback function or method to connect to the signal.
        """
        on_signal(self, signal_type, func)

    def off(self, signal_type, func=None):
        """Disconnect a callback function from a signal.

        Args:
            signal_type(str): Name of the signal. "before_delete", "delete", "before_change", or "change"
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        off_signal(self, signal_type, func)

    def fire(self, signal_type, *args, **kwargs):
        """Trigger the signal, calling all callback functions for a signal.

        Args:
            signal_type(str): Name of the signal. "before_delete", "delete", "before_change", or "change"
            *args (tuple): Arguments to pass to all callback functions.
            **kwargs(dict): Named arguments to pass to all callback functions
        """
        emit_signal(self, signal_type, *args, **kwargs)

    # ===== Pre Delete =====
    def connect_before_delete(self, func):
        """Connect a callback function to the before_delete signal."""
        if func not in self._before_delete_funcs:
            self._before_delete_funcs.append(func)

    def disconnect_before_delete(self, func=None):
        """Disconnect from the before_delete signal.

        Args:
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        if func is None:
            self._before_delete_funcs = []
        else:
            try:
                self._before_delete_funcs.remove(func)
            except:
                pass

    def emit_before_delete(self):
        """Trigger the before_delete signal, calling all callback functions for a signal.

        Args:
            *args (tuple): Arguments to pass to all callback functions.
            **kwargs(dict): Named arguments to pass to all callback functions
        """
        for func in self._before_delete_funcs:
            func()

    # ===== Delete =====
    def connect_delete(self, func):
        """Connect a callback function to the delete signal."""
        if func not in self._delete_funcs:
            self._delete_funcs.append(func)

    def disconnect_delete(self, func=None):
        """Disconnect from the delete signal.

        Args:
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        if func is None:
            self._delete_funcs = []
        else:
            try:
                self._delete_funcs.remove(func)
            except:
                pass

    def emit_delete(self):
        """Trigger the delete signal, calling all callback functions for a signal.

        Args:
            *args (tuple): Arguments to pass to all callback functions.
            **kwargs(dict): Named arguments to pass to all callback functions
        """
        for func in self._delete_funcs:
            func()

    # ===== Pre Change =====
    def connect_before_change(self, func):
        """Connect a callback function to the before_change signal."""
        if func not in self._before_change_funcs:
            self._before_change_funcs.append(func)

    def disconnect_before_change(self, func=None):
        """Disconnect from the before_change signal.

        Args:
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        if func is None:
            self._before_change_funcs = []
        else:
            try:
                self._before_change_funcs.remove(func)
            except:
                pass

    def emit_before_change(self, value):
        """Trigger the before_change signal, calling all callback functions for a signal.

        Args:
            *args (tuple): Arguments to pass to all callback functions.
            **kwargs(dict): Named arguments to pass to all callback functions
        """
        for func in self._before_change_funcs:
            func(value)

    # ===== Normal Post Change signal =====
    def connect_change(self, func):
        """Connect a callback function to the change signal."""
        if func not in self._change_funcs:
            self._change_funcs.append(func)

    def disconnect_change(self, func=None):
        """Disconnect from the change signal.

        Args:
            func (function/method)[None]: Callback function or method to disconnect from the signal.
                None removes all callback functions.
        """
        if func is None:
            self._change_funcs = []
        else:
            try:
                self._change_funcs.remove(func)
            except:
                pass

    def emit_change(self, value):
        """Trigger the change signal, calling all callback functions for a signal.

        Args:
            *args (tuple): Arguments to pass to all callback functions.
            **kwargs(dict): Named arguments to pass to all callback functions
        """
        for func in self._change_funcs:
            func(value)

    connect = connect_change
    disconnect = disconnect_change
    emit = emit_change
