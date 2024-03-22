(define (domain maze)

  (:requirements 
    :strips 
    :typing 
    :negative-preconditions
  )

  (:types 
    position
  )

  (:predicates
    (path ?a ?b - position)
    (at ?x - position)
  )
  
  (:action move
    :parameters (?x ?xn - position)
    :precondition (and
      (at ?x)
      (path ?x ?xn)
    )
    :effect (and
      (at ?xn)
      (not (at ?x))
    )
  )
)