import os.path
import os.path
import shutil
from typing import Union, Optional

import pygame
import unified_planning as up
from unified_planning.engines import CompilationKind, PlanGenerationResultStatus
from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.model import Problem, Object
from unified_planning.shortcuts import OneshotPlanner, get_environment
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from util.environments import Environment
from util.environment_object import EnvironmentObject
import glob
import math


class ProblemGenerator:

    def __init__(self, domain, **options):
        self._domain = domain
        self.__reader = PDDLReader()
        self._set_arguments(**options)
        self._clear_directory(self._image_directory)
        self._clear_directory(self._problem_directory)
        self._set_problems()
        get_environment().credits_stream = None

    def _set_arguments(self, **options) -> None:
        self._auto: bool = options.get("auto", False)
        self._problem_count: int = options.get("problem_count", 10)
        self._program_lines: int = options.get("program_lines", 10)
        self._tile_size: int = options.get("tile_size", 5)
        self._image_directory: str = options.get("image_directory", "images_temp")
        self._plan_directory: str = options.get("plan_directory", "plan_temp")
        self._problem_directory: str = options.get("problem_directory", "problem_temp")

    def _set_problems(self) -> None:
        self._problems: list[Problem] = []
        self._environments: list[Environment] = []
        for i in range(self._problem_count):
            pygame.init()
            environment = self._generate_environment()
            self._environments.append(environment)
            self._add_problem(environment)

    @staticmethod
    def _clear_directory(directory):
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

    def _generate_environment_manual(self) -> Environment:
        pass

    def _generate_environment_auto(self) -> Environment:
        pass

    def _generate_environment(self) -> Environment:
        return self._generate_environment_auto() if self._auto else self._generate_environment_manual()

    def _add_problem(self, environment: Environment) -> None:
        self._problem = self.__reader.parse_problem(f"domains/{self._domain}.pddl")
        self._problem.name = f"{self._domain}{len(self._problems)}"
        self._obj_map = {}
        self._setup_problem(environment)
        self._problems.append(self._problem)
        print("[DEBUG] problem added")

    def _setup_problem(self, environment: Environment) -> None:
        raise NotImplementedError

    def _add_mapping(self, env_obj: EnvironmentObject, *pddl_objects: Object) -> None:
        eo_hash = hash(env_obj)
        pddl_objects = list(pddl_objects)
        observed_mapping = self._obj_map.get(eo_hash)
        if observed_mapping:
            self._obj_map[eo_hash].extend(pddl_objects)
        else:
            self._obj_map[eo_hash] = pddl_objects

    def _get_mapping(self, env_obj: EnvironmentObject) -> Union[Object, list[Object]]:
        eo_hash = hash(env_obj)
        mapping = self._obj_map.get(eo_hash, [])
        if len(mapping) == 1:
            return mapping[0]
        return mapping

    def _save_pygame_environment(self, screen: pygame.Surface):
        if not os.path.exists(self._image_directory):
            os.makedirs(self._image_directory)
        pygame.image.save(screen, f"{self._image_directory}/{self._domain}{len(self._environments)}.jpg")
        print(f"[DEBUG] {self._domain} environment generated successfully")

    def save_as_pddl(self) -> None:
        if not os.path.exists(self._problem_directory):
            os.makedirs(self._problem_directory)
        for problem in self._problems:
            file_path = f"{self._problem_directory}/{problem.name}.pddl"
            open(file_path, 'a').close()
            writer = PDDLWriter(problem)
            writer.write_problem(file_path)

    def display_problems(self) -> None:
        """Display problems for debugging purposes"""
        for i, problem in enumerate(self._problems):
            print(f"Problem {i}:")
            print(problem)

    def display_images(self) -> None:
        """Display images as iPython plots (For Notebook purposes only)"""
        images = []
        for img_path in glob.glob(f"{self._image_directory}/*.jpg"):
            images.append(mpimg.imread(img_path))
        plt.figure(figsize=(20, 10))
        columns = math.floor(math.sqrt(len(images)))
        for i, image in enumerate(images):
            plt.subplot(len(images) // columns + 1, columns, i + 1)
            plt.imshow(image)
            plt.axis("off")

    def solve_each(self) -> bool:
        """Solves each problem one by one using classical planning"""
        all_passing = True
        for i, problem in enumerate(self._problems):
            print(f"Plan {i + 1}:")
            with OneshotPlanner(problem_kind=problem.kind) as planner:
                result = planner.solve(problem)
                print(f"Status: {result.status}")
                if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                    print(f"Found plan with {len(result.plan.actions)} steps!")
                    for j, action in enumerate(result.plan.actions):
                        print(f"{j}: {action}")
                else:
                    print("Unable to find a plan.")
                    all_passing = False
            print("")
        return all_passing

    def solve_all(self) -> bool:
        """Solves all problems at once using generalised planning"""
        with up.environment.get_environment().factory.FewshotPlanner(name="bfgp") as planner:
            planner.set_arguments(program_lines=self._program_lines, theory="cpp")
            result = planner.solve(self._problems, output_stream=None)
            return all(r == PlanGenerationResultStatus.SOLVED_SATISFICING for r in result)
