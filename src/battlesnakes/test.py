def f():
    return (4,3)
a = (4, 3)
b = min(*f(), 2)
print(b)