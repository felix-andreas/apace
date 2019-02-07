import cProfile
import io
import pstats
from time import process_time as timer, perf_counter as timer2


def profile(fun, num=1, print_pstats=True):

    """A decorator that uses cProfile to profile a function."""

    def inner(*args, **kwargs):
        print(f"\n{fun.__name__}:")
        pr = cProfile.Profile()
        t1 = timer()
        t2 = timer2()
        pr.enable()
        for _ in range(num):
            retval = fun(*args, **kwargs)
        pr.disable()
        print(f"{'': <9}{timer.__name__}: {timer() - t1:.9f}s")
        print(f"{'': <9}{timer2.__name__}: {timer2() - t2:.9f}s")
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        if print_pstats:
            ps.print_stats()
            print(s.getvalue())
        return retval

    return inner