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
    def __init__(self, name, body, health):
        self.name = name
        self.body = body
        self.health = health
        self.length = None
        self.head = None
        self.neck = None
        self.tail = None

    def dict(self):
        return {k: self.__dict__[k] for k in ["name", "health", "body", ]}

g = None


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
        # if s.health == 100:
            #eat food, tail will not move in the next step
            # body = body + [body[-1]]
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

######################################################

def experiment_condition():
    # mes = [snake for snake in g.snakes if snake.name == "mark_snake"]
    # if len(mes) >= 2: return True
    # return False
    return len(g.others) > 1

def special_experimenting_code(game_state):
    #if functional2.special_experimenting_code(game_state): return True

    init_game(game_state)
    if not experiment_condition(): return False

    g.log["experiment"] = "Yes"
    start_time = time.time()
    #g.e.localtime = time.localtime()

    decision()
    g.state["next_move"] = get_adjacent_dir(g.me.head, g.next_coord)

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

    g.snakes = [ Snake(
            name=snake["name"],
            body=get_coord(snake["body"]),
            health=snake["health"],
        ) for snake in game_state["board"]["snakes"] ]
    for snake in g.snakes:
        snake.length = len(snake.body)
        snake.head = snake.body[0]
        snake.neck = snake.body[1]
        snake.tail = snake.body[-1]

    g.me = [snake for snake in g.snakes for c in [game_state["you"]["body"][0]] if snake.head == (c["x"], c["y"])][0]
    g.others = [snake for snake in g.snakes if snake.head != g.me.head]
    # g.me = [snake for snake in g.snakes if snake.id == game_state["you"]["id"]]
    # g.others = [snake for snake in g.snakes if snake.id != g.me.id]
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
        first_two_turn,
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
            move_group,
            avoid_collision_1_vs_n,
            avoid_equal_collision,
            kill_oppotunies,
            (killer_near),
            split_choice,
            wayout,
            get_food_1_vs_n,
            prefer_open_space,
            prefer_more_next_moves,
            prefer_straight,
        ])(moves)

def get_food_1_vs_n(moves):
    return cases([
        get_food_1,
        get_food_near,
    ])(moves)

def kill_oppotunies(moves):
    return cases([
        enemy_in_trap_move,
    ])(moves)

def enemy_in_trap_move(moves):
    if enemy_in_trap():
        kill_moves = [a for a in moves if on_border(a)]
        if len(kill_moves) != 0:
            g.decision_path.append("kill")
            return kill_moves

def enemy_in_trap():
    if not off_border_1(g.me.head):
        return False
    in_trap = False
    for i,c in enumerate(g.me.body):
        if c == g.me.tail and g.me.health != 100: continue
        for snake in g.others:
            if not is_adjacent(snake.head, c): continue
            if not on_border(snake.head): continue
            if on_border(c): continue
            b = g.me.body[i-1]
            if g.me.health == 100:
                b = g.me.body[i-2]
            if get_adjacent_dir(c, b) == get_adjacent_dir(snake.neck, snake.head):
                in_trap = True
                break
    if not in_trap:
        return False
    if any([on_border(g.me.body[j]) for j in range(i)]):
        #already performed kill action
        return False
    return True

def first_two_turn(moves):
    if g.state["turn"] < 2:
        return moves

def prefer_open_space(moves):
    if g.x.ngroup != 1: return

    aset = path_connected_set(g.me.head)
    killers = [snake for snake in g.others if snake.length > g.me.length]
    nonkillers = [snake for snake in g.others if snake.length <= g.me.length]
    aset = [a for a in aset 
     if all([path_distance_pq(a, g.me.head) < path_distance_pq(a, snake.head) for snake in killers])
     #and all([path_distance_pq(a, g.me.head) <= path_distance_pq(a, snake.head) for snake in nonkillers])
     ]
    nset = len(aset)
    center = int(round(sum([x for x,y in aset])/nset, 0)), int(round(sum([y for x,y in aset])/nset, 0))
    if distance_pq(center, g.me.head) >= 3:
        g.decision_path.append("go to open space")
        return prefer_by_rank(lambda a: distance_pq(a, center))(moves)

def prefer_straight(moves):
    return prefer_yes(is_straight)(moves)

def prefer_more_next_moves(moves):
    def n_next_moves(a):
        next_moves = [p for p in adj_cells(a) if p not in g.occupied_cells[1]]
        return len(next_moves)
    return prefer_by_score(n_next_moves)(moves)

def killer_near(moves):
    if min(distance_to_border(g.me.head)) < 2:
        killers = [snake for snake in g.others if snake.length > g.me.length and distance_pq(snake.head, g.me.head) <= 6]
        if len(killers) != 0:
            real_killers = [snake for snake in killers if path_distance_pq(snake.head, g.me.head) <= 10]
            if len(real_killers) != 0:
                g.decision_path.append("killer near")
                g.x.real_killers = real_killers
                return cases([
                    me_at_corner,
                    me_at_off_border,
                    me_on_border,
                ])(moves)

def me_at_corner(moves):
    dist = distance_to_border(g.me.head)
    if dist in [(0,1), (1,0), (1,1), (0,2), (2,0)]:
        g.decision_path.append("me at corner")
        return prefer_no(on_border)(moves)

def me_on_border(moves):
    if not on_border(g.me.head): return
    real_killers = g.x.real_killers
    if len(real_killers) == 1:
        killer = real_killers[0]
        dist1 = distance_pq(g.me.head, killer.head)
        dist2 = path_distance_pq(g.me.head, killer.head)
        if dist1 <= 4 and dist1 == dist2:
            g.decision_path.append("return off border")
            return prefer_no(on_border)(moves)
        if dist1 == 6 and dist1 == dist2:
            if coming_near(killer):
                g.decision_path.append("return off border")
                return prefer_no(on_border)(moves)

def coming_near(killer):
    killer_next = [p for p in adj_cells(killer.head) if get_adjacent_dir(killer.neck, killer.head) == get_adjacent_dir(killer.head, p)]
    killer_next = [p for p in killer_next if p not in g.occupied_cells[0]]
    if len(killer_next) == 0:
        return False
    killer_next = killer_next[0]
    my_next = [p for p in adj_cells(g.me.head) if is_straight(p) and p not in g.occupied_cells[0]]
    if len(my_next) == 0:
        return False
    my_next = my_next[0]
    if distance_pq(killer_next, my_next) < distance_pq(g.me.head, killer.head):
        return True
    return False

def me_at_off_border(moves):
    if off_border_1(g.me.head):
        real_killers = g.x.real_killers
        if len(real_killers) == 1:
            killer = real_killers[0]
            dist1 = distance_pq(g.me.head, killer.head)
            dist2 = path_distance_pq(g.me.head, killer.head)
            if dist1 <= 4 and dist1 == dist2:
                if coming_near(killer):
                    g.decision_path.append("don't go border")
                    return prefer_no(on_border)(moves)

def wayout(moves):
    ngroup = move_connected_group(moves)
    if ngroup == 1:
        aset = path_connected_set(g.me.head)
        aset = [p for p in aset if p != g.me.head]
        if len(aset) <= int(g.me.length * 1.5):
            g.decision_path.append("consider wayout")
            adj_indexes = [i for i in range(g.me.length) if any([p in aset for p in adj_cells(g.me.body[i])])]
            max_index = max(adj_indexes)
            wayout_point = g.me.body[max_index]
            required_steps = g.me.length - max_index - 1
            if path_connected(g.me.head, wayout_point):
                if required_steps < path_distance_pq(g.me.head, wayout_point):
                    g.decision_path.append("wayout point far enough")
                else:
                    if len(aset) > 12:
                        g.decision_path.append("confined space too large - meander")
                        far_points = prefer_by_score(lambda a: path_distance_pq(a, wayout_point))(moves)
                        if len(far_points) == 1:
                            return far_points

                        #then there are 2 points, cannot  have 3
                        #and they are perpendicular, ie, one straight, one left or right
                        #and they have a common adjacent point
                        a,b = far_points
                        c = [c for c in adj_cells(a) if c in adj_cells(b) and c != g.me.head][0]
                        occupied = g.occupied_cells[0]+[c]
                        a_connection = path_connected(a, wayout_point, occupied)
                        b_connection = path_connected(b, wayout_point, occupied)
                        if not all([a_connection, b_connection]):
                            choice = a if not a_connection else b
                            g.decision_path.append(f"go first {choice}")
                            return [choice]

                    else:
                        g.decision_path.append("confined space calculate wayout")

                        layers = [[[g.me.head]]]
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
                        if len(moves) != 0:
                            return moves
                        g.decision_path.append("no calculated wayout")

def move_connected_group(moves):
    if len(moves) == 1:
        return 1
    elif len(moves) == 2:
        a,b = moves
        if path_distance_pq(a, b) >= 4:
            return 2
        return 1
    elif len(moves) == 3:
        straight = [a for a in moves if is_straight(a)][0]
        others = [a for a in moves if a != straight]
        if any([path_distance_pq(a, straight) > 2 for a in others]):
            return 2
        return 1
    turn = g.state["turn"]
    id = g.state["game"]["id"]
    print(f"MARK_EXCEPTION, id: {id}, turn: {turn}, move_connected_group")

def move_group(moves):
    ngroup = move_connected_group(moves)
    g.x.ngroup = ngroup

def split_choice(moves):
    ngroup = g.x.ngroup
    if ngroup > 1:
        g.decision_path.append("split choice")
        confined_moves = [a for a in moves if len(path_connected_set(a)) < g.me.length //2]
        confined_moves = [a for a in confined_moves if not path_connected(a, g.me.tail)]
        if len(confined_moves) == 0:
            g.decision_path.append("no confinement - need further consideration")
            return
        g.decision_path.append("has confined moves")
        good_moves = [a for a in moves if a not in confined_moves]
        if len(good_moves) != 0:
            g.decision_path.append("avoid confined moves")
            return good_moves
        g.decision_path.append("both confined moves")
        #prefer near tail
        def tail_index(a):
            aset = path_connected_set(a)
            adj_set = [i for i,c in enumerate(g.me.body) if any([p in aset for p in adj_cells(c)])]
            max_index = max(adj_set) if len(adj_set) != 0 else 0
            return max_index
        return prefer_by_score(tail_index)(moves)

def avoid_collision_1_vs_n(moves):
    danger_moves = [a for a in moves
        for snakes in [[snake for snake in g.others if is_adjacent(a, snake.head) and snake.length > g.me.length]]
        if len(snakes) != 0 ]
    if len(danger_moves) != 0:
        moves = [a for a in moves if a not in danger_moves]
        if len(moves) != 0:
            if len(moves) == 1:
                a = moves[0]
                next_next_move = [p for p in adj_cells if a not in g.occupied_cells[1]]
                if len(next_next_move) <= 1:
                    g.decision_path.append("take risk")
                    return danger_moves
            g.decision_path.append("avoid collision")
            return moves
        g.decision_path.append("nowhere to avoid")

def avoid_equal_collision(moves):
    danger_moves = [a for a in moves
        for snakes in [[snake for snake in g.others if is_adjacent(a, snake.head) and snake.length == g.me.length]]
        if len(snakes) != 0 ]
    if len(danger_moves) != 0:
        g.decision_path.append("avoid equal collision")
        moves = [a for a in moves if a not in danger_moves]
        if len(moves) != 0:
            return moves
        g.decision_path.append("nowhere to avoid")

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
    log = {'id': 'f7ed1721-e9a3-41e2-9393-70b0f6228f7b', 'turn': 181, 'me': {'name': 'mark_snake', 'health': 89, 'body': [(1, 9), (0, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (8, 9), (8, 8), (8, 7), (9, 7), (10, 7), (10, 6), (9, 6), (8, 6), (7, 6), (6, 6), (5,6)], 'id': 'gs_Wpt7XGBbwjG6D8T3fFrR9VC8'}, 'others': [{'name': 'mark_snake', 'health': 99, 'body': [(6, 0), (5, 0), (4, 0), (3, 0), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (10, 2), (9, 2), (9,2)], 'id': 'gs_GS7Dhmw6Hb43XrrYwvJ3DD9C'}], 'food': [(5, 4), (6, 2)], 'experiment': 'Yes', 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 9), (2, 8)], 'head_distance': 14, 'head_path_distance': 999}, 'decision_path': ['go to food'], 'next_coord': (3, 9), 'next_move': 'right', 'time': '0.005s'}
    log = {'id': '5608d1f2-0099-4520-881a-244574bfeaab', 'turn': 25, 'me': {'name': 'mark_snake', 'health': 89, 'body': [(1,8), (2, 8), (3, 8), (4, 8), (5, 8)], 'id': 'gs_f4PYDQ3Cf6KGk9FjXXvTJPV7'}, 'others': [{'name': 'mark_snake', 'health': 96, 'body': [(3,0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0)], 'id': 'gs_dVwxDDHKpBVqXrSj4XFwjgy9'}], 'food': [(4, 5), (4, 3), (2, 1)], 'experiment': 'Yes', 'decision_support': {'n_other': 1, 'allowed_moves': [(1, 8), (2, 9), (2, 7)], 'head_distance': 10, 'head_path_distance': 10}, 'decision_path': ['go to food'], 'next_coord': (4, 1), 'next_move': 'right', 'time': '0.010s'}
    log = {'id': 'e7f4cae2-49e9-45c6-983d-6e24763e280f', 'turn': 84, 'me': {'name': 'mark_snake', 'health': 98, 'body': [(10,4), (9,4), (8,4), (7,4), (6,4), (6, 5), (6, 6), (6, 7), (5, 7), (4, 7), (3, 7), (3, 6), (3, 5), (3, 4), (3, 3)], 'id': 'gs_rjt4MgXVRPTgQbwdfHv3YmMc'}, 'others': [{'name': 'mark_snake', 'health': 96, 'body': [(6,8), (5,8), (4,8), (3,8), (2,8), (1, 8), (1, 9), (2, 9), (3, 9), (4, 9)], 'id': 'gs_qCmJqkQrx3YP8XwjrhM7qgFc'}], 'food': [(10, 2)], 'experiment': 'Yes', 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 5), (5, 5), (6, 4)], 'head_distance': 8, 'head_path_distance': 10}, 'decision_path': ['get food1'], 'next_coord': (6, 4), 'next_move': 'down', 'time': '0.002s'}
    log = {'id': '4a988799-cda8-4914-b716-27b2346aeb88', 'turn': 105, 'me': {'name': 'mark_snake', 'health': 94, 'body': [(6, 7), (6, 6), (6, 5), (5, 5), (4, 5), (4, 6), (4, 7), (3, 7), (2, 7), (2, 8), (2, 9), (3, 9), (3, 10)], 'id': 'gs_8YxYqXPxrbqr4PYDkmM94FDR'}, 'others': [{'name': 'Frank The Tank', 'health': 89, 'body': [(4, 9), (5, 9), (6, 9), (7, 9), (7, 8), (8, 8), (8, 9), (9, 9), (9, 8), (9, 7)], 'id': 'gs_v8CMgg4bg7cf8Sw8PMbq9mXQ'}, {'name': 'Wim HU [dev]', 'health': 77, 'body': [(7, 2), (7, 3), (7, 4), (8, 4), (9, 4), (10, 4), (10, 3), (10, 2)], 'id': 'gs_YRKKjjVPT8jTq7jXXBhcDmSP'}, {'name': 'Kakemonsteret-v2', 'health': 96, 'body': [(3, 2), (3, 1), (3, 0), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 4), (3, 3), (4, 3)], 'id': 'gs_jYfmcXQSdvPBxvcDGYgKq7kT'}], 'food': [(9, 10)], 'experiment': 'Yes', 'decision_path': ['split choice', 'no confinement'], 'next_coord': (5, 7), 'next_move': 'left', 'time': '0.004s'}
    log = {'id': 'bf9336d7-ab5c-4452-8a90-3ab7d004304f', 'turn': 116, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(9, 3), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (9, 9), (9, 8)]}, 'others': [{'name': 'Frank The Tank', 'health': 99, 'body': [(7, 3), (7, 4), (8, 4), (8, 5), (8, 6), (7, 6), (7, 5), (6, 5), (5, 5), (5, 6), (4, 6), (3, 6), (3, 7), (2, 7), (2, 6)]}, {'name': 'Wim HU [dev]', 'health': 100, 'body': [(2, 4), (1, 4), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (6, 2), (6, 1), (6, 0), (7, 0), (7, 0)]}], 'food': [(0, 1)], 'experiment': 'Yes', 'decision_path': ['avoid collision', 'killer near', 'split choice', 'no confinement'], 'next_coord': (9, 2), 'next_move': 'down', 'time': '0.099s'}
    log = {'id': '6f80615c-5936-434c-9112-8c2e95153299', 'turn': 35, 'me': {'name': 'mark_snake', 'health': 98, 'body': [(8, 9), (8, 8), (8, 7), (8, 6), (8, 5)]}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 83, 'body': [(9, 4), (9, 3), (8, 3), (8, 2), (8, 1), (8, 0)]}, {'name': 'Frank The Tank', 'health': 97, 'body': [(2, 3), (1, 3), (0, 3), (0, 2), (1, 2), (2, 2), (3, 2), (3, 3)]}, {'name': 'Wim HU [dev]', 'health': 95, 'body': [(2, 9), (2, 8), (2, 7), (3, 7), (4, 7), (5, 7)]}], 'food': [(3, 9)], 'experiment': 'Yes', 'decision_path': ['killer near'], 'next_coord': (9, 9), 'next_move': 'right', 'time': '0.199s'}
    log = {'id': '6f80615c-5936-434c-9112-8c2e95153299', 'turn': 35, 'me': {'name': 'mark_snake', 'health': 98, 'body': [(8, 9), (8, 8), (8, 7), (8, 6), (8, 5)]}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 83, 'body': [(9, 4), (9, 3), (8, 3), (8, 2), (8, 1), (8, 0)]}, {'name': 'Frank The Tank', 'health': 97, 'body': [(2, 3), (1, 3), (0, 3), (0, 2), (1, 2), (2, 2), (3, 2), (3, 3)]}, ], 'food': [(3, 9)], 'experiment': 'Yes', 'decision_path': ['killer near'], 'next_coord': (9, 9), 'next_move': 'right', 'time': '0.199s'}
    log = {'id': '67fd9c27-534e-497f-8e81-45d556be239b', 'turn': 144, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(2, 0), (1, 0), (1, 1), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (3, 1), (4, 1), (4, 2), (5, 2)]}, 'others': [{'name': 'Frank The Tank', 'health': 99, 'body': [(6, 8), (6, 7), (7, 7), (7, 6), (6, 6), (5, 6), (5, 5), (5, 4), (6, 4), (7, 4), (7, 3), (8, 3), (8, 4), (9, 4), (9, 5)]}, {'name': 'Wim HU [dev]', 'health': 95, 'body': [(5, 3), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (3, 9), (2, 9), (1, 9), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5)]}], 'food': [(10, 0)], 'experiment': 'Yes', 'decision_path': ['killer near', 'me at corner'], 'next_coord': (2, 1), 'next_move': 'up', 'time': '0.000s'}
    log = {'id': '4b1cfdc7-775f-459e-bbbb-02c4e4e2efbf', 'turn': 144, 'me': {'name': 'mark_snake', 'health': 62, 'body': [(9, 9), (8, 9), (8, 8), (8, 7), (7, 7), (7, 6), (7, 5), (8, 5), (9, 5)]}, 'others': [{'name': 'Frank The Tank', 'health': 88, 'body': [(6, 8), (5, 8), (4, 8), (4, 7), (3, 7), (3, 8), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (3, 4), (3, 3), (4, 3), (4, 2), (5, 2), (5, 3)]}, {'name': 'Wim HU [dev]', 'health': 90, 'body': [(6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3)]}, {'name': 'Kakemonsteret-v2', 'health': 96, 'body': [(8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (0, 6)]}], 'food': [(10, 9)], 'experiment': 'Yes', 'decision_path': ['avoid collision', 'killer near', 'me at corner'], 'next_coord': (9, 8), 'next_move': 'down', 'time': '0.001s'}
    log = {'id': 'fe74fdfa-4aeb-43de-8395-870f61ce5b7b', 'turn': 219, 'me': {'name': 'mark_snake', 'health': 68, 'body': [(0, 9), (0, 8), (1, 8), (1, 7), (2, 7), (3, 7), (3, 8), (3, 9), (4, 9), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10)]}, 'others': [{'name': 'Wim HU [dev]', 'health': 86, 'body': [(0, 1), (0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 5), (3, 6), (2, 6), (1, 6), (0, 6), (0, 5)]}, {'name': 'Kakemonsteret-v2', 'health': 91, 'body': [(5, 0), (4, 0), (3, 0), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (5, 7), (5, 6), (6, 6), (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (7, 1), (7, 0)]}], 'food': [(6, 0)], 'experiment': 'Yes', 'decision_path': ['consider wayout', 'wayout point far enough'], 'next_coord': (1, 9), 'next_move': 'right', 'time': '0.001s'}
    log = {'id': '32fcee8d-03d8-4e6e-981f-83a54c3445ca', 'turn': 149, 'me': {'name': 'mark_snake', 'health': 85, 'body': [(10, 5), (9, 5), (8, 5), (7, 5), (6, 5), (5, 5), (5, 6), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (10, 6)]}, 'others': [{'name': 'Wim HU [dev]', 'health': 56, 'body': [(8, 1), (8, 0), (7, 0), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (7, 4), (8, 4), (8, 3), (9, 3)]}, {'name': 'Kakemonsteret-v2', 'health': 99, 'body': [(0, 5), (0, 6), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, 10), (3, 10), (3, 9), (2, 9), (2, 8), (2, 7), (2, 6), (3, 6), (4, 6)]}], 'food': [(1, 0)], 'experiment': 'Yes', 'decision_path': ['split choice', 'has confined moves', 'avoid confined moves'], 'next_coord': (10, 4), 'next_move': 'down', 'time': '0.000s'}
    log = {'id': '49650c4c-8b0b-40a8-be5a-4312fe526212', 'turn': 104, 'me': {'name': 'mark_snake', 'health': 94, 'body': [(9, 3), (9, 2), (10, 2), (10, 1), (9, 1), (8, 1), (7, 1), (7, 2), (7, 3)]}, 'others': [{'name': 'Frank The Tank', 'health': 100, 'body': [(8, 4), (7, 4), (6, 4), (6, 5), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (9, 9)]}, {'name': 'Kakemonsteret-v2', 'health': 92, 'body': [(3, 3), (3, 2), (2, 2), (2, 1), (2, 0), (1, 0), (1, 1), (1, 2), (1, 3), (2, 3), (2, 4), (1, 4), (1, 5)]}], 'food': [(10, 7)], 'experiment': 'Yes', 'decision_path': ['avoid collision'], 'next_coord': (10, 3), 'next_move': 'right', 'time': '0.001s'}


    game_state = init_from_log(log)
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()

