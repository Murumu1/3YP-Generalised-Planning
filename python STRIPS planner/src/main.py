from domain.type import Type

predicates = [
    {"position": "one"},
]

plan = []


def move_up_from_one():
    if {"position": "one"} in predicates:
        predicates.remove({"position": "one"})
        predicates.append({"position": "two"})
        plan.append("move_up_from_one")
        return True
    return False


actions = [
    move_up_from_one
]

goal = {"position": "two"}

if __name__ == '__main__':

    while True:
        for action in actions:
            if action():
                break
        else:
            print("No plan found...")

        if goal in predicates:
            print(plan)
            break


