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
        for f in fs:
            result = f(moves)
            if result is not None:
                return result
        return moves
    return fn

def sequential(fs):
    def fn(moves):
        for f in fs:
            result = f(moves)
            if result is not None:
                moves = result
        return moves
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
        return cases([shorter, equal_length, longer])(moves)

def avoid_danger(moves):
    g.decision_path.append("avoid_danger")
    return cases([
        head_distance_2, 
        head_distance_4, 
        head_distance_6, 
        head_distance_more,
    ])(moves)

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
            fmoves = [a for a in fmoves if a in moves]
            if len(fmoves) != 0:
                g.decision_path.append("go to food")
                return fmoves

def shorter(moves):
    if g.s.my_length < g.s.other_length:
        g.decision_path.append("shorter")
        return sequential([
            avoid_danger,
            no_room_danger,
            get_food,
            prefer_middle_by_3,
            prefer_straight,
        ])(moves)

def head_distance_2(moves):
    if g.e.head_distance == 2:
        g.decision_path.append("head_distance_2")
        g.x.possible_collision_points = [p for p in adj_cells(g.s.my_head) if p in adj_cells(g.s.other_head)]
        return cases([ type_1_collision, type_2_collision ])(moves)

def type_1_collision(moves):
    if len(g.x.possible_collision_points) == 1:
        g.decision_path.append("type_1_collision")
        g.x.collision_point = g.x.possible_collision_points[0]
        g.e.me_heading_collision_point = get_adjacent_dir(g.s.my_head, g.x.collision_point) == get_adjacent_dir(g.s.my_neck, g.s.my_head)
        g.e.other_heading_collision_point = get_adjacent_dir(g.s.other_head, g.x.collision_point) == get_adjacent_dir(g.s.other_neck, g.s.other_head)
        return cases([
            type_1_blocked, 
            head_to_head, 
            other_to_me, 
            me_to_other, 
            parallel, 
            parallel_opposite,
        ])(moves)

def off_border_danger(moves):
    if g.s.my_length+1 < g.s.other_length:
        if off_border_1(g.s.my_head):
            moves = prefer_no(on_border)(moves)
            return moves

def crawling(moves):
    if on_border(g.s.my_neck):
        return prefer_no(on_border)(moves)

def danger_distance_average(a):
    d1 = distance_pq(a, g.s.other_head)
    d2 = path_distance_pq(a, g.s.other_head)
    if d2 >= 100:
        d2 = min([(g.s.my_length+1)//2, (g.s.other_length+1)//2])
    return (d1+d2+1)//2

def heading_border(moves):
    if not on_border(g.s.my_neck):
        moves = prefer_by_score(danger_distance_average)(moves)
        return moves

def on_border_danger(moves):
    if on_border(g.s.my_head):
        return cases([
            crawling,
            heading_border,
        ])(moves)

def killer_near(moves):
    return cases([
        off_border_danger,
        on_border_danger,
    ])(moves)

def type_1_blocked(moves):
    if g.x.collision_point in g.occupied_cells[0]:
        g.decision_path.append("type_1_blocked")
        return sequential([
            killer_near, 
            other_considerations,
        ])(moves)

def avoid_collision_point_1(moves):
    moves = [a for a in moves if a != g.x.collision_point]
    return moves

def head_to_head(moves):
    if g.e.me_heading_collision_point and g.e.other_heading_collision_point:
        g.decision_path.append("head_to_head")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ])(moves)

def other_to_me(moves):
    if g.e.other_heading_collision_point:
        g.decision_path.append("other_to_me")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ])(moves)

def me_to_other(moves):
    if g.e.me_heading_collision_point:
        g.decision_path.append("me_to_other")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ])(moves)

def parallel(moves):
    if get_adjacent_dir(g.s.my_neck, g.s.my_head) == get_adjacent_dir(g.s.other_neck, g.s.other_head):
        g.decision_path.append("parallel")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ])(moves)

def parallel_opposite(moves):
    if get_adjacent_dir(g.s.my_head, g.s.my_neck) == get_adjacent_dir(g.s.other_neck, g.s.other_head):
        g.decision_path.append("parallel_opposite")
        return sequential([
            avoid_collision_point_1, 
            killer_near, 
            other_considerations,
        ])(moves)

def type_2_with_no_avoid_points(moves):
    if len(g.e.avoid_points) == 0:
        moves = prefer_no(lambda a: a in g.food)(moves)
        g.decision_path.append("take risk at no food")
        return moves

def type_2_with_1_avoid_point(moves):
    if len(g.e.avoid_points) == 1:
        avoid_point = g.e.avoid_points[0]
        avoid_point_next = [p for p in adj_cells(avoid_point) if p not in g.occupied_cells[1]]
        if len(avoid_point_next) > 1:
            return prefer_yes(lambda a: a == avoid_point)(moves)

        g.decision_path.append("take risk - take the opposite of avoid point")
        return sequential([
            prefer_no(lambda a: a == avoid_point),
            prefer_no(lambda a: a in g.food),
            prefer_no(is_straight),
        ])(moves)

def type_2_with_2_collision_points(moves):
    if len(g.x.collision_points) == 2:
        return cases([
            type_2_with_no_avoid_points,
            type_2_with_1_avoid_point,
        ])(moves)

def type_2_with_1_collision_points(moves):
    if len(g.x.collision_points) == 1:
        g.decision_path.append("avoid collision")
        return sequential([
            prefer_no(lambda a: a in g.x.collision_points),
            cases([ shorter_by_1, near_border, ]),
        ])(moves)

def type_2_with_0_collision_points(moves):
    if len(g.x.collision_points) == 0:
        return moves

def type_2_collision(moves):
    if len(g.x.possible_collision_points) == 2:
        g.decision_path.append("type_2_collision")
        g.x.collision_points = [p for p in g.x.possible_collision_points if p not in g.occupied_cells[0]]
        g.e.avoid_points = [p for p in g.e.allowed_moves if not p in g.x.collision_points]
        return cases([
            type_2_with_2_collision_points,
            type_2_with_1_collision_points,
            type_2_with_0_collision_points,
        ])(g.e.allowed_moves)

def shorter_by_1(moves):
    if g.s.my_length+1 == g.s.other_length:
        if off_border_1(g.s.my_head):
            if any([a in g.food for a in moves]):
                g.decision_path.append("get the food and length will be equal")
                return moves

def near_border(moves):
    if off_border_1(g.s.my_head):
        g.decision_path.append("avoid border")
        return prefer_no(on_border)(moves)

def head_distance_4(moves):
    if g.e.head_distance == 4:
        g.decision_path.append("head_distance_4")
        moves = cases([
            shorter_by_1,
            killer_near,
        ])(moves)
        return moves

def head_distance_6(moves):
    if g.e.head_distance == 6:
        g.decision_path.append("head_distance_6")
        if g.e.head_path_distance == 6:
            if distance_to_border(g.s.my_head) in [(1,1), (1,2), (2,1)]:
                g.decision_path.append("near corner")
                return killer_near(moves)
            if on_border(g.s.my_head):
                g.decision_path.append("on border")
                return killer_near(moves)

def head_distance_more(moves):
    if g.e.head_distance > 6:
        g.decision_path.append("head_distance_more")
        return moves

def equal_length_danger(moves):
    if g.e.head_distance == 2:
        collision_points = [a for a in adj_cells(g.s.my_head) if is_adjacent(a, g.s.other_head) and a not in g.occupied_cells[0]]
        return prefer_no(lambda a: a in collision_points)(moves)

def equal_length(moves):
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

def split_branches(moves):
    if len(g.e.allowed_moves) == 2:
        a,b = g.e.allowed_moves
        if path_distance_pq(a, b) > 4:
            g.decision_path.append("2 split branches")
            return sequential([
                chase_my_tail,
                chase_other_tail,
                prefer_no(not_enough_space),
                prefer_by_score(lambda a: path_distance_pq(a, g.s.other_head)),
                #cut_danger,
            ])(moves)

def no_room_danger(moves):
    return cases([
        split_branches,
    ])(moves)

def equal_line():
    g.x.distance_map = [(p, distance_pq(p, g.s.my_head), distance_pq(p, g.s.other_head))
        for x in range(g.state["board"]["width"])
        for y in range(g.state["board"]["height"])
        for p in [(x,y)] ]
    g.x.my_territory = [p for p,d1,d2 in g.x.distance_map if d1 < d2]
    g.x.other_territory = [p for p,d1,d2 in g.x.distance_map if d1 > d2]
    g.x.equal_territory = [p for p,d1,d2 in g.x.distance_map if d1 == d2]
    g.x.equal_border = [p for p in g.x.equal_territory if any([q in g.x.other_territory for q in adj_cells(p)])]

def kill_opportunity(moves):
    if g.e.head_distance <= 4:
        if g.e.head_distance == g.e.head_path_distance:
            if g.s.my_length >= 20:
                if int(g.s.my_length/1.5) >= g.s.other_length:
                    g.decision_path.append("kill opportunity")
                    occupied_cells = g.occupied_cells[0]+g.x.my_territory+g.x.equal_territory
                    orig_room = {a: len(path_connected_set(a)) for a in g.x.other_allowed_moves}
                    cut_room = {a: len(path_connected_set(a, occupied_cells)) for a in g.x.other_allowed_moves}
                    target = [a for a in g.x.other_allowed_moves if orig_room[a] >= g.s.other_length and 1 < cut_room[a] <= 5]
                    if len(target) != 0:
                        g.decision_path.append("kill target")
                        target = take_first(target)
                        moves = shortest_path_move(g.s.my_head, target)
                        if len(moves) != 0:
                            return moves

def chase_other_tail(moves):
    #chase enemy tail
    if path_connected(g.s.my_head, g.s.other_tail):
        if g.s.other_tail in g.x.my_territory:
            if distance_pq(g.s.my_head, g.s.other_tail) > 1:
                tail_moves = shortest_path_move(g.s.my_head, g.s.other_tail)
                return prefer_yes(lambda a: a in tail_moves)(moves)
            else:
                g.decision_path.append("don't follow too close")
                return prefer_no(lambda a: a != g.s.other_tail)(moves)

def chase_my_tail(moves):
    if path_connected(g.s.my_head, g.s.my_tail):
        if g.s.my_tail in g.x.my_territory:
            tail_moves = shortest_path_move(g.s.my_head, g.s.my_tail)
            return prefer_yes(lambda a: a in tail_moves)(moves)

def chase_tail(moves):
    return cases([
        chase_other_tail,
        chase_my_tail,
    ])(moves)

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
            chase_tail,
            prefer_straight,
        ])(moves)
        return moves

def longer(moves):
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
    log = {'id': '84cf23e1-dfe5-448e-a294-c70678353346', 'turn': 34, 'me': {'name': 'mark_snake', 'health': 77, 'body': [(10,0), (10,1), (10,2), (10,3)]}, 'others': [{'name': 'Snakeformatika', 'health': 92, 'body': [(9,1), (9,2), (9,3), (9,4), (9,5), (9,6)]}], 'food': [(10, 8), (5, 3), (0, 4)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 10), (9, 9)], 'other_allowed_moves': [(7, 9), (6, 10), (6, 8)], 'head_distance': 4, 'head_path_distance': 4, 'decision_path': ['battle_1_vs_1', 'shorter', 'head_distance_4'], 'possible_collision_points': [(2, 9)], 'collision_points': [(3, 9), (2, 8)], 'avoid_points': [(2, 10)], 'collision_point': (2, 9), 'me_heading_collision_point': False, 'other_heading_collision_point': False}, 'next_coord': (10, 10), 'next_move': 'right', 'time': '0.000s'}
    log = {'id': '7c48225a-d788-4d12-8e67-4887d87c34b3', 'turn': 10, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(3, 9), (2, 9), (1, 9), (0, 9)]}, 'others': [{'name': 'Snakeformatika', 'health': 100, 'body': [(5, 5), (6, 5), (6, 6), (6, 7), (6, 7)]}], 'food': [(4, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(4, 9), (3, 10), (3, 8)], 'other_allowed_moves': [(4, 5), (5, 6), (5, 4)], 'head_distance': 6, 'head_path_distance': 6, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_6'], 'food_near': [], 'food_good': [((0, 8), 1)], 'situation': 'go to food', 'food_target': (0, 8)}, 'next_coord': (4, 9), 'next_move': 'right', 'time': '0.000s'}
    log = {'id': '77c3316d-ce9b-4042-8fa3-ec82d4ed60d5', 'turn': 27, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(2, 7), (2, 6), (1, 6), (0, 6), (0, 5)]}, 'others': [{'name': 'Snakeformatika', 'health': 85, 'body': [(3, 6), (3, 5), (3, 4), (3, 3), (2, 3), (2, 4)]}], 'food': [(10, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 7), (1, 7), (2, 8)], 'other_allowed_moves': [(4, 6), (3, 7)], 'head_distance': 2, 'head_path_distance': 2, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_2', 'type_2_collision'], 'food_near': [], 'food_good': [((0, 4), 1)], 'food_target': (0, 4), 'possible_collision_points': [(3, 7), (2, 6)], 'collision_point': (1, 4), 'me_heading_collision_point': False, 'other_heading_collision_point': False, 'collision_points': [(3, 7)], 'avoid_points': [(1, 7), (2, 8)]}, 'next_coord': (3, 7), 'next_move': 'right', 'time': '0.000s'}
    log = {'id': '7fff092c-92ae-4e1e-8169-e4500fef2ef3', 'turn': 0, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(1, 5), (1, 5), (1, 5)]}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 100, 'body': [(5, 9), (5, 9), (5, 9)]}], 'food': [(0, 4), (4, 10), (5, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(2, 5), (0, 5), (1, 6), (1, 4)], 'head_distance': 8, 'head_path_distance': 8, 'other_allowed_moves': [(6, 9), (4, 9), (5, 10), (5, 8)]}, 'decision_path': ['battle_1_vs_1', 'equal_length'], 'next_coord': (2, 5), 'next_move': 'right', 'time': '0.000s'}
    log = {'id': '5f648fc4-9adf-455e-bb63-9abfa80687f1', 'turn': 53, 'me': {'name': 'mark_snake', 'health': 77, 'body': [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2)]}, 'others': [{'name': 'Snakeformatika', 'health': 90, 'body': [(5, 4), (5, 5), (6, 5), (7, 5), (8, 5), (8, 6), (9, 6), (9, 7)]}], 'food': [(10, 9), (9, 3), (4, 6)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(0, 2), (1, 3), (1, 1)], 'food_good': [], 'head_distance': 6, 'head_path_distance': 6, 'other_allowed_moves': [(6, 4), (4, 4), (5, 3)]}, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_6'], 'next_coord': (0, 2), 'next_move': 'left', 'time': '0.000s'}
    log = {'id': '172066ab-8202-4f36-a347-ddfc6ba27539', 'turn': 130, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(10, 2), (9, 2), (8, 2), (7, 2), (6, 2), (6, 3), (5, 3), (5, 2), (5, 1), (4, 1), (3, 1), (2, 1), (2, 0), (2, 0)]}, 'others': [{'name': 'Snakeformatika', 'health': 95, 'body': [(7, 3), (7, 4), (6, 4), (5, 4), (4, 4), (4, 5), (5, 5), (5, 6), (5, 7), (5, 8), (6, 8), (6, 7), (6, 6), (6, 5)]}], 'food': [(8, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 3), (10, 1)], 'food_good': [], 'head_distance': 4, 'head_path_distance': 4}, 'decision_path': ['battle_1_vs_1', 'equal_length'], 'next_coord': (10, 3), 'next_move': 'up', 'time': '0.001s'}
    log = {'id': '172066ab-8202-4f36-a347-ddfc6ba27539', 'turn': 129, 'me': {'name': 'mark_snake', 'health': 93, 'body': [(9, 2), (8, 2), (7, 2), (6, 2), (6, 3), (5, 3), (5, 2), (5, 1), (4, 1), (3, 1), (2, 1), (2, 0), (3, 0)]}, 'others': [{'name': 'Snakeformatika', 'health': 96, 'body': [(7, 4), (6, 4), (5, 4), (4, 4), (4, 5), (5, 5), (5, 6), (5, 7), (5, 8), (6, 8), (6, 7), (6, 6), (6, 5), (7, 5)]}], 'food': [(10, 2), (8, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 2), (9, 3), (9, 1)], 'food_good': [((10, 2), 1)], 'food_target': (10, 2), 'head_distance': 4, 'head_path_distance': 4}, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_4', 'go to food'], 'next_coord': (10, 2), 'next_move': 'right', 'time': '0.001s'}
    log = {'id': '3e709a1a-b948-412c-8b13-e07222388dd5', 'turn': 21, 'me': {'name': 'mark_snake', 'health': 89, 'body': [(2, 1), (2, 2), (3, 2), (4, 2), (5, 2)]}, 'others': [{'name': 'Snakeformatika', 'health': 95, 'body': [(4, 3), (4, 4), (5, 4), (6, 4), (6, 5), (6, 6), (5, 6)]}], 'food': [(2, 0), (0, 9), (6, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 1), (1, 1), (2, 0)], 'food_good': [((2, 0), 1)], 'food_target': (2, 0), 'head_distance': 4, 'head_path_distance': 6}, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_4', 'go to food'], 'next_coord': (2, 0), 'next_move': 'down', 'time': '0.001s'}
    log = {'id': '5cccae4a-72ae-4d1f-a915-8584abd5d06e', 'turn': 172, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(10, 6), (9, 6), (9, 5), (9, 4), (9, 3), (9, 2), (8, 2), (7, 2), (6, 2), (5, 2), (4, 2), (4, 1), (4, 0), (5, 0), (6, 0), (7, 0), (7, 0)]}, 'others': [{'name': 'Snakeformatika', 'health': 93, 'body': [(4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (1, 7), (2, 7), (2, 8), (1, 8), (1, 9), (2, 9), (3, 9), (3, 8), (3, 7), (4, 7)]}], 'food': [(1, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 7), (10, 5)], 'head_distance': 10, 'head_path_distance': 10}, 'decision_path': ['battle_1_vs_1', 'shorter', 'avoid_danger', 'head_distance_more'], 'next_coord': (10, 7), 'next_move': 'up', 'time': '0.000s'}
    log = {'id': '6bd08f62-8a6d-415c-9cf8-4b3cb89f88eb', 'turn': 152, 'me': {'name': 'mark_snake', 'health': 82, 'body': [(8, 6), (9, 6), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (1, 8), (1, 7), (2, 7)]}, 'others': [{'name': 'ich heisse marvin', 'health': 94, 'body': [(7, 7), (7, 6), (6, 6), (5, 6), (5, 5), (4, 5), (4, 4), (5, 4), (6, 4)]}], 'food': [(2, 1), (3, 1)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(8, 7), (8, 5)], 'head_distance': 2, 'head_path_distance': 2}, 'decision_path': ['battle_1_vs_1', 'longer', '2 split branches', 'kill opportunity'], 'next_coord': (8, 7), 'next_move': 'up', 'time': '0.003s'}
    log = {'id': '11267b85-972f-4d4f-99f2-4dbf108475f6', 'turn': 141, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(9, 4), (10, 4), (10, 5), (9, 5), (8, 5), (8, 6), (8, 7), (8, 8), (8, 9), (8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (0, 6)]}, 'others': [{'name': 'ich heisse marvin', 'health': 65, 'body': [(7, 4), (6, 4), (5, 4), (4, 4), (3, 4), (2, 4), (1, 4), (1, 3), (1, 2), (1, 1), (2, 1)]}], 'food': [(3, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(8, 4), (9, 3)], 'food_good': [], 'head_distance': 2, 'head_path_distance': 2}, 'decision_path': ['battle_1_vs_1', 'longer', 'kill opportunity', 'kill target'], 'next_coord': (8, 4), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': '17322939-0b18-45ac-ba99-074992e1d611', 'turn': 240, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(10, 6), (9, 6), (9, 5), (9, 4), (9, 3), (9, 2), (8, 2), (8, 1), (8, 0), (7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8)]}, 'others': [{'name': 'ich heisse marvin', 'health': 80, 'body': [(8, 8), (8, 7), (8, 6), (8, 5), (7, 5), (7, 4), (8, 4), (8, 3), (7, 3), (6, 3), (6, 4), (6, 5), (5, 5)]}], 'food': [(10, 1)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 7), (10, 5)], 'food_good': [((10, 1), 5)], 'food_target': (10, 1), 'head_distance': 4, 'head_path_distance': 4}, 'decision_path': ['battle_1_vs_1', 'longer', '2 split branches', 'kill opportunity', 'go to food'], 'next_coord': (10, 7), 'next_move': 'up', 'time': '0.005s'}
    log = {'id': '17322939-0b18-45ac-ba99-074992e1d611', 'turn': 239, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(9, 6), (9, 5), (9, 4), (9, 3), (9, 2), (8, 2), (8, 1), (8, 0), (7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 8)]}, 'others': [{'name': 'ich heisse marvin', 'health': 81, 'body': [(8, 7), (8, 6), (8, 5), (7, 5), (7, 4), (8, 4), (8, 3), (7, 3), (6, 3), (6, 4), (6, 5), (5, 5), (5, 4)]}], 'food': [(10, 1)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 6), (9, 7)], 'food_good': [((10, 1), 6)], 'food_target': (10, 1), 'head_distance': 2, 'head_path_distance': 2}, 'decision_path': ['battle_1_vs_1', 'longer', 'kill opportunity', 'go to food'], 'next_coord': (10, 6), 'next_move': 'right', 'time': '0.005s'}
    log = {'id': '17322939-0b18-45ac-ba99-074992e1d611', 'turn': 227, 'me': {'name': 'mark_snake', 'health': 93, 'body': [(3, 0), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (10, 8)]}, 'others': [{'name': 'ich heisse marvin', 'health': 93, 'body': [(5, 4), (5, 3), (5, 2), (5, 1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (3, 6), (2, 6), (1, 6)]}], 'food': [(9, 6)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(4, 0), (3, 1)], 'head_distance': 6, 'head_path_distance': 8}, 'decision_path': ['battle_1_vs_1', 'longer', '2 split branches'], 'next_coord': (4, 0), 'next_move': 'right', 'time': '0.001s'}
    log = {'id': '6e27e442-d9d0-453b-851f-4f4206bb22d7', 'turn': 16, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(8, 4), (7, 4), (6, 4), (5, 4), (4, 4), (4, 4)]}, 'others': [{'name': 'ich heisse marvin', 'health': 95, 'body': [(6, 8), (6, 7), (5, 7), (4, 7), (3, 7)]}], 'food': [(9, 9), (8, 5), (7, 1)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 4), (8, 5), (8, 3)], 'food_good': [((8, 5), 1), ((7, 1), 4)], 'food_target': (8, 5), 'head_distance': 6, 'head_path_distance': 6}, 'decision_path': ['battle_1_vs_1', 'food opportunity', 'go to food'], 'next_coord': (9, 4), 'next_move': 'right', 'time': '0.002s'}
    log = {'id': '1901b242-962a-4f2e-8baf-d39056bc45e8', 'turn': 174, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(9, 7), (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (10, 2), (9, 2), (8, 2), (7, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (1, 2), (0, 2), (0, 3), (0, 4), (0, 5), (0, 5)]}, 'others': [{'name': 'ich heisse marvin', 'health': 90, 'body': [(5, 9), (5, 8), (6, 8), (7, 8), (8, 8), (8, 7), (8, 6), (8, 5), (7, 5), (6, 5), (6, 6), (6, 7), (5, 7), (4, 7), (3, 7)]}], 'food': [(4, 5), (9, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 8), (9, 6)], 'head_distance': 6, 'head_path_distance': 6}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (9, 8), 'next_move': 'up', 'time': '0.001s'}
    log = {'id': '1fa01b8f-f774-4323-9bd6-42adc1d5a43f', 'turn': 199, 'me': {'name': 'mark_snake', 'health': 75, 'body': [(5, 4), (4, 4), (3, 4), (2, 4), (2, 3), (3, 3), (3, 2), (2, 2), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (3, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (7, 1), (7, 2)]}, 'others': [{'name': 'ich heisse marvin', 'health': 57, 'body': [(6, 3), (7, 3), (7, 4), (8, 4), (8, 5), (8, 6), (8, 7), (7, 7), (6, 7), (5, 7), (5, 6), (5, 5)]}], 'food': [(1, 6), (2, 10), (0, 7), (1, 10), (0, 5), (10, 7), (10, 9), (5, 3), (9, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 4), (5, 5), (5, 3)], 'head_distance': 2, 'head_path_distance': 2}, 'decision_path': ['battle_1_vs_1'], 'next_coord': (5, 3), 'next_move': 'down', 'time': '0.001s'}
    log = {'id': 'a35321ef-1b87-44ba-8593-20113f0c5cb5', 'turn': 136, 'me': {'name': 'mark_snake', 'health': 97, 'body': [(4, 0), (4, 1), (4, 2), (3, 2), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (1, 9), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (2, 0)]}, 'others': [{'name': 'ich heisse marvin', 'health': 62, 'body': [(7, 1), (7, 2), (7, 3), (6, 3), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8)]}], 'food': [(9, 7), (8, 1), (10, 6), (5, 0), (6, 0), (10, 7), (5, 9), (1, 4), (7, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(5, 0), (3, 0)], 'head_distance': 4, 'head_path_distance': 4, 'cut': [(5, 0), (3, 0)]}, 'decision_path': ['battle_1_vs_1', 'has cut danger'], 'next_coord': (5, 0), 'next_move': 'right', 'time': '0.017s'}
    log = {'id': '3e5faac2-5b9e-48aa-a6ba-ef8f6020548e', 'turn': 150, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(10, 8), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (4, 9), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 1)]}, 'others': [{'name': 'ich heisse marvin', 'health': 69, 'body': [(6, 6), (6, 5), (6, 4), (5, 4), (5, 5), (4, 5), (3, 5), (2, 5), (2, 6), (2, 7)]}], 'food': [(9, 7), (3, 8)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 9), (10, 7)], 'head_distance': 6, 'head_path_distance': 6, 'cut': [(10, 9), (10, 7)]}, 'decision_path': ['battle_1_vs_1', 'has cut danger'], 'next_coord': (10, 9), 'next_move': 'up', 'time': '0.023s'}


    game_state = init_from_log(log)
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()

