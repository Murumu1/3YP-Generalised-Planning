import argparse
from generators import *

parser = argparse.ArgumentParser(description="PDDL Path Solver",
                                 formatter_class=argparse.RawTextHelpFormatter)

domain_choices = ["blockly_maze", "directional_maze", "non_directional_maze", "snake"]
solution_choices = ["each", "all"]

parser.add_argument("-d", "--domain", choices=domain_choices, default="blockly_maze", required=False)
parser.add_argument("-r", "--display_problems", type=bool, default=False, required=False)
parser.add_argument("-t", "--solution_type", choices=solution_choices, default="each", required=False)

parser.add_argument("-a", "--auto", type=bool, default=True, required=False)
parser.add_argument("-p", "--problem_count", type=int, default=5, required=False)
parser.add_argument("-l", "--program_lines", type=int, default=10, required=False)
parser.add_argument("-s", "--tile_size", type=int, default=5, required=False)
parser.add_argument("-i", "--image_directory", type=str, default="image_temp", required=False)
parser.add_argument("-j", "--plan_directory", type=str, default="plan_temp", required=False)
parser.add_argument("-k", "--problem_directory", type=str, default="problem_temp", required=False)
parser.add_argument("-c", "--apple_count", type=int, default="5", required=False)

if __name__ == '__main__':
    args = parser.parse_args()
    options = vars(args)

    generator = BlocklyMazeProblemGenerator
    if options["domain"] == "blockly_maze":
        generator = BlocklyMazeProblemGenerator
    elif options["domain"] == "directional_maze":
        generator = DirectionalProblemReducedMazeProblemGenerator
    elif options["domain"] == "non_directional_maze":
        generator = NonDirectionalProblemReducedMazeProblemGenerator
    elif options["domain"] == "snake":
        generator = SnakeProblemGenerator

    generator = generator(**options)

    if options["display_problems"]:
        generator.display_problems()

    if options["solution_type"] == "each":
        generator.solve_each()
    elif options["solution_type"] == "all":
        generator.solve_all()

