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

def prefer_off_border(moves):
    moves_rank = [(a, 1 if on_border(a) else 0) for a in moves]
    moves = first_group(moves_rank)
    return moves

def go_straight():
    moves = prefer_straight(g.e.allowed_moves)
    g.next_coord = moves[0]

def default():
    moves = prefer_straight(prefer_more_next_move(prefer_off_border(g.e.allowed_moves)))
    g.next_coord = moves[0]

def battle_bigger():
    default()
    get_food()

def battle_not_bigger():
    default()
    get_food()
    avoid_danger()

def get_food():
    d_food = 8
    food_near = [f for f in g.food if distance_pq(f, g.s.my_head) < d_food]
    g.e.food_near = food_near
    if len(food_near) != 0:
        food_good_d = [f for f in food_near if distance_pq(f, g.s.my_head) <= distance_pq(f, g.s.other_head)]
        food_good_dd = [(f, path_distance_pq(f, g.s.my_head), path_distance_pq(f, g.s.other_head)) for f in food_good_d]
        food_good = [(f, d1) for f,d1,d2 in food_good_dd if d1 <= d2]
        g.e.food_good = food_good
        if len(food_good) != 0:
            food_targets = first_group(food_good)
            food_target = food_targets[0]
            g.e.food_target = food_target
            moves = shortest_path_move(g.s.my_head, food_target)
            moves = prefer_straight(prefer_more_next_move(moves))
            g.next_coord = moves[0]
        else:
            food_worth = [f for f in food_near if path_distance_pq(f, g.s.other_head) > 2]
            g.e.food_worth = food_worth
            if len(food_worth) != 0:
                food_worth_d = [(f, path_distance_pq(f, g.s.my_head)) for f in food_worth]
                food_worth = first_group(food_worth_d)
                food_target = food_worth[0]
                g.e.food_target = food_target
                moves = shortest_path_move(g.s.my_head, food_target)
                moves = prefer_straight(prefer_more_next_move(moves))
                g.next_coord = moves[0]

def head_collision():

    common_adj = [p for p in adj_cells(g.s.my_head) if p in adj_cells(g.s.other_head)]
    if len(common_adj) == 2:
        g.e.collision_type = 2
        collision_points = [p for p in common_adj if p not in g.occupied_cells[0]]
        if len(collision_points) == 2:
            avoid_points = [p for p in g.e.allowed_moves if p not in collision_points]
            g.e.avoid_points = avoid_points
            if len(avoid_points) != 0:
                avoid_point = avoid_points[0]
                if not on_border(avoid_point):
                    g.next_coord = avoid_point
                else:
                    if g.s.my_length < g.s.other_length:
                        collision_food = [p for p in collision_points if p in g.food]
                        g.e.collision_food = collision_food
                        if len(collision_food) == 1:
                            #take chance by avoiding food
                            one = [p for p in collision_points if p not in collision_food]
                            g.next_coord = one[0]
                        else:
                            avoid_point_next = [p for p in adj_cells(avoid_point) if p not in g.occupied_cells[1]]
                            g.e.avoid_point_next = avoid_point_next
                            g.next_coord = collision_points[0]
                            if len(avoid_point_next) == 2:
                                #intense calc point
                                #let's say b is the farther point (to other_head), check if b has wayout
                                b = [p for p in avoid_point_next if distance_pq(p, g.s.other_head) > 2][0]
                                wayout_room = path_connected_set(b, g.occupied_cells[0]+[avoid_point])
                                g.e.wayout_room = len(wayout_room)
                                if g.e.wayout_room >= g.s.my_length:
                                    g.next_coord = avoid_point
                                else:
                                    #take risk
                                    g.next_coord = collision_points[0]
                            else:
                                #avoid point has not enough wayout dir
                                #take risk
                                g.next_coord = collision_points[0]
                    else:
                        #equal length
                        #do nothing for now
                        pass
            else:
                #no avoid point
                #has risk, but nothing need to do
                pass
        else:
            #type 2 collision, 1 collision point
            if len(g.e.allowed_moves) == 3:
                #type 2, 1 collision point, 3 allowed moves
                if g.s.my_length < g.s.other_length:
                    #enemy is chasing
                    #go straight to the end
                    g.e.situation = "enemy is chasing"
                    go_straight()
                else:
                    #equal length
                    #nothing need to do
                    pass
            else:
                #there is an avoid point beside the single collision point
                #take the avoid point
                avoid_point = [p for p in g.e.allowed_moves if p not in collision_points]
                avoid_point = avoid_point[0]
                g.next_coord = avoid_point
    else:
        #type 1 collision with exactly one collision point - because heads are path connected
        collision_point = common_adj[0]
        me_heading_collision_point = get_adjacent_dir(g.s.my_head, collision_point) == get_adjacent_dir(g.s.my_neck, g.s.my_head)
        other_heading_collision_point = get_adjacent_dir(g.s.other_head, collision_point) == get_adjacent_dir(g.s.other_neck, g.s.other_head)
        same_dir = get_adjacent_dir(g.s.my_neck, g.s.my_head) == get_adjacent_dir(g.s.other_neck, g.s.other_head)
        if me_heading_collision_point and other_heading_collision_point:
            #collision trains

            if g.s.my_length < g.s.other_length:
                avoid_points = [p for p in g.e.allowed_moves if p != collision_point]
                if len(avoid_points) == 1:
                    avoid_point = avoid_points[0]
                    g.next_coord = avoid_point
                else:
                    #2 avoid points
                    #may need intense calc but here we simply do more next move choice - for now
                    moves = prefer_straight(prefer_more_next_move(prefer_off_border(avoid_points)))
                    g.next_coord = moves[0]
            else:
                #equal length
                #do the same as shorter length - for now
                avoid_points = [p for p in g.e.allowed_moves if p != collision_point]
                if len(avoid_points) == 1:
                    avoid_point = avoid_points[0]
                    g.next_coord = avoid_point
                else:
                    #2 avoid points
                    #may need intense calc but here we simply do more next move choice - for now
                    moves = prefer_straight(prefer_more_next_move(prefer_off_border(avoid_points)))
                    g.next_coord = moves[0]

        elif me_heading_collision_point:
            #perpendicular
            #do the same as above for now

            if g.s.my_length < g.s.other_length:
                avoid_points = [p for p in g.e.allowed_moves if p != collision_point]
                if len(avoid_points) == 1:
                    avoid_point = avoid_points[0]
                    g.next_coord = avoid_point
                else:
                    #2 avoid points
                    #may need intense calc but here we simply do more next move choice - for now
                    moves = prefer_straight(prefer_more_next_move(prefer_off_border(avoid_points)))
                    g.next_coord = moves[0]
            else:
                #equal length
                #do the same as shorter length - for now
                avoid_points = [p for p in g.e.allowed_moves if p != collision_point]
                if len(avoid_points) == 1:
                    avoid_point = avoid_points[0]
                    g.next_coord = avoid_point
                else:
                    #2 avoid points
                    #may need intense calc but here we simply do more next move choice - for now
                    moves = prefer_straight(prefer_more_next_move(prefer_off_border(avoid_points)))
                    g.next_coord = moves[0]                       

        elif other_heading_collision_point:
            #perpendicular
            #other is coming to me
            #do the same as above for now

            if g.s.my_length < g.s.other_length:
                avoid_points = [p for p in g.e.allowed_moves if p != collision_point]
                if len(avoid_points) == 1:
                    avoid_point = avoid_points[0]
                    g.next_coord = avoid_point
                else:
                    #2 avoid points
                    #may need intense calc but here we simply do more next move choice - for now
                    moves = prefer_straight(prefer_more_next_move(prefer_off_border(avoid_points)))
                    g.next_coord = moves[0]
            else:
                #equal length
                #do the same as shorter length - for now
                avoid_points = [p for p in g.e.allowed_moves if p != collision_point]
                if len(avoid_points) == 1:
                    avoid_point = avoid_points[0]
                    g.next_coord = avoid_point
                else:
                    #2 avoid points
                    #may need intense calc but here we simply do more next move choice - for now
                    moves = prefer_straight(prefer_more_next_move(prefer_off_border(avoid_points)))
                    g.next_coord = moves[0]                       

        elif same_dir:
            #parallel same dir
            if g.s.my_length < g.s.other_length:
                if off_border_1(g.s.my_head):
                    #my snake is 1-off border
                    #go towards the border until 2 away
                    if len([off_border_1(p) for p in adj_cells(g.s.my_head)]) == 2:
                        #go straight to 2-off border then take risk
                        g.next_coord = collision_point
                    else:
                        #go straight
                        moves = prefer_straight(prefer_more_next_move(prefer_off_border(avoid_points)))
                        g.next_coord = moves[0]
                else:
                    #my snake is not 1-off border
                    #can't think of now
                    pass
            else:
                #equal length
                pass
        else:
            #parallel opposite dir
            g.e.situation = "type 1 collision, parallel opposite dir"
            moves = [a for a in moves if a != collision_point]
            moves = prefer_more_next_move(moves)
            g.next_coord = moves[0]

def avoid_danger():
    #danger override
    d_danger = 6
    if g.e.head_distance <= d_danger:
        g.e.head_path_distance = path_distance_pq(g.s.my_head, g.s.other_head)
        if g.e.head_path_distance <= d_danger:
            if g.e.head_path_distance == 2:
                head_collision()
            elif g.e.head_path_distance == 4:
                if g.s.my_length < g.s.other_length:
                    if g.s.my_length+1 == g.s.other_length and g.next_coord in g.food:
                        pass
                    else:
                        #don't go border
                        if on_border(g.next_coord):
                            moves = [a for a in g.e.allowed_moves if a != g.next_coord]
                            moves = prefer_straight(prefer_more_next_move(moves))
                            g.next_coord = moves[0]
                        else:
                            pass
                else:
                    pass
            else:
                #path distance 6
                #don't go on border unless in the middle
                if g.s.my_length < g.s.other_length:
                    if g.s.my_length+1 == g.s.other_length and g.next_coord in g.food:
                        pass
                    else:
                        #don't go border
                        if on_border(g.next_coord):
                            dx,dy = distance_to_border(g.next_coord)
                            md = max([dx, dy])
                            if md < 3:
                                moves = [a for a in g.e.allowed_moves if a != g.next_coord]
                                moves = prefer_straight(prefer_more_next_move(moves))
                                g.next_coord = moves[0]
                            else:
                                pass
                        else:
                            pass
                else:
                    pass
        else:
            #no danger
            pass
    else:
        #no danger
        pass

def battle():
    #1_vs_1
    if g.s.my_length > g.s.other_length:
        #no danger
        g.e.my_snake_bigger = True
        battle_bigger()
    else:
        g.e.my_snake_bigger = False
        battle_not_bigger()

def init_env():
    #estimated 5-step occupied cells
    g.occupied_cells = [
        occupied_cells(step)
        for step in [1,2,3,4,5]
    ]
    g.e.allowed_moves = [a for a in adj_cells(g.s.my_head) if a not in g.occupied_cells[0]]
    g.e.other_allowed_moves = [a for a in adj_cells(g.s.other_head) if a not in g.occupied_cells[0]]
    g.e.head_distance = distance_pq(g.s.my_head, g.s.other_head)

def decision():
    init_env()

    if len(g.e.allowed_moves) == 0:
        #no allowed moves, die on myself
        g.next_coord = g.s.my_neck
        return
    
    if len(g.e.allowed_moves) == 1:
        #no choice
        g.next_coord = g.e.allowed_moves[0]
        return
    
    #2 or 3 allowed moves
    g.next_coord = g.e.allowed_moves[0]
    if g.e.n_other == 1:
        battle()
    else:
        #1_vs_n, for now, use the same
        default()

######################################################
# initial functions
######################################################

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
    g.s.my_length = len(g.me["body"])
    g.s.other_length = len(g.other["body"])

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

