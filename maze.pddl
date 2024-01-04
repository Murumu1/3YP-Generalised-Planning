(define (domain maze)

  (:requirements 
    :strips 
    :typing 
    :negative-preconditions 
    :conditional-effects
    :disjunctive-preconditions
  )

  (:types 
    position
    direction
  )

  (:predicates
    (inc ?a ?b - position)
    (dec ?a ?b - position)
    (at ?x ?y - position)
    (path ?x ?y - position)
    (facing ?d - direction)
    (is-north ?d - direction)
    (is-east ?d - direction)
    (is-south ?d - direction)
    (is-west ?d - direction)
    (left-rot ?d ?dn - direction)
    (right-rot ?d ?dn - direction)
  )
  
  (:action move-forward
    :parameters (?x ?y ?xn ?yn - position ?d - direction)
    :precondition (and 
      (at ?x ?y)
      (path ?xn ?yn)
      (facing ?d)
      (or
        (and (is-north ?d) (dec ?y ?yn) (at ?xn ?y))
        (and (is-south ?d) (inc ?y ?yn) (at ?xn ?y))
        (and (is-east ?d) (inc ?x ?xn) (at ?x ?yn))
        (and (is-west ?d) (dec ?x ?xn) (at ?x ?yn))
      )
    )
    :effect (and
      (at ?xn ?yn)
      (not (at ?x ?y))
    )
  )

  (:action turn-left
    :parameters (?d ?dn - direction)
    :precondition (and 
      (facing ?d)
      (left-rot ?d ?dn)
    )
    :effect (and 
      (facing ?dn)
      (not (facing ?d))
    )
  )

  (:action turn-right
    :parameters (?d ?dn - direction)
    :precondition (and 
      (facing ?d)
      (right-rot ?d ?dn)
    )
    :effect (and
      (facing ?dn)
      (not (facing ?d))
    )
  )
)