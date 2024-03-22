import os.path
import os.path
import shutil
import unified_planning as up
from unified_planning.engines import CompilationKind, PlanGenerationResultStatus
from unified_planning.io import PDDLReader
from unified_planning.model import Problem
from unified_planning.shortcuts import OneshotPlanner
from util.constants import *


# TODO: Add Options
class ProblemGenerator:

    def __init__(self, problem_count: int, **options):

        self._reader = PDDLReader()
        if os.path.isdir(MAZE_DIRECTORY):
            shutil.rmtree(MAZE_DIRECTORY)
        os.mkdir(MAZE_DIRECTORY)
        self._problems: list[Problem] = []

    def display_problems(self) -> None:
        """
        Display problems for debugging purposes
        """
        for i, problem in enumerate(self._problems):
            print(f"Problem {i}:")
            print(problem)

    def solve_each(self) -> bool:
        """
        Solves each problem one by one using classical planning
        """
        all_passing = True
        for i, problem in enumerate(self._problems):
            print(f"Plan {i + 1}:")
            with OneshotPlanner(problem_kind=problem.kind) as planner:
                result = planner.solve(problem)
                if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                    print(f"Found plan with {len(result.plan.actions)} steps!")
                    for j, action in enumerate(result.plan.actions):
                        print(f"{j}: {action}")
                else:
                    print("Unable to find a plan.")
                    all_passing = False
            print("")
        return all_passing

    def solve_all(self, program_lines: int = 15) -> bool:
        """
        Solves all problems at once using generalised planning
        :param program_lines: constraint on the maximum number of lines available to the planner
        """
        with up.environment.get_environment().factory.FewshotPlanner(name="bfgp") as planner:
            planner.set_arguments(program_lines=program_lines, theory="cpp")
            result = planner.solve(self._problems, output_stream=None)
            return all(r == PlanGenerationResultStatus.SOLVED_SATISFICING for r in result)
