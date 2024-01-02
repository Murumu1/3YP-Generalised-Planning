; It looks like this:
;
; J . . X
; . . . .
; . . . .
; . . . .

(define (problem maze0)

(:domain maze)
(:objects 
  x1 x2 x3 x4 y1 y2 y3 y4 - position 
  north east south west - direction
)
(:init
  (inc x1 x2) (inc x2 x3) (inc x3 x4)
  (inc y1 y2) (inc y2 y3) (inc y3 y4)
  (dec x4 x3) (dec x3 x2) (dec x2 x1)
  (dec y4 y3) (dec y3 y2) (dec y2 y1)
  (is-north north) 
  (is-east east)
  (is-south south)
  (is-west west)
  (left-rot north west)
  (left-rot west south)
  (left-rot south east)
  (left-rot east north)
  (right-rot north east)
  (right-rot east south)
  (right-rot south west)
  (right-rot west north)
  (facing north)
  (at x1 y1))
(:goal
  (at x4 y1))
)