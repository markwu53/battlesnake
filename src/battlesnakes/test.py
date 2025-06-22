class A:
    x = 1
    y = None
    z = "good"

a = A()
a.w = "new"
#a.x = 5
b = a.__dict__
print(b)
print(A.x)
print(a.x)

# To get class attributes too:
print({k: getattr(a, k) for k in dir(a) if not k.startswith('__') and not callable(getattr(a, k))})
