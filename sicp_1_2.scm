(define (factorial n)
  (define (fact-iter product counter max-count)
    (if (> counter max-count)
        product
        (fact-iter (* counter product)
                   (+  counter 1)
                   max-count)))
  (fact-iter 1 1 n))


(define (fib n)
  (define (fib-iter a b counter)
    (if (= counter 0)
        b
        (fib-iter b
                  (+ a b)
                  (- counter 1))))
  (fib-iter 1 0 n))


(define (new-cons x y)
  (lambda (m) (m x y)))

(define (new-car z)
  (z (lambda (p q) p)))

(define (new-cdr z)
  (z (lambda (p q) q)))


(define (append x y)
  (if (= x ())
    y
    (cons (car x) (append (cdr x) y))))
