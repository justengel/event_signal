

def test_basics():
    from event_signal import signaler

    test = {'my_function': (),
            'print_signal': (),
            'another_signal': (),}

    def my_function(a, b, c):
        test['my_function'] = (a, b, c)

    my_function = signaler(my_function)

    # Call the signaler like a normal function
    my_function(1, 2, 3)
    assert test['my_function'] == (1, 2, 3)


    def print_signal(value1, value2):
        test['print_signal'] = (value1, value2)

    my_function.on('my_signal', print_signal)
    my_function.fire('my_signal', 1, 2)
    assert test['my_function'] == (1, 2, 3)  # Fire called, the function was not called
    assert test['print_signal'] == (1, 2)

    def another_signal(value1, value2):
        test['another_signal'] = (value1, value2)

    my_function.on('my_signal', another_signal)
    my_function.fire('my_signal', 2, 2)
    assert test['my_function'] == (1, 2, 3)  # Fire called, the function was not called
    assert test['print_signal'] == (2, 2)
    assert test['another_signal'] == (2, 2)

    my_function.off('my_signal', print_signal)
    my_function.fire('my_signal', 3, 2)
    assert test['my_function'] == (1, 2, 3)  # Fire called, the function was not called
    assert test['print_signal'] == (2, 2)  # No Change
    assert test['another_signal'] == (3, 2)

    print(my_function.get_signal('my_signal'))
    # print = [<function ...another_signal at 0x056076F0>]

    my_function.block('my_signal')
    my_function.fire('my_signal', 4, 5)
    assert test['my_function'] == (1, 2, 3)  # Fire called, the function was not called
    assert test['print_signal'] == (2, 2)  # No change blocked
    assert test['another_signal'] == (3, 2)  # No change blocked

    # No print!
    my_function.block('my_signal', False)
    my_function.fire('my_signal', 5, 6)
    assert test['my_function'] == (1, 2, 3)  # Fire called, the function was not called
    assert test['print_signal'] == (2, 2)  # No change off and blocked
    assert test['another_signal'] == (5, 6)  # No change blocked
    # print = another_signal called 5 6 False


if __name__ == '__main__':
    test_basics()
