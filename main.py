from up_bfgp.bfgp import BestFirstGeneralizedPlanner
from glob import glob

path_to = "up-bfgp/tests/domains/gripper/"
pddl_domain = path_to + "domain.pddl"
pddl_problems = glob(path_to + "p??.pddl")
print(pddl_problems)

with BestFirstGeneralizedPlanner() as planner:
    problems = planner.generate_problems(pddl_domain, pddl_problems)
    plan = planner.solve(problems)
    print(plan)

