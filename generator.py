# coding=utf-8
#
# From book: Functional Programming in Python, by David Mertz
#
# About generator function

from itertools import takewhile
from itertools import islice, tee, accumulate
from operator import mul


def get_primes():
    """
    Simple lazy Sieve of Eratosthenes
    """
    candidate = 2
    found = []
    while True:
        if all(candidate % p != 0 for p in found):
            yield candidate
            found.append(candidate)

        candidate += 1



def fabonacci():
    a, b = 0, 1
    while True:
        yield a 
        a, b = b, a+b 



if __name__ == '__main__':
    """
    Take the first 10 primes
    """
    for _, p in zip(range(10), get_primes()):
        print(p, end = ' ')


    """
    Another way to do it
    """
    print()
    takeSecond = lambda el: el[1]
    print(list(map(takeSecond, zip(range(10), get_primes()))))


    """
    Yet another way to take the first 10 primes
    """
    print(list(map(takeSecond
                  , takewhile(lambda el: el[0] < 10
                             , enumerate(get_primes())))))


    """
    Using the built in 'islice' function, to retrieve the elements of index
    [0, 10)    
    """
    print(list(islice(get_primes(), 0, 10)))



    """
    The new problem: find out the prime number, which makes the product of
    all prime numbers equal or smaller than it > 1,000

    prime   sum of sqaures
    2       2
    3       6
    5       30
    ...
    ?       > 1,000

    """
    s, t = tee(get_primes())
    pairs = zip(t, accumulate(s, mul))
    for (prime, total) in takewhile(lambda x: x[1] < 1000, pairs):
        print(prime, total)