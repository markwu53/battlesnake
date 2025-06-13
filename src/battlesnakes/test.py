from itertools import product

a = [
    set([1,2]),
    set([4]),
    set([5,6,7]),
]

for path in product(*a):
    print(path)