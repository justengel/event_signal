from event_signal import MethodObserver


def test_method_observer():
    class Point(MethodObserver):
        def __init__(self, x=0, y=0):
            self._x = x
            self._y = y

        def get_x(self):
            return self._x

        def set_x(self, x):
            self._x = x

        def get_y(self):
            return self._y

        def set_y(self, y):
            self._y = y

        def move(self, x, y):
            self.set_x(x)
            self.set_y(y)

    p = Point()
    x_before_vals = []
    x_post_vals = []
    y_before_vals = []
    y_post_vals = []
    xy_before_vals = []
    xy_post_vals = []
    move_before_vals = []
    move_post_vals = []

    @p.set_x.on("before_change")
    def before_x(x):
        x_before_vals.append(x)

    def post_x(x):
        x_post_vals.append(x)
    p.set_x.on("change", post_x)

    def before_y(y):
        y_before_vals.append(y)
    def post_y(y):
        y_post_vals.append(y)
    p.set_y.on("before_change", before_y)
    p.set_y.on("change", post_y)

    @p.set_x.on("before_change")
    @p.set_y.on("before_change")
    def before_xy(value):
        xy_before_vals.append(value)
    @p.set_x.on("change")
    @p.set_y.on("change")
    def post_xy(value):
        xy_post_vals.append(value)

    @p.move.on("before_change")
    def before_move(x, y):
        move_before_vals.append((x, y))
    @p.move.on("change")
    def post_move(x, y):
        move_post_vals.append((x, y))

    # ===== Set values =====
    assert p.get_x() == 0
    assert p.get_y() == 0

    p.set_x("x0")
    assert p.get_x() == "x0"
    assert p.get_y() == 0
    assert x_before_vals == ["x0"]
    assert x_post_vals == ["x0"]
    assert y_before_vals == []
    assert y_post_vals == []
    assert xy_before_vals == ["x0"]
    assert xy_post_vals == ["x0"]
    assert move_before_vals == []
    assert move_post_vals == []

    p.set_y("y0")
    assert p.get_x() == "x0"
    assert p.get_y() == "y0"
    assert x_before_vals == ["x0"]
    assert x_post_vals == ["x0"]
    assert y_before_vals == ["y0"]
    assert y_post_vals == ["y0"]
    assert xy_before_vals == ["x0", "y0"]
    assert xy_post_vals == ["x0", "y0"]
    assert move_before_vals == []
    assert move_post_vals == []

    p.move("x1", "y1")
    assert p.get_x() == "x1"
    assert p.get_y() == "y1"
    assert x_before_vals == ["x0", "x1"]
    assert x_post_vals == ["x0", "x1"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert xy_before_vals == ["x0", "y0", "x1", "y1"]
    assert xy_post_vals == ["x0", "y0", "x1", "y1"]
    assert move_before_vals == [("x1", "y1")]
    assert move_post_vals == [("x1", "y1")]

    # ===== Test decorated function still callable =====
    before_x("Test decorated func")
    assert p.get_x() == "x1"
    assert p.get_y() == "y1"
    assert x_before_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert xy_before_vals == ["x0", "y0", "x1", "y1"]
    assert xy_post_vals == ["x0", "y0", "x1", "y1"]
    assert move_before_vals == [("x1", "y1")]
    assert move_post_vals == [("x1", "y1")]

    # ===== Test disconnect function =====
    p.set_x.off("before_change", before_x)
    p.set_x("x2")
    assert p.get_x() == "x2"
    assert p.get_y() == "y1"
    assert x_before_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1", "x2"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert xy_before_vals == ["x0", "y0", "x1", "y1", "x2"]
    assert xy_post_vals == ["x0", "y0", "x1", "y1", "x2"]
    assert move_before_vals == [("x1", "y1")]
    assert move_post_vals == [("x1", "y1")]

    # ===== Test disconnect all =====
    p.set_y.off("before_change")
    p.set_y("y2")
    assert p.get_x() == "x2"
    assert p.get_y() == "y2"
    assert x_before_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1", "x2"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1", "y2"]
    assert xy_before_vals == ["x0", "y0", "x1", "y1", "x2"]
    assert xy_post_vals == ["x0", "y0", "x1", "y1", "x2", "y2"]
    assert move_before_vals == [("x1", "y1")]
    assert move_post_vals == [("x1", "y1")]


def test_inheritance():
    class Point(MethodObserver):
        def __init__(self, x=0, y=0):
            self._x = x
            self._y = y

        def get_x(self):
            return self._x

        def set_x(self, x):
            self._x = x

        def get_y(self):
            return self._y

        def set_y(self, y):
            self._y = y

        def move(self, x, y):
            self.set_x(x)
            self.set_y(y)

    class Vector(Point):
        def __init__(self, x=0, y=0, z=0):
            self._z = z
            super(Vector, self).__init__(x=x, y=y)

        def get_z(self):
            return self._z

        def set_z(self, value):
            self._z = value

        def move(self, x, y, z):
            super().move(x, y)
            self.set_z(z)

    p = Vector()
    x_before_vals = []
    x_post_vals = []
    y_before_vals = []
    y_post_vals = []
    z_before_vals = []
    z_post_vals = []
    xyz_before_vals = []
    xyz_post_vals = []
    move_before_vals = []
    move_post_vals = []

    @p.set_x.on("before_change")
    def before_x(x):
        x_before_vals.append(x)

    def post_x(x):
        x_post_vals.append(x)
    p.set_x.on("change", post_x)

    def before_y(y):
        y_before_vals.append(y)
    def post_y(y):
        y_post_vals.append(y)
    p.set_y.on("before_change", before_y)
    p.set_y.on("change", post_y)

    def before_z(z):
        z_before_vals.append(z)
    def post_z(z):
        z_post_vals.append(z)
    p.set_z.on("before_change", before_z)
    p.set_z.on("change", post_z)

    @p.set_x.on("before_change")
    @p.set_y.on("before_change")
    @p.set_z.on("before_change")
    def before_xy(value):
        xyz_before_vals.append(value)
    @p.set_x.on("change")
    @p.set_y.on("change")
    @p.set_z.on("change")
    def post_xy(value):
        xyz_post_vals.append(value)

    @p.move.on("before_change")
    def before_move(x, y, z):
        move_before_vals.append((x, y, z))
    @p.move.on("change")
    def post_move(x, y, z):
        move_post_vals.append((x, y, z))

    # ===== Set values =====
    assert p.get_x() == 0
    assert p.get_y() == 0
    assert p.get_z() == 0

    p.set_x("x0")
    assert p.get_x() == "x0"
    assert p.get_y() == 0
    assert p.get_z() == 0
    assert x_before_vals == ["x0"]
    assert x_post_vals == ["x0"]
    assert y_before_vals == []
    assert y_post_vals == []
    assert z_before_vals == []
    assert z_post_vals == []
    assert xyz_before_vals == ["x0"]
    assert xyz_post_vals == ["x0"]
    assert move_before_vals == []
    assert move_post_vals == []

    p.set_y("y0")
    assert p.get_x() == "x0"
    assert p.get_y() == "y0"
    assert p.get_z() == 0
    assert x_before_vals == ["x0"]
    assert x_post_vals == ["x0"]
    assert y_before_vals == ["y0"]
    assert y_post_vals == ["y0"]
    assert z_before_vals == []
    assert z_post_vals == []
    assert xyz_before_vals == ["x0", "y0"]
    assert xyz_post_vals == ["x0", "y0"]
    assert move_before_vals == []
    assert move_post_vals == []

    p.set_z("z0")
    assert p.get_x() == "x0"
    assert p.get_y() == "y0"
    assert p.get_z() == "z0"
    assert x_before_vals == ["x0"]
    assert x_post_vals == ["x0"]
    assert y_before_vals == ["y0"]
    assert y_post_vals == ["y0"]
    assert z_before_vals == ["z0"]
    assert z_post_vals == ["z0"]
    assert xyz_before_vals == ["x0", "y0", "z0"]
    assert xyz_post_vals == ["x0", "y0", "z0"]
    assert move_before_vals == []
    assert move_post_vals == []

    p.move("x1", "y1", "z1")
    assert p.get_x() == "x1"
    assert p.get_y() == "y1"
    assert p.get_z() == "z1"
    assert x_before_vals == ["x0", "x1"]
    assert x_post_vals == ["x0", "x1"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert z_before_vals == ["z0", "z1"]
    assert z_post_vals == ["z0", "z1"]
    assert xyz_before_vals == ["x0", "y0", "z0", "x1", "y1", "z1"]
    assert xyz_post_vals == ["x0", "y0", "z0", "x1", "y1", "z1"]
    assert move_before_vals == [("x1", "y1", "z1")]
    assert move_post_vals == [("x1", "y1", "z1")]

    # ===== Test decorated function still callable =====
    before_x("Test decorated func")
    assert p.get_x() == "x1"
    assert p.get_y() == "y1"
    assert p.get_z() == "z1"
    assert x_before_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert z_before_vals == ["z0", "z1"]
    assert z_post_vals == ["z0", "z1"]
    assert xyz_before_vals == ["x0", "y0", "z0", "x1", "y1", "z1"]
    assert xyz_post_vals == ["x0", "y0", "z0", "x1", "y1", "z1"]
    assert move_before_vals == [("x1", "y1", "z1")]
    assert move_post_vals == [("x1", "y1", "z1")]

    # ===== Test disconnect function =====
    p.set_x.off("before_change", before_x)
    p.set_x("x2")
    assert p.get_x() == "x2"
    assert p.get_y() == "y1"
    assert p.get_z() == "z1"
    assert x_before_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1", "x2"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert z_before_vals == ["z0", "z1"]
    assert z_post_vals == ["z0", "z1"]
    assert xyz_before_vals == ["x0", "y0", "z0", "x1", "y1", "z1", "x2"]
    assert xyz_post_vals == ["x0", "y0", "z0", "x1", "y1", "z1", "x2"]
    assert move_before_vals == [("x1", "y1", "z1")]
    assert move_post_vals == [("x1", "y1", "z1")]

    # ===== Test disconnect all =====
    p.set_y.off("before_change")
    p.set_y("y2")
    assert p.get_x() == "x2"
    assert p.get_y() == "y2"
    assert p.get_z() == "z1"
    assert x_before_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1", "x2"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1", "y2"]
    assert z_before_vals == ["z0", "z1"]
    assert z_post_vals == ["z0", "z1"]
    assert xyz_before_vals == ["x0", "y0", "z0", "x1", "y1", "z1", "x2"]
    assert xyz_post_vals == ["x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2"]
    assert move_before_vals == [("x1", "y1", "z1")]
    assert move_post_vals == [("x1", "y1", "z1")]

    # ===== Test disconnect function =====
    p.set_z.off("before_change", before_z)
    p.set_z("z2")
    assert p.get_x() == "x2"
    assert p.get_y() == "y2"
    assert p.get_z() == "z2"
    assert x_before_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1", "x2"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1", "y2"]
    assert z_before_vals == ["z0", "z1"]
    assert z_post_vals == ["z0", "z1", "z2"]
    assert xyz_before_vals == ["x0", "y0", "z0", "x1", "y1", "z1", "x2", "z2"]
    assert xyz_post_vals == ["x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2"]
    assert move_before_vals == [("x1", "y1", "z1")]
    assert move_post_vals == [("x1", "y1", "z1")]

    # ===== Test disconnect all =====
    p.set_z.off("before_change")
    p.set_z("z3")
    assert p.get_x() == "x2"
    assert p.get_y() == "y2"
    assert p.get_z() == "z3"
    assert x_before_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1", "x2"]
    assert y_before_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1", "y2"]
    assert z_before_vals == ["z0", "z1"]
    assert z_post_vals == ["z0", "z1", "z2", "z3"]
    assert xyz_before_vals == ["x0", "y0", "z0", "x1", "y1", "z1", "x2", "z2"]
    assert xyz_post_vals == ["x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2", "z3"]
    assert move_before_vals == [("x1", "y1", "z1")]
    assert move_post_vals == [("x1", "y1", "z1")]


if __name__ == '__main__':
    test_method_observer()
    test_inheritance()
    print("All tests passed!")
