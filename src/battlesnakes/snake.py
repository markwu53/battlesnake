import typing
import time

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "markwu2025",  # TODO: Your Battlesnake Username
        "color": "#FF0000",  # TODO: Choose color
        "head": "all-seeing",  # TODO: Choose head
        "tail": "flake",  # TODO: Choose tail
    }

def get_up_coord(head_coord: dict[str, int]) -> dict[str, int]:
    if "x" not in head_coord.keys() or "y" not in head_coord.keys():
        raise ValueError(f"head_coord must have both 'x' and 'y' keys: {head_coord}")

    return {"x": head_coord["x"], "y": head_coord["y"] + 1}

def get_direction_coord(direction: str, head_coord: dict[str, int]) -> dict[str, int]:
    if "x" not in head_coord.keys() or "y" not in head_coord.keys():
        raise ValueError(f"head_coord must have both 'x' and 'y' keys: {head_coord}")

    match direction:
        case "up":
            return {"x": head_coord["x"], "y": head_coord["y"] + 1}
        case "down":
            return {"x": head_coord["x"], "y": head_coord["y"] - 1}
        case "left":
            return {"x": head_coord["x"] - 1, "y": head_coord["y"]}
        case "right":
            return {"x": head_coord["x"] + 1, "y": head_coord["y"]}

    raise ValueError(f"invalid direction: {direction}")

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


#this gives me #20 score 8603 on 6/3/2025
def move(game_state: typing.Dict) -> typing.Dict:

    def main():

        game_state["start_time"] = time.time()

        #do this first
        save_lean_board()
        save_occupied_cells()

        #gather information, provide suggestions
        allowed_move()
        routine_move()
        avoid_danger()
        find_food()
        try_kill()

        #combine information and suggestions and make a decision
        best_choice()

        game_state["end_time"] = time.time()

        game_state["next_move"] = get_next_move(get_my_head(), game_state["next_head_coord"])

        logging()


    def save_lean_board():
        me = game_state["you"]
        me = {
            "name": me["name"],
            "health": me["health"],
            "body": get_coord(me["body"]),
        }
        others = [
            {
                "name": snake["name"],
                "health": snake["health"],
                "body": get_coord(snake["body"]),
            } for snake in game_state["board"]["snakes"]
        ]
        others = [snake for snake in others if snake["body"][0] != me["body"][0]]
        game_state["me"] = me
        game_state["others"] = others
        game_state["snakes"] = [me, *others]
        game_state["food"] = get_coord(game_state["board"]["food"])

    def save_occupied_cells():

        def occupied_cells(step):
            #not including head
            #assuming no die
            #assuming no eating food
            #if eating food it will be more
            snakes = game_state["snakes"]
            sbody = []
            for s in snakes:
                body = s["body"]
                if s["health"] == 100:
                    #eat food, tail will not move in the next step
                    body = body + [body[-1]]
                sbody.append(body[:-step])
            cells = [c for s in sbody for c in s]
            return cells

        game_state["occupied_cells"] = [
            occupied_cells(step)
            for step in [1,2,3,4,5]
        ]

    def allowed_move():

        def permissible_nstep(head, n):
            paths = [[head]]
            for step in range(1, n+1):
                occupied = game_state["occupied_cells"][step-1]
                paths = [ npath 
                        for path in paths 
                        for npath in [path+[p] for p in adj_cells(path[-1]) 
                                if p not in occupied and p not in path] ]
            result = list(set([path[1] for path in paths]))
            return result


        head = get_my_head()
        allowed = permissible_nstep(head, 5)
        allowed_1 = permissible_nstep(head, 1)
        game_state["allowed_move"] = allowed
        game_state["allowed_move_1"] = allowed_1

    def routine_move():
        #sophistacated routine move is not very useful now
        #replace with simple go straight
        #it can go off-board, must be checked by allowed moves
        move = go_straight()
        game_state["routine_move"] = move

    def avoid_danger():
        game_state["avoid_danger"] = []

        max_step = 3
        if len(game_state["snakes"]) <=3:
            max_step = 4

        def grow_path(head, steps=max_step):
            paths = [[head]]
            for step in range(steps):
                paths = [path+[nhead] 
                        for path in paths
                        for head in [path[-1]]
                        for nhead in adj_cells(head)
                        if nhead not in game_state["occupied_cells"][step]
                        and nhead not in path
                        ]
            return paths

        for snake in game_state["snakes"]:
            snake["paths"] = grow_path(snake["body"][0])

        my_snake = game_state["me"]

        def danger_rank(apath, safer):
            length = len(apath)
            if apath[-1] in [
                path[length-1] 
                for snake in game_state["others"]
                for path in snake["paths"]
                if (len(snake["body"]) >= len(my_snake["body"])
                    if safer
                    else len(snake["body"]) > len(my_snake["body"])
                )
            ]:
                return length-1
            if length == max_step+1:
                #no danger
                return 99
            return max([danger_rank(apath+[nhead], safer)
                for nhead in set([
                    path[length]
                    for path in my_snake["paths"]
                    if tuple(path[:length]) == tuple(apath)
                ])])
        
        game_state["avoid_danger"].append([
            [(apath[1], danger_rank(list(apath), safer=True))
                    for apath in set([tuple(path[:2]) for path in my_snake["paths"]])],
            [(apath[1], danger_rank(list(apath), safer=False))
                    for apath in set([tuple(path[:2]) for path in my_snake["paths"]])],
        ])


    def find_food():

        def find_food_condition() -> bool:
            snakes = game_state["others"]
            if len(snakes) >= 2 and game_state["you"]["length"] < 20: return True
            if len(snakes) >= 3 and game_state["you"]["health"] < 60: return True
            if len(snakes) >= 2 and game_state["you"]["health"] < 40: return True
            if len(snakes) == 1 and game_state["you"]["length"] < 40: return True
            if len(snakes) == 1 and game_state["you"]["health"] < 20: return True
            if len(snakes) == 0: return True
            return False

        def food_move():
            snakes = game_state["others"]
            snake_heads = [snake["body"][0] for snake in snakes]
            my_head = get_my_head()
            food_target = game_state["food"]
            food_target = [p for p in food_target 
                           if all([path_distance_pq(my_head, p) < path_distance_pq(snake_head, p) 
                                   for snake_head in snake_heads ])]
            if len(food_target) == 0:
                return
            food_target = sorted([(path_distance_pq(my_head, p), p) for p in food_target])
            _, target = food_target[0]
            my_body = game_state["me"]["body"]
            result = shortest_path_move(my_head, target)
            if len(result) == 0:
                return
            if game_state["turn"] > 3:
                #assumption: before turn 3 the body is fold, no direction
                result = [(0 if get_adjacent_dir(my_head, move) == get_adjacent_dir(my_body[1], my_head) else 1, move) for move in result]
                result = sorted(result)
                result = [move for rank, move in result]
            game_state["find_food"].append(result)

        game_state["find_food"] = []

        if find_food_condition():
            food_move()

    def try_kill():
        game_state["try_kill"] = []

        #kill in any case
        #if len(game_state["board"]["snakes"]) != 2: return

        if len(game_state["me"]["body"]) < 4:
            return

        my_snake = game_state["me"]

        def entering_trap(snake):
            #any part of the other snake is on border
            #one of my body cell is adjacent to the other snake that part at off-border position
            #they moving in the same dir
            for i, ic in enumerate(snake["body"]):
                for j, jc in enumerate(my_snake["body"]):
                    if 1 <= j < len(my_snake["body"])-1 and i < len(snake["body"])-2:
                        if on_border(ic) and is_adjacent(ic, jc) and not on_border(jc):
                            if get_adjacent_dir(jc, my_snake["body"][j-1]) == get_adjacent_dir(snake["body"][i+1], ic):
                                return True
            return False

        def kill_action_performed():
            return any([on_border(cell) for cell in my_snake["body"]])

        def crawl_path_len(head, neck, q):
            if not on_border(head):
                return 999
            if not on_border(neck):
                return 999
            if not on_border(q):
                return 999
            path = []
            while True:
                nhead = [p for p in adj_cells(head) if p != neck and on_border(p)][0]
                path.append(nhead)
                if nhead == q:
                    break
                neck = head
                head = nhead
            return len(path)


        if not any([entering_trap(snake) for snake in game_state["others"]]):
            return

        if kill_action_performed():
            return

        for snake in game_state["others"]:
            if entering_trap(snake):
                break
        
        game_state["entered_trap"] = snake["name"]
        #assume only one
        #go to the closest kill position
        #1. It's on border
        #2. It's closer to me than the snake I'm trying to kill
        #3. It has shortest path to the snake head so that fastest kill
        width = game_state["board"]["width"]
        height = game_state["board"]["height"]
        my_head = my_snake["body"][0]
        snake_head = snake["body"][0]
        snake_neck = snake["body"][1]
        kill_position = [(x,y) for x in range(width) for y in range(height)]
        kill_position = [p for p in kill_position if on_border(p)]
        kill_position = [p for p in kill_position if distance_pq(p, my_head) < distance_pq(p, snake_head)]
        kill_position = [p for p in kill_position if crawl_path_len(snake_head, snake_neck, p) <= (width+height)//2]
        if len(kill_position) == 0:
            return

        #nearest to the other so fastest kill
        #min_distance = min([distance_pq(p, snake_head) for p in kill_position])
        #kill_position = [p for p in kill_position if distance_pq(p, snake_head) == min_distance]

        #nearest to me so fastest action
        min_distance = min([distance_pq(p, my_head) for p in kill_position])
        if min_distance >= len(my_snake["body"]) //2:
            #kill position too far - abort
            return

        kill_position = [p for p in kill_position if distance_pq(p, my_head) == min_distance]

        #may have more than 1, anyone is good
        target_kill_position = kill_position[0]
        game_state["target_kill_position"] = kill_position
        #route to get there
        if is_adjacent(my_head, target_kill_position):
            game_state["try_kill"].append([target_kill_position])
            return
        #must go to target_kill_position in a perpendicular way
        next_to_target = [p for p in adj_cells(target_kill_position) if not on_border(p)][0]
        if is_adjacent(my_head, next_to_target):
            game_state["try_kill"].append([next_to_target])
            return
        suggest = [p for p in adj_cells(my_head) if distance_pq(p, next_to_target) == distance_pq(my_head, next_to_target)-1]

        #suggest = [p for p in adj_cells(get_my_head()) if on_border(p)]
        game_state["try_kill"].append(suggest)
       
    def best_choice_avoid_danger():

        if len(game_state["avoid_danger"]) == 0:
            return

        avoid_danger_1, avoid_danger_2 = game_state["avoid_danger"][0]
        #avoid_danger_1 consider dangers coming from all opponents snakes that have length greater or equal to 
        #avoid_danger_2 only consider length greater than mine


        def is_a_trap(head, p):
            #p has only one allowed move
            #besides head, p is blocked in two directions
            #each direction is either a border
            #or a cell of snake body that moves in the same direction
            if not is_adjacent(head, p):
                return False
            
            snakes = game_state["snakes"]

            if on_border(p):
                if not on_border(head):
                    return False
                for snake in snakes:
                    for i,ic in enumerate(snake["body"]):
                        if 1<= i < len(snake["body"])-1:
                            if is_adjacent(ic, p) and not on_border(ic):
                                if get_adjacent_dir(head, p) == get_adjacent_dir(ic, snake["body"][i-1]):
                                    return True
                return False
            else:
                #p has 4 adjacent cells
                #one of it is current head
                #two others are occupied
                #the last one is the only direction to move
                #this is a trap signal
                abc = [q for q in adj_cells(p) if q != head]
                c = [q for q in abc if q not in game_state["occupied_cells"][1]]
                if len(c) != 1:
                    return False
                c = c[0]
                for a in [q for q in abc if q != c]:
                    for snake in snakes:
                        for i,ic in enumerate(snake["body"]):
                            if 1 <= i < len(snake["body"])-2:
                                if ic == a:
                                    if get_adjacent_dir(a, snake["body"][i-1]) == get_adjacent_dir(p, c):
                                        return True
                return False


        def avoid_trap():
            my_head = get_my_head()
            traps = [a for a in game_state["allowed_move_1"] if is_a_trap(my_head, a)]
            game_state["log_traps"] = traps
            for i in range(len(avoid_danger_1)):
                move, rank = avoid_danger_1[i]
                if move in traps:
                    if rank > 5:
                        avoid_danger_1[i] = (move, 5)
            for i in range(len(avoid_danger_2)):
                move, rank = avoid_danger_2[i]
                if move in traps:
                    if rank > 5:
                        avoid_danger_2[i] = (move, 5)

        def avoid_dead_end():
            connected = set([p for snake in game_state["snakes"] for p in path_connected(snake["body"][-1])])
            dead_ends = [a for a in game_state["allowed_move_1"] if a not in connected]
            game_state["log_dead_end"] = dead_ends
            for i in range(len(avoid_danger_1)):
                move, rank = avoid_danger_1[i]
                if move in dead_ends:
                    if rank > 6:
                        avoid_danger_1[i] = (move, 6)
            for i in range(len(avoid_danger_2)):
                move, rank = avoid_danger_2[i]
                if move in dead_ends:
                    if rank > 6:
                        avoid_danger_2[i] = (move, 6)

        def case_3_condition():
            #don't crawl on border
            #whenever there is a chance, go back to off-border
            #this is taken care of already by avoid danger default process
            my_head = get_my_head()



        def go_straight_when_chased():
            #go straight when being chased
            if not (
                1 == 1
                and len([move for move, rank in avoid_danger_2 if rank == 99]) == 2
                and len([move for move, rank in avoid_danger_2 if rank == 1]) == 1
            ):
                return False

            my_head = get_my_head()
            a,b = [move for move, rank in avoid_danger_2 if rank == 99]
            if (get_adjacent_dir(my_head, a) == get_adjacent_dir(my_head, b)
                or get_adjacent_dir(a, my_head) == get_adjacent_dir(my_head, b)):
                return False
            my_head = get_my_head()
            move_danger_rank_1 = [move for move, rank in avoid_danger_2 if rank == 1][0]
            move_keep = [move for move, rank in avoid_danger_2 if rank == 99
                and get_adjacent_dir(my_head, move_danger_rank_1) != get_adjacent_dir(move, my_head)][0]
            move_opposite = [move for move, rank in avoid_danger_2 if rank == 99
                and get_adjacent_dir(my_head, move_danger_rank_1) == get_adjacent_dir(move, my_head)][0]
            if on_border(move_keep) and not on_border(move_opposite):
                suggest = move_opposite
            else:
                suggest = move_keep
            if suggest in game_state["allowed_move"]:
                game_state["next_head_coord"] = suggest
                return True

            return False

        def avoid_danger_default_process():

            result = [move for move, rank in avoid_danger_1 if rank == 99]
            if len(result) == 0:
                result = [move for move, rank in avoid_danger_2 if rank == 99]
            if len(result) == 0:
                result = first_group(avoid_danger_2, reverse=True)

            #prefer off-border when killer near
            def killer_near():
                my_head = get_my_head()
                return len([snake_head
                    for snake in game_state["others"]
                    for snake_head in [snake["body"][0]]
                    if len(snake["body"]) >= len(game_state["me"]["body"])
                        and path_distance_pq(my_head, snake_head) <= 4
                    ]) != 0

            if (killer_near()
                    or len(game_state["find_food"]) == 0):
                result = [(move, 1 if on_border(move) else 0) for move in result]
                result = first_group(result, reverse=False)
            result = [move for move in result if move in game_state["allowed_move"]]
            if len(result) != 0:
                if game_state["next_head_coord"] not in result:
                    game_state["next_head_coord"] = result[0]


        if go_straight_when_chased(): return

        #more special cases here:


        #avoid_trap function modifies avoid_danger suggest
        avoid_trap()
        avoid_dead_end()

        #avoid danger default process
        avoid_danger_default_process()


    def path_distance_pq(p, q):
        occuppied = game_state["occupied_cells"][0]
        connected = [set([p])]
        layer = set([q for q in adj_cells(p) if q not in occuppied])
        while len(layer) != 0:
            connected.append(layer)
            layer = set([x for q in layer for x in adj_cells(q) if x not in occuppied and x not in connected[-2]])
        for i,layer in enumerate(connected):
            if q in layer:
                return i
        return 999

    def path_connected(p):
        occuppied = game_state["occupied_cells"][0]
        #remove p from occupied
        occuppied = [q for q in occuppied if q != p]
        layers = [set([p])]
        layer = set([q for q in adj_cells(p) if q not in occuppied])
        while len(layer) != 0:
            layers.append(layer)
            layer = set([x for q in layer for x in adj_cells(q) if x not in occuppied and x not in layers[-2]])
        return set([q for layer in layers for q in layer])

    def path_connected_layers(p):
        occuppied = game_state["occupied_cells"][0]
        #remove p from occupied
        occuppied = [q for q in occuppied if q != p]
        layers = [set([p])]
        layer = set([q for q in adj_cells(p) if q not in occuppied])
        while len(layer) != 0:
            layers.append(layer)
            layer = set([x for q in layer for x in adj_cells(q) if x not in occuppied and x not in layers[-2]])
        return layers

    def go_straight():
        body = get_coord(game_state["you"]["body"])
        x0,y0 = body[0]
        x1,y1 = body[1]
        x,y = x1-x0, y1-y0
        x,y = -x, -y
        return (x0+x, y0+y)

    def shortest_path_move(p, q):
        if is_adjacent(p, q):
            return [q]
        if q in path_connected(p):
            dist = path_distance_pq(p, q)
            layers = path_connected_layers(p)
            if len(layers) > 1:
                result = [x for x in layers[1] if path_distance_pq(x, q) == dist-1]
                return result
        return []

    def chasing_my_tail():
        my_body = game_state["me"]["body"]
        my_head = my_body[0]
        my_neck = my_body[1]
        result = shortest_path_move(my_body[0], my_body[-1])
        result = [(0 if get_adjacent_dir(my_head, move) == get_adjacent_dir(my_neck, my_head) else 1, move) for move in result]
        result = sorted(result)
        result = [move for rank, move in result]
        return result

    def chasing_other_tail(snake):
        my_body = game_state["me"]["body"]
        my_head = my_body[0]
        my_neck = my_body[1]
        snake_body = snake["body"]
        snake_tail = snake_body[-1]
        target = snake_tail
        tail_next = [p for p in adj_cells(snake_tail) if p not in my_body and p not in snake_body]
        if len(tail_next) != 0:
            target = tail_next[0]
        result = shortest_path_move(my_head, target)
        result = [(0 if get_adjacent_dir(my_head, move) == get_adjacent_dir(my_neck, my_head) else 1, move) for move in result]
        result = sorted(result)
        result = [move for rank, move in result]
        return result

    def chasing_tail():
        #this is only used in 1v1 case
        result_me = chasing_my_tail()
        result_other = chasing_other_tail(game_state["others"][0])
        if len(result_other) != 0:
            return result_other
        return result_me

    def best_choice():

        #lower priority first, higher priority will override lower priority

        #routine move always exists and set as default
        if len(game_state["board"]["snakes"]) >=3:
            game_state["next_head_coord"] = go_straight()
            if len(game_state["you"]["body"]) >= 15:
                result = chasing_my_tail()
                if len(result) != 0:
                    game_state["next_head_coord"] = result[0]
        elif len(game_state["board"]["snakes"]) ==2:
            #1v1 mode
            #game_state["next_head_coord"] = game_state["routine_move"]
            game_state["next_head_coord"] = go_straight()
            result = chasing_tail()
            if len(result) != 0:
                game_state["next_head_coord"] = result[0]
        else:
            #self
            game_state["next_head_coord"] = game_state["routine_move"]
            result = chasing_my_tail()
            if len(result) != 0:
                game_state["next_head_coord"] = result[0]


        if len(game_state["allowed_move"]) == 0:
            #most strict allowed move empty
            #immediate allowed move may still have some
            if len(game_state["allowed_move_1"]) != 0:
                #use the first of the allowed move
                game_state["next_head_coord"] = game_state["allowed_move_1"][0]
            return

        #set to the first of the allowed moves, then let other considerations override it

        if game_state["next_head_coord"] not in game_state["allowed_move"]:
            game_state["next_head_coord"] = game_state["allowed_move"][0]

        if len(game_state["find_food"]) != 0:
            suggest = game_state["find_food"][0]
            if len(suggest) != 0:
                food = suggest[0]
                if food in game_state["allowed_move"]:
                    game_state["next_head_coord"] = food

        #do not check off-border anymore
        #instead let attractor boxes move the snake off-border

        #new avoid danger
        best_choice_avoid_danger()

        #try kill
        if len(game_state["try_kill"]) != 0:
            #try kill is activated
            result = game_state["try_kill"][0]

            #no danger in 3 steps
            result = [move for move in result if move in game_state["allowed_move"]]
            if len(result) != 0:
                if game_state["next_head_coord"] not in result:
                    game_state["next_head_coord"] = result[0]


#############################################
# utility functions
#############################################

    def get_adjacent_dir(p: typing.Tuple, q: typing.Tuple) -> str:
        assert(is_adjacent(p, q))
        x,y = p
        nx,ny = q
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        return get_adjacent_dir(head_coord, next_head_coord)

    def pos_on_board(pos: typing.Tuple) -> bool:
        x,y = pos
        if x < 0:
            return False
        if y < 0:
            return False
        if x >= game_state["board"]["width"]:
            return False
        if y >= game_state["board"]["height"]:
            return False
        return True

    def adj_cells(pos: typing.Tuple) -> typing.List:
        x,y = pos
        moves = [(1,0), (-1,0), (0,1), (0,-1)]
        npos = [(a+x,b+y) for a,b in moves]
        npos = [p for p in npos if pos_on_board(p)]
        return npos

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

    def on_border(coord: typing.Tuple) -> bool:
        x,y = coord
        if x == 0 or x == game_state["board"]["width"]-1:
            return True
        if y == 0 or y == game_state["board"]["height"]-1:
            return True
        return False

    def distance_pq(p: typing.Tuple, q: typing.Tuple) -> int:
        x1,y1 = p
        x2,y2 = q
        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def is_adjacent(p1: typing.Tuple, p2: typing.Tuple) -> bool:
        return distance_pq(p1, p2) == 1

    def get_my_head() -> typing.Tuple:
        return game_state["me"]["body"][0]

    def get_my_tail() -> typing.Tuple:
        return game_state["me"]["body"][-1]

    def get_coord(items: typing.List) -> typing.List:
        return [(c["x"], c["y"]) for c in items]

    def logging():

        #logging
        log_move = game_state["next_move"]
        log_routine_move = game_state["routine_move"]
        log_allowed_move = game_state["allowed_move"]
        log_avoid_danger = game_state["avoid_danger"]
        log_time_diff = game_state["end_time"] - game_state["start_time"]
        log_time_diff = f"time: {log_time_diff:.3f}s"
        log_find_food = game_state["find_food"]
        log_try_kill = game_state["try_kill"]
        log_target_kill_pos = game_state.get("target_kill_position", [])
        log_entered_trap = game_state.get("entered_trap", "")

        log_board = {
            "id": game_state["game"]["id"],
            "turn": game_state["turn"],
            "me": {
                "name": game_state["me"]["name"],
                "length": len(game_state["me"]["body"]),
                "head": game_state["me"]["body"][0],
                "health": game_state["me"]["health"],
            },
            "others": [ {
                "name": snake["name"],
                "length": len(snake["body"]),
                "head": snake["body"][0],
                "health": snake["health"],
            } for snake in game_state["others"] ],
        } 
        log_traps = game_state.get("log_traps", [])
        log_dead_end = game_state.get("log_dead_end", [])

        log_text = ", ".join([
            f"board: {log_board}",
            f"move: {log_move}",
            f"routine_move: {log_routine_move}",
            f"avoid_danger: {log_avoid_danger}",
            f"allowed_move: {log_allowed_move}",
            f"find_food: {log_find_food}",
            f"try_kill: {log_try_kill}, target: {log_target_kill_pos}, entered_trap: {log_entered_trap}",
            f"trap: {log_traps}",
            f"dead_end: {log_dead_end}",
            log_time_diff,
        ])

        print(log_text)

#############################################
# end of utility functions
#############################################


    #main
    main()

    return {"move": game_state["next_move"]}

