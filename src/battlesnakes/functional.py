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
        self.other_connected_set = None
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

def is_opposite_dir(dir1, dir2):
    if dir1 == "up" and dir2 == "down":
        return True
    if dir1 == "down" and dir2 == "up":
        return True
    if dir1 == "left" and dir2 == "right":
        return True
    if dir1 == "right" and dir2 == "left":
        return True
    return False

def is_perpendicular_dir(dir1, dir2):
    if dir1 == "up" and dir2 in ["left", "right"]:
        return True
    if dir1 == "down" and dir2 in ["left", "right"]:
        return True
    if dir1 == "left" and dir2 in ["up", "down"]:
        return True
    if dir1 == "right" and dir2 in ["up", "down"]:
        return True
    return False

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

def distance_vector_abs(p, q):
    x1,y1 = p
    x2,y2 = q
    dx,dy = x2-x1, y2-y1
    return (abs(dx), abs(dy))

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
    """
    if g.other["name"] not in (
        "Snakeformatika", #inform
        #"Kakemonsteret-v2", #pettso
        #"Wim HU [dev]", #wim
        #"Frank The Tank", #djnuller
        "ich heisse marvin", #Wrenger
    ): 
        return False
    """
    return True

def special_experimenting_code(game_state):
    #if functional2.special_experimenting_code(game_state): return True

    init_game(game_state)
    if not experiment_condition(): return False

    g.log["module"] = "functional"
    start_time = time.time()
    #g.e.localtime = time.localtime()

    decision()
    g.state["next_move"] = get_adjacent_dir(g.s.my_head, g.next_coord)

    #g.log["decision_support"] = {k:v for k,v in g.e.__dict__.items() if v is not None}
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
        #battle_1_vs_n,
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
        try:
            moves = cases([
                equal_line,
                kill_oppotunities,
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

def push_to_equal_border(moves):
    targets = prefer_by_rank(lambda p: path_distance_pq(p, g.s.other_head))(g.x.equal_border)
    if len(targets) == 0:
        return
    distance = path_distance_pq(g.s.my_head, take_first(targets))
    if distance > 4:
        return
    targets = prefer_by_score(lambda p: min(distance_to_border(p)))(targets)
    g.decision_path.append(f"push to equal border {targets}")
    moves = [a for p in targets for a in shortest_path_move(g.s.my_head, p) if a in moves]
    if len(moves) != 0:
        return moves

def avoid_collision(moves):
    moves = cases([
        single_collision_point,
        (two_collision_points),
        (avoid_multi_step_collision),
    ])(moves)
    return moves

def coming_near():
    killer_next = [p for p in adj_cells(g.s.other_head) if get_adjacent_dir(g.s.other_neck, g.s.my_head) == get_adjacent_dir(g.s.other_head, p)]
    killer_next = [p for p in killer_next if p not in g.occupied_cells[0]]
    if len(killer_next) == 0:
        return False
    killer_next = killer_next[0]
    my_next = [p for p in adj_cells(g.s.my_head) if is_straight(p) and p not in g.occupied_cells[0]]
    if len(my_next) == 0:
        return False
    my_next = my_next[0]
    if distance_pq(killer_next, my_next) < distance_pq(g.s.my_head, g.s.other_head):
        return True
    return False

def killer_near(moves):
    if on_border(g.s.my_head):
        return cases([
            killer_near_crawling,
            killer_near_heading_border,
        ])(moves)

def enemy_can_come_near():
    return any([a for a in adj_cells(g.s.other_head)
                if a not in g.occupied_cells[0] 
                and distance_pq(a, g.s.my_head) < distance_pq(g.s.other_head, g.s.my_head)])

def killer_near_crawling(moves):
    if on_border(g.s.my_neck):
        d = path_distance_pq(g.s.my_head, g.s.other_head)
        if d <= 6:
            if enemy_can_come_near():
                if path_distance_pq(g.s.other_head, g.s.my_head, g.occupied_cells[d//2-1]) == d:
                    #direct connect
                    g.decision_path.append("killer near crawling")
                    moves = prefer_no(on_border)(moves)
                    if len(moves) != 0:
                        return moves

def killer_near_heading_border(moves):
    if not on_border(g.s.my_neck):
        if distance_pq(g.s.my_head, g.s.other_head) == 4:
            if path_distance_pq(g.s.my_head, g.s.other_head) == 4:
                vdist = distance_vector_abs(g.s.my_head, g.s.other_head)
                if vdist in [(1,3), (3,1), (2,2)]:
                    g.decision_path.append("killer near heading border")
                    return prefer_by_score(lambda a: path_distance_pq(a, g.s.other_head))(moves)

def avoid_multi_step_collision(moves):
    if g.s.my_length >= g.s.other_length:
        return

    def score_a_move_by_second_step(a):
        aa = [p for p in adj_cells(a) if p not in g.occupied_cells[1]]
        if len(aa) == 0:
            return 1

        if all([
            path_distance_pq(g.s.other_head, p) == 2 
            or (len(path_connected_set(p, occupied)) <= 2
                    and not path_connected(p, g.s.my_tail, occupied)
                    and not path_connected(p, g.s.other_tail, occupied))    
            or (len(adj_p) == 1 and path_distance_pq(g.s.other_head, take_first(adj_p)) == 3)
                for p in aa
                for occupied in [g.occupied_cells[1]+[a]] 
                for adj_p in [[q for q in adj_cells(p) if q not in occupied]]
        ]):
            return 2
        return 999

    return prefer_by_score(score_a_move_by_second_step)(moves)

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
        food_good = [(f, d1) for f,d1,d2 in food_good_dd if 
                     (d1 < d2)
                     or (d1 == d2 and g.s.my_length < g.s.other_length and 4 < d1 < 999)
                     or (d1 == d2 and g.s.my_length >= g.s.other_length)
                     ]
        g.e.food_good = food_good
        if len(food_good) != 0:
            g.decision_path.append("food opportunity")
            food_targets = first_group(food_good)
            food_target = food_targets[0]
            g.e.food_target = food_target
            fmoves = shortest_path_move(g.s.my_head, food_target)
            moves = [a for a in moves if a in fmoves]
            if len(moves) != 0:
                g.decision_path.append(f"go to food {food_target}")
                return moves

def get_food_or_chase_tail(moves):
    if g.s.my_length < 20:
        return get_food(moves)
    return chase_tail(moves)

def my_snake_is_shorter(moves):
    if g.s.my_length < g.s.other_length:
        g.decision_path.append("shorter")
        return sequential([
            (avoid_collision),
            (killer_near),
            (split_choice),
            (wayout2),
            (get_food_or_chase_tail),
            #prefer_no(on_border),
            #prefer_more_next_move,
            #prefer_middle_by_3,
            push_to_equal_border,
            prefer_straight,
        ])(moves)

def single_collision_point(moves):
    if g.e.head_distance == 2:
        collision_points = [p for p in moves if p in adj_cells(g.s.other_head)]
        if len(collision_points) == 1:
            g.decision_path.append("avoid single collision point")
            moves = prefer_no(lambda a: a in collision_points)(moves)
            if distance_vector_abs(g.s.my_head, g.s.other_head) != (1,1):
                if distance_to_border(g.s.my_head) == (1,1):
                    if get_adjacent_dir(g.s.my_neck, g.s.my_head) == get_adjacent_dir(g.s.other_neck, g.s.other_head):
                        g.decision_path.append("enemy is parallel following me")
                        moves = prefer_no(lambda a: distance_vector_abs(a, g.s.other_head) in [(0,3), (3,0)])(moves)
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
                if g.s.my_length >= 15:
                    return [avoid_point]

def equal_length_danger(moves):
    if g.e.head_distance == 2:
        collision_points = [a for a in adj_cells(g.s.my_head) if is_adjacent(a, g.s.other_head) and a not in g.occupied_cells[0]]
        return prefer_no(lambda a: a in collision_points)(moves)

def longer_but_not_enough(moves):
    if g.s.my_length > g.s.other_length and g.s.my_length - g.s.other_length <= 5:
        g.decision_path.append("longer but not eough")
        moves = sequential([
            (split_choice),
            wayout2,
            get_food,
            (chase_tail),
            push_to_equal_border,
            prefer_straight,
        ])(moves)
        return moves

def snake_equal_length(moves):
    if g.s.my_length == g.s.other_length:
        g.decision_path.append("equal_length")
        moves = sequential([
            equal_length_danger,
            split_choice,
            wayout2,
            get_food_or_chase_tail,
            #prefer_more_next_move,
            #prefer_middle_by_3,
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

def split_choice_batch_1(moves):
    ok_moves = (
            (static_see_my_tail(moves) or [])
            +(static_see_other_tail(moves) or [])
            +((cut_see_my_tail)(moves) or [])
            +(cut_can_reach_my_tail(moves) or [])
            +(cut_see_other_tail(moves) or [])
            +(cut_can_reach_other_tail(moves) or [])
            +(static_spacious(moves) or [])
    )
    print(ok_moves)
    moves = [a for a in moves if a in ok_moves]
    if len(moves) != 0: 
        return moves

def split_choice_batch_2(moves):
    sequential([
        static_wayout_info_me,
        static_wayout_info_other,
        cut_wayout_info_me,
    ])(moves)
    moves = [a for a in moves if a in (
        ((cut_spacious)(moves) or [])
        +((static_wayout_on_myself)(moves) or [])
        +(static_wayout_on_other(moves) or [])
        +((cut_wayout_on_me)(moves) or [])
    )]
    if len(moves) != 0: 
        return moves

def split_choice2(moves):
    return (cases([
        no_split_return,
        #too_short_return,
        #there is a split
        #favor easy choice
        connected_set_info,
        (split_choice_batch_1),
        cut_info,
        split_choice_batch_2,
        (cut_just_see_other_tail),
        (fallout),
    ]))(moves)

def split_choice(moves):
    ngroup = move_connected_group(moves)
    if ngroup > 1:
        g.decision_path.append("split choice")
        return cases([
            simple_confined_moves_info,
            cut_confined_moves_info,
            avoid_confinement,
            #(no_simple_confinement),
            both_confined_moves,
        ])(moves)
    
def simple_confined_moves_info(moves):
    confined_moves = [a for a in moves
                    if len(path_connected_set(a)) < g.s.my_length //2
                    and not path_connected(a, g.s.my_tail)
                    and not path_connected(a, g.s.other_tail)
                    ]
    g.x.confined_moves = confined_moves

def cut_confined_moves_info(moves):
    head_space = path_connected_set(g.s.my_head)
    if g.s.my_length <= g.s.other_length:
        my_space = g.x.my_territory
    else:
        my_space = g.x.my_territory+g.x.equal_territory
    occupied = g.occupied_cells[0]+[a for a in head_space if a not in my_space]
    confined_moves = [a for a in moves
                      if path_connected(a, g.s.other_head)
                      for aset in [path_connected_set(a, occupied)]
                      if len(aset) < g.s.my_length //2
                      and not path_connected(a, g.s.my_tail, occupied)
                      and not path_connected(a, g.s.other_tail, occupied)
                      ]
    g.x.cut_confined_moves = confined_moves

def avoid_confinement(moves):
    confined_moves = list(set(g.x.confined_moves+g.x.cut_confined_moves))
    good_moves = [a for a in moves if a not in confined_moves]
    g.x.split_good_moves = good_moves
    if len(good_moves) != 0:
        if len(confined_moves) != 0:
            g.decision_path.append("avoid confined moves")
        else:
            g.decision_path.append("both good moves")
        return good_moves

def no_simple_confinement(moves):
    confined_moves = g.x.confined_moves
    if len(confined_moves) == 0:
        g.decision_path.append("no simple confinement")
        head_space = path_connected_set(g.s.my_head)
        if g.s.my_length <= g.s.other_length:
            my_space = g.x.my_territory
        else:
            my_space = g.x.my_territory+g.x.equal_territory
        occupied = g.occupied_cells[0]+[a for a in head_space if a not in my_space]
        
        def move_space(a):
            return len(path_connected_set(a, occupied))
        distinct = list(set([move_space(a) for a in moves]))
        if len(distinct) == 2:
            m,n = sorted(distinct)
            if n > int(1.5 * m):
                g.decision_path.append("one has substantial bigger space")
                return prefer_by_score(move_space)(moves)

def both_confined_moves(moves):
    #prefer near tail
    def tail_index(a):
        aset = path_connected_set(a)
        rank = min([ len(snake["body"]) - max(adj_set)
            for snake in [g.me, g.other]
            for adj_set in [[i for i,c in enumerate(snake["body"]) if any([p in aset for p in adj_cells(c)])]]
            if len(adj_set) != 0 ])
        return rank
    if len(g.x.split_good_moves) == 0:
        g.decision_path.append("both confined moves")
        return prefer_by_rank(tail_index)(moves)

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
    if ngroup == 1:
        return moves

def too_short_return(moves):
    if g.s.my_length < 15:
        return moves

def equal_line(moves):
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
    g.x.other_connected_set = other_connected_set

def food1(moves):
    tail_moves = shortest_path_move(g.s.my_head, g.s.my_tail)
    food1 = [a for a in moves if a in g.food]
    if len(food1) != 0:
        food_and_tail = [a for a in food1 if a in tail_moves]
        if len(food_and_tail) != 0:
            return food_and_tail
        food_tail_connect = [a for a in food1 if any([path_connected(a, p) for p in tail_moves])]
        if len(food_tail_connect) != 0:
            g.decision_path.append("detour get food1")
            return food_tail_connect

def food4(tail):
    def fn(moves):
        food4 = [f for f in g.food if 1< distance_pq(f, g.s.my_head) <= 4]
        if len(food4) != 0:
            foods = []
            for f in food4:
                paths = add_waypoint(g.s.my_head, f, tail)
                good_paths = [path for path in paths if len(path) <= path_distance_pq(g.s.my_head, tail)+5]
                if len(good_paths) == 0:
                    continue
                sn = min([len(path) for path in good_paths])
                shortest_path = [path for path in good_paths if len(path) == sn]
                foods.append([f, sn, list({path[1] for path in shortest_path})])
            food4 = foods
            if len(food4) != 0:
                min_sn = min([sn for f,sn,m in food4])
                f,sn,food_moves = take_first([(f,sn,m) for f,sn,m in food4 if sn == min_sn])
                food_moves = [a for a in food_moves if a in moves]
                if len(food_moves) != 0:
                    g.decision_path.append(f"add food waypoint {f}")
                    return food_moves
    return fn

def replace_tail_path(moves):
    if g.s.my_length < 20:
        return moves
    tail_distances = [distance_pq(g.s.my_head, c) for c in reversed(g.me["body"][-10:])]
    inflection_indexes = [i for i,d in enumerate(tail_distances[1:-1]) if d < tail_distances[i] and d < tail_distances[i+2]]
    if len(inflection_indexes) == 0:
        return moves
    first_inflection_index = inflection_indexes[0]+1

    #first inflection point is a fixed point on board
    first_inflection_point = g.me["body"][-1-first_inflection_index]
    g.decision_path.append(f"tail inflection point {first_inflection_point}")
    if not path_connected(g.s.my_head, first_inflection_point):
        return moves
    if path_distance_pq(g.s.my_head, first_inflection_point) <= first_inflection_index+1:
        tail_moves = shortest_path_move(g.s.my_head, first_inflection_point)
        tail_moves = [a for a in tail_moves if a in moves]
        if len(tail_moves) != 0:
            g.decision_path.append(f"replace tail path - direct")
            return tail_moves
    else:
        tail_moves = shortest_path_move(g.s.my_head, first_inflection_point)
        meander_moves = [a for a in moves if a not in tail_moves and path_connected(a, g.s.my_tail)]
        if len(meander_moves) != 0:
            g.decision_path.append(f"replace tail path - meander")
            return meander_moves

def chase_my_tail(moves):
    if path_distance_pq(g.s.other_head, g.s.my_tail) > path_distance_pq(g.s.my_head, g.s.my_tail):
        if len(moves) != 0:
            return cases([
                food1,
                food4(g.s.my_tail),
                replace_tail_path,
                tail_move(g.s.my_tail),
            ])(moves)

def tail_move(tail):
    def fn(moves):
        tail_moves = shortest_path_move(g.s.my_head, tail)
        if len(tail_moves) != 0:
            moves = [a for a in moves if a in tail_moves]
            if len(moves) != 0:
                g.decision_path.append(f"chase tail {tail}")
                return moves
    return fn

def chase_other_tail_has_distance(moves):
    if path_distance_pq(g.s.other_head, g.s.other_tail) > path_distance_pq(g.s.my_head, g.s.other_tail):
        if len(moves) != 0:
            return cases([
                (food1),
                food4(g.s.other_tail),
                tail_move(g.s.other_tail),
            ])(moves)

def chase_other_tail_too_close(moves):
    if is_adjacent(g.s.my_head, g.s.other_tail):
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
    moves = cases([
        chase_other_tail_too_close,
        (chase_other_tail_has_distance),
        #(chase_other_tail_long_shot),
    ])(moves)
    return moves

def shortest_path(a, b):
    d = path_distance_pq(a, b)
    if d == 999:
        return []
    occupied = [p for p in g.occupied_cells[0] if p != b]
    layers = path_connected_layers(a, occupied)
    paths = [[a]]
    for i in range(d):
        paths = [path+[nhead] 
                 for path in paths 
                 for end in [path[-1]] 
                 for nhead in layers[i+1] 
                 if is_adjacent(end, nhead) ]
    paths = [path for path in paths if path[-1] == b]
    return paths

def add_waypoint(a, b, c):
    ab = shortest_path(a, b)
    bc = shortest_path(b, c)
    paths = [pab+pbc[1:] for pab in ab for pbc in bc if not any([p in pab for p in pbc[1:]])]
    return paths

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

def kill_oppotunities(moves):
    return cases([
        #me_longer_enemy_has_only_one_move,
        enemy_is_backed_distance_2,
        enemy_is_backed_distance_4,
        enemy_is_backed_distance_6,
        cut_opportunities,
    ])(moves)

def grow_back(cut_set):
    new_cut_set = list(set([q for p in cut_set for q in adj_cells(p) 
                        if q not in g.occupied_cells[0] 
                        and q != g.s.my_head
                        and path_distance_pq(g.s.other_head, q) > path_distance_pq(g.s.other_head, p)]))
    return new_cut_set

def single_grow_set(head, occupied):
    result = []
    while True:
        moves = [a for a in adj_cells(head) if a not in occupied]
        if len(moves) != 1: break
        result += moves
        occupied += moves
        head = take_first(moves)
    return result

def cut_opportunities(moves):
    #I'll cut enemy if I can
    #conditions
    #1. determine cut set
    #1.1. if my snake is longer than enemy then the cut set is the equal border
    #1.2. otherwise, the cut set is the set that adjacent to the equal territory on my side
    #2. cut set is not too long
    #3. cut set is close to my head
    #4. with cut set, enemy head is not path connected to his tail or my tail
    #5. the resulting cut space is small enough so that the enemy cannot escape

    cut_set = g.x.equal_border 
    if g.s.my_length <= g.s.other_length:
        cut_set = [p for p in g.x.my_territory if p != g.s.my_head and any([q in g.x.equal_territory for q in adj_cells(p)])]

    if len(cut_set) == 0:
        return
    if len(cut_set) > 4:
        return
    """
    if len(cut_set) == 1:
        #cut_set is in a tunnel, maynot have path that can come back
        #get a cut_set by retract back adjacent cells
        while True:
            new_cut_set = grow_back(cut_set)
            if len(new_cut_set) != 1: break
            cut_set = new_cut_set
    """

    max_cut_length = 8
    max_dist = max([path_distance_pq(p, g.s.my_head) for p in cut_set])
    if max_dist > max_cut_length:
        return
    occupied = g.occupied_cells[0]+cut_set
    oset = path_connected_set(g.s.other_head, occupied)
    if g.s.other_tail in oset:
        return
    if g.s.my_tail in oset:
        return
    remove_set = single_grow_set(g.s.other_head, occupied)
    if len(oset)-len(remove_set) >= int(g.s.other_length * 1.1):
        return
    g.decision_path.append(f"cut opportunities - {cut_set}")

    cut_paths = [[[g.s.my_head]]]
    for _ in range(max_cut_length):
        layer = [path+[p] for path in cut_paths[-1] for end in [path[-1]] for p in adj_cells(end) 
                 if p not in g.occupied_cells[0] and p not in path]
        if len(layer) == 0: break
        cut_paths.append(layer)
    all_paths = [path for layer in cut_paths for path in layer]


    my_territory = g.x.my_territory
    if g.s.my_length > g.s.other_length:
        my_territory = my_territory + g.x.equal_territory

    has_cut = False
    for it in range(3):
        cut_paths = [path for path in all_paths if all([p in path for p in cut_set])]
        if len(cut_paths) == 0:
            #g.decision_path.append("no cut paths")
            cut_set = grow_back(cut_set)
            continue
        cut_paths = [path for path in cut_paths if all([p in my_territory for p in path])]
        if len(cut_paths) == 0:
            #g.decision_path.append("no cut paths all in my territory")
            cut_set = grow_back(cut_set)
            continue
        cut_paths = [path for path in cut_paths for end in [path[-1]] for occupied in [g.occupied_cells[0]+path]
                    if any([
                        p not in oset 
                        and p not in path 
                        and p not in g.occupied_cells[1] 
                        and len(path_connected_set(p, occupied)) > len(path_connected_set(g.s.other_head, occupied))
                        for p in adj_cells(end) ])
                    ]
        if len(cut_paths) == 0:
            #g.decision_path.append("no cut paths that come back")
            cut_set = grow_back(cut_set)
            continue
        has_cut = True
        break

    if len(cut_set) == 0:
        g.decision_path.append("cut is done")
        return
    if has_cut:
        cut_paths = prefer_by_rank(lambda path: len(path))(cut_paths)
        cut_moves = [path[1] for path in cut_paths]
        g.decision_path.append("go cut")
        return prefer_yes(lambda a: a in cut_moves)(moves)

def enemy_is_backed_distance_2(moves):
    if g.s.my_length > g.s.other_length:
        if distance_pq(g.s.my_head, g.s.other_head) == 2:
            collision = [p for p in g.e.allowed_moves if p in g.x.other_allowed_moves]
            if len(collision) == 1:
                c = take_first(collision)
                if len(g.x.other_allowed_moves) == 1:
                    g.decision_path.append("kill!")
                    return collision
                if len(g.x.other_allowed_moves) == 2:
                    a,b = g.x.other_allowed_moves
                    if path_distance_pq(a, b) == 2:
                        kill_move = [a for a in moves if a in collision]
                        if len(kill_move) != 0:
                            g.decision_path.append("enemy is backed")
                            return collision
                if len(g.x.other_allowed_moves) == 3:
                    if distance_vector_abs(g.s.my_head, g.s.other_head) in [(0,2), (2,0)]:
                        g.decision_path.append("squeeze one more step")
                        return collision

def enemy_is_backed_distance_4(moves):
    if g.s.my_length <= g.s.other_length:
        return
    if distance_pq(g.s.my_head, g.s.other_head) != 4:
        return
    if path_distance_pq(g.s.my_head, g.s.other_head) != 4:
        return

    if len(g.x.other_allowed_moves) > 2:
        return
    #enemy is backed by a wall

    #coming
    if not all([distance_pq(a, g.s.my_head) == 3 for a in g.x.other_allowed_moves]):
        return

    if len(g.x.other_allowed_moves) == 1:
        e = take_first(g.x.other_allowed_moves)
        kill_moves = [a for a in moves if distance_vector_abs(a, e) in [(0,2), (2,0)]]
        if len(kill_moves) != 0:
            g.decision_path.append("try squeeze enemy")
            return kill_moves
    
    if len(g.x.other_allowed_moves) == 2:
        kill_moves = [a for a in moves if distance_vector_abs(a, g.s.other_head) in [(1,2), (2,1)]]
        if len(kill_moves) != 0:
            g.decision_path.append("try squeeze enemy")
            return kill_moves

def enemy_is_backed_distance_6(moves):
    if g.s.my_length <= g.s.other_length:
        return
    if distance_pq(g.s.my_head, g.s.other_head) != 6:
        return
    if path_distance_pq(g.s.my_head, g.s.other_head) != 6:
        return

    if len(g.x.other_allowed_moves) > 2:
        return
    #enemy is backed by a wall

    #coming
    if not all([distance_pq(a, g.s.my_head) == 5 for a in g.x.other_allowed_moves]):
        return

    if len(g.x.other_allowed_moves) == 1:
        e = take_first(g.x.other_allowed_moves)
        kill_moves = [a for a in moves if distance_vector_abs(a, e) in [(1,3), (3,1)]]
        if len(kill_moves) != 0:
            g.decision_path.append("try squeeze enemy")
            return kill_moves
    
    if len(g.x.other_allowed_moves) == 2:
        straight = [a for a in g.x.other_allowed_moves if get_adjacent_dir(g.s.other_head, a) == get_adjacent_dir(g.s.other_neck, g.s.other_head)]
        if len(straight) != 0:
            straight = take_first(straight)
            kill_moves = [a for a in moves if min(distance_vector_abs(a, straight)) ==1 ]
            if len(kill_moves) != 0:
                g.decision_path.append("try squeeze enemy")
                return kill_moves

def me_longer_enemy_has_only_one_move(moves):
    if g.s.my_length > g.s.other_length:
        if distance_pq(g.s.my_head, g.s.other_head) == 2:
            occupied = g.occupied_cells[0]+g.x.my_territory+g.x.equal_territory
            oset = path_connected_set(g.s.other_head, occupied)

            other_moves = g.x.other_allowed_moves
            if len(other_moves) == 1:
                g.decision_path.append("enemy is cornered")
                moves = [a for a in moves if a in other_moves]
                if len(moves) == 1:
                    return moves
            if len(other_moves) == 2:
                a,b = other_moves
                if path_connected(a, b):
                    g.decision_path.append("enemy is cornered")
                    moves = [a for a in moves if a in other_moves]
                    if len(moves) == 1:
                        return moves

def not_too_long(moves):
    if g.s.my_length < 20:
        moves = sequential([
            split_choice,
            wayout2,
            get_food,
            #prefer_more_next_move,
            #prefer_middle_by_3,
            push_to_equal_border,
            prefer_straight,
        ])(moves)
        return moves

def wayout2(moves):
    ngroup = move_connected_group(moves)
    if ngroup != 1: 
        return
    if path_connected(g.s.my_head, g.s.my_tail):
        if distance_pq(g.s.my_head, g.s.my_tail) > 1:
            return
        if any([path_connected(p, g.s.my_tail) for p in g.e.allowed_moves]):
            return
    if path_connected(g.s.my_head, g.s.other_tail):
        if distance_pq(g.s.my_head, g.s.other_tail) > 1:
            return
        if any([path_connected(p, g.s.other_tail) for p in g.e.allowed_moves]):
            return
    #if path_connected(g.s.my_head, g.s.other_head): return moves
    g.decision_path.append("confined")
    return cases([
        meander2("me"),
        meander2("other"),
    ])(moves)

def log_print(anything=None):
    turn = g.state["turn"]
    id = g.state["game"]["id"]
    print(f"MARK_EXCEPTION, TURN: {turn}, id: {id}, {anything}")

def meander2(who):
    def fn(moves):
        aset = path_connected_set(g.s.my_head)
        aset = [p for p in aset if p != g.s.my_head]
        calc = [ (snake, adj_set, len(snake["body"]) - max(adj_set), max(adj_set), snake["body"][max(adj_set)]) 
            for snake in [g.me, g.other]
            for adj_set in [[i for i,c in enumerate(snake["body"]) if any([p in aset for p in adj_cells(c)])]]
            if len(adj_set) != 0 ]
        print(calc)
        min_wayout = min([a[2] for a in calc])
        calc = [a for a in calc if a[2] == min_wayout]
        wayout_point = take_first(prefer_yes(lambda a: a[0]["body"][0] == g.s.my_head)(calc))[4]

        #meander
        g.decision_path.append(f"meander to {wayout_point}")
        far_points = prefer_by_score(lambda a: path_distance_pq(a, wayout_point))(moves)
        if len(far_points) == 1:
            return far_points

        #then there are 2 points, cannot have 3
        #and they are perpendicular, ie, one straight, one left or right
        #and they have a common adjacent point
        a,b = far_points
        c = [c for c in adj_cells(a) if c in adj_cells(b) and c != g.s.my_head]
        if len(c) == 0:
            return far_points
        c = c[0]
        occupied = g.occupied_cells[0]+[c]
        a_connection = path_connected(a, wayout_point, occupied)
        b_connection = path_connected(b, wayout_point, occupied)
        if not all([a_connection, b_connection]):
            choice = a if not a_connection else b
            g.decision_path.append(f"go first {choice}")
            return [choice]
    return fn

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

        g.decision_path.append(f"wayout on {who} at {wayout_point}")
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
            g.decision_path.append(f"no calculated wayout on {who}")
            return
        g.decision_path.append(f"calculated wayout on {who}")
        return moves
    return fn

def chase_tail(moves):
    #if int(g.s.my_length / 1.5) >= g.s.other_length:
    if g.s.my_length >= 35:
        return cases([
            (chase_my_tail),
            (chase_other_tail),
        ])(moves)
    else:
        moves = cases([
            (chase_other_tail),
            (chase_my_tail),
        ])(moves)
        return moves

def prefer_more_territory(moves):
    def distance_to_frontier(a):
        dist_set = [d for p in g.x.other_territory for d in [path_distance_pq(a, p)] if d != 999]
        if len(dist_set) == 0:
            return 0
        return 999-min(dist_set)
    return prefer_by_score(distance_to_frontier)(moves)

def too_long(moves):
    if g.s.my_length >= 20:
        moves = sequential([
            (split_choice),
            wayout2,
            (chase_tail),
            #prefer_more_next_move,
            #prefer_middle_by_3,
            #get_food,
            #prefer_more_territory,
            push_to_equal_border,
            prefer_straight,
        ])(moves)
        return moves

def my_snake_is_longer(moves):
    if g.s.my_length > g.s.other_length:
        return cases([
            longer_but_not_enough,
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
    log = {'id': 'fa8959d9-f41f-4e93-af93-cb89ee68765b', 'turn': 122, 'me': {'name': 'mark_snake', 'health': 84, 'body': [(10, 6), (9, 6), (9, 7), (8, 7), (7, 7), (7, 8), (7, 9), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (1, 9), (1, 8), (1, 7), (2, 7)]}, 'others': [{'name': 'Frank The Tank', 'health': 99, 'body': [(8, 4), (9, 4), (10, 4), (10, 3), (10, 2), (10, 1), (9, 1), (8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3), (1, 4)]}], 'food': [(10, 7)], 'module': 'functional', 'decision_path': ['battle_1_vs_1', 'longer but not eough', 'split choice', 'no simple confinement', 'one has substantial bigger space'], 'next_coord': (10, 7), 'next_move': 'up', 'time': '0.004s'}
    log = {'id': 'fa8959d9-f41f-4e93-af93-cb89ee68765b', 'turn': 121, 'me': {'name': 'mark_snake', 'health': 85, 'body': [(9, 6), (9, 7), (8, 7), (7, 7), (7, 8), (7, 9), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (1, 9), (1, 8), (1, 7), (2, 7), (3, 7)]}, 'others': [{'name': 'Frank The Tank', 'health': 100, 'body': [(9, 4), (10, 4), (10, 3), (10, 2), (10, 1), (9, 1), (8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 4)]}], 'food': [(10, 7)], 'module': 'functional', 'decision_path': ['battle_1_vs_1', 'longer but not eough', 'food opportunity', 'go to food (10, 7)'], 'next_coord': (10, 6), 'next_move': 'right', 'time': '0.007s'}
    log = {'id': 'fa7e4e9d-73fd-4011-b4bd-4532541059ff', 'turn': 126, 'me': {'name': 'mark_snake', 'health': 79, 'body': [(9, 9), (9, 8), (9, 7), (9, 6), (9, 5), (8, 5), (8, 6), (8, 7), (7, 7), (6, 7), (5, 7)]}, 'others': [{'name': 'Frank The Tank', 'health': 88, 'body': [(7, 5), (7, 4), (7, 3), (8, 3), (9, 3), (9, 2), (8, 2), (8, 1), (8, 0), (7, 0), (6, 0), (5, 0), (4, 0), (4, 1), (5, 1), (5, 2), (6, 2), (6, 1)]}], 'food': [(10, 3), (8, 10)], 'module': 'functional', 'decision_path': ['battle_1_vs_1', 'shorter', 'food opportunity', 'go to food (8, 10)'], 'next_coord': (9, 10), 'next_move': 'up', 'time': '0.012s'}
    log = {'id': '0103aeb4-8690-4989-87c9-fb5291571022', 'turn': 212, 'me': {'name': 'mark_snake', 'health': 88, 'body': [(6, 6), (6, 5), (7, 5), (7, 4), (8, 4), (9, 4), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (9, 9), (9, 8), (9, 7), (8, 7), (8, 8), (8, 9), (7, 9), (6, 9), (6, 8)]}, 'others': [{'name': 'Frank The Tank', 'health': 91, 'body': [(5, 5), (5, 4), (5, 3), (6, 3), (6, 2), (6, 1), (5, 1), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, 8), (3, 8), (4, 8), (4, 7), (3, 7), (2, 7), (2, 6), (3, 6)]}], 'food': [(5, 7), (9, 6), (3, 9)], 'module': 'functional', 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid single collision point', 'add food waypoint (5, 7)', 'push to equal border [(5, 6)]'], 'next_coord': (5, 6), 'next_move': 'left', 'time': '0.013s'}
    log = {'id': 'b991941f-3e58-4cc7-9195-ae846b75b9f1', 'turn': 254, 'me': {'name': 'mark_snake', 'health': 86, 'body': [(9, 3), (8, 3), (7, 3), (7, 4), (6, 4), (5, 4), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (1, 3), (2, 3), (2, 2), (2, 1), (2, 0), (3, 0), (3, 1), (4, 1)]}, 'others': [{'name': 'Snakeformatika', 'health': 70, 'body': [(10, 4), (10, 3), (10, 2), (10, 1), (10, 0), (9, 0), (9, 1), (8, 1)]}], 'food': [(8, 8), (3, 8), (10, 5)], 'module': 'functional', 'decision_path': ['battle_1_vs_1', 'split choice', 'no simple confinement', 'chase tail (8, 1)'], 'next_coord': (9, 2), 'next_move': 'down', 'time': '0.008s'}
    log = {'id': '03319342-5259-4b66-974f-c9d65a34cd3e', 'turn': 255, 'me': {'name': 'mark_snake', 'health': 98, 'body': [(3, 4), (3, 3), (3, 2), (3, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (3, 9)]}, 'others': [{'name': 'Snakeformatika', 'health': 73, 'body': [(0, 7), (0, 8), (0, 9), (0, 10), (1, 10), (2, 10), (2, 9), (1, 9), (1, 8), (2, 8), (2, 7), (1, 7)]}], 'food': [(0, 3), (7, 7), (1, 5), (2, 5), (8, 8), (8, 7), (1, 0), (8, 6)], 'module': 'functional', 'decision_path': ['battle_1_vs_1', 'add food waypoint (2, 5)', 'push to equal border [(2, 6)]'], 'next_coord': (3, 5), 'next_move': 'up', 'time': '0.024s'}
    log = {'id': '88c0ddf1-a77b-4fa3-884a-7494e3b44cb7', 'turn': 143, 'me': {'name': 'mark_snake', 'health': 72, 'body': [(6, 9), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (1, 8), (2, 8), (3, 8)]}, 'others': [{'name': 'ich heisse marvin', 'health': 81, 'body': [(6, 7), (6, 6), (6, 5), (5, 5), (5, 6), (4, 6), (3, 6), (2, 6), (1, 6), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7)]}], 'food': [(10, 2), (10, 1)], 'module': 'functional', 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid single collision point', 'split choice', 'no simple confinement', 'one has substantial bigger space'], 'next_coord': (7, 9), 'next_move': 'right', 'time': '0.003s'}
    log = {'id': 'e6dc2666-c6e5-4cc7-a2e9-eab2b4f888fc', 'turn': 262, 'me': {'name': 'mark_snake', 'health': 89, 'body': [(1, 3), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, 8), (2, 8), (3, 8), (3, 9), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (10, 8), (10, 7), (9, 7)]}, 'others': [{'name': 'ich heisse marvin', 'health': 72, 'body': [(5, 3), (4, 3), (4, 2), (3, 2), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 6), (3, 7), (2, 7), (1, 7), (1, 6)]}], 'food': [(10, 0), (10, 1), (4, 0), (3, 5), (9, 2), (9, 6), (1, 0)], 'module': 'functional', 'decision_path': ['battle_1_vs_1', 'split choice', 'has confined moves', 'avoid confined moves'], 'next_coord': (1, 2), 'next_move': 'down', 'time': '0.003s'}


    game_state = init_from_log(log)
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()

