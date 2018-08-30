from event_signal import signaler_property, signaler


def test_property():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x

        @signaler_property
        def x(self):
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

        @x.deleter
        def x(self):
            del self._x

    t = XTest()
    assert t.x == 0

    t.x = 1
    assert t.x == 1

    del t.x
    try:
        t.x
        raise AssertionError("Deleter failed")
    except AttributeError:
        pass

    assert isinstance(XTest.x, property)

    print("test_property passed!")


def test_no_setter():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self._before_val = None
            self._post_val = None

        @signaler_property
        def x(self):
            return self._x

    t = XTest()
    try:
        t.x = 1
        raise AssertionError("No setter was set. The cmd 't.x = 1' should have failed.")
    except AttributeError:
        pass

    print("test_no_setter passed!")


def test_no_deleter():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self._before_val = None
            self._post_val = None

        @signaler_property
        def x(self):
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

        @x.on("before_delete")
        def x_deleting(self):
            self._before_val = True

        @x.on("delete")
        def x_deleted(self):
            self._post_val = True

    t = XTest()
    try:
        del t.x
        raise AssertionError("No deleter was set. The cmd 'del t.x' should have failed.")
    except AttributeError:
        pass

    print("test_no_deleter passed!")


def test_change():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self._before_val = None
            self._post_val = None

        @signaler_property
        def x(self):
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

        @x.on("before_change")
        def x_changing(self, value):
            self._before_val = value

        @x.on("change")
        def x_changed(self, value):
            self._post_val = value

    t = XTest()
    assert t.x == 0
    assert t._before_val is None
    assert t._post_val is None

    value = 1
    t.x = value
    assert t.x == value
    assert t._before_val == value
    assert t._post_val == value

    existed = XTest.x.off(t, "change", t.x_changed)
    assert existed
    new_value = 2
    t.x = new_value
    assert t.x == new_value
    assert t._before_val == new_value
    assert t._post_val == value

    existed = XTest.x.off(t, "before_change", t.x_changing)
    assert existed
    new_value2 = 3
    t.x = new_value2
    assert t.x == new_value2
    assert t._before_val == new_value
    assert t._post_val == value

    XTest.x.off(t, "change")
    existed = XTest.x.off(t, "change")
    assert not existed

    print("test_change passed!")


def test_delete():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self._before_val = None
            self._post_val = None

        @signaler_property
        def x(self):
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

        @x.deleter
        def x(self):
            del self._x

        @x.on("before_delete")
        def x_deleting(self):
            self._before_val = True

        @x.on("delete")
        def x_deleted(self):
            self._post_val = True

    t = XTest()
    assert t.x == 0
    assert t._before_val is None
    assert t._post_val is None

    del t.x
    try:
        t.x
        raise AssertionError("t.x should not exist. The deleter failed.")
    except AttributeError:
        pass
    assert t._before_val == True
    assert t._post_val == True

    t._x = 0
    assert t.x == 0

    XTest.x.off(t, "delete", t.x_deleted)
    t._before_val = None
    t._post_val = None
    del t.x
    try:
        t.x
        raise AssertionError("t.x should not exist. The deleter failed.")
    except AttributeError:
        pass
    assert t._before_val == True
    assert t._post_val is None

    t._x = 0
    assert t.x == 0

    XTest.x.off(t, "before_delete")
    t._before_val = None
    t._post_val = None
    del t.x
    try:
        t.x
        raise AssertionError("t.x should not exist. The deleter failed.")
    except AttributeError:
        pass
    assert t._before_val is None
    assert t._post_val is None

    print("test_delete passed!")


def test_property_block_signal():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self._before_val = None
            self._post_val = None

        @signaler_property
        def x(self):
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

        @x.on("before_change")
        def x_changing(self, value):
            self._before_val = value

        @x.on("change")
        def x_changed(self, value):
            self._post_val = value

    t = XTest()
    assert t.x == 0
    assert t._before_val is None
    assert t._post_val is None

    value = 1
    t.x = value
    assert t.x == value
    assert t._before_val == value
    assert t._post_val == value

    XTest.x.block(t, "change", True)
    new_value = 2
    t.x = new_value
    assert t.x == new_value
    assert t._before_val == new_value
    assert t._post_val == value

    XTest.x.block(t, "change", False)
    new_value2 = 3
    t.x = new_value2
    assert t.x == new_value2
    assert t._before_val == new_value2
    assert t._post_val == new_value2

    XTest.x.block(t)
    new_value3 = 4
    t.x = new_value3
    assert t.x == new_value3
    assert t._before_val == new_value2
    assert t._post_val == new_value2

    XTest.x.block(t, block=False)
    new_value4 = 5
    t.x = new_value4
    assert t.x == new_value4
    assert t._before_val == new_value4
    assert t._post_val == new_value4

    print("test_property_block_signal passed!")


def test_signal_dot_property():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self._before_val = None
            self._post_val = None

        @signaler.property
        def x(self):
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

        @x.on("before_change")
        def x_changing(self, value):
            self._before_val = value

        @x.on("change")
        def x_changed(self, value):
            self._post_val = value

    t = XTest()
    assert t.x == 0
    assert t._before_val is None
    assert t._post_val is None

    value = 1
    t.x = value
    assert t.x == value
    assert t._before_val == value
    assert t._post_val == value

    XTest.x.off(t, "change", t.x_changed)
    new_value = 2
    t.x = new_value
    assert t.x == new_value
    assert t._before_val == new_value
    assert t._post_val == value

    XTest.x.off(t, "before_change", t.x_changing)
    new_value2 = 3
    t.x = new_value2
    assert t.x == new_value2
    assert t._before_val == new_value
    assert t._post_val == value

    print("test_signal_dot_property passed!")


if __name__ == '__main__':
    test_property()
    test_no_setter()
    test_no_deleter()
    test_change()
    test_delete()
    test_property_block_signal()
    test_signal_dot_property()
    print("All tests passed!")
