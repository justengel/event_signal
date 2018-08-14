# Event Signal

This library was created to help maintain when variables are changed and when functions are called.

There are 5 main utilities provided

    * signaler - Function decorator to help observe functions
    * signaler_property - Custom property that helps observe when a property value is changed or deleted.
    * MethodObserver - class mixin to make all function observable
    * Signal - Similar to Qt's signal without requiring PyQT or PySide
    * bind - Make two object share the same value
    
## Use

There are 5 main functions to use the signals.

    * get_signal - returns a list of connected function callbacks
    * on - connect a callback function to a signal
    * off - disconnect a callback funciton from a signal
    * fire - Call all callback functions that are associated with a signal
    * block - Temporarily block a signal from calling callback functions
    
Two basic signals are provided `'before_change'` and `'change'`. The signaler_property also has delete signals.

    * 'before_change' - This signal automatically fires before a function is called.
    * 'change' - This signal automatically fires after a function is called.
    * 'before_delete' - signaler_property fired before `del obj.property` is called.
    * 'delete' - signaler_property fired after `del obj.property` is called.
    
## Basics

A signaler is a custom class decorator. It acts just like a function (it is callable). A signaler can have other 
functions attached to it with a name. When the signaler fire is called it will call all of the attached functions.

```python
from event_signal import signaler

def my_function(a, b, c):
    print(a, b, c)

my_function = signaler(my_function)

# Call the signaler like a normal function
my_function(1, 2, 3)
# print = 1, 2, 3
print('=====\n')

def print_signal(value1, value2):
    print('print_signal called', value1, value2)

my_function.on('my_signal', print_signal)
my_function.fire('my_signal', 1, 2)
# print = print_signal called 1 2
print('=====\n')

def another_signal(value1, value2):
    print('another_signal called', value1, value2, value1 == value2)

my_function.on('my_signal', another_signal)
my_function.fire('my_signal', 2, 2)
# print = print_signal called 2 2
# print = another_signal called 2 2 True
print('=====\n')

my_function.off('my_signal', print_signal)
my_function.fire('my_signal', 3, 2)
# print = another_signal called 3 2 False
print('=====\n')

print(my_function.get_signal('my_signal'))
# print = [<function ...another_signal at 0x056076F0>]
print('=====\n')

my_function.block('my_signal')
my_function.fire('my_signal', 4, 5)
# No print!
my_function.block('my_signal', False)
my_function.fire('my_signal', 5, 6)
# print = another_signal called 5 6 False
print('=====\n')
``` 

    
## Example - signaler
Javascript like events for functions and objects. 
The signaler automatically creates and fires signals `'before_change'` and `'change'`.


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

t.set_x.block()
t.set_x(4)

t.set_x.block(block=False)
t.set_x(5)
# x changed 3
# new signal

t.set_x.block('change', True)
t.set_x(6)
```


Change the value that is passed to the change callback functions.
```python
from event_signal import signaler

class XTest(object):
    def __init__(self, x=0):
        self._x = x

    def get_x(self):
        return self._x

    @signaler(getter=get_x)
    def set_x(self, x):
        """Set x and force the value to be between 1 and 100."""
        if x < 0:
            x = 0
        elif x > 100:
            x = 100
        self._x = x
        
    @set_x.on("before_change")
    def x_changing(self, x):
        print("x is changing", x)
        
    @set_x.on("change")
    def x_changed(self, x):
        print("x changed", x)
        
t = XTest()

t.set_x(1)
# x is changing 1
# x changed 1

# Normally (without the getter) the change callback functions receive 
# the x value that was passed into set_x
t.set_x(-1)
# x is changing -1
# x changed 0

t.set_x(102)
# x is changing 102
# x changed 100

# In this case the value passed into the change callback functions
# is the value returned from the signaler getter (t.get_x) 
# which is how the signaler_property works.
```

## Example - signaler_property
A property with signaler capabilities.
The signaler_property automatically creates and fires signals `'before_change'`, `'change'`, `'before_delete'`, and `'delete'`.

```python
from event_signal import signaler_property


class XTest(object):
    def __init__(self, x=0):
        self._x = x

    @signaler_property  # or signaler.property
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
t.x = 3
# x changed 3
# new signal

XTest.x.block(t, 'change')
t.x = 4

XTest.x.block(t, 'change', False)
t.x = 5
# x changed 
# new signal
```

## Example - MethodObserver
Inheritable class or metaclass that makes every function/method in a class a signaler.

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
Qt like signal.


**Warning:**

Qt's signals are thread safe (depending on how you connect them). They call the callback functions in the main thread.
Many Qt widgets error and do not update when a value is set from a separate thread. So Qt's Signal is a good way to 
update a QWidget's value display, but can be slow. 

The event_signal.Signal works like a Qt Signal with a direct connection. 
The callback functions are called in the same thread that originally called the function. If you are using Qt and use 
this Signal from a separate thread to udate a QWidget it may not work properly and throw errors or warnings.

For more information on how to make a QWidget thread safe go to <https://tasks.justengel.com/project/justengel-event-signal/wiki/signal-qt-thread-safe>

Also this signal does not do any kind of type checking. Passing types into the Signal constructor ```Signal(int, str)``` 
is just for looks and maybe code readability.

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

## Example - bind
bind the value of two objects together. This will automatically use properties or find setter methods 
("set_" + property_name or "set" + property_name). The binder will change a property to a signaler_property or if a 
property is not found and a setter function is used it will change that setter function to a signaler if it is not 
already a signaler.

The main goal is to help two objects keep the same value for a variable.

When using Qt I found this very annoying. I wanted a regular python object to store data and a GUI Widget to display 
the value and let the user change value. I wanted the two items decoupled. Occasionally, I wanted to programmatically 
set the data object value and wanted the GUI Widget to display this change automatically. The signals became annoying 
to deal with since I do a lot of work with threading. After several overly complex solutions, I made this bind function 
to make the GUI and data objects match values.

```python
from event_signal import bind, bind_signals  # bind_signals is only for directly giving signalers.


class XTest(object):
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x
    
    @property    
    def y(self):
        return self._y
    
    @y.setter
    def y(self, y):
        self._y = y
    
        
t = XTest()
t2 = XTest()
bind(t, "x", t2)
t.set_x(1)
print(t.get_x())
# 1
assert t.get_x() == t2.get_x()

bind(t, "y", t2, "y")
t2.y = 2
print(t2.y)
# 2
assert t.y == t2.y
```

You can manually bind the signalers as well.
```python
from event_signal import signaler, bind_signals  # bind_signals is only for directly giving signalers.


class Test2(object):
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def get_x(self):
        return self._x

    @signaler(getter=get_x)
    def set_x(self, x):
        self._x = x
        
t1 = Test2()
t2 = Test2()
bind_signals(t1.set_x, t2.set_x)

t1.set_x(2)
assert t1.get_x() == t2.get_x()

t2.set_x(5)
assert t1.get_x() == t2.get_x()
```

An unbind option is also available and works just like the examples above accept you can choose to unbind a single object at a time
```python
from event_signal import bind, unbind, unbind_signals  # unbind_signals is only for directly giving one or more signalers.


class XTest(object):
    def __init__(self, x=0):
        self._x = x

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x
        
t = XTest()
t2 = XTest()
bind(t, "x", t2)

t.set_x(1)
print(t.get_x())
# 1
assert t.get_x() == t2.get_x()

unbind(t, "x")
t.set_x(2)
print(t.get_x())
# 2
assert t.get_x() != t2.get_x()

t2.set_x(3)
print(t2.get_x())
# 3
assert t.get_x() == t2.get_x()


unbind(t2.set_x)
t2.set_x(4)
print(t2.get_x())
# 4
assert t.get_x() != t2.get_x()


bind(t, "x", t2)
t.set_x(1)
print(t.get_x())
# 1
assert t.get_x() == t2.get_x()

unbind(t, "x", t2)
t.set_x(2)
print(t.get_x())
# 2
assert t.get_x() != t2.get_x()

t2.set_x(3)
print(t2.get_x())
# 3
assert t.get_x() != t2.get_x()
```
