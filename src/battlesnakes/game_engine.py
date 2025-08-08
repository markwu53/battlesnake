from simp_entry import Snake
import random, time, uuid
import functional, snake_1vn, simp_entry

class GameEngine:
    def __init__(self):
        self.snakes: list[Snake] = None
        self.turn = None
        self.food = None
        self.width = 11
        self.height = 11
        self.id = None
        self.die_turn = {}
        self.start_time = None
        self.end_time = None
        self.game_steps = []

    def run(self):
        self.start_time = time.time()
        self.start()
        while len([snake for snake in self.snakes if snake.alive]) > 1:
            start_time = time.time()
            self.next_turn()
            end_time = time.time()
            diff_time = f"{end_time-start_time:.3f}s"
            print(self.turn, diff_time, [(snake.name, snake.alive) for snake in self.snakes])
            print()

        #save the last turn
        self.save_turn()

        self.end_time = time.time()
        self.end()

    def save_game(self):
        with open("last_game.log", "w") as fd:
            for game_step in self.game_steps:
                fd.write(f"{game_step}\n")

    def end(self):
        self.save_game()
        diff_time = f"{self.end_time-self.start_time:.3f}s"
        print(diff_time, self.die_turn)

    def start(self):
        self.id = str(uuid.uuid4())
        self.turn = 0
        self.snakes = [
            Snake( name="mark_snake_test RED", body=[(5,1), (5,1), (5,1)], health=100,),
            Snake( name="mark_snake_test BLUE", body=[(9,5), (9,5), (9,5)], health=100,),
            Snake( name="mark_snake_test GREEN", body=[(5,9), (5,9), (5,9)], health=100,),
            Snake( name="mark_snake_test YELLOW", body=[(1,5), (1,5), (1,5)], health=100,),
        ]
        for snake in self.snakes:
            snake.alive = True
            snake.delay = 0
        self.food = [(4,0), (10,4), (6,10), (0,6), (5,5)]

    def create_food(self):
        ncells = self.width * self.height
        while True:
            food = random.randint(0, ncells-1)
            x = food % self.width
            y = food // self.width
            food = (x,y)
            if food not in [cell for snake in self.snakes if snake.alive for cell in snake.body]:
                if food not in self.food:
                    return food

    def save_turn(self):
        game_turn = {
            "id": self.id,
            "turn": self.turn,
            "nalive": len([snake for snake in self.snakes if snake.alive]),
            "snakes": [{
                "name": snake.name,
                "health": snake.health,
                "length": snake.length,
                "alive": snake.alive,
                "delay": snake.delay,
                "body": [cell for cell in snake.body],
            } for snake in self.snakes],
            "food": [f for f in self.food], #need to copy not reference
        }
        #print(game_turn)
        self.game_steps.append(game_turn)

    def call_snake_model(self, snake, game_state):
        if snake.name in [
            "mark_snake_test RED",
            "mark_snake_test BLUE",
        ]:
            if functional.special_experimenting_code(game_state, log=False): 
                return {"move": game_state["next_move"]}
            return snake_1vn.snake_1vn(game_state, log=False)
        elif snake.name in [
            #"mark_snake_test GREEN",
            "mark_snake_test YELLOW",
        ]:
            if simp_entry.main(game_state, log=False): 
                return {"move": game_state["next_move"]}
        elif snake.name in [
            "mark_snake_test GREEN",
            #"mark_snake_test YELLOW",
        ]:
            if simp_entry.main(game_state, log=False): 
                return {"move": game_state["next_move"]}

        raise ValueError("no snake model specified")

    def next_turn(self):
        self.save_turn()

        for snake in self.snakes:
            if not snake.alive: continue
            game_state = self.assemble_game_state(snake)

            start_time = time.time()
            #main(game_state, log=False)

            try:
                result = self.call_snake_model(snake, game_state)
            except:
                print("ERROR")
                self.save_game()
                raise

            end_time = time.time()

            snake.delay = int((end_time-start_time)*1000)
            snake.next_move = dir_to_coord(snake.head, result["move"])

        #move and update body
        for snake in self.snakes:
            if not snake.alive: continue
            snake.body = [snake.next_move]+snake.body[:-1]
            snake.health -= 1
            snake.head = snake.body[0]

        #resolve who is alive
        snake_update_alive = [(snake, all([
                snake.alive,
                self.pos_on_board(snake.head),
                snake.health != 0,
                not any([snake.head in s.body[1:] and s.alive for s in self.snakes ]),
                not any([snake.head == s.head and s.alive and s.name != snake.name and s.length >= snake.length for s in self.snakes ]),
            ])) for snake in self.snakes]

        for snake, update_alive in snake_update_alive:
            if snake.alive and not update_alive:
                snake.alive = False
                self.die_turn[snake.name] = self.turn

        #eat food
        for snake in self.snakes:
            if not snake.alive: continue
            if snake.head in self.food:
                snake.body.append(snake.body[-1])
                snake.health = 100
                snake.length += 1
                self.food.remove(snake.head)

        #create food
        if len(self.food) == 0 or random.randint(0, 99) < 20:
            self.food.append(self.create_food())

        self.turn += 1

    def assemble_game_state(self, snake: Snake):
        snakes = [ {
                "name": snake.name,
                "health": snake.health,
                "body": reverse_coord(snake.body),
                "length": snake.length,
            } for snake in self.snakes if snake.alive
        ]
        me = {
            "name": snake.name,
            "health": snake.health,
            "body": reverse_coord(snake.body),
            "length": snake.length,
        }
        game_state = {
            "game": { "id": self.id },
            "turn": self.turn,
            "you": me,
            "board": {
                    "width": self.width,
                    "height": self.height,
                    "snakes": snakes,
                    "food": reverse_coord(self.food),
                },
        }
        return game_state

    def pos_on_board(self, pos):
        x,y = pos
        if x < 0:
            return False
        if y < 0:
            return False
        if x >= self.width:
            return False
        if y >= self.height:
            return False
        return True

def dir_to_coord(head, d):
    x,y = head
    if d == "left": x -= 1
    elif d == "right": x += 1
    elif d == "up": y += 1
    elif d == "down": y -= 1
    return (x,y)

def reverse_coord(cs):
    return [{"x":x, "y":y} for x,y in cs]

def run():
    game = GameEngine()
    game.run()

if __name__ == "__main__":
    run()
