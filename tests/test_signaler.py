from event_signal import signaler


def test_simple_before_change_change():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self.test = None
            self.test2 = None

        def get_x(self):
            return self._x

        @signaler
        def set_x(self, x):
            self._x = x

        @set_x.on("before_change")
        def test_before_change(self, value):
            self.test = value

        @set_x.on("change")
        def text_changed(self, value):
            self.test2 = value

    t = XTest()
    assert t.get_x() == 0
    assert t.test is None
    assert t.test2 is None

    value = 1
    t.set_x(value)
    assert t.get_x() == value
    assert t.test == value
    assert t.test2 == value

    print("test_simple_before_change_change passed!")


def test_signaler_getter_simple():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self.test = None

        def get_x(self):
            return "GETTER VALUE"

        @signaler(getter=get_x)
        def set_x(self, x):
            self._x = x

        @set_x.on("change")
        def test_getter(self, value):
            self.test = value

    t = XTest()
    assert t.get_x() == "GETTER VALUE"
    assert t._x == 0
    assert t.test is None

    value = 1
    t.set_x(value)
    assert t.get_x() == "GETTER VALUE"
    assert t._x == value
    assert t.test == "GETTER VALUE"

    print("test_signaler_getter_simple passed!")


def test_signaler_getter():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self.test = None

        def get_x(self):
            return self._x

        @signaler(getter=get_x)
        def set_x(self, x):
            if x < 0:
                x = 0
            elif x > 100:
                x = 100
            self._x = x

        @set_x.on("change")
        def test_getter(self, value):
            self.test = value

    t = XTest()
    assert t.get_x() == 0
    assert t._x == 0
    assert t.test is None

    value = 1
    t.set_x(value)
    assert t.get_x() == 1
    assert t._x == value
    assert t.test == 1

    value = -1
    t.set_x(value)
    assert t.get_x() == 0
    assert t._x == 0
    assert t.test == 0

    value = 101
    t.set_x(value)
    assert t.get_x() == 100
    assert t._x == 100
    assert t.test == 100

    print("test_signaler_getter passed!")


def test_signaler_instances():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self.test = None
            self.test2 = None

        def get_x(self):
            return self._x

        @signaler
        def set_x(self, x):
            self._x = x

    t = XTest()
    def set_test(value):
        t.test = value
    def set_test2(value):
        t.test2 = value
    t.set_x.on("before_change", set_test)
    t.set_x.on("change", set_test2)

    assert t.get_x() == 0
    assert t.test is None
    assert t.test2 is None

    value = 2
    t.set_x(value)
    assert t.get_x() == value
    assert t.test == value
    assert t.test2 == value

    print("test_signaler_instances passed!")


def test_signaler_block():
    class XTest(object):
        def __init__(self, x=0):
            self._x = x
            self.test = None
            self.test2 = None

        def get_x(self):
            return self._x

        @signaler
        def set_x(self, x):
            self._x = x

    t = XTest()
    def set_test(value):
        t.test = value
    def set_test2(value):
        t.test2 = value
    t.set_x.on("before_change", set_test)
    t.set_x.on("change", set_test2)

    assert t.get_x() == 0
    assert t.test is None
    assert t.test2 is None

    t.set_x.block('before_change')
    value = 2
    t.set_x(value)
    assert t.get_x() == value
    assert t.test is None
    assert t.test2 == value

    t.set_x.block('before_change', block=False)
    value = 3
    t.set_x(value)
    assert t.get_x() == value
    assert t.test == value
    assert t.test2 == value

    t.set_x.block()
    last_value = value
    value = 4
    t.set_x(value)
    assert t.get_x() == value
    assert t.test == last_value
    assert t.test2 == last_value

    t.set_x.block(block=False)
    value = 5
    t.set_x(value)
    assert t.get_x() == value
    assert t.test == value
    assert t.test2 == value

    print("test_signaler_block passed!")


def test_chaining():
    class Point(object):
        def __init__(self, x=0, y=0):
            self._x = x
            self._y = y
            self._xy_pre = []
            self._xy_post = []
            self._x_pre = []
            self._x_post = []
            self._y_pre = []
            self._y_post = []
            self._move_pre = []
            self._move_post = []

        def get_x(self):
            return self._x

        @signaler
        def set_x(self, x):
            self._x = x

        def get_y(self):
            return self._y

        @signaler
        def set_y(self, y):
            self._y = y

        @signaler
        def move(self, x, y):
            self.set_x(x)
            self.set_y(y)

        @set_x.on("before_change")
        def changing_x_value(self, value):
            # print('X value is about to change')
            self._x_pre.append(value)

        @set_x.on("change")
        def changed_x_value(self, value):
            # print('X value has changed', self.get_x(), self.get_y())
            self._x_post.append(value)

        @set_y.on("before_change")
        def changing_y_value(self, value):
            # print('Y value is about to change')
            self._y_pre.append(value)

        @set_y.on("change")
        def changed_y_value(self, value):
            # print('Y value has changed', self.get_x(), self.get_y())
            self._y_post.append(value)

        @set_x.on("before_change")
        @set_y.on("before_change")
        def changing_values(self, value):
            self._xy_pre.append(value)

        @set_x.on("change")
        @set_y.on("change")
        def changed_values(self, value):
            self._xy_post.append(value)

        @move.on("before_change")
        def moving(self, *args):
            # print("Attempting to move to", *args)
            self._move_pre.append(args)

        @move.on("change")
        def moved(self, *args):
            # print("Moved to", self.get_x(), self.get_y())
            self._move_post.append(args)

        def __repr__(self):
            return self.__class__.__name__ + "(%d, %d)" % (self.get_x(), self.get_y())

    p = Point()
    assert p._xy_pre == []
    assert p._xy_post == []
    assert p._x_pre == []
    assert p._x_post == []
    assert p._y_pre == []
    assert p._y_post == []
    assert p._move_pre == []
    assert p._move_post == []

    p.set_x("x1")
    assert p._xy_pre == ["x1"]
    assert p._xy_post == ["x1"]
    assert p._x_pre == ["x1"]
    assert p._x_post == ["x1"]
    assert p._y_pre == []
    assert p._y_post == []
    assert p._move_pre == []
    assert p._move_post == []

    p.set_y("y1")
    assert p._xy_pre == ["x1", "y1"]
    assert p._xy_post == ["x1", "y1"]
    assert p._x_pre == ["x1"]
    assert p._x_post == ["x1"]
    assert p._y_pre == ["y1"]
    assert p._y_post == ["y1"]
    assert p._move_pre == []
    assert p._move_post == []

    p.move("x2", "y2")
    assert p._xy_pre == ["x1", "y1", "x2", "y2"]
    assert p._xy_post == ["x1", "y1", "x2", "y2"]
    assert p._x_pre == ["x1", "x2"]
    assert p._x_post == ["x1", "x2"]
    assert p._y_pre == ["y1", "y2"]
    assert p._y_post == ["y1", "y2"]
    assert p._move_pre == [("x2", "y2")]
    assert p._move_post == [("x2", "y2")]

    existed = p.set_x.off("before_change")
    assert existed
    p.move("x3", "y3")
    assert p._xy_pre == ["x1", "y1", "x2", "y2", "y3"]  # Note: x3 not updated
    assert p._xy_post == ["x1", "y1", "x2", "y2", "x3", "y3"]
    assert p._x_pre == ["x1", "x2"]  # Note: x3 not updated
    assert p._x_post == ["x1", "x2", "x3"]
    assert p._y_pre == ["y1", "y2", "y3"]
    assert p._y_post == ["y1", "y2", "y3"]
    assert p._move_pre == [("x2", "y2"), ("x3", "y3")]
    assert p._move_post == [("x2", "y2"), ("x3", "y3")]

    existed = p.set_x.off("change")
    assert existed
    p.move("x4", "y4")
    assert p._xy_pre == ["x1", "y1", "x2", "y2", "y3", "y4"]  # Note: x4 not updated
    assert p._xy_post == ["x1", "y1", "x2", "y2", "x3", "y3", "y4"]  # Note: x4 not updated
    assert p._x_pre == ["x1", "x2"]  # Note: x4 not updated
    assert p._x_post == ["x1", "x2", "x3"]  # Note: x4 not updated
    assert p._y_pre == ["y1", "y2", "y3", "y4"]
    assert p._y_post == ["y1", "y2", "y3", "y4"]
    assert p._move_pre == [("x2", "y2"), ("x3", "y3"), ("x4", "y4")]
    assert p._move_post == [("x2", "y2"), ("x3", "y3"), ("x4", "y4")]

    existed = p.set_x.off("change")
    assert not existed

    print("test_chaining passed!")


if __name__ == '__main__':
    test_simple_before_change_change()
    test_signaler_getter_simple()
    test_signaler_getter()
    test_signaler_instances()
    test_signaler_block()
    test_chaining()
    print("All tests passed!")
