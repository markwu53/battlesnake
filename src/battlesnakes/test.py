from functools import partial

def add(a, b):
    return a+b

x = partial(add, 5)(6)
print(x)