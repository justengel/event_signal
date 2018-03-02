# Event Signal

This library was created to help maintain when variables are changed and when functions are called.

There are 4 main utilities provided

    * signaler - Function decorator to help observe functions
    * signaler_property - Custom property that helps observe when a property value is changed or deleted.
    * MethodObserver - class mixin to make all function observable
    * Signal - Similar to Qt's signal without requiring PyQT or PySide
    
## Use

There are 4 main functions to use the signals.

    * get - returns a list of connected function callbacks
    * on - connect a callback function to a signal
    * off - disconnect a callback funciton from a signal
    * fire - Call all callback functions that are associated with a signal
    
## Example - signaler

```python
from event_signal import signaler


class XTest(object):
    def __init__(self, x=0):
        self._x = x

    def get_x(self):
        return self._x

    @signaler
    def set_x(self, x):
        self._x = x
        
    @set_x.on("before_change")
    def x_changing(self, x):
        print("x is changing")
        
    @set_x.on("change")
    def x_changed(self, x):
        print("x changed", x)
        
t = XTest()
t.set_x(1)
# x is changing
# x changed 1
t.set_x.on("change", lambda x: print("new signal"))
t.set_x(2)
# x is changing
# x changed 2
# new signal
t.set_x.off("before_change", t.x_changing)
t.set_x(3)
# x changed 3
# new signal
```

## Example - signaler_property
```python
from event_signal import signaler_property


class XTest(object):
    def __init__(self, x=0):
        self._x = x

    @signaler_property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        
    @x.on("before_change")
    def x_changing(self, x):
        print("x is changing")
        
    @x.on("change")
    def x_changed(self, x):
        print("x changed", x)
        
t = XTest()
t.x = 1
# x is changing
# x changed 1
XTest.x.on(t, "change", lambda x: print("new signal"))
t.x = 2
# x is changing
# x changed 2
# new signal
XTest.x.off(t, "before_change", t.x_changing)
t = 3
# x changed 3
# new signal
```

## Example - MethodObserver
```python
from event_signal import MethodObserver


class XTest(MethodObserver):
    def __init__(self, x=0):
        self._x = x

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x
        
    def x_changing(self, x):
        print("x is changing")
        
    def x_changed(self, x):
        print("x changed", x)
        
t = XTest()
t.set_x(1)
t.set_x.on("change", t.x_changed)
t.set_x(2)
# x changed 2
t.set_x.on("before_change", t.x_changing)
t.set_x(3)
# x is changing
# x changed 3
t.set_x.off("before_change", t.x_changing)
t.set_x(4)
# x changed 4
```

## Example - Signal
```python
from event_signal import Signal


class XTest(object):
    x_changed = Signal(int)

    def __init__(self, x=0):
        self._x = x

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x
        self.x_changed.emit(self._x)
        
    def notify_x_changed(self, x):
        print("x changed", x)
        
t = XTest()
t.set_x(1)
t.x_changed.connect(t.notify_x_changed)
t.set_x(2)
# x changed 2
t.x_changed.emit(3)
# x changed 3
print(t.get_x())
# 2
t.x_changed.disconnect(t.notify_x_changed)  # or t.x_changed.disconnect()
t.set_x(4)
print(t.get_x())
# 4
```
