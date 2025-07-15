import time

#these class variables are used to trick the editor to display them in intellisense

class DecisionSupport:
    def __init__(self):
        self.n_other = 1
        self.allowed_moves = None
        self.food_good = None
        self.food_target = None
        self.head_distance = None
        self.head_path_distance = None
        self.collision_type = None
        self.avoid_points = None
        self.situation = None
        self.move_connected_group = None

class DecisionAux:
    def __init__(self):
        self.other_allowed_moves = None
        self.food_near = None
        self.food_worth = None
        self.collision_food = None
        self.border_distance = None
        self.collision_points = None
        self.collision_point = None
        self.possible_collision_points = None
        self.distance_map = None
        self.my_territory = None
        self.other_territory = None
        self.equal_territory = None
        self.equal_border = None
        self.moves_info = None

class Game:
    def __init__(self):
        self.state = None
        self.me = None
        self.other = None
        self.others = None
        self.snakes = None
        self.food = None
        self.next_coord = None
        self.occupied_cells = None
        self.dir_order = [(0,1), (-1,0), (0,-1), (1,0)]
        self.log = {}
        self.big = {}
        self.decision_path = []
        self.e = DecisionSupport()
        self.x = DecisionAux()

class Snake:
    def __init__(self, name, body, health, id=None):
        self.name = name
        self.body = body
        self.health = health
        self.length = None
        self.head = None
        self.neck = None
        self.tail = None
        self.id = id

    def dict(self):
        return {k: self.__dict__[k] for k in ["name", "health", "body", "id"]}

g = Game()


######################################################
# utility functions
######################################################

def get_coord(ds):
    return [(d["x"], d["y"]) for d in ds]

def get_adjacent_dir(p, q):
    x,y = p
    nx,ny = q
    if nx > x:
        return "right"
    if nx < x:
        return "left"
    if ny > y:
        return "up"
    return "down"

def get_next_move(head_coord, next_head_coord):
    return get_adjacent_dir(head_coord, next_head_coord)

def pos_on_board(pos):
    x,y = pos
    if x < 0:
        return False
    if y < 0:
        return False
    if x >= g.state["board"]["width"]:
        return False
    if y >= g.state["board"]["height"]:
        return False
    return True

def on_border(p):
    x,y = p
    if x == 0 or x == g.state["board"]["width"]-1:
        return True
    if y == 0 or y == g.state["board"]["height"]-1:
        return True
    return False

def off_border_1(p):
    return not on_border(p) and any([on_border(q) for q in adj_cells(p)])

def adj_cells(pos):
    x,y = pos
    moves = [(1,0), (-1,0), (0,1), (0,-1)]
    npos = [(a+x,b+y) for a,b in moves]
    npos = [p for p in npos if pos_on_board(p)]
    return npos

def occupied_cells(step):
    #not including head
    #assuming no die
    #assuming no eating food
    #if eating food it will be more
    sbody = []
    for s in g.snakes:
        body = s.body
        if s.health == 100:
            #eat food, tail will not move in the next step
            body = body + [body[-1]]
        sbody.append(body[:-step])
    cells = [c for s in sbody for c in s]
    return cells

def first_group(alist, reverse=False):
    #result is a list of tuple of (item, rank)
    if len(alist) == 0:
        return []
    result_dict = {}
    for item, rank in alist:
        if rank not in result_dict:
            result_dict[rank] = []
        result_dict[rank].append(item)
    result = list(result_dict.items())
    result.sort(reverse=reverse)
    result = result[0][1]
    return result

def distance_pq(p, q):
    x1,y1 = p
    x2,y2 = q
    distance = abs(x1-x2) + abs(y1-y2)
    return distance

def is_adjacent(p, q):
    return distance_pq(p, q) == 1

def path_distance_pq(p, q, occupied=None):
    if occupied is None:
        occupied = g.occupied_cells[0]
    #remove q from occupied otherwise there is no path
    occupied = [p for p in occupied if p != q]
    layers = path_connected_layers(p, occupied)
    for i,layer in enumerate(layers):
        if q in layer:
            return i
    return 999

def path_connected_layers(p, occupied=None):
    if occupied is None:
        occupied = g.occupied_cells[0]
    #remove p from occupied
    occupied = [q for q in occupied if q != p]
    layers = [set([p])]
    layer = set([q for q in adj_cells(p) if q not in occupied])
    while len(layer) != 0:
        layers.append(layer)
        layer = set([x for q in layer for x in adj_cells(q) if x not in occupied and x not in layers[-2]])
    return layers

def path_connected_set(p, occupied=None):
    if occupied is None:
        occupied = g.occupied_cells[0]
    layers = path_connected_layers(p, occupied)
    return set([q for layer in layers for q in layer])

def path_connected(p, q, occupied=None):
    if occupied is None:
        occupied = g.occupied_cells[0]
    occupied = [x for x in occupied if x != q]
    return q in path_connected_set(p, occupied)

def shortest_path_move(p, q, occupied=None):
    if is_adjacent(p, q):
        return [q]
    if occupied is None:
        occupied = g.occupied_cells[0]
    occupied = [c for c in occupied if c != q]
    if q in path_connected_set(p, occupied):
        dist = path_distance_pq(p, q, occupied)
        layers = path_connected_layers(p, occupied)
        if len(layers) > 1:
            result = [x for x in layers[1] if path_distance_pq(x, q, occupied) == dist-1]
            return result
    return []

def distance_to_border(p):
    x,y = p
    dx = min([x, g.state["board"]["width"]-x-1])
    dy = min([y, g.state["board"]["height"]-y-1])
    return (dx, dy)

def get_dir_number(p, q):
    assert(is_adjacent(p, q))
    x1,y1 = p
    x2,y2 = q
    dx,dy = x2-x1,y2-y1
    dir_dict = {dir:i for i, dir in enumerate(g.dir_order)}
    return dir_dict[(dx,dy)]

def add_coord(p, dq):
    x,y = p
    dx,dy = dq
    return (x+dx, y+dy)

def minus(dq):
    dx,dy = dq
    return (-dx, -dy)

######################################################

def cases(fs):
    def fn(moves):
        if len(moves) <= 1:
            return moves
        for f in fs:
            result = f(moves)
            if result is not None:
                return result
    return fn

def sequential(fs):
    def fn(moves):
        for f in fs:
            if len(moves) <= 1:
                return moves
            result = f(moves)
            if result is not None:
                moves = result
        return moves
    return fn

def take_first(moves):
    try:
        assert(len(moves) != 0)
    except AssertionError:
        turn = g.state["turn"]
        id = g.state["game"]["id"]
        print(f"id: {id}, TURN: {turn}")
        raise AssertionError
    return moves[0]

def other_considerations(moves):
    return moves

def is_straight(p):
    return get_adjacent_dir(g.me.head, p) == get_adjacent_dir(g.me.neck, g.me.head)

def score_more_next_move(p):
    moves = [a for a in adj_cells(p) if a not in g.occupied_cells[1]]
    return len(moves)

def score_more_room(p):
    cells = path_connected_set(p)
    return len(cells)

def prefer_by_rank(rank):
    def fn(moves):
        moves = [(a, rank(a)) for a in moves]
        moves = first_group(moves)
        return moves
    return fn

def prefer_yes(check):
    return prefer_by_rank(lambda a: 0 if check(a) else 1)

def prefer_no(check):
    return prefer_yes(lambda a: not check(a))

def prefer_by_score(score):
    def fn(moves):
        moves = [(a, score(a)) for a in moves]
        moves = first_group(moves, reverse=True)
        return moves
    return fn

def id(moves):
    return moves

######################################################

def experiment_condition():
    mes = [snake for snake in g.snakes if snake.name == "mark_snake"]
    if len(mes) >= 2: return True
    return False

def special_experimenting_code(game_state):
    #if functional2.special_experimenting_code(game_state): return True

    init_game(game_state)
    if not experiment_condition(): return False

    g.log["experiment"] = "Yes"
    start_time = time.time()
    #g.e.localtime = time.localtime()

    decision()
    g.state["next_move"] = get_adjacent_dir(g.me.head, g.next_coord)

    g.log["decision_support"] = {k:v for k,v in g.e.__dict__.items() if v is not None}
    g.log["decision_path"] = g.decision_path
    g.log["next_coord"] = g.next_coord
    g.log["next_move"] = g.state["next_move"]

    end_time = time.time()
    g.log["time"] = f"{end_time-start_time:.3f}s"

    print(g.log)
    return True

def init_game(game_state):
    global g
    g = Game()
    g.state = game_state

    g.snakes = [ Snake(
            name=snake["name"],
            body=get_coord(snake["body"]),
            health=snake["health"],
            id=snake["id"],
        ) for snake in game_state["board"]["snakes"] ]
    for snake in g.snakes:
        snake.length = len(snake.body)
        snake.head = snake.body[0]
        snake.neck = snake.body[1]
        snake.tail = snake.body[-1]

    g.me = [snake for snake in g.snakes for c in [game_state["you"]["body"][0]] if snake.head == (c["x"], c["y"])][0]
    g.others = [snake for snake in g.snakes if snake.head != g.me.head]
    if len(g.others) == 0:
        turn = game_state["turn"]
        id = game_state["game"]["id"]
        print(f"MARK_EXCEPTION, TURN: {turn}, id: {id}")
    else:
        g.other = g.others[0]

    g.food = get_coord(game_state["board"]["food"])

    g.log["id"] = game_state["game"]["id"]
    g.log["turn"] = game_state["turn"]
    g.log["me"] = g.me.dict()
    g.log["others"] = [snake.dict() for snake in g.others]
    g.log["food"] = g.food

######################################################

def decision():
    #estimated 5-step occupied cells
    g.occupied_cells = [
        occupied_cells(step)
        for step in [1,2,3,4,5]
    ]
    g.e.allowed_moves = [a for a in adj_cells(g.me.head) if a not in g.occupied_cells[0]]
    g.x.other_allowed_moves = [a for a in adj_cells(g.other.head) if a not in g.occupied_cells[0]]
    g.e.head_distance = distance_pq(g.me.head, g.other.head)
    g.e.head_path_distance = path_distance_pq(g.me.head, g.other.head)

    if len(g.e.allowed_moves) == 0:
        #no allowed moves, die on myself
        g.next_coord = g.me.neck
        return
    
    if len(g.e.allowed_moves) == 1:
        #no choice
        g.next_coord = g.e.allowed_moves[0]
        return

    #allowed_moves must be 2 or 3
    moves = cases([
        #battle_1_vs_1, 
        battle_1_vs_n,
        id, #cases at entry point ends by id to close possible None return
    ])(g.e.allowed_moves)
    g.next_coord = take_first(moves)

def battle_1_vs_1(moves):
    return moves

def battle_1_vs_n(moves):
    #if len(g.others) > 1:
    if len(g.others) >= 1:
        return sequential([
            avoid_danger_1_vs_n,
            get_food_1_vs_n,
        ])(moves)

def avoid_danger_1_vs_n(moves):
    return sequential([
        avoid_collision_1_vs_n,
        avoid_equal_collision,
    ])(moves)

def avoid_collision_1_vs_n(moves):
    danger_moves = [a for a in moves
        for snakes in [[snake for snake in g.others if is_adjacent(a, snake.head) and snake.length > g.me.length]]
        if len(snakes) != 0 ]
    if len(danger_moves) != 0:
        g.decision_path.append("avoid collision")
        moves = [a for a in moves if a not in danger_moves]
        if len(moves) != 0:
            return moves
        g.decision_path.append("nowhere to avoid")

def avoid_equal_collision(moves):
    return moves

def get_food_1_vs_n(moves):
    return cases([
        get_food_1,
        get_food_near,
    ])(moves)

def get_food_1(moves):
    food1 = [a for a in moves if a in g.food]
    if len(food1) != 0:
        g.decision_path.append("get food1")
        return food1

def get_food_near(moves):
    food_near = [f for f in g.food if distance_pq(f, g.me.head) <= 8]
    if len(food_near) != 0:
        food_good = [f for f in food_near 
                     if path_connected(f, g.me.head)
                     and all([path_distance_pq(f, g.me.head) < path_distance_pq(f, snake.head) for snake in g.others])]
        if len(food_good) != 0:
            food_best = prefer_by_score(lambda f: 999-path_distance_pq(f, g.me.head))(food_good)
            target = take_first(food_best)
            food_moves = shortest_path_move(g.me.head, target)
            food_moves = [a for a in moves if a in food_moves]
            if len(food_moves) != 0:
                g.decision_path.append("go to food")
                return food_moves

######################################################

def reverse_coord(cs):
    return [{"x":x, "y":y} for x,y in cs]

def init_from_log(log):

    others = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
            "id": snake["id"],
        } for snake in log["others"] ]
    me = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
            "id": snake["id"],
        } for snake in [log["me"]] ][0]

    game_state = {
        "game": {
                "id": log["id"]
            },
        "turn": log["turn"],
        "you": me,
        "board": {
                "width": 11,
                "height": 11,
                "snakes": [me, *others],
                "food": reverse_coord(log["food"]),
            },
    }
    return game_state

def run():
    log = {'id': '7a8ee3fa-4a53-4876-b5f1-88c377278654', 'turn': 270, 'me': {'name': 'mark_snake', 'health': 94, 'body': [(6, 8), (7, 8), (8, 8), (8, 9), (9, 9), (9, 10), (10, 10), (10, 9), (10, 8), (9, 8), (9, 7), (8, 7), (7, 7), (7, 6), (7, 5), (6, 5), (5, 5), (4, 5), (3, 5), (3, 6), (3, 7), (3, 8), (4, 8), (5, 8), (5, 9), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (1, 9), (1, 8), (2, 8), (2, 7), (2, 6), (2, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 54, 'body': [(2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (7, 1), (8, 1), (8, 0), (7, 0), (6, 0), (6, 1), (5, 1), (4, 1)]}], 'food': [(0, 0), (0, 4), (0, 5), (4, 6)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 10)], 'head_distance': 12, 'head_path_distance': 999}, 'decision_path': [], 'next_coord': (9, 10), 'next_move': 'left', 'time': '0.000s'}

    log = {'id': 'cde24395-e19c-4d2f-bab3-e103a94d0785', 'turn': 201, 'me': {'name': 'mark_snake', 'health': 74, 'body': [(8, 5), (7, 5), (6, 5), (5, 5), (5, 4), (6, 4), (7, 4), (7, 3), (7, 2), (7, 1), (6, 1), (5, 1), (5, 2), (4, 2), (4, 1), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (8, 1), (9, 1), (10, 1)]}, 'others': [{'name': 'ich heisse marvin', 'health': 63, 'body': [(7, 8), (8, 8), (9, 8), (10, 8), (10, 7), (9, 7), (9, 6), (8, 6), (7, 6), (6, 6)]}], 'food': [(3, 9), (9, 10), (0, 1), (1, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 5), (8, 4)], 'head_distance': 4, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (8, 4), 'next_move': 'down', 'time': '0.003s'}
    log = {'id': '8a6fedf8-bd56-4698-876d-938a7a7508fa', 'turn': 219, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(6, 5), (7, 5), (7, 4), (8, 4), (9, 4), (9, 3), (8, 3), (7, 3), (7, 2), (7, 1), (8, 1), (8, 2), (9, 2), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (9, 9)]}, 'others': [{'name': 'ich heisse marvin', 'health': 93, 'body': [(4, 7), (3, 7), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), (2, 2), (3, 2), (4, 2), (4, 3), (4, 4), (3, 4), (3, 5)]}], 'food': [(1, 4), (7, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(5, 5), (6, 6), (6, 4)], 'head_distance': 4, 'head_path_distance': 4, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (6, 6), 'next_move': 'up', 'time': '0.047s'}
    log = {'id': '5dc2811e-214e-428b-8810-400c1df1efa2', 'turn': 242, 'me': {'name': 'mark_snake', 'health': 52, 'body': [(4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (9, 5), (9, 4), (9, 3), (9, 2), (9, 1), (8, 1), (7, 1), (6, 1), (6, 2)]}, 'others': [{'name': 'ich heisse marvin', 'health': 53, 'body': [(6, 4), (6, 3), (5, 3), (4, 3), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (4, 7), (5, 7), (6, 7)]}], 'food': [(0, 8), (1, 1), (2, 10), (5, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 0), (4, 1)], 'head_distance': 6, 'head_path_distance': 8, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (4, 1), 'next_move': 'up', 'time': '0.026s'}
    log = {'id': '835014c5-5b48-48f6-a2f4-a7fe96eaf2e7', 'turn': 236, 'me': {'name': 'mark_snake', 'health': 66, 'body': [(5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (2, 3), (1, 3), (0, 3), (0, 4), (0, 5), (0, 6), (1, 6), (1, 7), (2, 7), (3, 7), (4, 7), (4, 6), (3, 6), (2, 6), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (6, 4), (6, 3), (6, 2), (6, 1)]}, 'others': [{'name': 'Snakeformatika', 'health': 98, 'body': [(7, 5), (7, 6), (7, 7), (6, 7), (6, 6), (5, 6), (5, 7), (5, 8), (5, 9), (6, 9), (6, 8), (7, 8), (7, 9), (8, 9), (8, 10)]}], 'food': [(10, 9), (0, 2), (4, 1), (0, 0), (7, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 1), (4, 1), (5, 0)], 'head_distance': 6, 'head_path_distance': 6, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (4, 1), 'next_move': 'left', 'time': '0.013s'}
    log = {'id': '835014c5-5b48-48f6-a2f4-a7fe96eaf2e7', 'turn': 237, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(4, 1), (5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (2, 3), (1, 3), (0, 3), (0, 4), (0, 5), (0, 6), (1, 6), (1, 7), (2, 7), (3, 7), (4, 7), (4, 6), (3, 6), (2, 6), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (6, 4), (6, 3), (6, 2), (6, 2)]}, 'others': [{'name': 'Snakeformatika', 'health': 97, 'body': [(7, 4), (7, 5), (7, 6), (7, 7), (6, 7), (6, 6), (5, 6), (5, 7), (5, 8), (5, 9), (6, 9), (6, 8), (7, 8), (7, 9), (8, 9)]}], 'food': [(10, 9), (0, 2), (0, 0), (7, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 1), (4, 2), (4, 0)], 'head_distance': 6, 'head_path_distance': 8, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (3, 1), 'next_move': 'left', 'time': '0.020s'}
    log = {'id': 'bd0f3d8d-6e72-4a4d-80af-593912511b4d', 'turn': 238, 'me': {'name': 'mark_snake', 'health': 73, 'body': [(4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (10, 3), (9, 3), (8, 3), (7, 3), (6, 3), (6, 2), (6, 1), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]}, 'others': [{'name': 'ich heisse marvin', 'health': 75, 'body': [(3, 9), (3, 8), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (9, 6), (9, 5), (8, 5), (7, 5)]}], 'food': [(0, 9), (8, 0), (0, 3), (10, 9), (3, 2), (9, 10), (5, 10), (7, 0), (7, 2), (0, 10), (1, 5), (6, 9)], 'experiment2': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 4), (4, 5), (4, 3)], 'head_distance': 6, 'head_path_distance': 8, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1', 'chase other tail, target (4, 7)', 'chase other tail detour food 1', 'chase my tail target (2, 3)', 'go to tail directly'], 'next_coord': (3, 4), 'next_move': 'left', 'time': '0.049s'}
    log = {'id': '4d2ca713-646a-4655-b7bd-aa713e3d3a35', 'turn': 362, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(3,6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (10, 5), (9, 5), (9, 4), (9, 3), (9, 2), (9, 1), (9, 0), (8, 0), (7, 0), (7, 1), (7, 2), (7, 3), (6, 3), (6, 2), (6, 1), (6, 0), (5, 0), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (3, 4), (3, 3), (2, 3), (1, 3), (1, 4), (1, 5), (2, 5), (2, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 92, 'body': [(0,5), (0, 6), (1, 6), (1, 7), (1, 8), (0, 8), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8)]}], 'food': [(10, 10), (3, 2), (2, 4), (9, 10), (10, 3)], 'experiment': 'No', 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 6), (4, 7), (4, 5)], 'head_distance': 4, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (3, 6), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': '9e93878d-1372-457d-a78d-f297c6c059af', 'turn': 206, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(8, 10), (9, 10), (10, 10), (10, 9), (10, 8), (9, 8), (9, 7), (9, 6), (9, 5), (9, 4), (9, 3), (8, 3), (7, 3), (7, 4), (7, 5), (7, 6), (8, 6), (8, 7), (8, 8), (8, 9)]}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 95, 'body': [(2, 2), (3, 2), (3, 3), (4, 3), (4, 2), (4, 1), (3, 1), (3, 0), (4, 0), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (4, 7), (3, 7), (3, 8), (3, 9)]}], 'food': [(0, 2), (2, 9)], 'experiment': 'No', 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 10), (8, 9)], 'head_distance': 14, 'head_path_distance': 14, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1', 'shorter'], 'next_coord': (8, 9), 'next_move': 'down', 'time': '0.002s'}
    log = {'id': '0912c014-ad4a-401d-b89c-84a043a9ad52', 'turn': 45, 'me': {'name': 'mark_snake', 'health': 75, 'body': [(2, 5), (1, 5), (0, 5), (0, 4)], 'id': 'gs_qmb373mdkGcYqcYfmFCtyTBQ'}, 'others': [{'name': 'mark_snake', 'health': 55, 'body': [(10, 9), (9, 9), (8, 9)], 'id': 'gs_MFmQw6768hfJXwGfmXgjhMRR'}], 'food': [(10, 8), (5, 5), (3, 3), (0, 3), (2, 6), (4, 5)], 'experiment': 'Yes', 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 5), (2, 6), (2, 4)], 'head_distance': 12, 'head_path_distance': 12}, 'decision_path': [], 'next_coord': (3, 5), 'next_move': 'right', 'time': '0.000s'}


    game_state = init_from_log(log)
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()

