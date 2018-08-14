

def test_basics():
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


if __name__ == '__main__':
    test_basics()
