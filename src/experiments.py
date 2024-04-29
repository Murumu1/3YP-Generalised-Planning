"""
**Experiments for path finding problems**

This module provides experiments to test classical and generalised planners.
Requires generators.py.

Functions:
    - ``variable_experiment``: Tests a planner on a variable under time.
    - ``efficiency_experiment``: Compares efficiency of solution between classical and generalised planners

Example usage::

    # Create an experiment
    plot = variable_experiment(SnakeProblemGenerator, problem_count=3)

    # Display the plot
    plot.show()
"""

import signal
import time
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from src.generators import ProblemGenerator
from src.validators import non_negative_and_non_zero


def limit_time(function, duration=60, *args, **kwargs):
    """
    Limit the execution time of a function.

    Arguments:
        function (callable): The function to be executed.
        duration (int): The maximum duration for the function to execute, in seconds.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        bool: True if the function executes within the specified duration, False otherwise.
    """

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


@non_negative_and_non_zero
def variable_experiment(generator: type[ProblemGenerator],
                        variable: str = 'tile_size',
                        solution: str = 'classical',
                        problem_count: int = 1,
                        min_size: int = 2,
                        max_size: int = 10,
                        step: int = 1,
                        timeout: int = 60,
                        display_images: bool = False) -> Figure:
    """
    Conducts an experiment varying a specified variable.

    Arguments:
        generator (Type[ProblemGenerator]): The type of problem generator to use.
        variable (str): The variable to be varied.
        solution (str): The solution method to use, either 'classical' or 'generalised'.
        problem_count (int): The number of problems to generate and solve.
        min_size (int): The minimum value of the variable.
        max_size (int): The maximum value of the variable.
        step (int): The step size for incrementing the variable.
        timeout (int): The maximum time allowed for each experiment iteration, in seconds.
        display_images (bool): Flag to display images after each problem has been generated.

    Returns:
        Figure: A matplotlib figure object showing the experiment results.
    """

    timings = []
    results = []
    for i in range(min_size, max_size, step):

        print("EXPERIMENT", str(i))

        kwargs = {
            'auto': True,
            'problem_count': problem_count,
            variable: i
        }

        current_generator = generator(**kwargs)
        start = time.time()

        if solution == 'classical':
            f = current_generator.solve_each
        elif solution == 'generalised':
            f = current_generator.solve_all
        else:
            raise NameError("solution must be either 'classical' or 'generalised'.")

        feedback = limit_time(f, duration=timeout)
        print(feedback)
        if feedback:
            end = time.time()
            timings.append(end - start)
            results.append(i)
            if display_images:
                current_generator.display_images()
        else:
            print("Couldn't finish in 60s")

    fig = plt.figure()
    plt.plot(results, timings, figure=fig)
    plt.title(f"Varying {variable} from {min_size} to {max_size}")
    plt.ylabel("time", figure=fig)
    plt.xlabel(variable, figure=fig)
    print(results, timings)

    return fig


@non_negative_and_non_zero
def efficiency_experiment(generator: type[ProblemGenerator],
                          problem_count: int = 2,
                          min_program_lines: int = 10,
                          max_program_lines: int = 100,
                          tile_size: int = 5):
    """
    Conducts an efficiency experiment comparing classical planning to generalised planning.

    Arguments:
        generator (Type[ProblemGenerator]): The type of problem generator to use.
        problem_count (int): The number of problems to generate and solve.
        tile_size (int): The size of the tiles in the environment.
        min_program_lines (int):
        max_program_lines (int):

    Returns:
        Figure: A matplotlib figure object showing the experiment results.
    """
    out_dir = 'tmp'

    kwargs = {
        'auto': True,
        'problem_count': problem_count,
        'tile_size': tile_size,
        'plan_directory': out_dir
    }

    scores = []

    generator = generator(**kwargs)
    classical_results = generator.solve_each()
    generalised_results = generator.solve_all()

    if len(classical_results) != len(generalised_results) or len(classical_results) != problem_count:
        return RuntimeError("Results not generated correctly...")

    generalised_plans = ...

    for i in range(len(classical_results)):
        scores.append(len(classical_results[i].plan) / len(generalised_plans[i]))

    fig = plt.figure()
    plt.plot(range(1, problem_count + 1), scores, figure=fig)
    plt.ylabel("scores", figure=fig)
    plt.xlabel("problem count", figure=fig)

    return fig
