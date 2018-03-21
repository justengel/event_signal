from event_signal.signaler import signaler
from event_signal.signaler_prop import signaler_property
from event_signal.binder import bind_signals, bind


def test_bind_signals():
    """The bind function is meant to connect two objects values.

    Originally this was created to help with GUI functionality. The theory is that you want a data model then you
    want some sort of GUI settings widget. When the widget value changes (like a checkbox or text input) then you want
    that setting to change on your data model. When your data model setting is change (maybe programatically due to some
    condition) then you want the settings widget to show that the data model value changed.

    This is a lot of back and forth and can easily cause some form of infinite looping.
    """
    class SignalerTest(object):
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        def set_x(self, x):
            self._x = x

    class DataModel(object):
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        @signaler
        def set_x(self, x):
            self._x = x

    class SettingWidget(object):
        """User interacts with this and the style and form of this widget can change."""
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        @signaler
        def set_x(self, x):
            self._x = x

    data_obj = DataModel()
    setting = SettingWidget(data_obj.get_x())

    # Test that only a signaler instance is given!
    try:
        signaler_test_obj = SignalerTest()
        bind_signals(signaler_test_obj.set_x, setting.set_x)
        raise AssertionError("bind_signals should only work if a SignalInstance is given!")
    except TypeError:
        pass

    # Raw bind signals does auto create a getter
    bind_signals(data_obj.set_x, setting.set_x)

    value = 20
    data_obj.set_x(value)
    assert setting.get_x() == data_obj.get_x()
    assert data_obj.get_x() == value
    assert setting.get_x() == value

    value = 100
    setting.set_x(value)
    assert setting.get_x() == data_obj.get_x()
    assert setting.get_x() == value
    assert data_obj.get_x() == value

    print("test_bind_signals passed!")


def test_bind_signals_getter():
    class DataModel(object):
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x - 3

        @signaler(getter=get_x)
        def set_x(self, x):
            self._x = x

    class SettingWidget(object):
        """User interacts with this and the style and form of this widget can change."""
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        @signaler(getter=get_x)
        def set_x(self, x):
            self._x = x

    data_obj = DataModel()
    setting = SettingWidget(data_obj.get_x())

    # Raw bind signals does auto create a getter
    bind_signals(data_obj.set_x, setting.set_x)

    value = 20
    data_obj.set_x(value)
    assert setting._x == data_obj._x - 3
    assert setting.get_x() == data_obj._x - 3
    assert setting.get_x() == data_obj.get_x()
    assert data_obj.get_x() == value - 3

    value = 100
    setting.set_x(value)
    assert setting._x == data_obj._x
    assert setting.get_x() == data_obj._x
    assert setting.get_x() - 3 == data_obj.get_x()
    assert data_obj.get_x() == value - 3

    print("test_bind_signals_getter passed!")


def test_bind_lazy_setter():
    class DataModel(object):
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        def set_x(self, x):
            self._x = x

    class SettingWidget(object):
        """User interacts with this and the style and form of this widget can change."""
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        def set_x(self, x):
            self._x = x

    data_obj = DataModel()
    setting = SettingWidget(data_obj.get_x())

    bind(data_obj, "x", setting)

    value = 20
    data_obj.set_x(value)
    assert data_obj.get_x() == value
    assert setting.get_x() == value

    value = 100
    setting.set_x(value)
    assert setting.get_x() == value
    assert data_obj.get_x() == value

    print("test_bind_lazy_setter passed!")


def test_bind_lazy_setter_obj2_property_name():
    class DataModel(object):
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        def set_x(self, x):
            self._x = x

    class SettingWidget(object):
        """User interacts with this and the style and form of this widget can change."""
        def __init__(self, xs=0):
            self._xs = xs

        def get_xs(self):
            return self._xs

        def set_xs(self, xs):
            self._xs = xs

    data_obj = DataModel()
    setting = SettingWidget(data_obj.get_x())

    bind(data_obj, "x", setting, "xs")

    value = 20
    data_obj.set_x(value)
    assert data_obj.get_x() == value
    assert setting.get_xs() == value

    value = 100
    setting.set_xs(value)
    assert setting.get_xs() == value
    assert data_obj.get_x() == value

    print("test_bind_lazy_setter_obj2_property_name passed!")


def test_bind_lazy_property():
    """For now bind_lazy prioritizes properties.

    It is bad (for this system) to have properties that also have getters and setters. bind will make the property a
    signal_property. If the old setter functions are called then the object values will not be bound properly.

    Examples:

        .. code-block:: python

            >>> class DataModel(object):
            >>>     def __init__(self, x=0):
            >>>         self._x = x
            >>>
            >>>     def get_x(self):
            >>>         return self._x
            >>>
            >>>     def set_x(self, x):
            >>>         self._x = x
            >>>
            >>>     x = property(get_x, set_x)
            >>>
            >>> data = DataModel()
            >>> other = DataModel()
            >>> bind(data, "x", other)
            >>> data.x = 1
            >>> assert data.x == other.x
            >>> data.set_x(2)
            >>> assert data.x == other.x, "This will fail! The property is connected with bind the set_x and get_x methods are not connected!"

    """
    class DataModel(object):
        def __init__(self, x=0):
            self._x = x

        # For now properties are always used as a priority.
        # Use _ to prevent the property functions from being called directly.
        def _get_x(self):
            return self._x

        def _set_x(self, x):
            self._x = x

        x = property(_get_x, _set_x)

    class SettingWidget(object):
        """User interacts with this and the style and form of this widget can change."""
        def __init__(self, xs=0):
            self._xs = xs

        @property
        def xs(self):
            return self._xs

        @xs.setter
        def xs(self, xs):
            self._xs = xs

    data_obj = DataModel()
    setting = SettingWidget(data_obj.x)

    bind(data_obj, "x", setting, "xs")

    value = 20
    data_obj.x = value
    assert data_obj.x == value
    assert setting.xs == value

    value = 100
    setting.xs = value
    assert setting.xs == value
    assert data_obj.x == value

    print("test_bind_lazy_property passed!")


def test_bind_with_signaler():
    class DataModel(object):
        def __init__(self, x=0, y=0):
            self._x = x
            self._y = 0

        def get_x(self):
            return self._x

        @signaler(getter=get_x)
        def set_x(self, x):
            self._x = x

        def get_y(self):
            return self._y

        @set_x.on("change")
        def set_y(self, y):
            self._y = y * 2

    class SettingWidget(object):
        """User interacts with this and the style and form of this widget can change."""
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        @signaler(getter=get_x)
        def set_x(self, x):
            self._x = x

    data_obj = DataModel()
    setting = SettingWidget(data_obj.get_x())

    bind(data_obj, "set_x", setting, "set_x")

    value = 20
    data_obj.set_x(value)
    assert data_obj.get_x() == value
    assert setting.get_x() == value
    assert data_obj.get_y() == value * 2

    value = 100
    setting.set_x(value)
    assert setting.get_x() == value
    assert data_obj.get_x() == value
    assert data_obj.get_y() == value * 2

    print("test_bind_with_signaler passed!")


if __name__ == '__main__':
    test_bind_signals()
    test_bind_signals_getter()
    test_bind_lazy_setter()
    test_bind_lazy_setter_obj2_property_name()
    test_bind_lazy_property()
    test_bind_with_signaler()
    print("All tests passed!")
