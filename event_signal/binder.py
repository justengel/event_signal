# import threading
from .signaler_inst import SignalerInstance
from .signaler_prop import signaler_property
from .signaler import signaler


__all__ = ["is_property", "is_signaler_property", "get_signaler", "bind_signals", "unbind_signals", "bind", "unbind"]


GETTER_PREFIXES = ["get_", "get", "is_", "is", "has_", "has"]


def is_property(instance, property_name):
    """Return if the object has a class property of the given property_name."""
    try:
        return isinstance(getattr(instance.__class__, property_name), property)
    except (AttributeError, ValueError, TypeError):
        return False


def is_signaler_property(instance, property_name):
    """Return if the object has a class property of the given property_name."""
    try:
        return isinstance(getattr(instance.__class__, property_name), signaler_property)
    except (AttributeError, ValueError, TypeError):
        return False


def get_signaler(obj, property_name):
    """Return the SignalerInstance for the given object and property name. If there is no SignalerInstance then
    the one will be made if there is an existing property of function.

    Raises:
        AttributeError: If obj does not have the property_name as a property or callable function.
    """
    if is_property(obj, property_name):
        # Force the property to be a signaler property to make the values change together
        if not is_signaler_property(obj, property_name):
            prop = getattr(obj.__class__, property_name)
            sig = signaler_property(fget=prop.fget, fset=prop.fset, fdel=prop.fdel)
            setattr(obj.__class__, property_name, sig)

        prop = getattr(obj.__class__, property_name)
        return prop.get_signaler_instance(obj)

    # Get the setter signaler instance
    if hasattr(obj, "set_" + property_name):
        setter_name = "set_" + property_name
    elif hasattr(obj, "set" + property_name):
        setter_name = "set" + property_name
    elif hasattr(obj, property_name):  # Maybe property name == "set_property_name"
        setter_name = property_name
        if not callable(getattr(obj, setter_name)):
            raise AttributeError("The given object property_name must be an attribute that is a property, callable, or "
                                 "have 'set_'+property_name, or 'set'+property_name methods.")
    else:
        raise AttributeError("The given object property_name must be an attribute that is a property, callable, or "
                             "have 'set_'+property_name, or 'set'+property_name methods.")

    # Force the setter to be a SignalerInstance (Signal, signaler, signaler_property)
    setter = getattr(obj, setter_name)
    if not isinstance(setter, SignalerInstance):
        sig = None

        # Check if there is a getter
        for getter_name in GETTER_PREFIXES:
            if hasattr(obj, getter_name):
                sig = signaler(setter, getter=getattr(obj, getter_name))
                break

        if sig is None:
            sig = signaler(setter)

        # Override the function or method with signaler instance
        setattr(obj, setter_name, sig)
        setter = sig

    return setter


def bind_signals(obj1_signaler, obj2_signaler):
    """Bind the obj1 setter signal function and the obj2 setter signal function so they share the same value.

    Args
        obj1_signaler (signaler/signaler_property/SignalerPropertyInstance): obj1 signal setter method to bind.
        obj2_signaler (signaler/signaler_property/SignalerPropertyInstance): obj2 signal setter method to bind.

    Raises:
        TypeError: If obj1_signaler or obj2_signaler does not have on or off methods to connect the signals
    """
    if not hasattr(obj1_signaler, "on") or not hasattr(obj1_signaler, "off"):
        raise TypeError("The given obj1_signaler must be a SignalerInstance or have 'on' and 'off' methods "
                        "to help connect and disconnect the signal callback functions. See event_signal.signaler")
    if not hasattr(obj2_signaler, "on") or not hasattr(obj2_signaler, "off"):
        raise TypeError("The given obj2_signaler must be a SignalerInstance or have 'on' and 'off' methods "
                        "to help connect and disconnect the signal callback functions. See event_signal.signaler")

    # if not hasattr(data_setter, "_signaler_lock"):
    #     data_setter._signaler_lock = threading.RLock()
    # if not hasattr(settings_setter, "_signaler_lock"):
    #     settings_setter._signaler_lock = threading.RLock()

    def call_obj2_setter(*args, **kwargs):
        # with data_setter._signaler_lock: # Maybe need to add a threading RLock to be safe?
        exists = obj2_signaler.off("change", call_obj1_setter)
        obj2_signaler(*args, **kwargs)
        if exists:
            obj2_signaler.on("change", call_obj1_setter)

    def call_obj1_setter(*args, **kwargs):
        # with settings_setter._signaler_lock: # Maybe need to add a threading RLock to be safe?
        exists = obj1_signaler.off("change", call_obj2_setter)
        obj1_signaler(*args, **kwargs)
        if exists:
            obj1_signaler.on("change", call_obj2_setter)

    # Bind the signalers together
    obj1_signaler.on("change", call_obj2_setter)
    obj2_signaler.on("change", call_obj1_setter)

    # Add a bind_methods variable so the signalers bind can be undone.
    if not hasattr(obj1_signaler, "bind_methods"):
        obj1_signaler.bind_methods = []
    obj1_signaler.bind_methods.append(call_obj2_setter)

    if not hasattr(obj2_signaler, "bind_methods"):
        obj2_signaler.bind_methods = []
    obj2_signaler.bind_methods.append(call_obj1_setter)


def unbind_signals(obj1_signaler, obj2_signaler=None):
    """Unbind all of the bind_methods for the signaler/SignalInstance. This will remove the binding done by
    'bind' or 'bind_signals' for ALL binds.

    Args
        obj1_signaler (signaler/signaler_property/SignalerPropertyInstance): obj1 signal setter method to unbind.
        obj2_signaler (signaler/signaler_property/SignalerPropertyInstance)[None]: obj2 signal setter method to unbind.

    Raises:
        TypeError: If obj1_signaler or obj2_signaler (is not None) does not have an off method to use to unbind.
    """
    if not hasattr(obj1_signaler, "off"):
        raise TypeError("The given obj1_signaler must be a SignalerInstance or have an 'off' method "
                        "to help disconnect the signal callback functions. See event_signal.signaler")
    if obj2_signaler is not None and not hasattr(obj2_signaler, "off"):
        raise TypeError("The given obj2_signaler must be a SignalerInstance or have an 'off' method "
                        "to help disconnect the signal callback functions. See event_signal.signaler")

    if hasattr(obj1_signaler, "bind_methods"):
        for i in reversed(range(len(obj1_signaler.bind_methods))):
            binding = obj1_signaler.bind_methods.pop(i)
            obj1_signaler.off("change", binding)

    if hasattr(obj2_signaler, "bind_methods"):
        for i in reversed(range(len(obj2_signaler.bind_methods))):
            binding = obj2_signaler.bind_methods.pop(i)
            obj2_signaler.off("change", binding)


def bind(obj1, property_name, obj2, obj2_name=None):
    """Find the signaler or signaler_property and bind the set functions together to make the objects have their
    values match.

    Examples:

        .. code-block:: python

            >>> class Test(object):
            >>>     def __init__(self, x=0):
            >>>         self._x = x
            >>>
            >>>     def get_x(self):
            >>>         return self._x
            >>>
            >>>     @signaler(getter=get_x)
            >>>     def set_x(self, value):
            >>>         self._x = value
            >>>
            >>> t1 = Test()
            >>> t2 = Test()
            >>> # Example acceptable arguments
            >>> bind_lazy(t1, "x", t2)
            >>> bind_lazy(t1, "x", t2, "x")
            >>> bind_lazy(t1, "set_x", t2, "x")
            >>> bind_lazy(t1.set_x, None, t2, "set_x")
            >>> bind_lazy(t1.set_x, None, t2.set_x)  # Same as bind_signals(t1.set_x, t2.set_x)

    Args:
        obj1(object): First object to bind. This can either be an object with a given property_name or a
            signaler/SignalerInstance.
        property_name(str)[None]: obj1's property name, name of setter method ("set_" or "set" + property_name), or
            None if obj1 was a signler/SignalerInstance.
        obj2(object): Second object to bind. This can either be an object with a given property_name/obj2_name or a
            signaler/SignalerInstance.
        obj2_name(str)[None]: obj2's property name or name of setter method ("set_" or "set" + property_name), or
            None if obj2 was a signaler/SignalerInstance or use property_name for obj2 as well.

    Raises:
        AttributeError: If obj1 does not have the property_name as a property or callable function or if obj2 does
            not have the obj2_name as a property or callable function.
        TypeError: If obj1_signaler or obj2_signaler does not have on or off methods to connect the signals
    """
    if isinstance(obj1, SignalerInstance) and property_name is None:
        obj1_sig = obj1
    else:
        property_name = str(property_name)
        obj1_sig = get_signaler(obj1, property_name)

    if isinstance(obj2, SignalerInstance) and obj2_name is None:
        obj2_sig = obj2
    else:
        if obj2_name is None:
             obj2_name = property_name
        obj2_sig = get_signaler(obj2, obj2_name)

    bind_signals(obj1_sig, obj2_sig)


def unbind(obj1, property_name=None, obj2=None, obj2_name=None):
    """Find the signaler or signaler_property and bind the set functions together to make the objects have their
    values match.

    Examples:

        .. code-block:: python

            >>> class Test(object):
            >>>     def __init__(self, x=0):
            >>>         self._x = x
            >>>
            >>>     def get_x(self):
            >>>         return self._x
            >>>
            >>>     @signaler(getter=get_x)
            >>>     def set_x(self, value):
            >>>         self._x = value
            >>>
            >>> t1 = Test()
            >>> t2 = Test()
            >>> bind(t1, "x", t2)
            >>> # Example acceptable arguments
            >>> unbind(t1, "x", t2)
            >>> unbind(t1, "x", t2, "x")
            >>> unbind(t1, "set_x", t2, "x")
            >>> unbind(t1.set_x, None, t2, "set_x")
            >>> unbind(t1.set_x, None, t2.set_x)  # Same as unbind_signals(t1.set_x, t2.set_x)
            >>> unbind(t1.set_x)

    Args:
        obj1(object): First object to unbind. This can either be an object with a given property_name or a
            signaler/SignalerInstance.
        property_name(str)[None]: obj1's property name, name of setter method ("set_" or "set" + property_name), or
            None if obj1 was a signler/SignalerInstance.
        obj2(object)[None]: Second object to unbind (optional). This can either be an object with a given
        property_name/obj2_name or a signaler/SignalerInstance.
        obj2_name(str)[None]: obj2's property name or name of setter method ("set_" or "set" + property_name), or
            None if obj2 was a signaler/SignalerInstance or use property_name for obj2 as well.

    Raises:
        AttributeError: If obj1 does not have the property_name as a property or callable function or if obj2 does
            not have the obj2_name as a property or callable function.
        TypeError: If obj1_signaler or obj2_signaler does not have on or off methods to connect the signals
    """
    if isinstance(obj1, SignalerInstance) and property_name is None:
        obj1_sig = obj1
    else:
        property_name = str(property_name)
        obj1_sig = get_signaler(obj1, property_name)

    if obj2 is None:
        obj2_sig = None
    elif isinstance(obj2, SignalerInstance) and obj2_name is None:
        obj2_sig = obj2
    else:
        if obj2_name is None:
             obj2_name = property_name
        obj2_sig = get_signaler(obj2, obj2_name)

    unbind_signals(obj1_sig, obj2_sig)
