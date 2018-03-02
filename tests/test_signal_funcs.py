from event_signal import get_signal, on_signal, off_signal, fire_signal, add_signal


def test_add_signal_to_class():
    class SignalTest(object):
        A = None

    add_signal(SignalTest, "testing")
    assert SignalTest.A is None
    assert hasattr(SignalTest, "event_signals")
    assert "testing" in SignalTest.event_signals
    assert SignalTest.event_signals["testing"] == []
    assert hasattr(SignalTest, "get_signal")
    assert hasattr(SignalTest, "on")
    assert hasattr(SignalTest, "off")
    assert hasattr(SignalTest, "fire")

    # ===== Test instances =====
    t = SignalTest()
    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.on("testing", testing)
    t.fire("testing", "abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    t.off("testing", testing)
    t.fire("testing", "blah", False)
    assert test == [("abc", "123")]

    # ===== Test the class =====
    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.on("testing", testing)
    t.fire("testing", "abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    t.off("testing", testing)
    t.fire("testing", "blah", False)
    assert test == [("abc", "123")]


def test_add_signal_to_obj():
    class SignalTest(object):
        A = None

    assert not hasattr(SignalTest, "event_signals")
    assert not hasattr(SignalTest, "get_signal")
    assert not hasattr(SignalTest, "on")
    assert not hasattr(SignalTest, "off")
    assert not hasattr(SignalTest, "fire")

    # ===== Test instances =====
    t = SignalTest()
    add_signal(t, "testing")

    assert not hasattr(SignalTest, "event_signals")
    assert not hasattr(SignalTest, "get_signal")
    assert not hasattr(SignalTest, "on")
    assert not hasattr(SignalTest, "off")
    assert not hasattr(SignalTest, "fire")
    assert hasattr(t, "event_signals")
    assert "testing" in t.event_signals
    assert t.event_signals['testing'] == []
    assert hasattr(t, "get_signal")
    assert hasattr(t, "on")
    assert hasattr(t, "off")
    assert hasattr(t, "fire")

    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.on("testing", testing)
    t.fire("testing", "abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    t.off("testing", testing)
    t.fire("testing", "blah", False)
    assert test == [("abc", "123")]


def test_get_signal():
    class SignalTest(object):
        def __init__(self):
            super().__init__()
            self.event_signals = {"testing": []}

    t = SignalTest()
    assert hasattr(t, "event_signals") and "testing" in t.event_signals
    assert get_signal(t, "testing") == []
    assert t.event_signals["testing"] == []

    t.event_signals["testing"].append(print)
    assert get_signal(t, "testing") == [print]

    def blah(*args):
        pass
    t.event_signals["testing"].append(blah)
    assert get_signal(t, "testing") == [print, blah]

    t.event_signals["testing"].remove(print)
    assert get_signal(t, "testing") == [blah]

    t.event_signals["testing"].remove(blah)
    assert get_signal(t, "testing") == []


def test_on_signal():
    class SignalTest(object):
        def __init__(self):
            super().__init__()
            self.event_signals = {"testing": []}

    t = SignalTest()
    assert hasattr(t, "event_signals") and "testing" in t.event_signals
    assert get_signal(t, "testing") == []
    assert t.event_signals["testing"] == []

    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    on_signal(t, "testing", testing)
    assert t.event_signals["testing"] == [testing]
    t.event_signals['testing'][0]("abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    t.event_signals["testing"].remove(testing)
    assert t.event_signals["testing"] == []


def test_off_signal():
    class SignalTest(object):
        def __init__(self):
            super().__init__()
            self.event_signals = {"testing": []}

    t = SignalTest()
    assert hasattr(t, "event_signals") and "testing" in t.event_signals
    assert get_signal(t, "testing") == []
    assert t.event_signals["testing"] == []

    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.event_signals["testing"].append(testing)
    t.event_signals["testing"][0]("abc", "123")
    assert test == [("abc", "123")]

    # Test disconnect
    off_signal(t, "testing", testing)
    assert t.event_signals["testing"] == []


def test_fire_signal():
    class SignalTest(object):
        def __init__(self):
            super().__init__()
            self.event_signals = {"testing": []}

    t = SignalTest()
    assert hasattr(t, "event_signals") and "testing" in t.event_signals
    assert get_signal(t, "testing") == []
    assert t.event_signals["testing"] == []

    test = []

    def testing(value1, value2):
        test.append((value1, value2))

    # Test connect and emit
    t.event_signals["testing"].append(testing)
    fire_signal(t, "testing", "abc", "123")
    assert test == [("abc", "123")]

    fire_signal(t, "testing", "Hello", "World!")
    assert test == [("abc", "123"), ("Hello", "World!")]


if __name__ == '__main__':
    test_add_signal_to_class()
    test_add_signal_to_obj()
    test_get_signal()
    test_on_signal()
    test_off_signal()
    test_fire_signal()
    print("All tests passed!")
