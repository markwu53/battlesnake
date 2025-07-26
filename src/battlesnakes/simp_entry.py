import time

class Snake:
    def __init__(self, name, body, health):
        self.name = name
        self.body = body
        self.health = health
        self.length = len(body)
        self.head = body[0]
        self.neck = body[1]
        self.tail = body[-1]
    def dict(self):
        return {k: self.__dict__[k] for k in ["name", "health", "body", ]}

class DecisionAux:
    def __init__(self):
        self.allowed_moves = None
        self.other_allowed_moves = None
        self.occupied_cells = None

class Game:
    def __init__(self):
        self.state = None
        self.me = None
        self.others = None
        self.other = None
        self.snakes = None
        self.food = None
        self.next_coord = None
        self.log = {}
        self.decision_path = []
        self.x = DecisionAux()

def main(game_state):

    ######################################################
    # "global" variable
    ######################################################

    g = Game()

    ######################################################
    # utility functions
    ######################################################

    def ________UTILITY_FUNCTIONS________():
        pass

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
            body = s.body
            # if s.health == 100:
                #eat food, tail will not move in the next step
                # body = body + [body[-1]]
            sbody.append(body[:-step])
        cells = [c for s in sbody for c in s]
        return cells

    def distance_pq(p, q):
        x1,y1 = p
        x2,y2 = q
        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def is_adjacent(p, q):
        return distance_pq(p, q) == 1

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

    def is_straight(p):
        return get_adjacent_dir(g.me.head, p) == get_adjacent_dir(g.me.neck, g.me.head)

    ######################################################

    def path_distance_pq(p, q, occupied=None):
        if occupied is None:
            occupied = g.x.occupied_cells[0]
        #remove q from occupied otherwise there is no path
        occupied = [p for p in occupied if p != q]
        layers = path_connected_layers(p, occupied)
        for i,layer in enumerate(layers):
            if q in layer:
                return i
        return 999

    def path_connected_layers(p, occupied=None):
        if occupied is None:
            occupied = g.x.occupied_cells[0]
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
            occupied = g.x.occupied_cells[0]
        layers = path_connected_layers(p, occupied)
        return set([q for layer in layers for q in layer])

    def path_connected(p, q, occupied=None):
        if occupied is None:
            occupied = g.x.occupied_cells[0]
        occupied = [x for x in occupied if x != q]
        return q in path_connected_set(p, occupied)

    def shortest_path_move(p, q, occupied=None):
        if is_adjacent(p, q):
            return [q]
        if occupied is None:
            occupied = g.x.occupied_cells[0]
        occupied = [c for c in occupied if c != q]
        if q in path_connected_set(p, occupied):
            dist = path_distance_pq(p, q, occupied)
            layers = path_connected_layers(p, occupied)
            if len(layers) > 1:
                result = [x for x in layers[1] if path_distance_pq(x, q, occupied) == dist-1]
                return result
        return []

    ######################################################

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

    def score_more_next_move(p):
        moves = [a for a in adj_cells(p) if a not in g.x.occupied_cells[1]]
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

    def prefer_in(aset):
        return prefer_yes(lambda a: a in aset)
    
    def prefer_not_in(aset):
        return prefer_no(lambda a: a in aset)

    def prefer_by_score(score):
        def fn(moves):
            moves = [(a, score(a)) for a in moves]
            moves = first_group(moves, reverse=True)
            return moves
        return fn

    def prefer_more_next_moves(moves):
        def n_next_moves(a):
            next_moves = [p for p in adj_cells(a) if p not in g.x.occupied_cells[1]]
            return len(next_moves)
        return prefer_by_score(n_next_moves)(moves)

    def prefer_open_space(moves):
        aset = path_connected_set(g.me.head)
        killers = [snake for snake in g.others if snake.length > g.me.length]
        nonkillers = [snake for snake in g.others if snake.length <= g.me.length]
        aset = [a for a in aset 
        if all([path_distance_pq(a, g.me.head) < path_distance_pq(a, snake.head) for snake in killers])
        #and all([path_distance_pq(a, g.me.head) <= path_distance_pq(a, snake.head) for snake in nonkillers])
        ]
        nset = len(aset)
        center = int(round(sum([x for x,y in aset])/nset, 0)), int(round(sum([y for x,y in aset])/nset, 0))
        if distance_pq(center, g.me.head) >= 2:
            g.decision_path.append(f"go to open space {center}")
            return prefer_by_rank(lambda a: distance_pq(a, center))(moves)

    def prefer_straight(moves):
        return prefer_yes(is_straight)(moves)

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

    def log_print(anything=None):
        turn = g.state["turn"]
        id = g.state["game"]["id"]
        print(f"MARK_EXCEPTION, TURN: {turn}, id: {id}, {anything}")

    ######################################################

    def ________DECISION_LOGIC________():
        pass

    def decision():
        #estimated 5-step occupied cells
        g.x.occupied_cells = [
            occupied_cells(step)
            for step in [1,2,3,4,5]
        ]
        g.x.allowed_moves = [a for a in adj_cells(g.me.head) if a not in g.x.occupied_cells[0]]

        if len(g.x.allowed_moves) == 0:
            #no allowed moves, die on myself
            g.next_coord = g.me.neck
            return
        
        if len(g.x.allowed_moves) == 1:
            #no choice
            g.next_coord = g.x.allowed_moves[0]
            return

        if len(g.others) == 0:
            #win
            g.next_coord = g.x.allowed_moves[0]
            return

        #allowed_moves must be 2 or 3
        moves = sequential([
            kill_oppotunities,
            avoid_danger,
            split_choice,
            wayout,
            get_food,
            other_considerations,
            prefer_straight,
        ])(g.x.allowed_moves)

        g.next_coord = take_first(moves)

    def kill_oppotunities(moves):
        return cases([
            collision_kill,
        ])(moves)

    def collision_kill(moves):
        others = [snake for snake in g.others if snake.length < g.me.length]
        others = [snake for snake in others if distance_pq(snake.head, g.me.head) == 2]

    def ____AVOID_DANGER____():
        pass

    def avoid_danger(moves):
        return sequential([
            confinement_danger,
            trap_danger,
            forming_trap_danger,
            collision_danger,
            two_step_collision,
        ])(moves)

    def confinement_danger(moves):
        def confined(a):
            aset = path_connected_set(a)
            if len(aset) <= 3:
                if not any([path_connected(a, snake.tail) for snake in g.snakes]):
                    return True
            return False
        confined_set = [a for a in moves if confined(a)]
        if len(confined_set) != 0:
            good_set = [a for a in moves if a not in confined_set]
            if len(good_set) != 0:
                g.decision_path.append(f"confined move {confined_set}")
                return good_set

    def is_a_border_trap(a):
        if not on_border(a):
            return False
        for snake in g.others:
            for i,c in enumerate(snake.body):
                if c == snake.tail and snake.health != 100: continue
                if not is_adjacent(c, a): continue
                if on_border(c): continue
                b = snake.body[i-1]
                if get_adjacent_dir(g.me.neck, g.me.head) == get_adjacent_dir(c, b):
                    return True
        return False

    def trap_danger(moves):
        trap = [a for a in moves if is_a_border_trap(a)]
        if len(trap) != 0:
            g.decision_path.append(f"trap {trap}")
            return prefer_not_in(trap)(moves)

    def forming_trap_danger(moves):
        others = [snake for snake in g.others if distance_pq(snake.head, g.me.head) == 2]
        if len(others) == 1:
            other = others[0]
            adj_points = [p for p in adj_cells(g.me.head) if p in adj_cells(other.head)]
            if len(adj_points) == 2:
                collision_points = [p for p in adj_points if p in moves]
                trap_point = [p for p in collision_points if len([q for q in adj_cells(p) if q in g.x.occupied_cells[1]]) == 1]
                if len(trap_point) == 1:
                    if not is_opposite_dir(get_adjacent_dir(g.me.head, trap_point[0]), get_adjacent_dir(other.neck, other.head)):
                        g.decision_path.append(f"forming trap {trap_point}")
                        return prefer_not_in(trap_point)(moves)

    def collision_danger(moves):
        if not any([distance_pq(snake.head, g.me.head) == 2 for snake in g.others]):
            return

        killers = [snake for snake in g.others if snake.length > g.me.length]
        nonkillers = [snake for snake in g.others if snake.length == g.me.length]
        killer_collision_points = [a for a in moves for snake in killers if is_adjacent(a, snake.head)]
        nonkiller_collision_points = [a for a in moves for snake in nonkillers if is_adjacent(a, snake.head)]
        return prefer_no(lambda a: a in nonkiller_collision_points)(
            prefer_no(lambda a: a in killer_collision_points)(moves))

    def two_step_collision(moves):
        if not any([distance_pq(snake.head, g.me.head) <= 4 for snake in g.others]):
            return

        killers = [snake for snake in g.others if snake.length > g.me.length]
        nonkillers = [snake for snake in g.others if snake.length == g.me.length]
        def collision(a):
            step2 = [p for p in adj_cells(a) if p not in g.x.occupied_cells[1]]
            collision = [p for p in step2 if any([path_distance_pq(p, snake.head) == 2 for snake in killers])]
            collision2 = [p for p in step2 if any([path_distance_pq(p, snake.head) == 2 for snake in nonkillers])]
            step2_safe = [p for p in step2 if p not in collision and p not in collision2]
            return len(step2_safe) == 0
        return prefer_no(collision)(moves)

    def ____SPLIT_CHOICES____():
        pass

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
        log_print("move_connected_group")

    def split_choice(moves):
        ngroup = move_connected_group(moves)
        if ngroup == 1:
            return
        return cases([
            split_1vn,
            split_1v1,
        ])(moves)

    def split_1v1(moves):
        if len(g.others) != 1:
            return
        return cases([
            split_1v1_short,
            split_1v1_long,
        ])(moves)
    
    def split_1v1_short(moves):
        if g.me.length <= 8:
            return moves

    def split_1v1_long(moves):
        if g.me.length <= 8:
            return
        g.decision_path.append("this needs careful classification")
        return sequential([
            split_avoid_deadend,
        ])(moves)

    def split_1vn(moves):
        if len(g.others) == 1:
            return
        return cases([
            split_1vn_short,
            split_1vn_medium,
            split_1vn_long,
        ])(moves)

    def split_1vn_short(moves):
        if g.me.length <= 6:
            return moves

    def split_1vn_medium(moves):
        if g.me.length <= 10:
            g.decision_path.append("split length medium")
            return split_avoid_deadend(moves)

    def split_avoid_deadend(moves):
        pass

    def split_1vn_long(moves):
        if g.me.length <= 10:
            return
        g.decision_path.append("split long")
        return sequential([
            split_avoid_absolute_danger,

            #1vn focus on survival, prefer easy and surely wayout
            cases([
                no_cut_can_see_my_tail,
                no_cut_can_see_other_tail,
                no_cut_can_reach_my_tail,
                no_cut_can_reach_other_tail,
            ]),
        ])(moves)

    def split_avoid_absolute_danger(moves):
        pass

    def no_cut_can_see_my_tail(moves):
        moves = [a for a in moves 
                 if not any([path_connected(a, snake.head) for snake in g.others]) 
                 and path_connected(a, g.me.tail)]
        if len(moves) != 0:
            g.decision_path.append("split choose my tail")
            return moves

    def no_cut_can_see_other_tail(moves):
        moves = [a for a in moves 
                 if not any([path_connected(a, snake.head) for snake in g.others]) 
                 and any([path_connected(a, snake.tail) for snake in g.others])]
        if len(moves) != 0:
            g.decision_path.append("split choose other tail")
            return moves

    def no_cut_can_reach_my_tail(moves):
        no_cut_moves = [a for a in moves if not any([path_connected(a, snake.head) for snake in g.others])]
        if len(no_cut_moves) == 0:
            return
        def wayout(a):
            aset = path_connected_set(a)
            max_index = max([i for i,c in enumerate(g.me.body) if any([p in aset for p in adj_cells(c)]) ])
            required_steps = g.me.length - max_index
            if required_steps < len(aset):
                return True
            return False
        wayout_moves = [a for a in moves if wayout(a)]
        if len(wayout_moves) != 0:
            g.decision_path.append("split choose wayout on me")
            return wayout_moves

    def no_cut_can_reach_other_tail(moves):
        no_cut_moves = [a for a in moves if not any([path_connected(a, snake.head) for snake in g.others])]
        if len(no_cut_moves) == 0:
            return
        def wayout(a):
            aset = path_connected_set(a)
            snakes = [snake for snake in g.others if any([p in aset for c in snake.body for p in adj_cells(c)])]
            if len(snakes) == 1:
                snake = take_first(snakes)
                max_index = max([i for i,c in enumerate(snake.body) if any([p in aset for p in adj_cells(c)]) ])
                required_steps = snake.length - max_index
                if required_steps < len(aset):
                    return True
            return False
        wayout_moves = [a for a in moves if wayout(a)]
        if len(wayout_moves) != 0:
            g.decision_path.append("split choose wayout on the other")
            return wayout_moves

    def ____WAYOUT____():
        pass

    def wayout(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 1:
            return

        return cases([
            wayout_see_one_tail,
        ])(moves)

    def wayout_see_one_tail(moves):
        aset = path_connected_set(g.me.head)
        if len(aset) >= int(g.me.length * 1.2):
            return
        snakes = [snake for snake in g.others if path_connected(g.me.head, snake.tail)]
        if len(snakes) != 1:
            return
        snake = take_first(snakes)
        if snake.length > g.me.length:
            #this case is to prevent a smaller snake try to confine me
            return
        waypoints = [(c,d) 
                     for i,c in enumerate(snake.body) if path_connected(g.me.head, c) 
                     for d in [abs(path_distance_pq(g.me.head, c) + i - snake.length)]
                        ]
        waypoints = [c for c,d in waypoints if d == min([d for c,d in waypoints])]
        waypoint = take_first(waypoints)
        g.decision_path.append(f"wayout tail shortcut {waypoint}")
        return shortest_path_move(g.me.head, waypoint)

    def ____GET_FOOD____():
        pass

    def get_food(moves):
        food_near = [f for f in g.food if distance_pq(f, g.me.head) <= 8]
        food_good = [f for f in food_near if path_connected(f, g.me.head) and all([path_distance_pq(f, g.me.head) < path_distance_pq(f, snake.head) for snake in g.others])]
        if len(food_good) != 0:
            food_better = prefer_by_rank(lambda f: path_distance_pq(f, g.me.head))(food_good)
            food_target = take_first(food_better)
            food_moves = shortest_path_move(g.me.head, food_target)
            return prefer_yes(lambda a: a in food_moves)(moves)

    def ____OTHER_CONSIDERATIONS____():
        pass

    def other_considerations(moves):
        return cases([
            short_prefer_more_move,
            crowd_prefer_open_space,
        ])(moves)

    def short_prefer_more_move(moves):
        if g.me.length <= 8:
            return prefer_more_next_moves(moves)

    def crowd_prefer_open_space(moves):
        if len(g.others) >= 2:
            g.decision_path.append("try to go to open space")
            return split_prefer_open_space(moves)

    def split_prefer_open_space(moves):
        ngroup = move_connected_group(moves)
        if ngroup >= 1:
            return prefer_open_space(moves)

    def ________GAME_ENTRY________():
        pass

    def init_game(game_state):
        g.state = game_state

        g.snakes = [
            Snake(
                name = snake["name"],
                body = get_coord(snake["body"]),
                health = snake["health"],
            )
            for snake in game_state["board"]["snakes"]
        ]
        g.me = [snake for snake in g.snakes for c in [game_state["you"]["body"][0]] if snake.head == (c["x"], c["y"])][0]
        g.others = [snake for snake in g.snakes if snake.head != g.me.head]

        if len(g.others) == 0:
            g.decision_path.append("only myself")
        elif len(g.others) == 1:
            g.decision_path.append("1v1")
            g.other = g.others[0]
        else:
            g.decision_path.append("1vn")

        g.food = get_coord(game_state["board"]["food"])

        g.log["id"] = game_state["game"]["id"]
        g.log["turn"] = game_state["turn"]
        g.log["me"] = g.me.dict()
        g.log["others"] = [snake.dict() for snake in g.others]
        g.log["food"] = g.food
        
    def entry_condition():
        if len(g.snakes) == 1:
            return True
        if g.me.name == "mark_snake": 
            return False
        if any(["mark_snake_test" in snake.name for snake in g.snakes]):
            return True
        if len([snake for snake in g.snakes if snake.name == "mark_snake"]) >= 2:
            return True
        return False

    

    ######################################################
    # main process
    ######################################################

    init_game(game_state)
    if not entry_condition(): return False

    g.log["module"] = "simp"
    start_time = time.time()
    #g.e.localtime = time.localtime()

    decision()
    next_move = get_adjacent_dir(g.me.head, g.next_coord)

    #g.log["decision_support"] = {k:v for k,v in g.e.__dict__.items() if v is not None}
    g.log["decision_path"] = g.decision_path
    g.log["next_coord"] = g.next_coord
    g.log["next_move"] = next_move

    end_time = time.time()
    g.log["time"] = f"{end_time-start_time:.3f}s"

    print(g.log)

    game_state["next_move"] = next_move
    return True

######################################################
# testing
######################################################

def ________TESTING________():
    pass

def init_from_log(log):
    def reverse_coord(cs):
        return [{"x":x, "y":y} for x,y in cs]

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

if __name__ == "__main__":
    log = {'id': '06c3573a-c6b9-45c2-b5f0-8505719d89fc', 'turn': 130, 'me': {'name': 'mark_snake', 'health': 93, 'body': [(9, 1), (8, 1), (7, 1), (6, 1), (5, 1), (5, 0), (4, 0), (3, 0), (3, 1), (2, 1)]}, 'others': [{'name': 'snakey_wakey', 'health': 59, 'body': [(7, 3), (6, 3), (5, 3), (4, 3), (4, 4), (4, 5), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6)]}, {'name': 'rustiger', 'health': 96, 'body': [(1, 3), (1, 2), (2, 2), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8)]}], 'food': [(5, 10), (8, 0)], 'module': 'functional2', 'decision_path': ['killer near', 'go to food'], 'next_coord': (9, 0), 'next_move': 'down', 'time': '0.008s'}
    log = {'id': 'cca6536b-7bd7-4438-9a43-9aa493fd9fb4', 'turn': 72, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(1, 7), (0, 7), (0, 6), (0, 5), (1, 5), (1, 6)]}, 'others': [{'name': 'Fairy Rust', 'health': 100, 'body': [(4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (9, 9), (10, 9), (10, 8), (10, 7), (9, 7), (9, 7)]}, {'name': 'MattIPv6', 'health': 76, 'body': [(4, 8), (4, 7), (4, 6), (4, 5), (4, 4), (5, 4), (6, 4)]}, {'name': 'Beholder', 'health': 95, 'body': [(3, 5), (2, 5), (2, 4), (3, 4), (3, 3), (3, 2), (2, 2), (2, 1)]}], 'food': [(0, 2)], 'module': 'functional2', 'decision_path': ['killer near'], 'next_coord': (1, 8), 'next_move': 'up', 'time': '0.178s'}
    log = {'id': '51dc66f7-b664-4b68-a3e8-39f3d129b024', 'turn': 136, 'me': {'name': 'mark_snake_test RED', 'health': 97, 'body': [(4, 0), (3, 0), (2, 0), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (0, 7), (0, 8), (0, 9), (1, 9)]}, 'others': [{'name': 'mark_snake_test GREEN', 'health': 83, 'body': [(10, 8), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8), (2, 8), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7)]}], 'food': [(9, 2)], 'module': 'simp', 'decision_path': ['1v1'], 'next_coord': (5, 0), 'next_move': 'right', 'allowed_moves': [(5, 0), (4, 1)], 'time': '0.001s'}
    log = {'id': '9dd43272-e5c3-482f-906d-e7b7f1734298', 'turn': 91, 'me': {'name': 'mark_snake_test BLUE', 'health': 100, 'body': [(8, 5), (8, 4), (9, 4), (10, 4), (10, 3), (9, 3), (8, 3), (8, 2), (9, 2), (10, 2), (10, 1), (9, 1), (9, 0), (9, 0)]}, 'others': [{'name': 'mark_snake', 'health': 96, 'body': [(2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5)]}, {'name': 'mark_snake_test GREEN', 'health': 49, 'body': [(7, 8), (6, 8), (6, 9), (5, 9), (4, 9), (3, 9), (2, 9), (1, 9)]}, {'name': 'mark_snake_test RED', 'health': 98, 'body': [(9, 6), (9, 7), (9, 8), (9, 9), (8, 9)]}], 'food': [(7, 7)], 'module': 'simp', 'decision_path': ['1vn', 'split long', 'avoid confined: []'], 'next_coord': (9, 5), 'next_move': 'right', 'allowed_moves': [(9, 5), (7, 5), (8, 6)], 'time': '0.011s'}
    log = {'id': 'a25bff64-e6a2-4f30-a2f6-dfa7c4ff234f', 'turn': 69, 'me': {'name': 'mark_snake_test RED', 'health': 93, 'body': [(5, 6), (6, 6), (7, 6), (8, 6), (8, 7), (8, 8), (8, 9), (7, 9), (7, 8), (7, 7)]}, 'others': [{'name': 'mark_snake', 'health': 100, 'body': [(4, 5), (3, 5), (3, 4), (3, 3), (4, 3), (4, 3)]}, {'name': 'mark_snake_test GREEN', 'health': 69, 'body': [(4, 7), (5, 7), (5, 8), (5, 9), (4, 9), (3, 9), (2, 9)]}, {'name': 'mark_snake_test BLUE', 'health': 93, 'body': [(2, 7), (1, 7), (1, 8), (1, 9), (1, 10), (0, 10), (0, 9)]}], 'food': [(8, 10)], 'module': 'simp', 'decision_path': ['1vn', 'split length medium', 'avoid confined: []', 'try to go to open space'], 'next_coord': (4, 6), 'next_move': 'left', 'time': '0.007s'}
    log = {'id': '26140136-e6ac-45b7-abf9-4938e61cad78', 'turn': 176, 'me': {'name': 'mark_snake_test BLUE', 'health': 81, 'body': [(0, 6), (0, 5), (0, 4), (1, 4), (2, 4), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (5, 8), (4, 8), (4, 7), (4, 6)]}, 'others': [{'name': 'mark_snake', 'health': 98, 'body': [(3, 7), (2, 7), (1, 7), (1, 8), (1, 9), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10)]}, {'name': 'mark_snake_test GREEN', 'health': 98, 'body': [(10, 8), (10, 7), (9, 7), (8, 7), (7, 7), (7, 6), (7, 5), (7, 4), (8, 4), (9, 4), (10, 4), (10, 3), (10, 2), (10, 1), (10, 0), (9, 0), (8, 0), (7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (3, 1)]}], 'food': [(3, 8)], 'module': 'simp', 'decision_path': ['1vn', 'split long', 'try to go to open space', 'go to open space (2, 6)'], 'next_coord': (1, 6), 'next_move': 'right', 'time': '0.004s'}

    game_state = init_from_log(log)
    main(game_state)
