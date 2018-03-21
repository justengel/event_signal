# import threading
from .signaler_inst import SignalerInstance
from .signaler_prop import signaler_property
from .signaler import signaler


__all__ = ["bind", "bind_lazy", "bind_signals"]


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


def bind_lazy(obj1, property_name, obj2, obj2_name=None):
    """Find the signaler or signaler_property and bind the set functions together to make the objects have their
    values match.

    Args:
        obj1(object): Data model object to have it's data match another object
        property_name(str): obj1's property name or name of setter method that can be found with "set_" + property_name
            or "set" + property_name
        obj2(object): Data model object to have it's data match another object
        obj2_name(str)[None]: obj2's property name or name of setter method that can be found with "set_" + other_name
            or "set" + other_name. If None is given this uses the given property_name.

    Raises:
        AttributeError: If obj1 does not have the property_name as a property or callable function or if obj2 does
            not have the obj2_name as a property or callable function.
        TypeError: If obj1_signaler or obj2_signaler does not have on or off methods to connect the signals
    """
    property_name = str(property_name)
    if obj2_name is None:
         obj2_name = property_name

    obj1_sig = get_signaler(obj1, property_name)
    obj2_sig = get_signaler(obj2, obj2_name)
    bind_signals(obj1_sig, obj2_sig)


bind = bind_lazy


def bind_signals(obj1_signaler, obj2_signaler):
    """Bind the data setter signal function and the settings setter signal function so they share the same value.

    Args
        data_setter (signaler/signaler_property/SignalerPropertyInstance): Data model signal setter method.
        settings_setter (signaler/signaler_property/SignalerPropertyInstance): Settings model signal setter method.

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
        obj2_signaler.off("change", call_obj1_setter)
        obj2_signaler(*args, **kwargs)
        obj2_signaler.on("change", call_obj1_setter)

    def call_obj1_setter(*args, **kwargs):
        # with settings_setter._signaler_lock: # Maybe need to add a threading RLock to be safe?
        obj1_signaler.off("change", call_obj2_setter)
        obj1_signaler(*args, **kwargs)
        obj1_signaler.on("change", call_obj2_setter)

    obj1_signaler.on("change", call_obj2_setter)
    obj2_signaler.on("change", call_obj1_setter)
