import random
a = list(range(5))
b = random.choice(a)

print(b)

def sort(xs):
    if len(xs) <= 1:
        return xs
    pivot = len(xs) // 2
    return sort(xs[:pivot]) + [xs[pivot]] + sort(xs[pivot+1:])

def sort(xs):
    return xs if len(xs) <= 1 else [
        sort(xs[:pivot]) + [xs[pivot]] + sort(xs[pivot+1:])
        for pivot in [len(xs) // 2]
    ][0]

