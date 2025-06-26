import time

#these class variables are used to trick the editor to display them in intellisense

class DecisionSupport:
    n_other = 1
    allowed_moves = None
    other_allowed_moves = None
    my_snake_bigger = None
    food_near = None
    food_good = None
    food_worth = None
    food_target = None
    head_distance = None
    head_path_distance = None
    collision_type = None
    avoid_points = None
    collision_food = None
    situation = None
    border_distance = None
    collision_points = None
    collision_point = None
    possible_collision_points = None
    decision_path = []

class SnakeInfo:
    my_head = None
    my_neck = None
    my_tail = None
    my_length = None
    other_head = None
    other_neck = None
    other_tail = None
    other_length = None

class Game:
    state = None
    me = None
    other = None
    others = None
    snakes = None
    food = None
    next_coord = None
    occupied_cells = None
    dir_order = [(0,1), (-1,0), (0,-1), (1,0)]
    log = {}
    big = {}
    e = DecisionSupport()
    s = SnakeInfo()

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

def experiment_condition():
    if g.e.n_other != 1: return False
    #Eastern time (7AM - 8PM) + 4
    #if not 11 <= time.localtime().tm_hour <= 23: return False
    if g.other["name"] not in (
        "Snakeformatika", #inform
        #"Kakemonsteret-v2", #pettso
        #"Wim HU [dev]", #wim
        #"Frank The Tank", #djnuller

    ): 
        return False
    return True

def special_experimenting_code(game_state):
    init_game(game_state)
    if not experiment_condition(): return False

    g.log["experiment"] = True
    g.start_time = time.time()
    #g.e.localtime = time.localtime()

    decision()
    g.state["next_move"] = get_adjacent_dir(g.s.my_head, g.next_coord)

    g.log["decision_support"] = g.e.__dict__
    g.log["next_coord"] = g.next_coord
    g.log["next_move"] = g.state["next_move"]

    g.end_time = time.time()
    g.log["time"] = f"{g.end_time-g.start_time:.3f}s"

    print(g.log)
    return True

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

    g.s.my_head = g.me["body"][0]
    g.s.my_neck = g.me["body"][1]
    g.s.my_tail = g.me["body"][-1]
    g.s.my_length = len(g.me["body"])

    g.e.n_other = len(g.others)

    if g.e.n_other != 0:
        g.other = g.others[0]
        g.s.other_head = g.other["body"][0]
        g.s.other_neck = g.other["body"][1]
        g.s.other_tail = g.other["body"][-1]
        g.s.other_length = len(g.other["body"])

    g.food = get_coord(game_state["board"]["food"])


    g.log["id"] = game_state["game"]["id"]
    g.log["turn"] = game_state["turn"]
    g.log["me"] = g.me
    g.log["others"] = g.others
    g.log["food"] = g.food

def sequential_cases(fs, moves=None):
    assert(len(fs) != 0)
    if moves is None:
        moves = g.e.allowed_moves
    
    cases = fs[:-1]
    last = fs[-1]
    for f in cases:
        result = f(moves)
        if not result is None:
            return result
    return last(moves)

def sequential(fs, moves=None):
    if moves is None:
        moves = g.e.allowed_moves
    for f in fs:
        moves = f(moves)
    return moves

def take_first(moves):
    assert(len(moves) != 0)
    return moves[0]

def other_considerations(moves):
    return moves
def get_food(moves):
    return moves
def avoid_danger(moves=g.e.allowed_moves):
    return moves

def rank_border(p):
    if on_border(p):
        return 1
    return 0

def rank_straight(p):
    if get_adjacent_dir(g.s.my_head, p) == get_adjacent_dir(g.s.my_neck, g.s.my_head):
        return 0
    return 1

def score_more_next_move(p):
    moves = [a for a in adj_cells(p) if a not in g.occupied_cells[1]]
    return len(moves)

def score_more_room(p):
    cells = path_connected_set(p)
    return len(cells)

def prefer_by_rank(moves, rank):
    moves = [(a, rank(a)) for a in moves]
    moves = first_group(moves)
    return moves

def prefer_by_score(moves, score):
    moves = [(a, score(a)) for a in moves]
    moves = first_group(moves, reverse=True)
    return moves

def id(moves):
    return moves

def decision():
    #estimated 5-step occupied cells
    g.occupied_cells = [
        occupied_cells(step)
        for step in [1,2,3,4,5]
    ]
    g.e.allowed_moves = [a for a in adj_cells(g.s.my_head) if a not in g.occupied_cells[0]]
    g.e.other_allowed_moves = [a for a in adj_cells(g.s.other_head) if a not in g.occupied_cells[0]]
    g.e.head_distance = distance_pq(g.s.my_head, g.s.other_head)
    g.e.head_path_distance = path_distance_pq(g.s.my_head, g.s.other_head)

    if len(g.e.allowed_moves) == 0:
        #no allowed moves, die on myself
        g.next_coord = g.s.my_neck
        return
    
    if len(g.e.allowed_moves) == 1:
        #no choice
        g.next_coord = g.e.allowed_moves[0]
        return

    #allowed_moves must be 2 or 3
    moves = sequential_cases([
        battle_1_vs_1, 
        battle_1_vs_n,
    ])
    g.next_coord = take_first(moves)

def battle_1_vs_n(moves):
    if g.e.n_other != 1:
        g.e.decision_path.append("battle_1_vs_n")
        return moves

def battle_1_vs_1(moves):
    if g.e.n_other == 1:
        g.e.decision_path.append("battle_1_vs_1")
        return sequential_cases([shorter, equal_length, longer], moves)

def shorter(moves):
    if g.s.my_length < g.s.other_length:
        g.e.decision_path.append("shorter")
        return sequential_cases([
            head_distance_2, 
            head_distance_4, 
            head_distance_6, 
            head_distance_more,
        ], moves)

def head_distance_2(moves):
    if g.e.head_distance == 2:
        g.e.decision_path.append("head_distance_2")
        g.e.possible_collision_points = [p for p in adj_cells(g.s.my_head) if p in adj_cells(g.s.other_head)]
        return sequential_cases([ type_1_collision, type_2_collision ], moves)

def type_1_collision(moves):
    if len(g.e.possible_collision_points) == 1:
        g.e.decision_path.append("type_1_collision")
        g.e.collision_point = g.e.possible_collision_points[0]
        g.e.me_heading_collision_point = get_adjacent_dir(g.s.my_head, g.e.collision_point) == get_adjacent_dir(g.s.my_neck, g.s.my_head)
        g.e.other_heading_collision_point = get_adjacent_dir(g.s.other_head, g.e.collision_point) == get_adjacent_dir(g.s.other_neck, g.s.other_head)
        return sequential_cases([
            type_1_blocked, 
            head_to_head, 
            other_to_me, 
            me_to_other, 
            parallel, 
            parallel_opposite,
        ], moves)

def off_border_danger(moves):
    if g.s.my_length+1 < g.s.other_length:
        if off_border_1(g.s.my_head):
            moves = prefer_by_rank(moves, rank_border)
            return moves

def crawling(moves):
    if on_border(g.s.my_neck):
        return prefer_by_rank(moves, rank_border)

def heading_border(moves):
    if not on_border(g.s.my_neck):
        moves = prefer_by_score(moves, lambda a: distance_pq(a, g.s.other_head))
        return moves

def on_border_danger(moves):
    if on_border(g.s.my_head):
        return sequential_cases([
            crawling,
            heading_border,
        ], moves)

def killer_near(moves):
    return sequential_cases([
        off_border_danger,
        on_border_danger,
        id,
    ], moves)

def type_1_blocked(moves):
    if g.e.collision_point in g.occupied_cells[0]:
        g.e.decision_path.append("type_1_blocked")
        return sequential([
            killer_near, 
            other_considerations,
        ], moves)

def avoid_collision_point_1(moves):
    moves = [a for a in moves if a != g.e.collision_point]
    return moves

def head_to_head(moves):
    if g.e.me_heading_collision_point and g.e.other_heading_collision_point:
        g.e.decision_path.append("head_to_head")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ], moves)

def other_to_me(moves):
    if g.e.other_heading_collision_point:
        g.e.decision_path.append("other_to_me")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ], moves)

def me_to_other(moves):
    if g.e.me_heading_collision_point:
        g.e.decision_path.append("me_to_other")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ], moves)

def parallel(moves):
    if get_adjacent_dir(g.s.my_neck, g.s.my_head) == get_adjacent_dir(g.s.other_neck, g.s.other_head):
        g.e.decision_path.append("parallel")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ], moves)

def parallel_opposite(moves):
    if get_adjacent_dir(g.s.my_head, g.s.my_neck) == get_adjacent_dir(g.s.other_neck, g.s.other_head):
        g.e.decision_path.append("parallel_opposite")
        return sequential([

            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ], moves)

def rank_by_no_food(p):
    if not p in g.food:
        return 0
    return 1

def type_2_with_no_avoid_points(moves):
    if len(g.e.avoid_points) == 0:
        moves = prefer_by_rank(moves, rank_by_no_food)
        return moves

def type_2_with_1_avoid_point(moves):
    if len(g.e.avoid_points) == 1:
        return g.e.avoid_points

def type_2_with_2_collision_points(moves):
    if len(g.e.collision_points) == 2:
        g.e.avoid_points = [a for a in g.e.allowed_moves if a not in g.e.collision_points]
        return sequential_cases([
            type_2_with_no_avoid_points,
            type_2_with_1_avoid_point,
        ], moves)

def type_2_with_1_collision_points(moves):
    if len(g.e.collision_points) == 1:
        g.e.avoid_points = [a for a in g.e.allowed_moves if a not in g.e.collision_points]

def type_2_with_0_collision_points(moves):
    if len(g.e.collision_points) == 0:
        g.e.avoid_points = [a for a in g.e.allowed_moves if a not in g.e.collision_points]

def type_2_collision(moves):
    if len(g.e.possible_collision_points) == 2:
        g.e.decision_path.append("type_2_collision")
        g.e.collision_points = [p for p in g.e.possible_collision_points if p not in g.occupied_cells[0]]
        return sequential_cases([
            type_2_with_2_collision_points,
            type_2_with_1_collision_points,
            type_2_with_0_collision_points,
        ])

def head_distance_4(moves):
    if g.e.head_distance == 4:
        g.e.decision_path.append("head_distance_4")
        return moves

def head_distance_6(moves):
    if g.e.head_distance == 6:
        g.e.decision_path.append("head_distance_6")
        return moves

def head_distance_more(moves):
    if g.e.head_distance > 6:
        g.e.decision_path.append("head_distance_more")
        return moves

def equal_length(moves):
    if g.s.my_length == g.s.other_length:
        g.e.decision_path.append("equal_length")
        return moves

def longer(moves):
    if g.s.my_length > g.s.other_length:
        g.e.decision_path.append("longer")
        return moves
