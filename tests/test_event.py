from event_signal import Signal, signal_change


def test_signal():

    class MyClass(object):
        something_happened = Signal(str)

        def process(self):
            self.something_happened.emit("process was called")

    t = MyClass()
    vals = [None, None, None]

    # ===== Test simple =====
    def save_something(value):
        vals[0] = value
    t.something_happened.connect(save_something)

    assert vals[0] is None

    t.process()
    assert vals[0] == "process was called"

    t.something_happened.emit("Hello World!")
    assert vals[0] == "Hello World!"

    # ===== Test multiple functions =====
    def second_func(value):
        vals[1] = value

    def third_func(*args):
        vals[2] = "alert!"

    t.something_happened.connect(second_func)
    t.something_happened.connect(third_func)

    vals[0] = None
    vals[1] = None
    vals[2] = None
    assert vals[0] is None
    assert vals[1] is None
    assert vals[2] is None

    t.process()
    assert vals[0] == "process was called"
    assert vals[1] == "process was called"
    assert vals[2] == "alert!"

    # Custom emit
    vals[0] = None
    vals[1] = None
    vals[2] = None
    assert vals[0] is None
    assert vals[1] is None
    assert vals[2] is None

    t.something_happened.emit("Custom")
    assert vals[0] == "Custom"
    assert vals[1] == "Custom"
    assert vals[2] == "alert!"

    # ===== Test Disconnect =====
    # Custom emit
    vals[0] = None
    vals[1] = None
    vals[2] = None
    assert vals[0] is None
    assert vals[1] is None
    assert vals[2] is None

    t.something_happened.disconnect(save_something)
    t.process()
    assert vals[0] is None
    assert vals[1] == "process was called"
    assert vals[2] == "alert!"

    # ===== Test Disconnect All =====
    # Custom emit
    vals[0] = None
    vals[1] = None
    vals[2] = None
    assert vals[0] is None
    assert vals[1] is None
    assert vals[2] is None

    t.something_happened.disconnect()
    t.process()
    assert vals[0] is None
    assert vals[1] is None
    assert vals[2] is None


def test_signal_change():
    class MyClass(object):
        def __init__(self, x=0):
            self._x = x

        def get_x(self):
            return self._x

        @signal_change
        def set_x(self, x):
            self._x = x

    t = MyClass()
    vals = [None]

    # ===== Test connect =====
    def save_value(value):
        vals[0] = value

    t.set_x.connect(save_value)

    assert vals[0] is None
    assert t.get_x() == 0
    t.set_x(1)
    assert t.get_x() == 1
    assert vals[0] == 1

    # ===== Test Disconnect =====
    t.set_x.disconnect(save_value)
    vals[0] = None
    assert vals[0] is None
    assert t.get_x() == 1
    t.set_x(2)
    assert t.get_x() == 2
    assert vals[0] is None


if __name__ == '__main__':
    test_signal()
    test_signal_change()
    print("All tests passed!")
