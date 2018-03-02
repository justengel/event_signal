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
    x_pre_vals = []
    x_post_vals = []
    y_pre_vals = []
    y_post_vals = []
    xy_pre_vals = []
    xy_post_vals = []
    move_pre_vals = []
    move_post_vals = []

    @p.set_x.on("pre_change")
    def pre_x(x):
        x_pre_vals.append(x)

    def post_x(x):
        x_post_vals.append(x)
    p.set_x.on("change", post_x)

    def pre_y(y):
        y_pre_vals.append(y)
    def post_y(y):
        y_post_vals.append(y)
    p.set_y.on("pre_change", pre_y)
    p.set_y.on("change", post_y)

    @p.set_x.on("pre_change")
    @p.set_y.on("pre_change")
    def pre_xy(value):
        xy_pre_vals.append(value)
    @p.set_x.on("change")
    @p.set_y.on("change")
    def post_xy(value):
        xy_post_vals.append(value)

    @p.move.on("pre_change")
    def pre_move(x, y):
        move_pre_vals.append((x, y))
    @p.move.on("change")
    def post_move(x, y):
        move_post_vals.append((x, y))

    # ===== Set values =====
    assert p.get_x() == 0
    assert p.get_y() == 0

    p.set_x("x0")
    assert p.get_x() == "x0"
    assert p.get_y() == 0
    assert x_pre_vals == ["x0"]
    assert x_post_vals == ["x0"]
    assert y_pre_vals == []
    assert y_post_vals == []
    assert xy_pre_vals == ["x0"]
    assert xy_post_vals == ["x0"]
    assert move_pre_vals == []
    assert move_post_vals == []

    p.set_y("y0")
    assert p.get_x() == "x0"
    assert p.get_y() == "y0"
    assert x_pre_vals == ["x0"]
    assert x_post_vals == ["x0"]
    assert y_pre_vals == ["y0"]
    assert y_post_vals == ["y0"]
    assert xy_pre_vals == ["x0", "y0"]
    assert xy_post_vals == ["x0", "y0"]
    assert move_pre_vals == []
    assert move_post_vals == []

    p.move("x1", "y1")
    assert p.get_x() == "x1"
    assert p.get_y() == "y1"
    assert x_pre_vals == ["x0", "x1"]
    assert x_post_vals == ["x0", "x1"]
    assert y_pre_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert xy_pre_vals == ["x0", "y0", "x1", "y1"]
    assert xy_post_vals == ["x0", "y0", "x1", "y1"]
    assert move_pre_vals == [("x1", "y1")]
    assert move_post_vals == [("x1", "y1")]

    # ===== Test decorated function still callable =====
    pre_x("Test decorated func")
    assert p.get_x() == "x1"
    assert p.get_y() == "y1"
    assert x_pre_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1"]
    assert y_pre_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert xy_pre_vals == ["x0", "y0", "x1", "y1"]
    assert xy_post_vals == ["x0", "y0", "x1", "y1"]
    assert move_pre_vals == [("x1", "y1")]
    assert move_post_vals == [("x1", "y1")]

    # ===== Test disconnect function =====
    p.set_x.off("pre_change", pre_x)
    p.set_x("x2")
    assert p.get_x() == "x2"
    assert p.get_y() == "y1"
    assert x_pre_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1", "x2"]
    assert y_pre_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1"]
    assert xy_pre_vals == ["x0", "y0", "x1", "y1", "x2"]
    assert xy_post_vals == ["x0", "y0", "x1", "y1", "x2"], str(xy_post_vals)
    assert move_pre_vals == [("x1", "y1")]
    assert move_post_vals == [("x1", "y1")]

    # ===== Test disconnect all =====
    p.set_y.off("pre_change")
    p.set_y("y2")
    assert p.get_x() == "x2"
    assert p.get_y() == "y2"
    assert x_pre_vals == ["x0", "x1", "Test decorated func"]
    assert x_post_vals == ["x0", "x1", "x2"]
    assert y_pre_vals == ["y0", "y1"]
    assert y_post_vals == ["y0", "y1", "y2"]
    assert xy_pre_vals == ["x0", "y0", "x1", "y1", "x2"]
    assert xy_post_vals == ["x0", "y0", "x1", "y1", "x2", "y2"]
    assert move_pre_vals == [("x1", "y1")]
    assert move_post_vals == [("x1", "y1")]


if __name__ == '__main__':
    test_method_observer()
    print("All tests passed!")