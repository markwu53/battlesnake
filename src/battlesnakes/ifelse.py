import time

class DecisionSupport:
    n_other = 1
    allowed_moves = None
    n_allowed = None
    dummy = None

class SnakeInfo:
    my_head = None
    my_neck = None
    my_tail = None
    other_head = None
    other_neck = None
    other_tail = None

class Game:
    state = None
    me = None
    other = None
    others = None
    snakes = None
    food = None
    next_coord = None
    occupied_cells = None
    log = {}
    big = {}
    e = DecisionSupport()
    s = SnakeInfo()

g = Game()

###########################################################

def prefer_more_next_move(moves):
    moves_rank = [(a, len([p for p in adj_cells(a) if p not in g.occupied_cells[1]])) for a in moves]
    moves = first_group(moves_rank, reverse=True)
    return moves

def prefer_straight(moves):
    moves_rank = [(a, 0 if get_adjacent_dir(g.s.my_neck, g.s.my_head) == get_adjacent_dir(g.s.my_head, a) else 1) for a in moves]
    moves = first_group(moves_rank)
    return moves

def todo_default():
    moves = prefer_straight(prefer_more_next_move(g.e.allowed_moves))
    g.next_coord = moves[0]

def battle():
    moves = prefer_straight(prefer_more_next_move(g.e.allowed_moves))
    g.next_coord = moves[0]

def init_env():
    #estimated 5-step occupied cells
    g.occupied_cells = [
        occupied_cells(step)
        for step in [1,2,3,4,5]
    ]
    g.e.allowed_moves = [a for a in adj_cells(g.s.my_head) if a not in g.occupied_cells[0]]
    g.e.n_allowed = len(g.e.allowed_moves)

def decision():
    init_env()

    if g.e.n_allowed == 0:
        #no allowed moves, die on myself
        g.next_coord = g.s.my_neck
        return
    
    if g.e.n_allowed == 1:
        #no choice
        g.next_coord = g.e.allowed_moves[0]
        return
    
    #2 or 3 allowed moves
    g.next_coord = g.e.allowed_moves[0]
    if g.e.n_other == 1:
        battle()
    else:
        #1_vs_n, for now, use the same
        todo_default()

def init_game(game_state):
    g.state = game_state
    g.snakes = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": get_coord(snake["body"]),
        } for snake in game_state["board"]["snakes"] ]
    g.me = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": get_coord(snake["body"]),
        } for snake in [game_state["you"]] ][0]
    g.others = [snake for snake in g.snakes if snake["body"][0] != g.me["body"][0]]
    g.other = g.others[0]
    g.food = get_coord(game_state["board"]["food"])

    g.s.my_head = g.me["body"][0]
    g.s.my_neck = g.me["body"][1]
    g.s.my_tail = g.me["body"][-1]
    g.s.other_head = g.other["body"][0]
    g.s.other_neck = g.other["body"][1]
    g.s.other_tail = g.other["body"][-1]

    g.e.n_other = len(g.others)

    g.log["id"] = game_state["game"]["id"]
    g.log["turn"] = game_state["turn"]
    g.log["me"] = g.me
    g.log["others"] = g.others
    g.log["food"] = g.food

def experiment_condition():
    if g.e.n_other != 1: return False
    if g.other["name"] not in (
        "Snakeformatika",
        #"Wim HU [dev]",
        #"Frank The Tank",

    ): 
        return False
    return True

def special_experimenting_code(game_state):
    init_game(game_state)
    if not experiment_condition(): return False

    g.log["experiment"] = True
    g.start_time = time.time()

    decision()
    g.state["next_move"] = get_adjacent_dir(g.s.my_head, g.next_coord)

    g.log["decision_support"] = g.e.__dict__
    g.log["next_coord"] = g.next_coord
    g.log["next_move"] = g.state["next_move"]

    g.end_time = time.time()
    g.log["time"] = f"{g.end_time-g.start_time:.3f}s"

    print(g.log)
    return True

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
        body = s["body"]
        if s["health"] == 100:
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

######################################################

def init_from_log(log):

    def reverse_coord(cs):
        return [{"x":x, "y":y} for x,y in cs]

    others = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
        } for snake in log["board"]["others"] ]
    me = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
        } for snake in [log["board"]["me"]] ][0]

    game_state = {
        "game": {
                "id": log["board"]["id"]
            },
        "turn": log["board"]["turn"],
        "you": me,
        "board": {
                "width": 11,
                "height": 11,
                "snakes": [me, *others],
                "food": reverse_coord(log["board"]["food"]),
            },
    }
    return game_state

def run():
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 16, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(9, 7), (9, 6), (8, 6), (8, 5), (8, 4)]}, 'others': [{'name': 'Snakeformatika', 'health': 98, 'body': [(6, 6), (6, 7), (7, 7), (7, 6), (7, 5), (7, 4)]}], 'food': [(3, 5), (0, 0)]}, 'experiment': True, 'allowed_moves': [(10, 7), (8, 7), (9, 8)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: Y', 'env_lt8_enemy_far?: N', 'env_lt8_food_1?: N', 'env_food_near?: N', 'routine_move!'], 'time': '0.000s'}
    game_state = init_from_log(log)
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()

