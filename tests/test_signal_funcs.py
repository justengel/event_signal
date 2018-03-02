from event_signal import get_signal, on_signal, off_signal, emit_signal, add_signal


def test_add_signal():
    class SignalTest(object):
        A = None

    NewSignalTest = add_signal("testing", SignalTest)
    assert NewSignalTest.A is None
    assert hasattr(NewSignalTest, "connect_testing")
    assert hasattr(NewSignalTest, "disconnect_testing")
    assert hasattr(NewSignalTest, "emit_testing")

    t = NewSignalTest()
    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.connect_testing(testing)
    t.emit_testing("abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    t.disconnect_testing(testing)
    t.emit_testing("blah", False)
    assert test == [("abc", "123")]


def test_add_signal_decorator():
    @add_signal("testing")
    class SignalTest(object):
        B = None

    assert SignalTest.B is None
    assert hasattr(SignalTest, "connect_testing")
    assert hasattr(SignalTest, "disconnect_testing")
    assert hasattr(SignalTest, "emit_testing")

    t = SignalTest()
    assert hasattr(t, "_testing_funcs")
    assert t._testing_funcs == []

    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.connect_testing(testing)
    t.emit_testing("abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    t.disconnect_testing(testing)
    t.emit_testing("blah", False)
    assert test == [("abc", "123")]


def test_get_signal():
    class SignalTest(object):
        def __init__(self):
            super().__init__()
            self._testing_funcs = []

        def connect_testing(self, func):
            if func not in self._testing_funcs:
                self._testing_funcs.append(func)

        def disconnect_testing(self, func=None):
            if func is None:
                self._testing_funcs = []
            else:
                try:
                    self._testing_funcs.remove(func)
                except:
                    pass

        def emit_testing(self, *args, **kwargs):
            for func in self._testing_funcs:
                func(*args, **kwargs)

    t = SignalTest()
    assert hasattr(t, "_testing_funcs")
    assert t._testing_funcs == []
    assert get_signal(t, "testing") == []

    t.connect_testing(print)
    assert get_signal(t, "testing") == [print]

    def blah(*args):
        pass
    t.connect_testing(blah)
    assert get_signal(t, "testing") == [print, blah]

    t.disconnect_testing(print)
    assert get_signal(t, "testing") == [blah]

    t.disconnect_testing(blah)
    assert get_signal(t, "testing") == []


def test_on_signal():
    class SignalTest(object):
        def __init__(self):
            super().__init__()
            self._testing_funcs = []

        def connect_testing(self, func):
            if func not in self._testing_funcs:
                self._testing_funcs.append(func)

        def disconnect_testing(self, func=None):
            if func is None:
                self._testing_funcs = []
            else:
                try:
                    self._testing_funcs.remove(func)
                except:
                    pass

        def emit_testing(self, *args, **kwargs):
            for func in self._testing_funcs:
                func(*args, **kwargs)

    assert hasattr(SignalTest, "connect_testing")
    assert hasattr(SignalTest, "disconnect_testing")
    assert hasattr(SignalTest, "emit_testing")

    t = SignalTest()
    assert hasattr(t, "_testing_funcs")
    assert t._testing_funcs == []

    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    on_signal(t, "testing", testing)
    t.emit_testing("abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    t.disconnect_testing(testing)
    t.emit_testing("blah", False)
    assert test == [("abc", "123")]


def test_off_signal():
    class SignalTest(object):
        def __init__(self):
            super().__init__()
            self._testing_funcs = []

        def connect_testing(self, func):
            if func not in self._testing_funcs:
                self._testing_funcs.append(func)

        def disconnect_testing(self, func=None):
            if func is None:
                self._testing_funcs = []
            else:
                try:
                    self._testing_funcs.remove(func)
                except:
                    pass

        def emit_testing(self, *args, **kwargs):
            for func in self._testing_funcs:
                func(*args, **kwargs)

    assert hasattr(SignalTest, "connect_testing")
    assert hasattr(SignalTest, "disconnect_testing")
    assert hasattr(SignalTest, "emit_testing")

    t = SignalTest()
    assert hasattr(t, "_testing_funcs")
    assert t._testing_funcs == []

    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.connect_testing(testing)
    t.emit_testing("abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    off_signal(t, "testing", testing)
    t.emit_testing("blah", False)
    assert test == [("abc", "123")]


def test_emit_signal():
    class SignalTest(object):
        def __init__(self):
            super().__init__()
            self._testing_funcs = []

        def connect_testing(self, func):
            if func not in self._testing_funcs:
                self._testing_funcs.append(func)

        def disconnect_testing(self, func=None):
            if func is None:
                self._testing_funcs = []
            else:
                try:
                    self._testing_funcs.remove(func)
                except:
                    pass

        def emit_testing(self, *args, **kwargs):
            for func in self._testing_funcs:
                func(*args, **kwargs)

    assert hasattr(SignalTest, "connect_testing")
    assert hasattr(SignalTest, "disconnect_testing")
    assert hasattr(SignalTest, "emit_testing")

    t = SignalTest()
    assert hasattr(t, "_testing_funcs")
    assert t._testing_funcs == []

    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.connect_testing(testing)
    emit_signal(t, "testing", "abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    t.disconnect_testing(testing)
    emit_signal(t, "testing", "blah", False)
    assert test == [("abc", "123")]


if __name__ == '__main__':
    test_add_signal()
    test_add_signal_decorator()
    test_get_signal()
    test_on_signal()
    test_off_signal()
    test_emit_signal()
    print("All tests passed!")
