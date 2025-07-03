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

class SnakeInfo:
    def __init__(self):
        self.my_head = None
        self.my_neck = None
        self.my_tail = None
        self.my_length = None
        self.other_head = None
        self.other_neck = None
        self.other_tail = None
        self.other_length = None

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
        self.s = SnakeInfo()
        self.x = DecisionAux()

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
        "ich heisse marvin", #Wrenger
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

    g.log["decision_support"] = {k:v for k,v in g.e.__dict__.items() if v is not None}
    g.log["decision_path"] = g.decision_path
    g.log["next_coord"] = g.next_coord
    g.log["next_move"] = g.state["next_move"]

    g.end_time = time.time()
    g.log["time"] = f"{g.end_time-g.start_time:.3f}s"

    print(g.log)
    return True

def init_game(game_state):
    global g
    g = Game()
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

def cases(fs):
    def fn(moves):
        if len(moves) <= 1:
            return moves
        for f in fs:
            result = f(moves)
            if result is not None:
                return result
        return moves
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

def direct_finish(f):
    def fn(moves):
        if len(moves) == 1:
            return moves
        return f(moves)
    return fn

def take_first(moves):
    assert(len(moves) != 0)
    return moves[0]

def other_considerations(moves):
    return moves

def is_straight(p):
    return get_adjacent_dir(g.s.my_head, p) == get_adjacent_dir(g.s.my_neck, g.s.my_head)

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

#############################################################
#############################################################

def decision():
    #estimated 5-step occupied cells
    g.occupied_cells = [
        occupied_cells(step)
        for step in [1,2,3,4,5]
    ]
    g.e.allowed_moves = [a for a in adj_cells(g.s.my_head) if a not in g.occupied_cells[0]]
    g.x.other_allowed_moves = [a for a in adj_cells(g.s.other_head) if a not in g.occupied_cells[0]]
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
    moves = cases([
        battle_1_vs_1, 
        battle_1_vs_n,
    ])(g.e.allowed_moves)
    g.next_coord = take_first(moves)

def battle_1_vs_n(moves):
    if g.e.n_other != 1:
        g.decision_path.append("battle_1_vs_n")
        return moves

def battle_1_vs_1(moves):
    if g.e.n_other == 1:
        g.decision_path.append("battle_1_vs_1")
        equal_line()
        return cases([
            my_snake_is_shorter, 
            snake_equal_length, 
            my_snake_is_longer,
        ])(moves)

def avoid_collision(moves):
    moves = cases([
        single_collision_point,
        two_collision_points,
    ])(moves)
    return moves

def prefer_straight(moves):
    return prefer_yes(is_straight)(moves)

def prefer_more_next_move(moves):
    return prefer_by_score(score_more_next_move)(moves)

def prefer_middle_by_3(moves):
    return prefer_yes(lambda a: all([d>=2 for d in distance_to_border(a)]))(moves)

def get_food(moves):
    d_food = 8
    food_near = [f for f in g.food if distance_pq(f, g.s.my_head) < d_food]
    g.x.food_near = food_near
    if len(food_near) != 0:
        food_good_d = [f for f in food_near if distance_pq(f, g.s.my_head) <= distance_pq(f, g.s.other_head)]
        food_good_dd = [(f, path_distance_pq(f, g.s.my_head), path_distance_pq(f, g.s.other_head)) for f in food_good_d]
        food_good = [(f, d1) for f,d1,d2 in food_good_dd if d1 <= d2 and d1 < 999]
        g.e.food_good = food_good
        if len(food_good) != 0:
            g.decision_path.append("food opportunity")
            food_targets = first_group(food_good)
            food_target = food_targets[0]
            g.e.food_target = food_target
            fmoves = shortest_path_move(g.s.my_head, food_target)
            moves = [a for a in moves if a in fmoves]
            if len(moves) != 0:
                g.decision_path.append("go to food")
                return moves

def my_snake_is_shorter(moves):
    if g.s.my_length < g.s.other_length:
        g.decision_path.append("shorter")
        return sequential([
            avoid_collision,
            near_border_danger,
            no_room_danger,
            get_food,
            #prefer_middle_by_3,
            prefer_more_next_move,
            prefer_straight,
        ])(moves)

def single_collision_point(moves):
    if g.e.head_distance == 2:
        collision_points = [p for p in moves if p in adj_cells(g.s.other_head)]
        if len(collision_points) == 1:
            g.decision_path.append("avoid single collision point")
            moves = prefer_no(lambda a: a not in collision_points)(moves)
            return moves

def two_collision_points(moves):
    if g.e.head_distance == 2:
        collision_points = [p for p in moves if p in adj_cells(g.s.other_head)]
        if len(collision_points) == 2:
            avoid_point = [p for p in moves if p not in collision_points]
            if len(avoid_point) == 1:
                avoid_point = take_first(avoid_point)
                if not on_border(avoid_point):
                    g.decision_path.append("avoid point is safe")
                    return [avoid_point]
                pos = max(distance_to_border(avoid_point))
                if pos > 2:
                    return [avoid_point]

def off_border_danger(moves):
    if off_border_1(g.s.my_head):
        if path_distance_pq(g.s.other_head, g.s.my_head) < 16:
            if any([a in g.food for a in moves]) and g.s.my_length+1 == g.s.other_length:
                g.decision_path.append("get the food and equal")
                return moves
            moves = prefer_no(on_border)(moves)
            return moves

def danger_distance_average(a):
    d1 = distance_pq(a, g.s.other_head)
    d2 = path_distance_pq(a, g.s.other_head)
    if d2 >= 100:
        d2 = min([(g.s.my_length+1)//2, (g.s.other_length+1)//2])
    return (d1+d2+1)//2

def on_border_danger(moves):
    if on_border(g.s.my_head):
        if path_distance_pq(g.s.other_head, g.s.my_head) < 16:
            if on_border(g.s.my_neck):
                return prefer_no(on_border)(moves)
            moves = prefer_by_score(danger_distance_average)(moves)
            return moves

def near_border_danger(moves):
    if distance_pq(g.s.my_head, g.s.other_head) > 6:
        return moves

    return cases([
        off_border_danger,
        on_border_danger,
    ])(moves)

def equal_length_danger(moves):
    if g.e.head_distance == 2:
        collision_points = [a for a in adj_cells(g.s.my_head) if is_adjacent(a, g.s.other_head) and a not in g.occupied_cells[0]]
        return prefer_no(lambda a: a in collision_points)(moves)

def snake_equal_length(moves):
    if g.s.my_length == g.s.other_length:
        g.decision_path.append("equal_length")
        moves = sequential([
            equal_length_danger,
            no_room_danger,
            get_food,
            prefer_middle_by_3,
            prefer_straight,
        ])(moves)
        return moves

def not_enough_space(a):
    room = len(path_connected_set(a))
    return room <= g.s.my_length //2

def enough_room(moves):
    #gradually more and more intensive calculation
    #1. room is enough in my territory
    #2. room is not enough, need find wayout
    move_room = [(a, myset, myset2)
                 for a in moves
                 for aset in [path_connected_set(a)]
                 for myset in [[p for p in aset if p in g.x.my_territory]]
                 for myset2 in [[p for p in aset if p not in g.x.other_territory]]
                 for cut in [any([is_adjacent(p, g.s.other_head) for p in aset])]
                 ]
    good_moves = [a for a, myset, myset2 in move_room if len(myset) >= g.s.my_length-2]
    if g.s.my_length >= g.s.other_length:
        good_moves = [a for a, myset, myset2 in move_room if len(myset2) >= g.s.my_length-2]
    if len(good_moves) != 0:
        return good_moves
    


def cut_danger(moves):
    other_territory = [a for a in g.x.other_territory if a not in g.occupied_cells[0]]
    other_territory = [a for a in other_territory if path_distance_pq(a, g.s.other_head) == distance_pq(a, g.s.other_head)]
    occupied_cells = g.occupied_cells[0]+other_territory
    cut = [(a, room) for a in moves for room in [len(path_connected_set(a, occupied_cells))]]
    cut_moves = [a for a, room in cut if room <= g.s.my_length-2]
    if len(cut_moves) != 0:
        g.decision_path.append("has cut danger")
        g.e.cut = cut_moves
        good_moves = [a for a in moves if a not in cut_moves]
        if len(good_moves) != 0:
            return good_moves

def split_move(moves):
    moves = sequential([
        cases([
            chase_my_tail,
            chase_other_tail,
        ]),
        #prefer_no(not_enough_space),
        enough_room,
        prefer_by_score(lambda a: path_distance_pq(a, g.s.other_head)),
        #cut_danger,
    ])(moves)
    return moves

def split_2_2(moves):
    if len(moves) == 2:
        a,b = moves
        if path_distance_pq(a, b) >= 4:
            g.decision_path.append("2 split 2")
            return split_move(moves)

def split_3_2(moves):
    if len(moves) == 3:
        straight = [a for a in moves if is_straight(a)][0]
        others = [a for a in moves if a != straight]
        if any([path_distance_pq(a, straight) > 2 for a in others]):
            g.decision_path.append("3 split 2")
            return split_move(moves)

def split_branches(moves):
    moves = cases([
        split_2_2,
        split_3_2,
    ])(moves)
    return moves

def no_room_danger(moves):
    return cases([
        split_branches,
    ])(moves)

def equal_line():
    my_connected_set = path_connected_layers(g.s.my_head)
    other_connected_set = path_connected_layers(g.s.other_head)
    my_connected_dict = {p:i for i,layer in enumerate(my_connected_set) for p in layer}
    other_connected_dict = {p:i for i,layer in enumerate(other_connected_set) for p in layer}
    my_territory = [p for p in my_connected_dict if my_connected_dict[p] < other_connected_dict.get(p, 999)]
    other_territory = [p for p in other_connected_dict if other_connected_dict[p] < my_connected_dict.get(p, 999)]
    equal_territory = [p for p in my_connected_dict if p in other_connected_dict and my_connected_dict[p] == other_connected_dict[p]]
    equal_border = [p for p in equal_territory if any([q in other_territory for q in adj_cells(p)])]
    g.x.my_territory = my_territory
    g.x.other_territory = other_territory
    g.x.equal_territory = equal_territory
    g.x.equal_border = equal_border

def chase_other_tail_has_distance(moves):
    if distance_pq(g.s.my_head, g.s.other_tail) > 1:
        tail_moves = shortest_path_move(g.s.my_head, g.s.other_tail)
        moves = prefer_yes(lambda a: a in tail_moves)(moves)
        return moves

def chase_other_tail_too_close(moves):
    if distance_pq(g.s.my_head, g.s.other_tail) <= 1:
        g.decision_path.append("don't follow too close")
        return prefer_no(lambda a: a != g.s.other_tail)(moves)

def wayout_from_other(moves):
    if g.s.my_length >= g.s.other_length:
        moves = [a for a in moves if len([p 
                    for p in g.x.my_territory+g.x.equal_territory
                    for adj in [[i for i in range(g.s.other_length) if is_adjacent(p, g.other["body"][i])]]
                    for d in [path_distance_pq(g.s.my_head, p)]
                    if 1==1
                        and path_connected(a, p) 
                        and len(adj) != 0
                        and d >= g.s.other_length-max(adj)-1
                    ]) != 0]
        if len(moves) != 0:
            return moves

def chase_other_tail(moves):
    #chase enemy tail
    if path_connected(g.s.my_head, g.s.other_tail):
        if g.s.other_tail in g.x.my_territory or g.s.other_tail in g.x.equal_territory:
            moves = cases([
                chase_other_tail_has_distance,
                chase_other_tail_too_close,
            ])(moves)
            return moves

def chase_my_tail_my_snake_not_longer(moves):
    if g.s.my_length <= g.s.other_length:
        if g.s.my_tail in g.x.my_territory:
            moves = [a for a in moves if path_connected(a, g.s.my_tail)]
            return moves

def chase_my_tail_my_snake_longer(moves):
    if g.s.my_length > g.s.other_length:
        if g.s.my_tail not in g.x.other_territory:
            moves = [a for a in moves if path_connected(a, g.s.my_tail)]
            return moves

def chase_my_tail_other_not_in_the_way(moves):
    if path_distance_pq(g.s.my_head, g.s.my_tail) <= path_distance_pq(g.s.my_head, g.s.other_head):
        moves = [a for a in moves if path_connected(a, g.s.my_tail) and path_distance_pq(a, g.s.my_tail) <= path_distance_pq(a, g.s.other_head)]
        return moves

def wayout_from_myself(moves):
    if g.s.my_length >= g.s.other_length:
        moves = [a for a in moves if len([p 
                    for p in g.x.my_territory+g.x.equal_territory
                    for adj in [[i for i in range(g.s.my_length) if is_adjacent(p, g.me["body"][i])]]
                    for d in [path_distance_pq(g.s.my_head, p)]
                    if 1==1
                        and path_connected(a, p) 
                        and len(adj) != 0
                        and d >= g.s.my_length-max(adj)-1
                    ]) != 0]
        if len(moves) != 0:
            return moves

def chase_my_tail(moves):
    if path_connected(g.s.my_head, g.s.my_tail):
        moves = cases([
            chase_my_tail_my_snake_not_longer,
            chase_my_tail_my_snake_longer,
            chase_my_tail_other_not_in_the_way,
        ])(moves)
        return moves

def not_too_long(moves):
    if g.s.my_length < 20:
        moves = sequential([
            no_room_danger,
            get_food,
            prefer_straight,
        ])(moves)
        return moves

def food1(moves):
    moves = prefer_yes(lambda a: a in g.food)(moves)
    return moves

def too_long(moves):
    if g.s.my_length >= 20:
        moves = sequential([
            #cut_danger,
            no_room_danger,
            food1,
            #kill_opportunity,
            cases([
                chase_other_tail,
                chase_my_tail,
            ]),
            prefer_more_next_move,
            prefer_middle_by_3,
            prefer_straight,
        ])(moves)
        return moves

def my_snake_is_longer(moves):
    if g.s.my_length > g.s.other_length:
        return cases([
            not_too_long,
            too_long,
        ])(moves)

######################################################

def reverse_coord(cs):
    return [{"x":x, "y":y} for x,y in cs]

def init_from_log2(log):

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

def init_from_log(log):

    others = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
        } for snake in log["others"] ]
    me = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
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
    log = {'id': 'eba983d4-3a28-42fc-a4b0-47438378a268', 'turn': 236, 'me': {'name': 'mark_snake', 'health': 98, 'body': [(1, 1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 6), (2, 6), (2, 5), (2, 4), (2, 3), (2, 2), (2, 1), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (4, 7), (5, 7)]}, 'others': [{'name': 'ich heisse marvin', 'health': 81, 'body': [(4, 2), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (8, 4), (8, 5), (7, 5), (7, 6), (7, 7), (7, 8), (6, 8), (5, 8)]}], 'food': [(1,0),(8,0), (10,1), (10,7), (4,9)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 3), (1, 3), (2, 2)], 'head_distance': 2, 'head_path_distance': 2}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (3, 3), 'next_move': 'right', 'time': '0.004s'}
    log = {'id': '4ac54524-622d-4a93-8a0e-f95d302e4043', 'turn': 239, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(2, 7), (1, 7), (0, 7), (0, 6), (0, 5), (1, 5), (1, 4), (2, 4), (2, 3), (2, 2), (3, 2), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (7, 0), (8, 0), (8, 1), (8, 2), (7, 2), (7, 3), (6, 3)]}, 'others': [{'name': 'ich heisse marvin', 'health': 54, 'body': [(8, 7), (7, 7), (6, 7), (6, 6), (6, 5), (5, 5), (4, 5), (3, 5), (3, 6), (4, 6), (4, 7), (4, 8), (4, 9), (5, 9)]}], 'food': [(0, 1), (3, 4), (6, 0), (8, 6), (2, 10), (0, 0)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 7), (2, 8), (2, 6)], 'head_distance': 6, 'head_path_distance': 12}, 'decision_path': ['battle_1_vs_1', '3 allowed divide into 2 split branches'], 'next_coord': (2, 6), 'next_move': 'down', 'time': '0.033s'}
    log = {'id': '1afd4ff4-5628-410f-931f-2926b4946dd3', 'turn': 301, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (10, 8), (10, 7), (10, 6), (10, 5), (9, 5), (9, 6), (9, 7), (9, 8), (8, 8), (8, 9), (7, 9), (6, 9), (6, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (1, 7), (2, 7)]}, 'others': [{'name': 'ich heisse marvin', 'health': 77, 'body': [(2, 5), (2, 4), (1, 4), (1, 5), (1, 6), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1)]}], 'food': [(8, 0), (1, 0), (6, 0), (7, 6), (7, 4), (4, 7)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(0, 10), (0, 8)], 'head_distance': 6, 'head_path_distance': 999}, 'decision_path': ['battle_1_vs_1', '2 split branches'], 'next_coord': (0, 10), 'next_move': 'up', 'time': '0.001s'}
    log = {'id': 'dde50687-bf70-4b5a-a589-3409ba3b1fdb', 'turn': 23, 'me': {'name': 'mark_snake', 'health': 87, 'body': [(1, 4), (2, 4), (2, 5), (2, 6), (2, 7)]}, 'others': [{'name': 'ich heisse marvin', 'health': 95, 'body': [(3, 4), (3, 3), (3, 2), (3, 1), (3, 0), (2, 0)]}], 'food': [(7, 4), (10, 7), (4, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(0, 4), (1, 5), (1, 3)], 'food_good': [], 'head_distance': 2, 'head_path_distance': 8, 'me_heading_collision_point': False, 'other_heading_collision_point': False}, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_2', 'type_1_collision', 'type_1_blocked'], 'next_coord': (0, 4), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': 'dde50687-bf70-4b5a-a589-3409ba3b1fdb', 'turn': 24, 'me': {'name': 'mark_snake', 'health': 87, 'body': [(0,4), (1, 4), (2, 4), (2, 5), (2, 6)]}, 'others': [{'name': 'ich heisse marvin', 'health': 95, 'body': [(4,4), (3, 4), (3, 3), (3, 2), (3, 1), (3, 0)]}], 'food': [(7, 4), (10, 7), (4, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(0, 4), (1, 5), (1, 3)], 'food_good': [], 'head_distance': 2, 'head_path_distance': 8, 'me_heading_collision_point': False, 'other_heading_collision_point': False}, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_2', 'type_1_collision', 'type_1_blocked'], 'next_coord': (0, 4), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': '330b335e-81ea-439b-9251-a9d94c9faf37', 'turn': 206, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(2, 6), (1, 6), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (2, 0), (2, 1), (1, 1), (1, 2)]}, 'others': [{'name': 'ich heisse marvin', 'health': 97, 'body': [(4, 6), (5, 6), (6, 6), (7, 6), (7, 5), (7, 4), (6, 4), (6, 3), (5, 3), (5, 2), (4, 2), (3, 2), (3, 3), (4, 3), (4, 4), (3, 4), (3, 5)]}], 'food': [(4, 10), (9, 10), (10, 7), (10, 4), (5, 10), (9, 8), (9, 9), (5, 9), (6, 7), (6, 8), (7, 1), (9, 7), (2, 8)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 6), (2, 7), (2, 5)], 'food_good': [((2, 8), 2)], 'food_target': (2, 8), 'head_distance': 2, 'head_path_distance': 2, 'me_heading_collision_point': True, 'other_heading_collision_point': True}, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_2', 'type_1_collision', 'head_to_head', 'food opportunity', 'go to food'], 'next_coord': (2, 7), 'next_move': 'up', 'time': '0.006s'}



    game_state = init_from_log(log)
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()

