# coding=utf-8
#
# From book: Functional Programming in Python, by David Mertz
#
# About generator function

from itertools import takewhile
from itertools import islice


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
    Using the built in library is the easiest to get first 10 elements
    """
    print(list(islice(get_primes(), 0, 10)))
