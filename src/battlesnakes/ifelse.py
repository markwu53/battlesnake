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

def prefer_turn(moves):
    moves_rank = [(a, 0 if get_adjacent_dir(g.s.my_neck, g.s.my_head) == get_adjacent_dir(g.s.my_head, a) else 1) for a in moves]
    moves = first_group(moves_rank, reverse=True)
    return moves

def prefer_off_border(moves):
    moves_rank = [(a, 1 if on_border(a) else 0) for a in moves]
    moves = first_group(moves_rank)
    return moves

def go_straight():
    moves = prefer_straight(g.e.allowed_moves)
    g.next_coord = moves[0]

def default2(moves=None):
    if moves is None:
        moves = g.e.allowed_moves
    moves = prefer_straight(prefer_more_next_move(prefer_off_border(moves)))
    g.next_coord = moves[0]

def default(moves=None):
    if moves is None:
        moves = g.e.allowed_moves
    moves = prefer_straight(prefer_more_next_move(moves))
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
        food_good = [(f, d1) for f,d1,d2 in food_good_dd if d1 <= d2 and d1 < 999]
        g.e.food_good = food_good
        if len(food_good) != 0:
            g.e.situation = "go to food"
            food_targets = first_group(food_good)
            food_target = food_targets[0]
            g.e.food_target = food_target
            moves = shortest_path_move(g.s.my_head, food_target)
            moves = prefer_straight(prefer_more_next_move(moves))
            g.next_coord = moves[0]
        else:
            food_worth = [f for f in food_near if 2 < path_distance_pq(f, g.s.other_head) < 999 and path_distance_pq(f, g.s.my_head) < 999]
            g.e.food_worth = food_worth
            if len(food_worth) != 0:
                g.e.situation = "food worth trying"
                food_worth_d = [(f, path_distance_pq(f, g.s.my_head)) for f in food_worth]
                food_worth = first_group(food_worth_d)
                food_target = food_worth[0]
                g.e.food_target = food_target
                moves = shortest_path_move(g.s.my_head, food_target)
                moves = prefer_straight(prefer_more_next_move(moves))
                g.next_coord = moves[0]

def type_2_avoid_near_border():

    g.e.situation = "avoid point on the border"
    collision_points = g.e.collision_points
    avoid_point = g.e.avoid_points[0]
    avoid_point_next = [p for p in adj_cells(avoid_point) if p not in g.occupied_cells[1]]
    g.e.avoid_point_next = avoid_point_next
    g.next_coord = collision_points[0]
    if len(avoid_point_next) == 2:
        #intense calc point
        #let's say b is the farther point (to other_head), check if b has wayout
        b = [p for p in avoid_point_next if distance_pq(p, g.s.other_head) > 2][0]
        wayout_room = path_connected_set(b, g.occupied_cells[0]+[avoid_point])
        g.e.wayout_room = len(wayout_room)
        if g.e.wayout_room+1 >= (g.s.my_length+1)//2:
            g.next_coord = avoid_point
            return

    #take risk
    collision_food = [p for p in collision_points if p in g.food]
    if len(collision_food) == 1:
        g.e.situation = "avoid point no wayout, try no food point"
        #take chance by avoiding food
        one = [p for p in collision_points if p not in collision_food]
        g.next_coord = one[0]

    #take risk
    g.e.situation = "avoid point no wayout, take risk"
    g.next_coord = collision_points[0]

def type_2_collision():

    g.e.collision_type = 2
    common_adj = [p for p in adj_cells(g.s.my_head) if p in adj_cells(g.s.other_head)]
    collision_points = [p for p in common_adj if p not in g.occupied_cells[0]]
    g.e.collision_points = collision_points
    if len(collision_points) == 2:
        avoid_points = [p for p in g.e.allowed_moves if p not in collision_points]
        g.e.avoid_points = avoid_points
        g.e.avoid_points = avoid_points
        if len(avoid_points) != 0:
            avoid_point = avoid_points[0]
            if not on_border(avoid_point):
                g.next_coord = avoid_point
            else:
                if g.s.my_length < g.s.other_length:
                    type_2_avoid_near_border()
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
        collision_point = collision_points[0]
        if len(g.e.allowed_moves) == 3:
            #type 2, 1 collision point, 3 allowed moves
            if g.s.my_length < g.s.other_length:
                g.e.situation = "enemy is chasing"
                if distance_to_border(g.s.my_head) == (1,1) and g.s.my_length == 4:
                    g.e.situation = "special - enemy chasing me at corner and length 4"
                    moves = [a for a in g.e.allowed_moves if a != collision_point]
                    moves = prefer_turn(moves)
                    g.next_coord = moves[0]
                else:
                    if g.s.my_length+1 == g.s.other_length and g.next_coord in g.food and g.next_coord != collision_point:
                        g.e.situation = "enemy is chasing but we get food and length will be equal"
                    else:
                        moves = [a for a in g.e.allowed_moves if a != collision_point]
                        moves = prefer_more_next_move(moves)
                        if g.next_coord in g.food and g.next_coord in moves:
                            g.e.situation = "enemy is chasing but food is safe"
                        else:
                            default()
            else:
                #equal length
                #don't collide
                moves = [a for a in g.e.allowed_moves if a != collision_point]
                default(moves)
        else:
            #there is an avoid point beside the single collision point
            #take the avoid point
            avoid_point = [p for p in g.e.allowed_moves if p not in collision_points]
            avoid_point = avoid_point[0]
            g.next_coord = avoid_point

def type_1_collision():

    #type 1 collision with exactly one collision point - because heads are path connected
    common_adj = [p for p in adj_cells(g.s.my_head) if p in adj_cells(g.s.other_head)]
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
                moves = prefer_more_next_move(avoid_points)
                if g.next_coord not in moves:
                    g.e.situation = "type 1 collision head to head, prefer more next move and straight"
                    moves = prefer_straight(moves)
                    g.next_coord = moves[0]
                else:
                    g.e.situation = "type 1 collision head to head, but both avoid points are fine, keep previous calc"
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
                default(avoid_points)

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
                default(avoid_points)
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
                default(avoid_points)

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
                default(avoid_points)
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
                default(avoid_points)

    elif same_dir:
        #parallel same dir
        g.e.situation = "type 1 collision parallel same dir"
        avoid_points = [p for p in g.e.allowed_moves if p != collision_point]
        if g.s.my_length < g.s.other_length:
            if off_border_1(g.s.my_head):
                #my snake is 1-off border
                #go towards the border until 2 away
                if len([off_border_1(p) for p in adj_cells(g.s.my_head)]) == 2:
                    #go straight to 2-off border then take risk
                    g.next_coord = collision_point
                else:
                    #go straight
                    default(avoid_points)
            else:
                #my snake is not 1-off border
                if g.next_coord not in avoid_points:
                    default(avoid_points)
        else:
            #equal length
            pass
    else:
        #parallel opposite dir
        g.e.situation = "type 1 collision, parallel opposite dir"
        moves = [a for a in g.e.allowed_moves if a != collision_point]
        moves = prefer_more_next_move(moves)
        if g.next_coord not in moves[0]:
            g.next_coord = moves[0]

def killer_near_special_case_1():
    #my snake crawling on border
    #other snake distance is 6, and in the head crossing position, so dangerous
    #3 positions - direct crossing, and the two other positions near it

    if g.e.head_distance != 6:
        return False
    #no barrier in between, so dangerous
    if g.e.head_path_distance != 6:
        return False

    #must have two adj cells on border - not on corner
    nb = [a for a in adj_cells(g.s.my_head) if a != g.s.my_neck]
    #the crossing point is the one that is adjacent to both nb
    #must have one
    crossing = [p for a in nb for p in adj_cells(a) if all([is_adjacent(p, a) for a in nb])][0]

    dx,dy = [(x2-x1,y2-y1) for x1,y1 in [g.s.my_head] for x2,y2 in [crossing]][0]
    x1,y1 = g.s.my_head
    x2,y2 = crossing
    dx,dy = x2-x1, y2-y1

    #double crossing
    double_crossing = x2+dx, y2+dy
    if not pos_on_board(double_crossing):
        return False

    next_p = [p for p in adj_cells(double_crossing) if distance_pq(p, g.s.my_head) == 5]
    if len(next_p) == 0:
        return False

    if any([is_adjacent(g.s.other_head, p) for p in next_p]):
        return True
    
    return False

def killer_near():

    if g.s.my_length+1 == g.s.other_length and g.next_coord in g.food:
        g.e.situation = "get the food and will be equal length"
        return

    if on_border(g.s.my_head):
        if not on_border(g.s.my_neck):
            g.e.situation = "heading border and take a move farther to danger"
            move_rank = [(a, 
            #path_distance_pq is not accurate because snakes are moving
            #distance_pq is rigid
            min([(distance_pq(a, g.s.other_head)+ path_distance_pq(a, g.s.other_head))//2,
                distance_pq(a, g.s.other_head)+g.s.my_length ])
                          ) for a in g.e.allowed_moves]
            print(move_rank)
            moves = first_group(move_rank, reverse=True)
            g.next_coord = moves[0]
        else:
            #crawl on border
            g.e.situation = "crawling on border try come back"
            if g.e.head_path_distance == 4:
                g.e.situation = "danger imminent, come back immediately"
                #1 one border, 1 not
                moves = [a for a in g.e.allowed_moves if not on_border(a)]
                g.next_coord = moves[0]
            elif killer_near_special_case_1():
                g.e.situation = "kill near special case 1, danger imminent"
                moves = [a for a in g.e.allowed_moves if not on_border(a)]
                g.next_coord = moves[0]
            else:
                default()
        return

    if g.e.head_distance == 6:
        if on_border(g.next_coord) and g.next_coord in g.food:
            dx,dy = distance_to_border(g.next_coord)
            md = max([dx, dy])
            if md >= 3:
                g.e.situation = "head distance is 6 but next move is in the middle"
                return

    if g.e.head_path_distance >= 12:
        g.e.situation = "enemy path distance far, consider no danger"
        return 

    #don't go border
    g.e.situation = "killer near don't go on border"
    moves = [a for a in g.e.allowed_moves if not on_border(a)]
    if g.next_coord not in moves:
        moves = prefer_straight(prefer_more_next_move(moves))
        g.next_coord = moves[0]

def avoid_danger():
    #danger override
    d_danger = 6
    if g.e.head_distance <= d_danger:
        g.e.head_path_distance = path_distance_pq(g.s.my_head, g.s.other_head)
        if g.e.head_distance == 2:
            common_adj = [p for p in adj_cells(g.s.my_head) if p in adj_cells(g.s.other_head)]
            if len(common_adj) == 2:
                if g.e.head_path_distance == 2:
                    type_2_collision()
                else:
                    g.e.situation = "type 2 form but blocked"
            else:
                if g.e.head_path_distance == 2:
                    type_1_collision()
                else:
                    g.e.situation = "type 1 form but collision point is blocked"
                    if g.e.head_path_distance <= 8:
                        killer_near()
        else:
            if g.s.my_length < g.s.other_length:
                killer_near()
    else:
        #no danger
        g.e.situation = "distance is more than 6, no danger"

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
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 16, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(9, 7), (9, 6), (8, 6), (8, 5), (8, 4)]}, 'others': [{'name': 'Snakeformatika', 'health': 98, 'body': [(6, 6), (6, 7), (7, 7), (7, 6), (7, 5), (7, 4)]}], 'food': [(3, 5), (0, 0)]}, 'experiment': True, 'allowed_moves': [(10, 7), (8, 7), (9, 8)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: Y', 'env_lt8_enemy_far?: N', 'env_lt8_food_1?: N', 'env_food_near?: N', 'routine_move!'], 'time': '0.000s'}
    log = {'id': '0a97fd24-57d7-4b48-b71a-20efc2a3118e', 'turn': 64, 'me': {'name': 'mark_snake', 'health': 100, 
                'body': [(8, 10), (8, 9), (7, 9), (6, 9), (6, 8), (6, 7)]}, 'others': [{'name': 'Snakeformatika', 'health': 100, 
                'body': [(3, 9), (4, 9), (5, 9), (5, 8), (5, 7), (5, 6), (5, 5)]}], 'food': [(0, 7), (9, 7), (0, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 7), (5, 7), (6, 8)], 'other_allowed_moves': [(4, 6), (5, 7)], 'head_distance': 2, 'my_snake_bigger': False, 'food_near': [(8, 10), (6, 8), (3, 9), (0, 7), (9, 7)], 'food_good': [((8, 10), 5), ((6, 8), 1), ((3, 9), 5), ((0, 7), 6), ((9, 7), 3)], 'food_target': (6, 8), 'food_worth': [(3, 9)], 'head_path_distance': 2, 'collision_type': 2, 'situation': 'enemy is chasing', 'avoid_points': [(2, 3)], 'collision_food': [], 'avoid_point_next': [(4, 0), (2, 0)], 'wayout_room': 112}, 'next_coord': (6, 8), 'next_move': 'up', 'time': '0.003s'}
    log = {'id': 'cfe00a8a-a82f-4c0c-9233-a104e0b1b96c', 'turn': 14, 'me': {'name': 'mark_snake', 'health': 98, 'body': [(9, 9), (8, 9), (8, 8), (8, 7), (7, 7)]}, 'others': [{'name': 'Snakeformatika', 'health': 96, 'body': [(6, 6), (7, 6), (7, 5), (6, 5), (5, 5), (5, 6)]}], 'food': [(2, 4), (1, 0)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 9), (9, 10), (9, 8)], 'other_allowed_moves': [(5, 6), (6, 7)], 'head_distance': 6, 'my_snake_bigger': False, 'food_near': [], 'food_good': [((8, 8), 1)], 'food_target': (8, 8), 'food_worth': [(5, 5), (2, 6)], 'head_path_distance': 8, 'collision_type': 2, 'avoid_points': [(4, 7)], 'situation': 'enemy is chasing'}, 'next_coord': (10, 9), 'next_move': 'right', 'time': '0.000s'}
    log = {'id': '2310d184-a0c3-4a40-9425-aacf651eeb39', 'turn': 59, 'me': {'name': 'mark_snake', 'health': 99, 'body':     [(10, 9), (10, 10), (9, 10), (8, 10), (7, 10), (7, 9), (8, 9), (9, 9)]
}, 'others': [{'name': 'Snakeformatika', 'health': 89, 'body': [(9, 6), (9, 5), (10, 5), (10, 4), (10, 3), (9, 3), (9, 4), (8, 4), (8, 5)]}], 'food': [(5, 5), (5, 2), (7, 1)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 7), (8, 7), (9, 8)], 'other_allowed_moves': [(8, 7), (8, 5)], 'head_distance': 2, 'my_snake_bigger': False, 'food_near': [(10, 10)], 'food_good': [((10, 10), 4)], 'food_target': (10, 10), 'situation': 'enemy is chasing', 'food_worth': [(7, 5), (5, 2)], 'head_path_distance': 2, 'collision_type': 2, 'avoid_points': [(2, 10)], 'collision_food': [], 'avoid_point_next': [(3, 10), (1, 10)], 'wayout_room': 109}, 'next_coord': (9, 8), 'next_move': 'up', 'time': '0.003s'}
    [(10, 9), (10, 10), (9, 10), (8, 10), (7, 10), (7, 9), (8, 9), (9, 9)]
    log = {'id': '6d735788-e36c-4402-ba43-f9b37b92b32a', 'turn': 32, 'me': {'name': 'mark_snake', 'health': 70, 'body': [(9, 1), (8, 1), (7, 1), (6, 1)]}, 'others': [{'name': 'Snakeformatika', 'health': 78, 'body': [(8, 2), (7, 2), (6, 2), (5, 2), (4, 2), (3, 2)]}], 'food': [(10, 4), (9, 7), (1, 7), (6, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 1), (9, 2), (9, 0)], 'other_allowed_moves': [(9, 2), (8, 3)], 'head_distance': 2, 'my_snake_bigger': False, 'food_near': [(10, 4), (9, 7), (6, 3)], 'food_good': [((10, 4), 4), ((9, 7), 6)], 'food_target': (10, 4), 'situation': 'enemy is chasing', 'head_path_distance': 2, 'food_worth': [(1, 7)], 'collision_type': 2}, 'next_coord': (10, 1), 'next_move': 'right', 'time': '0.005s'}
    log = {'id': '6d735788-e36c-4402-ba43-f9b37b92b32a', 'turn': 33, 'me': {'name': 'mark_snake', 'health': 69, 'body': [(9, 0), (9, 1), (8, 1), (7, 1)]}, 'others': [{'name': 'Snakeformatika', 'health': 77, 'body': [(8, 3), (8, 2), (7, 2), (6, 2), (5, 2), (4, 2)]}], 'food': [(10, 4), (9, 7), (1, 7), (6, 3)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 2), (10, 0)], 'other_allowed_moves': [(9, 3), (7, 3), (8, 4)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(10, 4), (9, 7), (6, 3)], 'food_good': [((10, 4), 3)], 'food_target': (10, 4), 'situation': 'heading border and take a move farther to danger', 'head_path_distance': 4, 'food_worth': [(1, 7)], 'collision_type': 2}, 'next_coord': (10, 0), 'next_move': 'down', 'time': '0.003s'}
    log = {'id': '4efe89ab-d90a-4cae-8350-eabe182a52f1', 'turn': 31, 'me': {'name': 'mark_snake', 'health': 71, 'body': [(1, 2), (1, 1), (2, 1), (3, 1)]}, 'others': [{'name': 'Snakeformatika', 'health': 97, 'body': [(2, 3), (3, 3), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2)]}], 'food': [(1, 3), (4, 2), (8, 5)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(10, 1), (8, 1), (9, 0)], 'other_allowed_moves': [(8, 3), (6, 3), (7, 2)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(4, 2), (8, 5)], 'food_good': [], 'food_target': (8, 5), 'situation': "killer near don't go on border", 'food_worth': [(4, 2), (8, 5)], 'head_path_distance': 4, 'collision_type': 2}, 'next_coord': (8, 1), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': '6c0ea246-100f-4fdd-80d0-a39d9b6c992c', 'turn': 11, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(6, 5), (6, 4), (7, 4), (8, 4), (9, 4)]}, 'others': [{'name': 'Snakeformatika', 'health': 95, 'body': [(5, 4), (4, 4), (4, 3), (4, 2), (4, 1)]}], 'food': [(5, 5), (0, 7), (7, 7)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 4), (7, 5), (7, 3)], 'other_allowed_moves': [(5, 3), (3, 3), (4, 4)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(5, 5), (7, 7)], 'food_good': [((5, 5), 3), ((7, 7), 3)], 'food_target': (5, 5), 'situation': 'distance is more than 6, no danger', 'head_path_distance': 4, 'food_worth': [(5, 5)], 'collision_type': 2, 'collision_points': [(9, 6)], 'avoid_points': [], 'avoid_point_next': [(6, 10), (4, 10)], 'wayout_room': 112}, 'next_coord': (6, 4), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': '34c019e0-2f08-49e6-ae1a-749d6565ce64', 'turn': 114, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(0, 8), (1, 8), (2, 8), (2, 7), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (10, 7), (10, 8), (9, 8), (9, 9)]}, 'others': [{'name': 'Snakeformatika', 'health': 96, 'body': [(0, 2), (0, 3), (0, 4), (0, 5), (1, 5), (1, 4), (1, 3), (2, 3), (3, 3), (3, 2), (2, 2), (1, 2), (1, 1), (2, 1)]}], 'food': [(2, 5), (5, 0)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 7), (10, 6)], 'other_allowed_moves': [(1, 1), (2, 2)], 'head_distance': 14, 'my_snake_bigger': True, 'food_near': [], 'food_good': [((10, 8), 1)], 'food_target': (10, 8), 'situation': 'distance is more than 6, no danger', 'food_worth': [(4, 3)], 'head_path_distance': 8, 'collision_type': 2, 'collision_points': [(4, 3), (5, 2)], 'avoid_points': [(6, 3)], 'avoid_point_next': [(7, 10), (5, 10)], 'wayout_room': 110}, 'next_coord': (10, 6), 'next_move': 'down', 'time': '0.000s'}
    log = {'id': '3f537eab-c0f6-4187-ab90-a40e96738adb', 'turn': 35, 'me': {'name': 'mark_snake', 'health': 72, 'body': [(8, 1), (9, 1), (9, 2), (8, 2), (7, 2)]}, 'others': [{'name': 'Snakeformatika', 'health': 98, 'body': [(9, 4), (9, 3), (8, 3), (7, 3), (6, 3), (6, 4), (5, 4), (4, 4)]}], 'food': [(8, 0), (8, 6), (3, 5), (2, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 1), (8, 0)], 'other_allowed_moves': [(10, 4), (8, 4), (9, 5)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(8, 0), (8, 6)], 'food_good': [((8, 0), 1)], 'food_target': (8, 0), 'situation': "killer near don't go on border", 'food_worth': [(6, 4)], 'head_path_distance': 8, 'collision_type': 2, 'collision_points': [(9, 3)], 'avoid_points': [(2, 0)], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 111}, 'next_coord': (7, 1), 'next_move': 'left', 'time': '0.001s'}
    log = {'id': '3f537eab-c0f6-4187-ab90-a40e96738adb', 'turn': 36, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(8, 0), (8, 1), (9, 1), (9, 2), (8, 2)]}, 'others': [{'name': 'Snakeformatika', 'health': 97, 'body': [(8, 4), (9, 4), (9, 3), (8, 3), (7, 3), (6, 3), (6, 4), (5, 4)]}], 'food': [(8, 6), (3, 5), (2, 10), (6, 7)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 1), (7, 2), (7, 0)], 'other_allowed_moves': [(7, 4), (8, 5)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(8, 0), (8, 6), (6, 7)], 'food_good': [((8, 0), 2)], 'food_target': (8, 0), 'situation': "killer near don't go on border", 'food_worth': [(6, 4)], 'head_path_distance': 10, 'collision_type': 2, 'collision_points': [(9, 3)], 'avoid_points': [(2, 0)], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 111}, 'next_coord': (6, 1), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': '3f537eab-c0f6-4187-ab90-a40e96738adb', 'turn': 48, 'me': {'name': 'mark_snake', 'health': 59, 'body': [(1, 7), (1, 6), (1, 5), (1, 4), (1, 3)]}, 'others': [{'name': 'Snakeformatika', 'health': 100, 'body': [(3, 5), (3, 4), (2, 4), (2, 3), (3, 3), (3, 2), (4, 2), (4, 3), (4, 3)]}], 'food': [(8, 0), (8, 6), (2, 10), (6, 7), (2, 7), (3, 0)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(2, 7), (0, 7), (1, 8)], 'other_allowed_moves': [(4, 5), (2, 5), (3, 6)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(2, 10), (6, 7), (2, 7)], 'food_good': [((2, 10), 4), ((6, 7), 5), ((2, 7), 1)], 'food_target': (2, 7), 'situation': "killer near don't go on border", 'food_worth': [(6, 4)], 'head_path_distance': 4, 'collision_type': 2, 'collision_points': [(2, 5)], 'avoid_points': [(2, 0)], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 111}, 'next_coord': (1, 8), 'next_move': 'up', 'time': '0.002s'}
    log = {'id': '3f537eab-c0f6-4187-ab90-a40e96738adb', 'turn': 52, 'me': {'name': 'mark_snake', 'health': 55, 'body': [(3, 9), (2, 9), (1, 9), (1, 8), (1, 7)]}, 'others': [{'name': 'Snakeformatika', 'health': 96, 'body': [(1, 5), (2, 5), (2, 6), (3, 6), (3, 5), (3, 4), (2, 4), (2, 3), (3, 3)]}], 'food': [(8, 0), (8, 6), (2, 10), (6, 7), (2, 7), (3, 0)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(4, 9), (3, 10), (3, 8)], 'other_allowed_moves': [(0, 5), (1, 6), (1, 4)], 'head_distance': 6, 'my_snake_bigger': False, 'food_near': [(2, 10), (6, 7), (2, 7)], 'food_good': [((2, 10), 2), ((6, 7), 5), ((2, 7), 3)], 'food_target': (2, 10), 'situation': 'head distance is 6 but next move is in the middle', 'food_worth': [(6, 4)], 'head_path_distance': 6, 'collision_type': 2, 'collision_points': [(2, 5)], 'avoid_points': [(2, 0)], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 111}, 'next_coord': (3, 10), 'next_move': 'up', 'time': '0.004s'}
    log = {'id': '3f537eab-c0f6-4187-ab90-a40e96738adb', 'turn': 53, 'me': {'name': 'mark_snake', 'health': 54, 'body': [(3, 10), (3, 9), (2, 9), (1, 9), (1, 8)]}, 'others': [{'name': 'Snakeformatika', 'health': 95, 'body': [(0, 5), (1, 5), (2, 5), (2, 6), (3, 6), (3, 5), (3, 4), (2, 4), (2, 3)]}], 'food': [(8, 0), (8, 6), (2, 10), (6, 7), (2, 7), (3, 0)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(4, 10), (2, 10)], 'other_allowed_moves': [(0, 6), (0, 4)], 'head_distance': 8, 'my_snake_bigger': False, 'food_near': [(2, 10), (6, 7), (2, 7)], 'food_good': [((2, 10), 1), ((6, 7), 6)], 'food_target': (2, 10), 'situation': 'distance is more than 6, no danger', 'food_worth': [(6, 4)], 'head_path_distance': 6, 'collision_type': 2, 'collision_points': [(2, 5)], 'avoid_points': [(2, 0)], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 111}, 'next_coord': (2, 10), 'next_move': 'left', 'time': '0.002s'}
    log = {'id': '3f537eab-c0f6-4187-ab90-a40e96738adb', 'turn': 59, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(4, 9), (3, 9), (2, 9), (1, 9), (1, 10), (2, 10)]}, 'others': [{'name': 'Snakeformatika', 'health': 98, 'body': [(1, 8), (2, 8), (2, 7), (1, 7), (1, 6), (0, 6), (0, 5), (1, 5), (2, 5), (2, 6)]}], 'food': [(8, 0), (8, 6), (6, 7), (3, 0), (4, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(5, 9), (4, 10), (4, 8)], 'other_allowed_moves': [(0, 8)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(8, 6), (6, 7), (4, 10)], 'food_good': [((8, 6), 7), ((6, 7), 4), ((4, 10), 1)], 'food_target': (4, 10), 'situation': "killer near don't go on border", 'food_worth': [], 'head_path_distance': 999, 'collision_type': 2, 'collision_points': [(3, 8)], 'avoid_points': [(2, 0)], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 111}, 'next_coord': (5, 9), 'next_move': 'right', 'time': '0.002s'}
    log = {'id': '3f537eab-c0f6-4187-ab90-a40e96738adb', 'turn': 61, 'me': {'name': 'mark_snake', 'health': 93, 'body': [(5, 10), (5, 9), (4, 9), (3, 9), (2, 9), (1, 9)]}, 'others': [{'name': 'Snakeformatika', 'health': 96, 'body': [(0, 9), (0, 8), (1, 8), (2, 8), (2, 7), (1, 7), (1, 6), (0, 6), (0, 5), (1, 5)]}], 'food': [(8, 0), (8, 6), (6, 7), (3, 0), (4, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(6, 10), (4, 10)], 'other_allowed_moves': [(1, 9), (0, 10)], 'head_distance': 6, 'my_snake_bigger': False, 'food_near': [(8, 6), (6, 7), (4, 10)], 'food_good': [((8, 6), 7), ((6, 7), 4), ((4, 10), 1)], 'food_target': (4, 10), 'situation': 'heading border and take a move farther to danger', 'food_worth': [], 'head_path_distance': 6, 'collision_type': 2, 'collision_points': [(3, 8)], 'avoid_points': [(2, 0)], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 111}, 'next_coord': (6, 10), 'next_move': 'right', 'time': '0.003s'}
    log = {'id': '3f537eab-c0f6-4187-ab90-a40e96738adb', 'turn': 67, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(6, 7), (7, 7), (7, 8), (7, 9), (7, 10), (6, 10), (6, 10)]}, 'others': [{'name': 'Snakeformatika', 'health': 90, 'body': [(3, 10), (2, 10), (2, 9), (1, 9), (1, 10), (0, 10), (0, 9), (0, 8), (1, 8), (2, 8)]}], 'food': [(8, 0), (8, 6), (3, 0), (4, 10), (3, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(5, 7), (6, 8), (6, 6)], 'other_allowed_moves': [(4, 10), (3, 9)], 'head_distance': 6, 'my_snake_bigger': False, 'food_near': [(8, 6), (4, 10)], 'food_good': [((8, 6), 3)], 'food_target': (8, 6), 'situation': "killer near don't go on border", 'food_worth': [], 'head_path_distance': 6, 'collision_type': 2, 'collision_points': [(3, 8)], 'avoid_points': [(2, 0)], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 111}, 'next_coord': (5, 7), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': 'bef290a0-1ee4-41ae-9b0a-f46c4b51a96f', 'turn': 118, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(7, 9), (8, 9), (9, 9), (9, 8), (9, 7), (9, 6), (9, 5), (9, 4), (10, 4), (10, 3)]}, 'others': [{'name': 'Snakeformatika', 'health': 94, 'body': [(6, 8), (6, 7), (6, 6), (6, 5), (6, 4), (6, 3), (6, 2), (7, 2), (7, 1), (6, 1), (6, 0)]}], 'food': [(5, 10), (5, 5), (6, 10), (2, 5), (4, 6)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(8, 4), (9, 5), (9, 3)], 'other_allowed_moves': [(6, 2), (7, 3)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(5, 5), (6, 2), (9, 7)], 'food_good': [((5, 5), 5), ((9, 7), 3)], 'food_target': (9, 7), 'situation': "killer near don't go on border", 'head_path_distance': 4, 'food_worth': [(5, 8)], 'collision_type': 2, 'collision_points': [(8, 0)], 'avoid_points': [(2, 1)], 'avoid_point_next': [(3, 10), (1, 10)], 'wayout_room': 110}, 'next_coord': (9, 5), 'next_move': 'up', 'time': '0.004s'}
    log = {'id': 'ed3fd8d5-be5d-4cbe-ab71-8dc0df6cce81', 'turn': 57, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(3,0), (3,1), (4, 1), (5, 1), (6, 1)]}, 'others': [{'name': 'Snakeformatika', 'health': 88, 'body': [(6,3), (7,3), (8, 3), (9, 3), (9, 4), (9, 5), (8, 5)]}], 'food': [(4, 4), (10, 1), (0, 2), (1, 10), (2, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 1), (4, 2), (4, 0)], 'other_allowed_moves': [(7, 3), (8, 2)], 'head_distance': 6, 'my_snake_bigger': False, 'food_near': [(3, 0), (4, 4), (10, 1), (0, 2), (2, 2)], 'food_good': [((3, 0), 2), ((4, 4), 3), ((0, 2), 5), ((2, 2), 3)], 'food_target': (3, 0), 'situation': "killer near don't go on border", 'head_path_distance': 6, 'food_worth': [], 'collision_type': 2, 'collision_points': [(8, 10)], 'avoid_points': [(9, 9)], 'avoid_point_next': [(9, 10), (7, 10)], 'wayout_room': 110}, 'next_coord': (3, 1), 'next_move': 'left', 'time': '0.004s'}
    log = {'id': '2674b6e5-1157-4682-bd20-c96f5db08445', 'turn': 103, 'me': {'name': 'mark_snake', 'health': 97, 'body': [(6, 9), (5, 9), (5, 8), (5, 7), (6, 7), (7, 7), (8, 7), (8, 6), (8, 5), (7, 5), (7, 6), (6, 6), (5, 6), (4, 6), (3, 6), (3, 7), (3, 8), (3, 9)]}, 'others': [{'name': 'Snakeformatika', 'health': 93, 'body': [(7, 2), (6, 2), (6, 3), (7, 3), (7, 4), (8, 4), (8, 3)]}], 'food': [(5, 3), (10, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 9), (6, 10), (6, 8)], 'other_allowed_moves': [(8, 2), (7, 1)], 'head_distance': 8, 'my_snake_bigger': True, 'food_near': [(5, 3)], 'food_good': [], 'food_target': (5, 3), 'situation': 'distance is more than 6, no danger', 'food_worth': [(5, 3)], 'head_path_distance': 6}, 'next_coord': (6, 10), 'next_move': 'up', 'time': '0.007s'}
    log = {'id': '9c19495c-edce-4d8b-bbbf-50d8f5aa939d', 'turn': 119, 'me': {'name': 'mark_snake', 'health': 100, 'body': [(10, 7), (9, 7), (9, 6), (9, 5), (8, 5), (7, 5), (6, 5), (5, 5)]}, 'others': [{'name': 'Snakeformatika', 'health': 94, 'body': [(7, 2), (7, 3), (8, 3), (8, 4), (7, 4), (6, 4), (5, 4), (5, 3), (4, 3), (3, 3)]}], 'food': [(9, 2), (9, 1), (10, 4), (0, 9)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(8, 5), (7, 6), (7, 4)], 'other_allowed_moves': [(7, 4), (6, 3)], 'head_distance': 2, 'my_snake_bigger': False, 'food_near': [(9, 2), (9, 1), (10, 4), (10, 7)], 'food_good': [((9, 2), 5), ((9, 1), 6), ((10, 4), 4), ((10, 7), 5)], 'food_target': (10, 4), 'situation': 'enemy is chasing', 'food_worth': [(5, 4)], 'head_path_distance': 2, 'collision_type': 2, 'collision_points': [(7, 4)], 'avoid_points': [], 'avoid_point_next': [(3, 0), (1, 0)], 'wayout_room': 106}, 'next_coord': (8, 5), 'next_move': 'right', 'time': '0.007s'}
    log = {'id': '630210cc-b8b4-44bb-b3c9-90eb04a5cb9f', 'turn': 57, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(10, 3), (10, 2), (9, 2), (9, 1), (9, 0), (8, 0), (7, 0), (6, 0)]}, 'others': [{'name': 'Snakeformatika', 'health': 99, 'body': [(7, 6), (7, 7), (6, 7), (6, 6), (6, 5), (5, 5), (4, 5), (3, 5), (3, 4)]}], 'food': [(7, 8), (9, 7), (9, 9)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 3), (10, 4)], 'other_allowed_moves': [(8, 6), (7, 5)], 'head_distance': 6, 'my_snake_bigger': False, 'food_near': [(9, 7), (9, 9)], 'food_good': [], 'food_target': (9, 7), 'situation': 'crawling on border try come back', 'food_worth': [(9, 7), (9, 9)], 'head_path_distance': 6, 'collision_type': 2, 'collision_points': [(1, 5)], 'avoid_points': [(2, 4)], 'avoid_point_next': [(4, 10), (2, 10)], 'wayout_room': 112}, 'next_coord': (10, 4), 'next_move': 'up', 'time': '0.007s'}
    log = {'id': '37c7b941-0b36-4ef5-93f4-55dbc137f8e4', 'turn': 139, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (10, 8), (10, 7), (10, 6), (10, 5), (10, 4)]}, 'others': [{'name': 'Snakeformatika', 'health': 95, 'body': [(5, 8), (5, 7), (5, 6), (4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (5, 1), (5, 0)]}], 'food': [(0, 1), (4, 4), (0, 7), (1, 9), (3, 10), (1, 4), (2, 3), (1, 8), (2, 7)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(9, 6), (10, 7)], 'other_allowed_moves': [(5, 2), (3, 2), (4, 3)], 'head_distance': 10, 'my_snake_bigger': False, 'food_near': [(10, 9)], 'food_good': [((10, 9), 3)], 'situation': 'distance is more than 6, no danger', 'food_target': (10, 9), 'food_worth': [(5, 0), (4, 4), (2, 3)], 'head_path_distance': 2, 'collision_type': 2, 'collision_points': [(8, 0)], 'avoid_points': [(7, 10)], 'avoid_point_next': [(8, 10), (6, 10)], 'wayout_room': 100}, 'next_coord': (10, 7), 'next_move': 'up', 'time': '0.003s'}
    log = {'id': 'd293c05a-ebd0-453e-b486-40b49cabd7c9', 'turn': 117, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (10, 7), (10, 6), (10, 5)]}, 'others': [{'name': 'Snakeformatika', 'health': 91, 'body': [(5, 6), (6, 6), (7, 6), (7, 5), (7, 4), (7, 3), (7, 2), (7, 1), (6, 1), (6, 0)]}], 'food': [(7, 0), (1, 6), (1, 4), (2, 1), (0, 1), (2, 5), (3, 1), (5, 7), (6, 10)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(7, 8), (8, 9), (8, 7)], 'other_allowed_moves': [(8, 5), (6, 5), (7, 6)], 'head_distance': 4, 'my_snake_bigger': False, 'food_near': [(5, 7), (6, 10)], 'food_good': [((5, 7), 4), ((6, 10), 4)], 'situation': "killer near don't go on border", 'food_target': (5, 7), 'food_worth': [], 'head_path_distance': 4, 'collision_type': 2, 'collision_points': [(6, 1)], 'avoid_points': [(7, 5)], 'avoid_point_next': [(10, 9), (10, 7)], 'wayout_room': 107}, 'next_coord': (7, 8), 'next_move': 'left', 'time': '0.005s'}
    log = {'id': 'e2cfb4c2-677a-46e3-bcc5-cd65d7ba2e2d', 'turn': 15, 'me': {'name': 'mark_snake', 'health': 97, 'body': [(1, 2), (2, 2), (3, 2), (4, 2), (4, 1)]}, 'others': [{'name': 'Snakeformatika', 'health': 95, 'body': [(2, 3), (3, 3), (4, 3), (4, 4), (4, 5), (5, 5)]}], 'food': [(0, 2)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(0, 2), (1, 3), (1, 1)], 'other_allowed_moves': [(1, 3), (2, 4)], 'head_distance': 2, 'my_snake_bigger': False, 'food_near': [(0, 2)], 'food_good': [((0, 2), 1)], 'situation': 'enemy is chasing', 'food_target': (0, 2), 'head_path_distance': 2, 'collision_type': 2, 'collision_points': [(1, 3)], 'avoid_points': [(5, 2)], 'food_worth': []}, 'next_coord': (1, 1), 'next_move': 'down', 'time': '0.002s'}
    log = {'id': '8a5cca89-1672-429a-844f-06ace099ad8b', 'turn': 62, 'me': {'name': 'mark_snake', 'health': 89, 'body': [(2, 8), (1, 8), (0, 8), (0, 9), (0, 10), (1, 10), (2, 10)]}, 'others': [{'name': 'Snakeformatika', 'health': 91, 'body': [(4, 8), (5, 8), (6, 8), (6, 9), (5, 9), (5, 10), (4, 10), (4, 9)]}], 'food': [(2, 0), (1, 0), (2, 6), (10, 0), (3, 3), (7, 10), (7, 4)], 'experiment': True, 'decision_support': {'n_other': 1, 'allowed_moves': [(3, 8), (2, 9), (2, 7)], 'other_allowed_moves': [(3, 8), (4, 9), (4, 7)], 'head_distance': 2, 'my_snake_bigger': False, 'food_near': [(2, 6), (3, 3), (7, 10)], 'food_good': [((2, 6), 2), ((3, 3), 6)], 'situation': 'go to food', 'food_target': (2, 6), 'head_path_distance': 2, 'collision_type': 2, 'collision_points': [(4, 10)], 'food_worth': [], 'avoid_points': [(3, 10)], 'avoid_point_next': [(4, 10), (2, 10)], 'wayout_room': 107}, 'next_coord': (2, 9), 'next_move': 'up', 'time': '0.003s'}





    game_state = init_from_log(log)
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()

