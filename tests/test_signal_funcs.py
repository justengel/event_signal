from __future__ import print_function

from event_signal import SignalError, get_signal, on_signal, off_signal, fire_signal, block_signals, add_signal


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

    print("test_add_signal_to_class passed!")


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

    print("test_add_signal_to_obj passed!")


def test_get_signal():
    class SignalTest(object):
        def __init__(self):
            super(SignalTest, self).__init__()
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

    try:
        get_signal(t, 'signal that does not exist')
        raise AssertionError("get_signal should raise an error if the signal does not exist.")
    except SignalError:
        pass

    print("test_get_signal passed!")


def test_on_signal():
    class SignalTest(object):
        def __init__(self):
            super(SignalTest, self).__init__()
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

    print("test_on_signal passed!")


def test_off_signal():
    class SignalTest(object):
        def __init__(self):
            super(SignalTest, self).__init__()
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
    existed = off_signal(t, "testing", testing)
    assert existed
    assert t.event_signals["testing"] == []

    existed = off_signal(t, "testing", testing)
    assert not existed

    print("test_off_signal passed!")


def test_fire_signal():
    class SignalTest(object):
        def __init__(self):
            super(SignalTest, self).__init__()
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

    print("test_fire_signal passed!")


def test_block_signal():
    class SignalTest(object):
        def __init__(self):
            super(SignalTest, self).__init__()
            self.event_signals = {"testing": [], "test2": []}

    t = SignalTest()
    assert hasattr(t, "event_signals") and "testing" in t.event_signals and "test2" in t.event_signals
    assert get_signal(t, "testing") == []
    assert t.event_signals["testing"] == []
    assert t.event_signals["test2"] == []

    test = []
    test2 = []

    def testing(value1, value2):
        test.append((value1, value2))

    def test2_func(*args):
        test2.append(args)

    # Test connect and emit
    t.event_signals["testing"].append(testing)
    t.event_signals["test2"].append(test2_func)

    fire_signal(t, "testing", "abc", "123")
    assert test == [("abc", "123")]

    block_signals(t)
    fire_signal(t, "testing", "Hello", "World!")
    assert test == [("abc", "123")]

    block_signals(t, block=False)
    fire_signal(t, "testing", "Hello", "World!")
    assert test == [("abc", "123"), ("Hello", "World!")]

    block_signals(t, "test2", True)
    fire_signal(t, "testing", "Hello", "again")
    fire_signal(t, "test2", False)
    assert test == [("abc", "123"), ("Hello", "World!"), ("Hello", "again")]
    assert test2 == [], "Failed to block the right signal"

    block_signals(t, "test2", False)
    fire_signal(t, "testing", "Hello", "again")
    fire_signal(t, "test2", True)
    assert test == [("abc", "123"), ("Hello", "World!"), ("Hello", "again"), ("Hello", "again")]
    assert test2 == [(True,)], "Failed to block the right signal"

    print("test_block_signal passed!")


if __name__ == '__main__':
    test_add_signal_to_class()
    test_add_signal_to_obj()
    test_get_signal()
    test_on_signal()
    test_off_signal()
    test_fire_signal()
    test_block_signal()
    print("All tests passed!")
