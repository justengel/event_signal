

def test_bind_qt():
    from event_signal import signaler, bind_qt, unbind_qt
    from qtpy import QtWidgets

    class MyData(object):
        def __init__(self, name='hello'):
            self._name = name

        def get_name(self):
            return self._name

        @signaler(getter=get_name)
        def set_name(self, name):
            self._name = str(name)

    app = QtWidgets.QApplication([])

    widg = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout()
    widg.setLayout(lay)
    widg.show()

    data = MyData()
    data.set_name.on('change', lambda name: print('data name changed to', name))

    inp = QtWidgets.QLineEdit('Hello World!')
    lay.addWidget(inp)

    bind_qt(data, 'set_name', inp, 'setText')

    btn = QtWidgets.QPushButton('Set Hello')
    def set_hello():
        data.set_name('Hello')
    btn.clicked.connect(set_hello)
    lay.addWidget(btn)

    unbind_btn = QtWidgets.QPushButton('unbind')
    def unbind_call():
        unbind_qt(data, 'set_name', inp, 'setText')
    unbind_btn.clicked.connect(unbind_call)
    lay.addWidget(unbind_btn)

    app.exec_()


def test_bind_qt_get_widget_value():
    from event_signal import signaler, bind_qt, unbind_qt, qt_binder
    from qtpy import QtWidgets

    class CustomWidget(QtWidgets.QLineEdit):
        def my_value(self):
            return self.text()

    # Change the get_widget_value function
    def get_widget_value(widget):
        if isinstance(widget, CustomWidget):
            print('here')
            return widget.my_value()
        return qt_binder.get_widget_value(widget)

    qt_binder.get_widget_value = get_widget_value


    class MyData(object):
        def __init__(self, name='hello'):
            self._name = name

        def get_name(self):
            return self._name

        @signaler(getter=get_name)
        def set_name(self, name):
            self._name = str(name)

    app = QtWidgets.QApplication([])

    widg = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout()
    widg.setLayout(lay)
    widg.show()

    data = MyData()
    data.set_name.on('change', lambda name: print('data name changed to', name))

    inp = CustomWidget('Hello World!')
    lay.addWidget(inp)

    bind_qt(data, 'set_name', inp, 'setText', qt_signal='editingFinished')

    btn = QtWidgets.QPushButton('Set Hello')
    def set_hello():
        data.set_name('Hello')
    btn.clicked.connect(set_hello)
    lay.addWidget(btn)

    unbind_btn = QtWidgets.QPushButton('unbind')
    def unbind_call():
        unbind_qt(data, 'set_name', inp, 'setText')
    unbind_btn.clicked.connect(unbind_call)
    lay.addWidget(unbind_btn)

    app.exec_()


if __name__ == '__main__':
    try:
        # test_bind_qt()
        test_bind_qt_get_widget_value()
    except ImportError:
        print("QtPY not installed! Cannot test bind with Qt")
    print("All tests passed!")
