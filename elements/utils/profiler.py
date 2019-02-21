import cProfile
import io
import pstats
from time import process_time as timer, perf_counter as timer2


def profile(fun, num=1, out_lines="all"):

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
        if out_lines:
            ps.print_stats()
            tmp = s.getvalue()
            tmp = tmp if out_lines == "all" else "\n".join(tmp.splitlines()[0:out_lines])
            print(tmp)
        return retval

    return inner