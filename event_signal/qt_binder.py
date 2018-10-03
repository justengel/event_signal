import os
from .signaler import signaler
from .binder import bind, unbind

try:
    from PyQt5 import QtWidgets
    os.environ['QT_API'] = 'pyqt5'  # Prevent annoying qtpy warning about chaning qt versions
except ImportError:
    try:
        from PySide2 import QtWidgets
        os.environ['QT_API'] = 'pyside2'  # Prevent annoying qtpy warning about chaning qt versions
    except ImportError:
        try:
            from PyQt4 import QtGui as QtWidgets
            os.environ['QT_API'] = 'pyqt4'  # Prevent annoying qtpy warning about chaning qt versions
        except ImportError:
            try:
                from PySide import QtGui as QtWidgets
                os.environ['QT_API'] = 'pyside'  # Prevent annoying qtpy warning about chaning qt versions
            except ImportError:
                QtWidgets = None
                # print('Cannot bind_qt or unbind_qt. The qtpy library is not installed!')
try:
    from qtpy import QtWidgets
except (ImportError, Exception):  # Exception because QtPy will raise it's own error if qt is not on the system
    pass


__all__ = ["get_qt_signal_name", "bind_qt", "unbind_qt", 'QT_SIGNALS']


QT_SIGNALS = ['toggled', 'currentIndexChanged', 'editingFinished', 'textChanged', 'valueChanged']


def get_qt_signal_name(obj):
    """Return the proper qt signal for the given QWidget."""
    for sig in QT_SIGNALS:
        if hasattr(obj, sig):
            return sig


def get_widget_value(widget):
    """Return the desired value from a widget."""
    if isinstance(widget, QtWidgets.QAbstractButton):
        return widget.isChecked()

    elif isinstance(widget, QtWidgets.QTreeView):
        return widget.selectedData()

    elif isinstance(widget, QtWidgets.QComboBox):
        item_data = widget.itemData(widget.currentIndex())
        if item_data is not None:
            return item_data
        else:
            return widget.currentText()

    elif isinstance(widget, QtWidgets.QTextEdit):
        return widget.toPlainText()

    elif hasattr(widget, "value"):
        return widget.value()

    elif not hasattr(widget, "text"):
        for item in widget.children():
            if isinstance(item, QtWidgets.QLineEdit):
                return item.text()
    else:
        return widget.text()


def bind_qt(obj1, property_name, obj2, obj2_name=None, qt_signal=None):
    """Find the signaler or signaler_property and bind the set functions together to make the objects have their
    values match.

    Examples:

        .. code-block:: python

            >>> class Test(object):
            >>>     def __init__(self, x=0):
            >>>         self._x = x
            >>>
            >>>     def get_x(self):
            >>>         return self._x
            >>>
            >>>     @signaler(getter=get_x)
            >>>     def set_x(self, value):
            >>>         self._x = value
            >>>
            >>> t1 = Test()
            >>> t2 = Test()
            >>> # Example acceptable arguments
            >>> bind_qt(t1, "x", t2)
            >>> bind_qt(t1, "x", t2, "x")
            >>> bind_qt(t1, "set_x", t2, "x")
            >>> bind_qt(t1.set_x, None, t2, "set_x")
            >>> bind_qt(t1.set_x, None, t2.set_x)  # Same as bind_signals(t1.set_x, t2.set_x)

    Args:
        obj1(object): First object to bind. This can either be an object with a given property_name or a
            signaler/SignalerInstance.
        property_name(str)[None]: obj1's property name, name of setter method ("set_" or "set" + property_name), or
            None if obj1 was a signler/SignalerInstance.
        obj2(object): Second object to bind. This can either be an object with a given property_name/obj2_name or a
            signaler/SignalerInstance.
        obj2_name(str)[None]: obj2's property name or name of setter method ("set_" or "set" + property_name), or
            None if obj2 was a signaler/SignalerInstance or use property_name for obj2 as well.
        qt_signal (str) [None]: variable name of the Qt Signal to connect.

    Raises:
        AttributeError: If obj1 does not have the property_name as a property or callable function or if obj2 does
            not have the obj2_name as a property or callable function.
        TypeError: If obj1_signaler or obj2_signaler does not have on or off methods to connect the signals

    Returns:
        obj1_sig (signaler): Object 1 signal that is bound to obj2_sig
        obj2_sig (signaler): Object 2 signal that is bound to obj1_sig
    """

    obj1_sig, obj2_sig = bind(obj1, property_name, obj2, obj2_name=obj2_name)

    if QtWidgets is not None:
        if isinstance(obj1, QtWidgets.QWidget):
            if qt_signal is None:
                qt_signal = get_qt_signal_name(obj1)

            if qt_signal is not None and hasattr(obj1, qt_signal):
                if not hasattr(obj2_sig, '_set_from_widget'):
                    def obj2_set_from_widget(*args, **kwargs):
                        obj2_sig(get_widget_value(obj1))
                    obj2_sig._set_from_widget = obj2_set_from_widget

                getattr(obj1, qt_signal).connect(obj2_sig._set_from_widget)
                return

        if isinstance(obj2, QtWidgets.QWidget):
            if qt_signal is None:
                qt_signal = get_qt_signal_name(obj2)

            if qt_signal is None or not hasattr(obj2, qt_signal):
                raise ValueError('Cannot find a qt_signal to connect!')

            if not hasattr(obj1_sig, '_set_from_widget'):
                def obj1_set_from_widget(*args, **kwargs):
                    obj1_sig(get_widget_value(obj2))
                obj1_sig._set_from_widget = obj1_set_from_widget

            getattr(obj2, qt_signal).connect(obj1_sig._set_from_widget)

    return obj1_sig, obj2_sig


def unbind_qt(obj1, property_name=None, obj2=None, obj2_name=None, qt_signal=None):
    """Find the signaler or signaler_property and bind the set functions together to make the objects have their
    values match.

    Examples:

        .. code-block:: python

            >>> class Test(object):
            >>>     def __init__(self, x=0):
            >>>         self._x = x
            >>>
            >>>     def get_x(self):
            >>>         return self._x
            >>>
            >>>     @signaler(getter=get_x)
            >>>     def set_x(self, value):
            >>>         self._x = value
            >>>
            >>> t1 = Test()
            >>> t2 = Test()
            >>> bind(t1, "x", t2)
            >>> # Example acceptable arguments
            >>> unbind(t1, "x", t2)
            >>> unbind(t1, "x", t2, "x")
            >>> unbind(t1, "set_x", t2, "x")
            >>> unbind(t1.set_x, None, t2, "set_x")
            >>> unbind(t1.set_x, None, t2.set_x)  # Same as unbind_signals(t1.set_x, t2.set_x)
            >>> unbind(t1.set_x)

    Args:
        obj1(object): First object to unbind. This can either be an object with a given property_name or a
            signaler/SignalerInstance.
        property_name(str)[None]: obj1's property name, name of setter method ("set_" or "set" + property_name), or
            None if obj1 was a signler/SignalerInstance.
        obj2(object)[None]: Second object to unbind (optional). This can either be an object with a given
        property_name/obj2_name or a signaler/SignalerInstance.
        obj2_name(str)[None]: obj2's property name or name of setter method ("set_" or "set" + property_name), or
            None if obj2 was a signaler/SignalerInstance or use property_name for obj2 as well.
        qt_signal (str) [None]: variable name of the Qt Signal that was connected.

    Raises:
        AttributeError: If obj1 does not have the property_name as a property or callable function or if obj2 does
            not have the obj2_name as a property or callable function.
        TypeError: If obj1_signaler or obj2_signaler does not have on or off methods to connect the signals

    Returns:
        obj1_sig (signaler): Object 1 signal that was disconnected from obj2_sig
        obj2_sig (signaler): Object 2 signal that was disconnected from obj1_sig
    """
    obj1_sig, obj2_sig = unbind(obj1, property_name=property_name, obj2=obj2, obj2_name=obj2_name)

    if QtWidgets is not None:
        if isinstance(obj1, QtWidgets.QWidget):
            if qt_signal is None:
                qt_signal = get_qt_signal_name(obj1)

            if qt_signal is not None and hasattr(obj1, qt_signal):
                try:
                    getattr(obj1, qt_signal).disconnect(obj2_sig._set_from_widget)
                except AttributeError:
                    pass
                return

        if isinstance(obj2, QtWidgets.QWidget):
            if qt_signal is None:
                qt_signal = get_qt_signal_name(obj2)

            if qt_signal is None or not hasattr(obj2, qt_signal):
                raise ValueError('Cannot find a qt_signal to disconnect from!')

            try:
                getattr(obj2, qt_signal).disconnect(obj1_sig._set_from_widget)
            except AttributeError:
                pass

    return obj1_sig, obj2_sig
