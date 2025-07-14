class Snake:
    def __init__(self, name, body, health):
        self.name = name
        self.body = body
        self.health = health
        self.length = None
        self.head = None
        self.neck = None
        self.tail = None
    def dict(self):
        return {k: self.__dict__[k] for k in ["name", "health", "body"]}

class Game:
    def __init__(self):
        self.me = None
        self.other = None
        self.others = None

g = Game()
g.me = Snake("Mark", [(1,0), (2,0)], 93)
print(g.me.dict())