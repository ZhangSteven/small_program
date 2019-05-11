# coding=utf-8
#
# From book: Functional Programming in Python, by David Mertz
#

from toolz.functoolz import juxt
from operator import add, mul


def catString(s1, s2):
    """
    Cat two items together as strings.
    """
    if s1 != None and s2 != None:
        return str(s1) + ' ' + str(s2)
    elif s1 == None and s2 == None:
        return ''
    elif s1 == None:
        return str(s2)
    elif s2 == None:
        return str(s1)



def doIt(f, *args):
    return f(*args)



def doAllFunctions(fns, *args):
    """
    Call all functions 
    """



if __name__ == '__main__':
    print(catString('hello', 'shutao'))
    print(catString(5, 'X'))
    print(catString('hello', None))
    print(catString(None, 'ok'))
    print(catString(None, None))

    """
    Note: 'map' allows a function taking multiple arguments to be called. In this
    case, it just take one argument from each list and stops as long as one of the
    list is exhausted. So the result would be:

    0 10
    1 20
    2 30
    """
    for x in map(catString, range(5), [10,20,30]):
        print(x)


    """
    What if we want multiple functions to called for the same set of arguments?
    """
    doAllFunctions = lambda fns, *args: [list(map(fn, *args)) for fn in fns]
    hello = lambda first, last: 'hello ' + catString(first, last)
    bye = lambda first, last: 'bye ' + catString(first, last)
    for x in doAllFunctions([hello, bye], ['steven', 'isaac'], ['zz', 'zhang']):
        print(x)


    """
    We can use the 'juxt' function from the third party library to achieve a
    similar result: calling multiple functions on the same set of arguments.

    Except that the list of results is a list of tuples. For example, the
    result for the below will look like:

    (1, 0)
    (4, 3)
    (7, 10)
    (10, 21)
    (13, 36)
    """
    for x in map(juxt([add, mul]), range(5), map(lambda x: 2*x+1, range(0,20))):
        print(x)


    """
    If we want to two lists, one for outcome of each function, like below:

    (1, 4, 7, 10, 13) and (0, 3, 10, 21, 36)

    Then we can use zip() to transpose the list:

    [(1,0), (4,3), (7,10), (10,21), (13,36)]

    into the new list:

    [(1, 4, 7, 10, 13), (0, 3, 10, 21, 36)]
    """
    out = zip(*map(juxt([add, mul]), range(5), map(lambda x: 2*x+1, range(0,20))))
    for x in out:
        print(x)
