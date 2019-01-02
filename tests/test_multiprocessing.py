import time

import event_signal
import multiprocessing


class Point(object):
    # Class level objects are not pickled!!! This is a different object in multiprocessing
    moved = event_signal.Signal(int, int)

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self._z = z

    def move_sig(self, x, y):
        self.x = x
        self.y = y
        self.moved.emit(self.x, self.y)

    @event_signal.signaler  # Decorators need functools.update_wrapper for naming issues with multiprocessing
    def move(self, x, y):
        self.x = x
        self.y = y

    @event_signal.signaler_property
    def z(self):
        return self._z

    @z.setter
    def z(self, z):
        self._z = z

    def move_z(self, z):
        self.z = z

    def move_z_parent(self, z):
        Point.z.fire(self, 'change', z)


class SimpleProperty(object):
    def __init__(self, a='a'):
        self._a = a

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, a):
        self._a = a

    def test_set_a(self, a):
        self.a = a


@event_signal.signaler(fire_results=True)
def run_calculation(a, b):
    return a**2 + b**2


def test_mp_signal():
    event_signal.multiprocessing_support()

    p = Point(-1, -1, -1)

    values = []
    def save_moved(x, y):
        values.append([x, y])

    p.moved.connect(save_moved)

    p.move_sig(0, 1)
    assert values == [[0, 1]]

    proc = multiprocessing.Process(target=p.move_sig, args=(1, 2))
    proc.start()
    # time.sleep(1)
    proc.join()
    time.sleep(0.1)

    print(values)
    assert values == [[0, 1], [1, 2]]


def test_mp_signaler():
    event_signal.multiprocessing_support()

    p = Point(-1, -1, -1)

    values = []
    def save_moved(x, y):
        values.append([x, y])

    p.move.on('change', save_moved)

    p.move(0, 1)
    assert values == [[0, 1]]

    proc = multiprocessing.Process(target=p.move, args=(1, 2))
    proc.start()
    # time.sleep(1)
    proc.join()
    time.sleep(0.1)

    print(values)
    assert values == [[0, 1], [1, 2]]


def test_multiprocessing_property():
    event_signal.multiprocessing_support()

    sp = SimpleProperty()

    sp.test_set_a('a1')

    proc = multiprocessing.Process(target=sp.test_set_a, args=('a2',))
    proc.start()
    # time.sleep(1)
    proc.join()
    time.sleep(0.1)

    print('Did not error!')


def test_mp_signaler_property():
    event_signal.multiprocessing_support()

    p = Point(-1, -1, -1)

    values = []
    def save_moved(z):
        values.append([z])

    Point.z.on(p, 'change', save_moved)

    p.move_z(0)
    assert values == [[0]]

    proc = multiprocessing.Process(target=p.move_z, args=(1,))
    proc.start()
    # time.sleep(1)
    proc.join()
    time.sleep(0.1)

    print(values)
    assert values == [[0], [1]]


def test_mp_signaler_property_parent():
    event_signal.multiprocessing_support()

    p = Point(-1, -1, -1)

    values = []
    def save_moved(z):
        values.append([z])

    Point.z.on(p, 'change', save_moved)

    p.move_z_parent(0)
    assert values == [[0]]

    proc = multiprocessing.Process(target=p.move_z_parent, args=(1,))
    proc.start()
    # time.sleep(1)
    proc.join()
    time.sleep(0.1)

    print(values)
    assert values == [[0], [1]]


def test_signaler_function():
    event_signal.multiprocessing_support()

    values = []

    def save_results(value):
        values.append([value])

    run_calculation.on('change', save_results)

    run_calculation(1, 2)
    assert values == [[1**2 + 2**2]]

    proc = multiprocessing.Process(target=run_calculation, args=(2, 3))
    proc.start()
    # time.sleep(1)
    proc.join()
    time.sleep(0.1)

    print(values)
    assert values == [[1**2 + 2**2], [2**2 + 3**2]]


if __name__ == '__main__':
    multiprocessing.freeze_support()

    test_mp_signal()
    test_mp_signaler()
    test_multiprocessing_property()
    test_mp_signaler_property()
    test_mp_signaler_property_parent()
    test_signaler_function()
    print("All tests passed!")
