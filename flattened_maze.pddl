(define (domain maze)

  (:requirements 
    :strips 
    :typing 
    :negative-preconditions 
    :conditional-effects
  )

  (:types 
    position
  )

  (:predicates
    (path ?a ?b - position)
    (at ?x - position)
  )
  
  (:action move-up
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