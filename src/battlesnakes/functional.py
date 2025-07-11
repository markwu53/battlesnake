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
    start_time = time.time()
    #g.e.localtime = time.localtime()

    decision()
    g.state["next_move"] = get_adjacent_dir(g.s.my_head, g.next_coord)

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
        id, #cases at entry point ends by id to close possible None return
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
        try:
            moves = cases([
                my_snake_is_shorter, 
                snake_equal_length, 
                my_snake_is_longer,
            ])(moves)
        except Exception as e:
            turn = g.state["turn"]
            id = g.state["game"]["id"]
            print(f"id: {id}, MARK_EXCEPTION, TURN: {turn}")
            raise

        return moves

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
            split_choice,
            get_food,
            prefer_more_next_move,
            prefer_middle_by_3,
            prefer_straight,
        ])(moves)

def single_collision_point(moves):
    if g.e.head_distance == 2:
        collision_points = [p for p in moves if p in adj_cells(g.s.other_head)]
        if len(collision_points) == 1:
            g.decision_path.append("avoid single collision point")
            moves = prefer_no(lambda a: a in collision_points)(moves)
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
            split_choice,
            get_food,
            prefer_more_next_move,
            prefer_middle_by_3,
            prefer_straight,
        ])(moves)
        return moves

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

def print_before(f):
    def fn(moves):
        print(moves)
        moves = f(moves)
        return moves
    return fn

def print_after(f):
    def fn(moves):
        moves = f(moves)
        print(moves)
        return moves
    return fn

def cut_too_small(moves):
    occupied = g.occupied_cells[0]+g.x.other_territory
    def space(a):
        return len(path_connected_set(a, occupied))
    moves = prefer_by_score(space)(moves)
    return moves

def static_too_small(moves):
    def bad(a):
        if path_connected(a, g.s.my_tail):
            return False
        if path_connected(a, g.s.other_tail):
            return False
        aset = path_connected_set(a)
        if any([p in aset for c in g.other["body"] for p in adj_cells(c)]):
            return False
        if len(aset) == 1:
            return True
        adj_indexes = [i for i,c in enumerate(g.me["body"]) if any([p in aset for p in adj_cells(c) if p != a])]
        max_index = max(adj_indexes)
        required_steps = g.s.my_length - max_index - 1
        if len(aset) < required_steps:
            return True
        return False

    removed = [a for a in moves if bad(a)]
    if len(removed) != 0:
        g.decision_path.append("removed static too small")
        moves = [a for a in moves if a not in removed]
        if len(moves) != 0:
            return moves

def fallout(moves):
    g.decision_path.append("fall out")
    return sequential([
        static_too_small,
        cut_too_small,
    ])(moves)

def split_choice(moves):
    return (cases([
        no_split_return,
        #too_short_return,
        #there is a split
        #favor easy choice
        connected_set_info,
        static_see_my_tail,
        static_see_other_tail,
        cut_see_my_tail,
        cut_can_reach_my_tail,
        cut_see_other_tail,
        cut_can_reach_other_tail,
        static_spacious,
        cut_info,
        (cut_spacious),
        static_wayout_info_me,
        (static_wayout_on_myself),
        static_wayout_info_other,
        static_wayout_on_other,
        cut_wayout_info_me,
        (cut_wayout_on_me),
        (cut_just_see_other_tail),
        (fallout),
    ]))(moves)

def cut_can_reach_other_tail(moves):
    occupied = g.occupied_cells[0]+g.x.other_territory
    def good(a):
        info = g.x.moves_info[a]
        if not info["see_other_head"]: return False
        aset = path_connected_set(a, occupied)
        adj_indexes = [i for i,c in enumerate(g.other["body"]) if any([p in aset for p in adj_cells(c)])]
        good_indexes = [i for i in adj_indexes if g.s.other_length-i-1<=path_distance_pq(a, g.other["body"][i])]
        return len(good_indexes) != 0
    moves = [a for a in moves if good(a)]
    if len(moves) != 0:
        if move_connected_group(moves) == 1:
            g.decision_path.append("cut can reach other tail")
            return moves

def cut_can_reach_my_tail(moves):
    occupied = g.occupied_cells[0]+g.x.other_territory
    def good(a):
        info = g.x.moves_info[a]
        if not info["see_other_head"]: return False
        aset = path_connected_set(a, occupied)
        adj_indexes = [i for i,c in enumerate(g.me["body"]) if c != g.s.my_tail and any([p in aset for p in adj_cells(c)])]
        good_indexes = [i for i in adj_indexes if g.s.my_length-i-1<=path_distance_pq(a, g.me["body"][i])]
        return len(good_indexes) != 0
    moves = [a for a in moves if good(a)]
    if len(moves) != 0:
        if move_connected_group(moves) == 1:
            g.decision_path.append("cut can reach my tail")
            return moves

def cut_see_my_tail(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
            if 1==1
            and info["see_other_head"]
            and path_connected(a, g.s.my_tail, g.occupied_cells[0]+g.x.other_territory)
            and path_distance_pq(a, g.s.my_tail) <= path_distance_pq(g.s.other_head, g.s.my_tail)
            and g.s.my_tail not in g.x.other_territory
            and not any([p in g.x.other_territory for p in adj_cells(g.me["body"][-2])])
    ]
    if len(moves) != 0:
        if move_connected_group(moves) == 1:
            g.decision_path.append("cut can see my tail")
            return moves

def cut_see_other_tail(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
            if 1==1
            and info["see_other_head"]
            and path_connected(a, g.s.other_tail)
            and path_distance_pq(a, g.s.other_tail) <= path_distance_pq(g.s.other_head, g.s.other_tail)
            and g.s.other_tail not in g.x.other_territory
    ]
    if len(moves) != 0:
        g.decision_path.append("cut see other tail")
        return moves

def static_see_my_tail(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
            if 1==1
            and not info["see_other_head"]
            and path_connected(a, g.s.my_tail)
            and path_distance_pq(a, g.s.my_tail) <= path_distance_pq(g.s.other_head, g.s.my_tail)
            and all([path_distance_pq(a, g.s.my_tail) <= path_distance_pq(g.s.other_head, p) for p in g.me["body"][-5:]])
    ]
    if len(moves) != 0:
        g.decision_path.append("static can see my tail")
        return moves

def static_see_other_tail(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
            if 1==1
            and not info["see_other_head"]
            and path_connected(a, g.s.other_tail)
            and path_distance_pq(a, g.s.other_tail) <= path_distance_pq(g.s.other_head, g.s.other_tail)
    ]
    if len(moves) != 0:
        g.decision_path.append("static can see other tail")
        return moves

def cut_just_see_other_tail(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
            if info["see_other_head"]
            and any([p in info["cut_set"] for p in adj_cells(g.s.other_tail)])
    ]
    if len(moves) != 0:
        g.decision_path.append("cut but can see other tail")
        return moves

def cut_wayout_on_me(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
             if info["see_other_head"]
             and len(info["cut_set"]) >= g.s.my_length - 1 - max(info["my_snake_adjacency"])
    ]
    if len(moves) != 0:
        g.decision_path.append("cut way out on me")
        return moves

def cut_wayout_info_me(moves):
    for a in moves:
        info = g.x.moves_info[a]
        if info["see_other_head"]:
            info["my_snake_adjacency"] = [
                i for i,c in enumerate(g.me["body"])
                if any([cx in info["cut_set"] for cx in adj_cells(c)])
            ]

def static_wayout_on_other(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
             if not info["see_other_head"]
             and len(info["other_snake_adjacency"]) != 0
             and len(info["aset"]) >= g.s.my_length - 1 - max(info["other_snake_adjacency"])
             ]
    if len(moves) != 0:
        g.decision_path.append("static way out on other")
        return moves

def static_wayout_info_other(moves):
    for a in moves:
        info = g.x.moves_info[a]
        if not info["see_other_head"]:
            info["other_snake_adjacency"] = [
                i for i,c in enumerate(g.other["body"])
                if any([cx in info["aset"] for cx in adj_cells(c)])
            ]

def static_wayout_on_myself(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
             if not info["see_other_head"]
             and len(info["aset"]) >= g.s.my_length - 1 - max(info["my_snake_adjacency"])
             ]
    if len(moves) != 0:
        g.decision_path.append("static way out on myself")
        return moves

def static_wayout_info_me(moves):
    for a in moves:
        info = g.x.moves_info[a]
        if not info["see_other_head"]:
            info["my_snake_adjacency"] = [
                i for i,c in enumerate(g.me["body"])
                if any([cx in info["aset"] for cx in adj_cells(c)])
            ]

def cut_spacious(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
        if info["see_other_head"] and len(info["cut_set"]) >= g.s.my_length ]
    if len(moves) != 0:
        g.decision_path.append("cut but spacious")
        return moves

def move_connected_group(moves):
    if len(moves) == 1:
        return 1
    if len(moves) == 2:
        a,b = moves
        if path_distance_pq(a, b) >= 4:
            return 2
        return 1
    if len(moves) == 3:
        straight = [a for a in moves if is_straight(a)][0]
        others = [a for a in moves if a != straight]
        if any([path_distance_pq(a, straight) > 2 for a in others]):
            return 2
        return 1

def cut_info(moves):
    for a in moves:
        info = g.x.moves_info[a]
        if info["see_other_head"]:
            info["cut_set"] = path_connected_set(a, g.occupied_cells[0]+g.x.other_territory)

def static_spacious(moves):
    moves = [a for a in moves for info in [g.x.moves_info[a]]
        if not info["see_other_head"] and len(info["aset"]) >= g.s.my_length ]
    if len(moves) != 0:
        g.decision_path.append("static spacious")
        return moves

def connected_set_info(moves):
    g.x.moves_info = {
        a: {
            "aset": aset,
            "see_other_head": any([p in aset for p in adj_cells(g.s.other_head)]),
        } for a in moves for aset in [path_connected_set(a)]
    }

def no_split_return(moves):
    ngroup = move_connected_group(moves)
    g.e.move_connected_group = ngroup
    if ngroup == 1:
        return moves

def too_short_return(moves):
    if g.s.my_length < 15:
        return moves

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

def chase_other_tail_has_distance2(moves):
    if distance_pq(g.s.my_head, g.s.other_tail) > 1:
        tail_moves = shortest_path_move(g.s.my_head, g.s.other_tail)
        tail_moves = [a for a in tail_moves if a in moves]
        if len(tail_moves) != 0:
            food1 = [a for a in moves if a in g.food]
            if len(food1) == 0:
                return tail_moves
            food_and_tail = [a for a in tail_moves if a in food1]
            if len(food_and_tail) != 0:
                return food_and_tail
            food_tail_connect = [a for a in food1 if any([path_connected(a, p) for p in tail_moves])]
            if len(food_tail_connect) != 0:
                return food_tail_connect
            return tail_moves

def chase_other_tail_long_shot(moves):
    if g.s.my_length <= g.s.other_length: return
    tail_info = [(i,c,d-i) for i,c in enumerate(reversed(g.other["body"])) 
                for d in [path_distance_pq(g.s.my_head, c)] if path_connected(g.s.my_head, c)]
    tail_info = [c for i,c,d in tail_info if abs(d) <= 2]
    if len(tail_info) != 0:
        tail_move = shortest_path_move(g.s.my_head, take_first(tail_info))
        tail_move = [a for a in moves if a in tail_move]
        if len(tail_move) != 0:
            return tail_move

def chase_other_tail_has_distance(moves):
    if g.s.my_length <= g.s.other_length: return
    tail_info = [(i,c,d-i) for i,c in enumerate(reversed(g.other["body"][-10:])) for d in [path_distance_pq(g.s.my_head, c)]]
    min_tail = min([d for i,c,d in tail_info])
    if min_tail >= 10: return
    if not any([d < path_distance_pq(g.s.other_head, g.s.other_tail) for i,c,d in tail_info]): return
    min_tail_target = [(i,c) for i,c,d in tail_info if d == min_tail]
    i,target = take_first(min_tail_target)
    if min_tail >= 2:
        tail_move = shortest_path_move(g.s.my_head, target)
        tail_move = [a for a in moves if a in tail_move]
        if len(tail_move) != 0:
            return tail_move
    else:
        detour = 2-min_tail
        paths = [[g.s.my_head]]
        for i in range(detour):
            paths = [path+[p] for path in paths for end in [path[-1]] for p in adj_cells(end)
                     if p not in path and p not in g.occupied_cells[0] ]
        paths = [path for path in paths for end in [path[-1]] if distance_pq(end, target) <= 2]
        paths = prefer_by_score(lambda path: len([p for p in path if p in g.food]))(paths)
        detour_moves = list(set([path[1] for path in paths]))
        moves = prefer_yes(lambda a: a in detour_moves)(moves)
        return moves

def chase_other_tail_too_close(moves):
    if is_adjacent(g.s.my_head, g.s.other_tail) == 1:
        if any([p for p in adj_cells(g.other["body"][-2]) if is_adjacent(p, g.s.other_head) and p not in g.occupied_cells[0]]):
            if g.s.other_tail in moves:
                return [g.s.other_tail]

        g.decision_path.append("don't follow too close")
        #not tail, not next to tail -1
        moves = prefer_yes(lambda a: path_distance_pq(a, g.s.other_tail) <= 4)(moves)
        moves = prefer_no(lambda a: a == g.s.other_tail or is_adjacent(a, g.other["body"][-2]))(moves)
        return moves
    if (distance_pq(g.s.my_head, g.s.other_tail) == 2 and g.other["health"] == 100):
        g.decision_path.append("don't follow too close")
        moves = prefer_yes(lambda a: path_distance_pq(a, g.s.other_tail) <= 4)(moves)
        moves = prefer_no(lambda a: a == g.s.other_tail or is_adjacent(a, g.other["body"][-2]))(moves)
        return moves

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
    #if path_connected(g.s.my_head, g.s.other_tail):
    #if g.s.other_tail in g.x.my_territory or g.s.other_tail in g.x.equal_territory:
    moves = cases([
        chase_other_tail_too_close,
        (chase_other_tail_has_distance),
        chase_other_tail_long_shot,
    ])(moves)
    return moves

def chase_my_tail_my_snake_not_longer(moves):
    if g.s.my_length <= g.s.other_length:
        if g.s.my_tail in g.x.my_territory:
            moves = [a for a in moves if path_connected(a, g.s.my_tail)]
            if len(moves) != 0:
                return moves

def shortest_path(a, b):
    d = path_distance_pq(a, b)
    if d == 999:
        return []
    layers = path_connected_layers(a)
    paths = [[a]]
    for i in range(d):
        paths = [path+[nhead] for path in paths for end in [path[-1]] for nhead in layers[i+1] if is_adjacent(end, nhead) ]
    paths = [path for path in paths if path[-1] == b]
    return paths

def add_waypoint(a, b, c):
    ab = shortest_path(a, b)
    bc = shortest_path(b, c)
    paths = [pab+pbc[1:] for pab in ab for pbc in bc if not any([p in pab for p in pbc[1:]])]
    return paths

def chase_my_tail_my_snake_longer(moves):
    if g.s.my_length <= g.s.other_length: return
    tail_info = [(i,c,d-i) for i,c in enumerate(reversed(g.me["body"][-5:])) for d in [path_distance_pq(g.s.my_head, c)]]
    min_tail = min([d for i,c,d in tail_info])
    if min_tail >= 10: return
    if not any([d < path_distance_pq(g.s.other_head, g.s.my_tail) for i,c,d in tail_info]): return
    min_tail_target = [(i,c) for i,c,d in tail_info if d == min_tail]
    i,target = take_first(min_tail_target)
    if min_tail >= 2:
        tail_move = shortest_path_move(g.s.my_head, target)
        tail_move = [a for a in moves if a in tail_move]
        if len(tail_move) != 0:
            return tail_move
    else:
        detour = 2-min_tail
        paths = [[g.s.my_head]]
        for i in range(detour):
            paths = [path+[p] for path in paths for end in [path[-1]] for p in adj_cells(end)
                     if p not in path and p not in g.occupied_cells[0] ]
        paths = [path for path in paths for end in [path[-1]] if distance_pq(end, target) <= 2]
        paths = prefer_by_score(lambda path: len([p for p in path if p in g.food]))(paths)
        detour_moves = list(set([path[1] for path in paths]))
        moves = prefer_yes(lambda a: a in detour_moves)(moves)
        return moves

def chase_my_tail_my_snake_longer2(moves):
    if g.s.my_length > g.s.other_length:
        if path_distance_pq(g.s.other_head, g.s.my_tail) > path_distance_pq(g.s.my_head, g.s.my_tail):
            # moves = [a for a in moves if path_connected(a, g.s.my_tail)]
            # if len(moves) != 0:
            #     return moves
            if distance_pq(g.s.my_head, g.s.my_tail) >= 1:
                tail_moves = shortest_path_move(g.s.my_head, g.s.my_tail)
                tail_moves = [a for a in tail_moves if a in moves]
                if len(tail_moves) != 0:
                    food1 = [a for a in moves if a in g.food]
                    if len(food1) != 0:
                        food_and_tail = [a for a in tail_moves if a in food1]
                        if len(food_and_tail) != 0:
                            return food_and_tail
                        food_tail_connect = [a for a in food1 if any([path_connected(a, p) for p in tail_moves])]
                        if len(food_tail_connect) != 0:
                            g.decision_path.append("detour get food1")
                            return food_tail_connect
                    #return tail_moves
                    else:
                        food4 = [f for f in g.food if distance_pq(f, g.s.my_head) <= 4]
                        if len(food4) == 0:
                            return tail_moves
                        foods = []
                        for f in food4:
                            paths = add_waypoint(g.s.my_head, f, g.s.my_tail)
                            good_paths = [path for path in paths if len(path) <= path_distance_pq(g.s.my_head, g.s.my_tail)+5]
                            if len(good_paths) == 0:
                                continue
                            sn = min([len(path) for path in good_paths])
                            shortest_path = [path for path in good_paths if len(path) == sn]
                            foods.append([f, sn, list({path[1] for path in shortest_path})])
                        food4 = foods
                        if len(food4) == 0:
                            return tail_moves
                        min_sn = min([sn for f,sn,m in food4])
                        f,sn,moves = take_first([(f,sn,m) for f,sn,m in food4 if sn == min_sn])
                        g.decision_path.append(f"add food waypoint {f}")
                        return moves

def chase_my_tail_other_not_in_the_way(moves):
    if path_distance_pq(g.s.my_head, g.s.my_tail) <= path_distance_pq(g.s.my_head, g.s.other_head):
        moves = [a for a in moves if path_connected(a, g.s.my_tail) and path_distance_pq(a, g.s.my_tail) <= path_distance_pq(a, g.s.other_head)]
        if len(moves) != 0:
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

def chase_my_tail_not_connected_return(moves):
    if not path_connected(g.s.my_head, g.s.my_tail):
        return moves

def chase_my_tail(moves):
    moves = cases([
        chase_my_tail_my_snake_longer,
        chase_my_tail_not_connected_return,
        chase_my_tail_my_snake_not_longer,
        chase_my_tail_other_not_in_the_way,
    ])(moves)
    return moves

def not_too_long(moves):
    if g.s.my_length < 20:
        moves = sequential([
            split_choice,
            get_food,
            #prefer_more_next_move,
            #prefer_middle_by_3,
            prefer_straight,
        ])(moves)
        return moves

def food1(moves):
    moves = prefer_yes(lambda a: a in g.food)(moves)
    return moves

def wayout2(moves):
    if g.e.move_connected_group != 1: return moves
    if path_connected(g.s.my_head, g.s.my_tail):
        if distance_pq(g.s.my_head, g.s.my_tail) > 1:
            return moves
        if any([path_connected(p, g.s.my_tail) for p in g.e.allowed_moves]):
            return moves
    if path_connected(g.s.my_head, g.s.other_tail):
        if distance_pq(g.s.my_head, g.s.other_tail) > 1:
            return moves
        if any([path_connected(p, g.s.other_tail) for p in g.e.allowed_moves]):
            return moves
    if path_connected(g.s.my_head, g.s.other_head): return moves
    g.decision_path.append("confined")
    return cases([
        wayout("me"),
        wayout("other"),
    ])(moves)

def wayout(who):
    def fn(moves):
        aset = path_connected_set(g.s.my_head)
        aset = [p for p in aset if p != g.s.my_head]
        adj_indexes = [i for i in range(g.s.my_length) if any([p in aset for p in adj_cells(g.me["body"][i])])]
        max_index = max(adj_indexes)
        wayout_point = g.me["body"][max_index]
        required_steps = g.s.my_length - max_index - 1
        if who == "other":
            adj_indexes = [i for i in range(g.s.other_length) if any([p in aset for p in adj_cells(g.other["body"][i])])]
            if len(adj_indexes) == 0: return
            max_index = max(adj_indexes)
            wayout_point = g.other["body"][max_index]
            required_steps = g.s.other_length - max_index - 1

        if len(aset) < required_steps:
            g.decision_path.append(f"no wayout on {who}: {len(aset)} < {required_steps}")
            return

        if len(aset) > 12:
            g.decision_path.append("confine too big, meander")
            def farther(a):
                d = path_distance_pq(a, wayout_point)
                if d == 999:
                    d = -1
                return d
            def packed(a):
                allowed = [p for p in adj_cells(a) if a not in g.occupied_cells[0]]
                n_packed = 3 - len(allowed)
                return n_packed
            return prefer_by_score(packed)(prefer_by_score(farther)(moves))

        layers = [[[g.s.my_head]]]
        while True:
            layer = layers[-1]
            layer = [path+[p] for path in layer for end in [path[-1]] for p in adj_cells(end) if p not in g.occupied_cells[0] and p not in path]
            if len(layer) == 0: break
            layers.append(layer)
        paths = [path for i,layer in enumerate(layers) if i >= required_steps for path in layer]
        paths = [path for path in paths if is_adjacent(path[-1], wayout_point)]
        paths = [path for path in paths 
                for food_in_path in [[p for p in path if p in g.food]] 
                if len(path)-len(food_in_path)>required_steps]
        moves = list({path[1] for path in paths})
        if len(moves) == 0:
            g.decision_path.append("no calculated wayout on {who}")
            return
        g.decision_path.append("calculated wayout on {who}")
        return moves
    return fn

def chase_tail(moves):
    #if int(g.s.my_length / 1.5) >= g.s.other_length:
    if g.s.my_length >= 35:
        return sequential([
            (chase_my_tail),
            (chase_other_tail),
        ])(moves)
    else:
        moves = sequential([
            (chase_other_tail),
            (chase_my_tail),
        ])(moves)
        return moves

def too_long(moves):
    if g.s.my_length >= 20:
        moves = sequential([
            (split_choice),
            wayout2,
            (chase_tail),
            #prefer_more_next_move,
            #prefer_middle_by_3,
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
    log = {'id': '5bd90b92-9e8a-4063-92d8-8c6880138ce8', 'turn': 337, 'me': {'name': 'mark_snake', 'health': 70, 'body': [(7, 6), (6, 6), (5, 6), (4, 6), (3, 6), (3, 5), (3, 4), (3, 3), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (7, 3), (6, 3), (5, 3), (4, 3), (4, 4), (4, 5), (5, 5), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)]}, 'others': [{'name': 'ich heisse marvin', 'health': 90, 'body': [(6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (2, 2), (1, 2), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]}], 'food': [(10, 0), (2, 0), (9, 1), (5, 0), (7, 0), (6, 0), (7, 5), (1, 8), (7, 7)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(8, 6), (7, 7), (7, 5)], 'head_distance': 6, 'head_path_distance': 10, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (7, 5), 'next_move': 'down', 'time': '0.005s'}
    log = {'id': '5bd90b92-9e8a-4063-92d8-8c6880138ce8', 'turn': 335, 'me': {'name': 'mark_snake', 'health': 72, 'body': [(5, 6), (4, 6), (3, 6), (3, 5), (3, 4), (3, 3), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (7, 3), (6, 3), (5, 3), (4, 3), (4, 4), (4, 5), (5, 5), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (10, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 92, 'body': [(4, 1), (3, 1), (2, 1), (2, 2), (1, 2), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 7), (1, 6)]}], 'food': [(10, 0), (2, 0), (9, 1), (5, 0), (7, 0), (6, 0), (7, 5), (1, 8), (7, 7)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 6), (5, 7)], 'head_distance': 6, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (6, 6), 'next_move': 'right', 'time': '0.004s'}
    log = {'id': '41a7cbf3-285b-474f-b3df-469db577410c', 'turn': 223, 'me': {'name': 'mark_snake', 'health': 87, 'body': [(6,1), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (6, 8), (6, 7), (6, 6), (6, 5), (6, 4), (7, 4), (8, 4), (9, 4), (9, 3), (9, 2), (9, 1), (8, 1), (8, 0), (7, 0), (6, 0), (5, 0), (4, 0), (3, 0)]}, 'others': [{'name': 'ich heisse marvin', 'health': 92, 'body': [(2,1), (3, 1), (3, 2), (3, 3), (3, 4), (2, 4), (1, 4), (0, 4), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5)]}], 'food': [(10, 8), (1, 8), (5, 9), (0,2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 1), (4, 1)], 'head_distance': 2, 'head_path_distance': 2, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'static way out on myself'], 'next_coord': (6, 1), 'next_move': 'right', 'time': '0.001s'}

    #cut, but I have more space than calculated
    log = {'id': 'f79b9708-5776-48bc-8c7e-599d8c7b340a', 'turn': 253, 'me': {'name': 'mark_snake', 'health': 91, 'body': [(10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (3, 9), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (8, 7), (8, 6), (8, 5), (8, 4), (9, 4), (9, 3), (9, 2), (9, 1), (8, 1), (7, 1), (7, 2), (6, 2), (5, 2), (4, 2)]}, 'others': [{'name': 'ich heisse marvin', 'health': 99, 'body': [(5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 7), (2, 7)]}], 'food': [(2, 6), (1, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 5), (10, 4)], 'head_distance': 10, 'head_path_distance': 10, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'static way out on myself'], 'next_coord': (9, 5), 'next_move': 'left', 'time': '0.004s'}

    #cut, shoudn't take that move
    log = {'id': 'd9ab5d3a-5a26-4cf5-984b-4eb39c91de15', 'turn': 258, 'me': {'name': 'mark_snake', 'health': 94, 'body': [(1, 5), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (4, 1), (5, 1), (5, 2), (5, 3), (6, 3), (7, 3), (7, 4), (7, 5), (7, 6), (6, 6), (5, 6), (5, 5), (4, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 88, 'body': [(2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (3, 9), (3, 10), (4, 10), (5, 10), (6, 10), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9)]}], 'food': [(10, 2), (9, 0), (9, 7), (10, 0), (4, 8)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(1, 6), (1, 4)], 'head_distance': 2, 'head_path_distance': 2, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (1, 4), 'next_move': 'down', 'time': '0.004s'}

    #calculated wayout
    log = {'id': 'f21a4b57-e082-4812-8ff8-b12f065383a6', 'turn': 200, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(1, 7), (0, 7), (0, 8), (0, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (4, 9), (4, 8), (4, 7), (4, 6), (3, 6), (2, 6), (1, 6), (0, 6), (0, 5), (0, 4), (1, 4), (2, 4), (2, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 72, 'body': [(3, 5), (4, 5), (5, 5), (5, 6), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (5, 10)]}], 'food': [(2, 9), (7, 0), (9, 0), (4, 3), (8, 0), (10, 9), (6, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(2, 7), (1, 8)], 'head_distance': 4, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1', 'confined', 'calculated wayout'], 'next_coord': (1, 8), 'next_move': 'up', 'time': '0.001s'}
    log = {'id': 'f21a4b57-e082-4812-8ff8-b12f065383a6', 'turn': 198, 'me': {'name': 'mark_snake', 'health': 98, 'body': [(0, 8), (0, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (4, 9), (4, 8), (4, 7), (4, 6), (3, 6), (2, 6), (1, 6), (0, 6), (0, 5), (0, 4), (1, 4), (2, 4), (2, 5), (3, 5), (4, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 74, 'body': [(5, 5), (5, 6), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (5, 10), (5, 9), (5, 8)]}], 'food': [(2, 9), (7, 0), (9, 0), (4, 3), (8, 0), (10, 9)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(1, 8), (0, 7)], 'head_distance': 8, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (0, 7), 'next_move': 'down', 'time': '0.001s'}
    log = {'id': 'f21a4b57-e082-4812-8ff8-b12f065383a6', 'turn': 197, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(0, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (4, 9), (4, 8), (4, 7), (4, 6), (3, 6), (2, 6), (1, 6), (0, 6), (0, 5), (0, 4), (1, 4), (2, 4), (2, 5), (3, 5), (4, 5), (4, 4)]}, 'others': [{'name': 'ich heisse marvin', 'health': 75, 'body': [(5, 6), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (5, 10), (5, 9), (5, 8), (5, 7)]}], 'food': [(2, 9), (7, 0), (9, 0), (4, 3), (8, 0), (10, 9)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(1, 9), (0, 8)], 'head_distance': 8, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (0, 8), 'next_move': 'down', 'time': '0.001s'}

    log = {'id': '55756e9b-762d-4fef-975d-00d2325f4c79', 'turn': 189, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(6, 3), (6, 4), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (6, 8), (6, 9), (7, 9), (8, 9), (8, 8), (8, 7), (8, 6), (8, 5), (8, 4), (8, 3), (8, 2), (7, 2), (7, 1), (6, 1), (5, 1), (4, 1)]}, 'others': [{'name': 'ich heisse marvin', 'health': 50, 'body': [(3, 2), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 6)]}], 'food': [(0, 8)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 3), (5, 3), (6, 2)], 'head_distance': 4, 'head_path_distance': 4, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'static way out on myself'], 'next_coord': (7, 3), 'next_move': 'right', 'time': '0.015s'}
    log = {'id': 'ad8b22d1-02af-4445-a516-58a7c5d7a0bd', 'turn': 344, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (9, 8), (8, 8), (8, 9), (8, 10), (7, 10), (6, 10), (5, 10), (5, 9), (5, 8), (6, 8), (7, 8), (7, 7), (7, 6), (7, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 84, 'body': [(4, 6), (3, 6), (3, 5), (4, 5), (5, 5), (6, 5), (6, 4), (5, 4), (5, 3), (5, 2), (4, 2), (3, 2), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3), (2, 3), (2, 4), (1, 4), (1, 5), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0)]}], 'food': [(10, 10), (0, 7), (8, 5), (6, 9)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 0), (4, 1)], 'head_distance': 6, 'head_path_distance': 999, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'static can see my tail'], 'next_coord': (4, 1), 'next_move': 'up', 'time': '0.001s'}

    #fall out - should be able to chase other tail
    log = {'id': '1c745175-013a-45bf-a94b-9300754f351c', 'turn': 285, 'me': {'name': 'mark_snake', 'health': 92, 'body': [(5, 4), (5, 5), (5, 6), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (10, 6), (10, 5), (9, 5), (8, 5), (8, 4), (8, 3), (7, 3), (6, 3), (5, 3), (4, 3), (3, 3), (3, 2), (3, 1), (4, 1), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (9, 3)]}, 'others': [{'name': 'ich heisse marvin', 'health': 90, 'body': [(2, 3), (1, 3), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, 9), (2, 9), (2, 8), (3, 8), (4, 8), (4, 7), (3, 7), (2, 7), (2, 6), (1, 6), (1, 5), (1, 4)]}], 'food': [(9, 10), (10, 10), (3, 9), (9, 9), (3, 0)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 4), (4, 4)], 'head_distance': 4, 'head_path_distance': 4, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'fall out'], 'next_coord': (6, 4), 'next_move': 'right', 'time': '0.004s'}

    log = {'id': '92080ebd-45ec-4778-a29e-0597e0953889', 'turn': 251, 'me': {'name': 'mark_snake', 'health': 79, 'body': [(5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (9, 6), (8, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1), (7, 1), (6, 1), (6, 2), (6, 3), (6, 4), (5,4), (4,4), (4,5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 37, 'body': [(2, 3), (2, 4), (2, 5), (2, 6), (1, 6), (0, 6), (0, 7), (0, 8), (1, 8), (2, 8), (3,8), (4,8)]}], 'food': [(1, 0), (3, 1), (0, 10), (2, 0), (0, 5), (5, 2), (2, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(8, 0), (9, 1)], 'head_distance': 14, 'head_path_distance': 14, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'cut can reach my tail'], 'next_coord': (8, 0), 'next_move': 'left', 'time': '0.004s'}
    log = {'id': '92080ebd-45ec-4778-a29e-0597e0953889', 'turn': 254, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(3, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (9, 6), (8, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1), (7, 1), (6, 1), (6, 2), (6, 3), (6, 4)]}, 'others': [{'name': 'ich heisse marvin', 'health': 37, 'body': [(4, 2), (3, 2), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (1, 6), (0, 6), (0, 7), (0, 8), (1, 8), (2, 8)]}], 'food': [(1, 0), (3, 1), (0, 10), (2, 0), (0, 5), (5, 2), (2, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(8, 0), (9, 1)], 'head_distance': 14, 'head_path_distance': 14, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'cut can reach my tail'], 'next_coord': (8, 0), 'next_move': 'left', 'time': '0.004s'}

    log = {'id': '3ce4cdcf-8c41-4bf7-8e05-639a3057cd4c', 'turn': 232, 'me': {'name': 'mark_snake', 'health': 92, 'body': [(7,7), (7,8), (6, 8), (5, 8), (4, 8), (4, 9), (3, 9), (2, 9), (1, 9), (0, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (5, 9), (6, 9), (7, 9), (7, 10), (8, 10), (8, 9), (8, 8), (9, 8), (9, 9), (9, 10), (10, 10), (10, 9), (10, 8), (10, 7)]}, 'others': [{'name': 'ich heisse marvin', 'health': 70, 'body': [(10,6), (9,6), (8, 6), (7, 6), (6, 6), (6, 5), (6, 4), (6, 3), (5, 3), (4, 3), (4, 4), (3, 4), (3, 5), (3, 6)]}], 'food': [(4, 0), (3, 0), (7, 1), (6, 10), (7, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 8), (6, 7)], 'head_distance': 4, 'head_path_distance': 4, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (7, 8), 'next_move': 'right', 'time': '0.003s'}

    log = {'id': 'd83c8858-574d-4a0f-a99a-b7696bb42b5f', 'turn': 211, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (10, 8), (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (10, 2), (10, 1), (10, 0), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (8, 6), (7, 6), (7, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 81, 'body': [(6, 5), (6, 6), (6, 7), (5, 7), (5, 6), (4, 6), (4, 7), (4, 8), (4, 9), (3, 9), (2, 9), (1, 9), (1, 8), (1, 7)]}], 'food': [(8, 1), (2, 0), (2, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(4, 10), (5, 9)], 'head_distance': 6, 'head_path_distance': 16, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'static way out on myself'], 'next_coord': (5, 9), 'next_move': 'down', 'time': '0.003s'}
    log = {'id': 'b9cfd4e8-a33b-4014-92ca-9922e0f432c8', 'turn': 241, 'me': {'name': 'mark_snake', 'health': 80, 'body': [(9, 2), (8, 2), (8, 3), (7, 3), (7, 2), (6, 2), (6, 3), (5, 3), (5, 2), (5, 1), (5, 0), (4, 0), (3, 0), (3, 1), (4, 1), (4, 2), (3, 2), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 7)]}, 'others': [{'name': 'ich heisse marvin', 'health': 100, 'body': [(7, 8), (8, 8), (9, 8), (9, 7), (8, 7), (7, 7), (6, 7), (6, 6), (6, 5), (7, 5), (7, 4), (8, 4), (9, 4), (9, 3), (10, 3), (10, 3)]}], 'food': [(0, 0), (0, 4), (0, 6), (8, 10), (9, 5), (6, 8), (1, 10), (2, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 2), (9, 1)], 'head_distance': 8, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (10, 2), 'next_move': 'right', 'time': '0.003s'}
    log = {'id': '9ed13cce-47c5-4a6c-a83a-c3dc9a030126', 'turn': 192, 'me': {'name': 'mark_snake', 'health': 97, 'body': [(4, 8), (3, 8), (2, 8), (1, 8), (1, 7), (0, 7), (0, 6), (0, 5), (1, 5), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (5, 3), (5, 2), (4, 2), (3, 2), (2, 2), (2, 1), (3, 1), (3, 0), (4, 0), (5, 0), (6, 0), (6, 1), (6, 2)]}, 'others': [{'name': 'ich heisse marvin', 'health': 78, 'body': [(6, 8), (6, 7), (6, 6), (6, 5), (6, 4), (7, 4), (8, 4), (9, 4), (9, 5), (9, 6), (9, 7)]}], 'food': [(1, 0), (1, 1)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(5, 8), (4, 9), (4, 7)], 'head_distance': 2, 'head_path_distance': 2, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (5, 8), 'next_move': 'right', 'time': '0.004s'}
    log = {'id': '7a8ee3fa-4a53-4876-b5f1-88c377278654', 'turn': 262, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(10, 8), (9, 8), (9, 7), (8, 7), (7, 7), (7, 6), (7, 5), (6, 5), (5, 5), (4, 5), (3, 5), (3, 6), (3, 7), (3, 8), (4, 8), (5, 8), (5, 9), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (1, 9), (1, 8), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), (2, 2), (2, 1), (2, 0), (3, 0), (4, 0)]}, 'others': [{'name': 'ich heisse marvin', 'health': 62, 'body': [(8, 0), (7, 0), (6, 0), (6, 1), (5, 1), (4, 1), (3, 1), (3, 2), (4, 2), (5, 2), (5, 3), (6, 3), (7, 3), (8, 3)]}], 'food': [(10, 10), (0, 0), (0, 4), (0, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 9), (10, 7)], 'head_distance': 10, 'head_path_distance': 10, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'static way out on myself'], 'next_coord': (10, 9), 'next_move': 'up', 'time': '0.003s'}
    log = {'id': '7a8ee3fa-4a53-4876-b5f1-88c377278654', 'turn': 270, 'me': {'name': 'mark_snake', 'health': 94, 'body': [(6, 8), (7, 8), (8, 8), (8, 9), (9, 9), (9, 10), (10, 10), (10, 9), (10, 8), (9, 8), (9, 7), (8, 7), (7, 7), (7, 6), (7, 5), (6, 5), (5, 5), (4, 5), (3, 5), (3, 6), (3, 7), (3, 8), (4, 8), (5, 8), (5, 9), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (1, 9), (1, 8), (2, 8), (2, 7), (2, 6), (2, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 54, 'body': [(2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (7, 1), (8, 1), (8, 0), (7, 0), (6, 0), (6, 1), (5, 1), (4, 1)]}], 'food': [(0, 0), (0, 4), (0, 5), (4, 6)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 10)], 'head_distance': 12, 'head_path_distance': 999}, 'decision_path': [], 'next_coord': (9, 10), 'next_move': 'left', 'time': '0.000s'}

    log = {'id': '648c0703-98f5-417b-b25e-f4c970229466', 'turn': 338, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(2,10), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (0, 6), (1, 6), (1, 7), (2, 7), (3, 7), (4, 7), (4, 6), (4, 5), (4, 4), (5, 4), (5, 5), (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (7, 1), (8, 1), (9, 1), (9, 2), (8, 2), (7, 2), (7, 3), (7, 4), (7, 5), (7, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 93, 'body': [(7,7), (8, 7), (8, 6), (8, 5), (9, 5), (10, 5), (10, 6), (10, 7), (10, 8), (9, 8), (8, 8), (8, 9), (8, 10), (7, 10), (7, 9), (6, 9), (6, 8)]}], 'food': [(2, 10), (1, 0), (3, 9)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(2, 10), (1, 9)], 'head_distance': 10, 'head_path_distance': 10, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (2, 10), 'next_move': 'right', 'time': '0.001s'}
    log = {'id': 'ce43fd42-b928-4697-9719-8fa2e970faae', 'turn': 196, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(5, 9), (5, 8), (5, 7), (6, 7), (7, 7), (8, 7), (8, 6), (8, 5), (8, 4), (7, 4), (6, 4), (5, 4), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (10, 2), (9, 2)]}, 'others': [{'name': 'ich heisse marvin', 'health': 29, 'body': [(2, 8), (3, 8), (4, 8), (4, 7), (4, 6), (4, 5), (4, 4), (4, 3), (3, 3), (3, 2), (2, 2), (2, 3), (1, 3), (1, 4)]}], 'food': [(1, 0), (5, 2), (0, 0)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 9), (4, 9), (5, 10)], 'head_distance': 4, 'head_path_distance': 4, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (4, 9), 'next_move': 'left', 'time': '0.004s'}
    log = {'id': 'ce43fd42-b928-4697-9719-8fa2e970faae', 'turn': 211, 'me': {'name': 'mark_snake', 'health': 80, 'body': [(8, 9), (8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (5, 8), (5, 7), (6, 7), (7, 7)]}, 'others': [{'name': 'ich heisse marvin', 'health': 94, 'body': [(4, 3), (3, 3), (3, 2), (3, 1), (3, 0), (2, 0), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 6), (2, 7)]}], 'food': [(5, 2), (0, 0), (0, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 9), (7, 9), (8, 8)], 'head_distance': 10, 'head_path_distance': 10, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (9, 9), 'next_move': 'right', 'time': '0.007s'}
    log = {'id': 'fc4f22a1-c088-4237-8352-b6387c143389', 'turn': 265, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(7, 6), (6, 6), (6, 7), (6, 8), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (10, 8), (10, 7), (9, 7), (9, 6), (9, 5), (9, 4), (9, 3), (9, 2), (9, 1), (8, 1), (7, 1), (6, 1), (6, 2), (7, 2), (8, 2), (8, 3), (8, 4), (8, 5), (7, 5), (7, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 78, 'body': [(5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (4, 8), (3, 8), (3, 7), (2, 7), (2, 8), (1, 8), (1, 7), (1, 6), (1, 5)]}], 'food': [(4, 10), (2, 2), (1, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(8, 6), (7, 7)], 'head_distance': 4, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (8, 6), 'next_move': 'right', 'time': '0.003s'}
    log = {'id': '40481703-0d9f-4cc7-9280-2d14d7d0e4fc', 'turn': 203, 'me': {'name': 'mark_snake', 'health': 70, 'body': [(7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3), (9, 3), (9, 4), (10, 4), (10, 5), (9, 5), (8, 5), (7, 5), (7, 6), (7, 7), (6, 7), (5, 7), (5, 6), (5, 5), (5, 4), (6, 4), (6, 3), (7, 3)]}, 'others': [{'name': 'ich heisse marvin', 'health': 91, 'body': [(6, 1), (5, 1), (5, 2), (4, 2), (4, 1), (3, 1), (2, 1), (1, 1), (1, 0), (2, 0), (3, 0), (4, 0)]}], 'food': [(9, 7), (7, 4), (8, 8)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 0), (7, 1)], 'head_distance': 2, 'head_path_distance': 2, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'cut can see my tail'], 'next_coord': (7, 1), 'next_move': 'up', 'time': '0.002s'}
    log = {'id': '21ba65da-5ff2-4771-8085-2ee78f662c7d', 'turn': 38, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(5,10), (5, 9), (5, 8), (5, 7), (5, 6), (4, 6), (3, 6), (2, 6)]}, 'others': [{'name': 'ich heisse marvin', 'health': 90, 'body': [(3,4), (4, 4), (5, 4), (6, 4), (6, 5), (6, 6)]}], 'food': [(1, 1)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 9), (4, 9), (5, 10)], 'head_distance': 6, 'head_path_distance': 12, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (5, 10), 'next_move': 'up', 'time': '0.005s'}
    log = {'id': '5a73447e-79ac-457d-ba17-adc89f00cd74', 'turn': 86, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(8, 10), (9, 10), (10, 10), (10, 9), (10, 8), (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (10, 2), (10, 1)]}, 'others': [{'name': 'ich heisse marvin', 'health': 99, 'body': [(7, 9), (7, 8), (6, 8), (6, 7), (6, 6), (6, 5), (6, 4), (6, 3), (6, 2)]}], 'food': [(7, 1), (0, 9)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 10), (8, 9)], 'head_distance': 2, 'head_path_distance': 2, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (7, 10), 'next_move': 'left', 'time': '0.002s'}
    log = {'id': '50309707-5dd2-45fc-890f-3710a06db5ba', 'turn': 141, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(10, 9), (9, 9), (8, 9), (7, 9), (7, 8), (6, 8), (5, 8), (5, 7), (4, 7), (4, 6), (4, 5), (3, 5), (3, 4), (2, 4), (2, 5), (2, 6), (1, 6), (1, 5), (1, 4), (0, 4), (0, 5), (0, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 88, 'body': [(8, 3), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (8, 7), (8, 6), (8, 5), (8, 4)]}], 'food': [(4, 9), (4, 2), (7, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 10), (10, 8)], 'head_distance': 8, 'head_path_distance': 10, 'move_connected_group': 2}, 'decision_path': ['battle_1_vs_1', 'cut can reach other tail'], 'next_coord': (10, 8), 'next_move': 'down', 'time': '0.009s'}
    log = {'id': 'cde24395-e19c-4d2f-bab3-e103a94d0785', 'turn': 201, 'me': {'name': 'mark_snake', 'health': 74, 'body': [(8, 5), (7, 5), (6, 5), (5, 5), (5, 4), (6, 4), (7, 4), (7, 3), (7, 2), (7, 1), (6, 1), (5, 1), (5, 2), (4, 2), (4, 1), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (8, 1), (9, 1), (10, 1)]}, 'others': [{'name': 'ich heisse marvin', 'health': 63, 'body': [(7, 8), (8, 8), (9, 8), (10, 8), (10, 7), (9, 7), (9, 6), (8, 6), (7, 6), (6, 6)]}], 'food': [(3, 9), (9, 10), (0, 1), (1, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 5), (8, 4)], 'head_distance': 4, 'head_path_distance': 999, 'move_connected_group': 1}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (8, 4), 'next_move': 'down', 'time': '0.003s'}

    game_state = init_from_log(log)
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()

