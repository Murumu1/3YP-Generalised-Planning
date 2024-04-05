import signal
import numpy as np
from matplotlib import pyplot as plt
import time
from generators import ProblemGenerator


def _limit_time(function, duration=60, *args, **kwargs):
    signal.signal(signal.SIGALRM, lambda signum, frame: TimeoutError())
    signal.alarm(duration)

    try:
        function(*args, **kwargs)
        feedback = True
    except TimeoutError:
        feedback = False
    finally:
        signal.alarm(0)

    return feedback


def tile_size_experiment_classical(generator: type[ProblemGenerator],
                                   min_size: int = 2,
                                   max_size: int = 10,
                                   step: int = 1):

    timings = np.array([])
    tile_sizes = np.array([])
    for i in range(min_size, max_size, step):
        current_generator = generator(auto=True, tile_size=i, problem_count=1)
        start = time.time()
        feedback = _limit_time(current_generator.solve_each)
        if feedback:
            end = time.time()
            np.append(timings, (start - end))
            np.append(tile_sizes, i)

    plt.plot(tile_sizes, timings)
    plt.ylabel("Time")
    plt.xlabel("Tile Size")
    plt.show()

