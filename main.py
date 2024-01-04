from unified_planning.engines import CompilationKind
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner, Compiler
import unified_planning as up
from generator import MazeProblemGenerator
from glob import glob

path_to = "problems/"
pddl_domain = "maze.pddl"
pddl_problem = path_to + "maze2.pddl"

problem_generator = MazeProblemGenerator(pddl_domain)
problem = problem_generator.generate_problem("maze_problem")

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
        print(f"Found plan in {len(result.plan.actions)} steps!")
        for i, action in enumerate(result.plan.actions):
            print(f"{i}: {action}")
    else:
        print("Unable to find a plan.")
