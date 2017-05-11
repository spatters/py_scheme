(define (fact n)
  (if (= n 1)
    1
    (* n (fact (- n 1)))))

(define (sq x) (* x x))
(set! x 42)
(set! y (sq x))
