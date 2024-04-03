;Domain for Snake
;Domain is a slightly modified version of IPC 2018 Optimal Snake
;https://github.com/fawcettc/planning-instances/blob/master/ipc-2018-optimal/snake/ipc-2018-optimal-snake.pddl

(define (domain snake)

(:requirements 
    :strips 
    :typing 
    :negative-preconditions
    :equality
)

(:types position)
(:constants dummypoint - position)

(:predicates
    (path ?x ?y - position)
    (head-at ?x - position)
    (tail-at ?x - position)
    (body-con ?x ?y - position)
    (blocked ?x - position)
    (apple-at ?x - position)
    (spawn-apple ?x - position)
    (next-apple ?x ?y - position)
)


(:action move
    :parameters (?head ?newhead ?tail ?newtail - position)
    :precondition (and 
        (head-at ?head)
        (path ?head ?newhead)
        (tail-at ?tail)
        (body-con ?newtail ?tail)
        (not (blocked ?newhead))
        (not (apple-at ?newhead))
    )
    :effect (and 
        (blocked ?newhead)
        (head-at ?newhead)
        (body-con ?newhead ?head)
        (not (head-at ?head))
        (not (blocked ?tail))
        (not (tail-at ?tail))
        (not (body-con ?newtail ?tail))
        (tail-at ?newtail)
    )
)

(:action move-and-eat
    :parameters (?head ?newhead ?spawn ?nextspawn - position)
    :precondition (and
        (head-at ?head)
        (path ?head ?newhead)
        (not (blocked ?newhead))
        (apple-at ?newhead)
        (spawn-apple ?spawn)
        (next-apple ?spawn ?nextspawn)
        (not (= ?spawn dummypoint))
    )
    :effect (and
        (blocked ?newhead)
        (head-at ?newhead)
        (body-con ?newhead ?head)
        (not (head-at ?head))
        (not (apple-at ?newhead))
        (apple-at ?spawn)
        (not (spawn-apple ?spawn))
        (spawn-apple ?nextspawn)
    )
)

(:action move-and-eat-no-spawn
    :parameters (?head ?newhead - position)
    :precondition
    (and
        (head-at ?head)
        (path ?head ?newhead)
        (not (blocked ?newhead))
        (apple-at ?newhead)
        (spawn-apple dummypoint)
    )
    :effect
    (and
        (blocked ?newhead)
        (head-at ?newhead)
        (body-con ?newhead ?head)
        (not (head-at ?head))
        (not (apple-at ?newhead))
    )
)

)