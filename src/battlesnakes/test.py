def irange(a, b):
    return list([a] if a == b else range(a, b+1) if a < b else range(a,b-1,-1,))

print(irange(7,4))
