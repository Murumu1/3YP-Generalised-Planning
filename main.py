from generators import ComplexProblemGenerator, PartiallySolvedProblemGenerator
import unified_planning as up
import unified_planning.shortcuts

# TODO: Observe time taken to solve along side program lines
# TODO: Add test suite and graphs to show performance of planners
# TODO: Add argparse so planners can be run through terminal (ext.)
# TODO: Start writing structure on report
# TODO: Efficiency of solution: classical plan lines/generalised plan lines * 100

if __name__ == '__main__':
    up.shortcuts.get_environment().credits_stream = None
    pspg = PartiallySolvedProblemGenerator(3)
    pspg.solve_all(program_lines=10)
