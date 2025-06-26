class A:
    decision_path = []
    length = None

class B:
    e = A()

b = B()
b.e.length = 15
#b.e.decision_path = []
b.e.decision_path.append("good")
b.e.decision_path.append("morning")

print(b.e.__dict__)
