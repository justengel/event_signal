import event_signal

try:
    import mp_event_loop
except ImportError:
    mp_event_loop = None


@event_signal.signaler(fire_results=True)
def run_calculations(a, b):
    return a**2 + b**2


def test_mp_event_loop_compat():
    if mp_event_loop is None:
        return

    event_signal.multiprocessing_support()

    results = []

    def save_results(res):
        results.append(res)

    run_calculations.on('change', save_results)

    out_res = []

    def process_output(event):
        out_res.append(event.results)

    with mp_event_loop.Pool(output_handlers=process_output) as loop:
        loop.add_event(run_calculations, 1, 2)
        loop.add_event(run_calculations, 2, 3)
        loop.add_event(run_calculations, 4, 5)

    print(results)
    assert 5 in results
    assert 13 in results
    assert 41 in results

    print(out_res)
    assert 5 in out_res
    assert 13 in out_res
    assert 41 in out_res


if __name__ == '__main__':
    test_mp_event_loop_compat()
    print('All tests finished!')
