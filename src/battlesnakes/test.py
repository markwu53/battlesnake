
xx1 = [(x1,) for x1 in range(3)]
xx2 = [(x1,x2) for x1 in range(3) for x2 in range(3) if x1 <= x2]
xx3 = [(x1,x2,x3) for x1 in range(3) for x2 in range(3) for x3 in range(3) if x1 <= x2 <= x3]
xx3 = [tuple(x*2+2 for x in xx) for xx in xx3]
print(xx3)