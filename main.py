from unified_planning.engines import CompilationKind
from unified_planning.shortcuts import OneshotPlanner
import unified_planning as up
from up_bfgp import BestFirstGeneralizedPlanner
from generator import MazeProblemGenerator

pddl_domain = "maze.pddl"
problem_generator = MazeProblemGenerator(pddl_domain)
# problem = problem_generator.generate_problem("maze_problem")

# with OneshotPlanner(problem_kind=problem.kind) as planner:
#     result = planner.solve(problem)
#     if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
#         print(f"Found plan with {len(result.plan.actions)} steps!")
#         for i, action in enumerate(result.plan.actions):
#             print(f"{i}: {action}")
#     else:
#         print("Unable to find a plan.")

problems = [
    problem_generator.generate_problem("maze_problem") for i in range(5)
]

with BestFirstGeneralizedPlanner(program_lines=20) as planner:
    result = planner.solve(problems)
    if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
        print(f"Found plan with {len(result.plan.actions)} steps!")
        for i, action in enumerate(result.plan.actions):
            print(f"{i}: {action}")
    else:
        print("Unable to find a plan.")
