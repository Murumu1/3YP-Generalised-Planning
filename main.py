from unified_planning.engines import CompilationKind
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner, Compiler
from generator import MazeProblemGenerator
from glob import glob


path_to = "problems/"
pddl_domain = "maze.pddl"
pddl_problem = path_to + "maze2.pddl"

problem_generator = MazeProblemGenerator(pddl_domain)
problem = problem_generator.generate_problem("maze_problem")
print(problem)

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)

print(result.plan)