class A:
    x = None
    y = None

class B:
    a = A()

b = B()

#call 1
b.a.x = (1,2)
b.a.y = (3,4)
print(b.a.__dict__)

#call 2
b.a.y = (5,6)
print(b.a.__dict__)
