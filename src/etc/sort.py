def argsort(list, *, key = None, reverse = False):
    new_list = [[i, e] for i, e in enumerate(list)]

    if key is None:
        fun = lambda r : r[1]
    else:
        fun = lambda r : key(r[1])
    
    new_list.sort(key = fun, reverse=reverse)
    arg = [ i for i, _ in new_list ]
    return arg


def sortarg(list, arg):
    return [ list[i] for i in arg ]

if __name__ == "__main__":
    from random import randint

    x = [ randint(0, 20) for i in range(10) ]
    print(x)
    y = argsort(x)
    print(x)
    print(y)
    z = sortarg(x, y)
    print(z)

