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

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


#this gives me #20 score 8603 on 6/3/2025
#def move(game_state: typing.Dict) -> typing.Dict:
def special_experimenting_code(game_state):

    def main():

        game_state["start_time"] = time.time()

        #do this first
        #do in outside
        #initialization()

        #gather information, provide suggestions
        allowed_move()
        routine_move()
        collision_ranking()
        trap_ranking()
        dead_end_ranking()
        #tail_connect_ranking()
        killer_near_watching()
        crowded_ranking()
        food_ranking()
        try_kill()

        #combine information and suggestions and make a decision
        #best_choice()
        decision_making()

        game_state["end_time"] = time.time()

        game_state["next_move"] = get_next_move(get_my_head(), game_state["next_head_coord"])

        logging()


    def initialization():
        game_state["logging"] = {}

        #lean board
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

        #estimated 5-step occupied cells
        game_state["occupied_cells"] = [
            occupied_cells(step)
            for step in [1,2,3,4,5]
        ]

    def allowed_move():
        occupied = game_state["occupied_cells"][0]
        allowed = [p for p in adj_cells(game_state["me"]["body"][0]) if p not in occupied]
        game_state["allowed_move"] = allowed
        game_state["danger_ranking"] = {p:{} for p in allowed}

    def routine_move():
        #sophistacated routine move is not very useful now
        #replace with simple go straight
        #it can go off-board, must be checked by allowed moves
        move = go_straight()
        game_state["routine_move"] = move

    def collision_ranking():
        #game_state["danger_ranking"] is now a dict, initialized in allowed move
        #game_state["danger_ranking"] = []

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

        def collision_rank(apath, safer):
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
            return max([collision_rank(apath+[nhead], safer)
                for nhead in set([
                    path[length]
                    for path in my_snake["paths"]
                    if tuple(path[:length]) == tuple(apath)
                ])])
        
        collision_ranking_1 = [(apath[1], collision_rank(list(apath), safer=True))
                    for apath in set([tuple(path[:2]) for path in my_snake["paths"]])]
        collision_ranking_2 = [(apath[1], collision_rank(list(apath), safer=False))
                    for apath in set([tuple(path[:2]) for path in my_snake["paths"]])]

        for p,rank in collision_ranking_1:
            game_state["danger_ranking"][p]["collision_1"] = rank
        for p,rank in collision_ranking_2:
            game_state["danger_ranking"][p]["collision_2"] = rank


    def food_ranking():
        game_state["food_ranking"] = [(p, 
                 path_distance_pq(game_state["me"]["body"][0], p),
                 [(path_distance_pq(snake["body"][0], p), len(snake["body"])) for snake in game_state["others"]],
                 ) for p in game_state["food"]]


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

    def trap_ranking():

        def is_a_trap(p):
            #p has only one allowed move
            #besides head, p is blocked in two directions
            #each direction is either a border
            #or a cell of snake body that moves in the same direction
            snakes = game_state["snakes"]
            head = game_state["me"]["body"][0]

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

        for p in game_state["allowed_move"]:
            game_state["danger_ranking"][p]["trap"] = is_a_trap(p)

    def dead_end_ranking():

        def dead_end_rank(p):
            connected = path_connected(p)
            return len(connected)

        for p in game_state["allowed_move"]:
            game_state["danger_ranking"][p]["dead_end"] = dead_end_rank(p)

    def tail_connect_ranking():
        my_head = get_my_head()
        my_tail = get_my_tail()
        for p in game_state["allowed_move"]:
            game_state["danger_ranking"][p]["tail_connect"] = (
                path_distance_pq(p, my_tail),
                *[path_distance_pq(p, snake["body"][-1]) for snake in game_state["others"]])

    def killer_near_watching():
        killers = [snake for snake in game_state["snakes"] if len(game_state["me"]["body"]) < len(snake["body"])]
        killers = [(head, path_distance_pq(get_my_head(), head), len(snake["body"])) for snake in killers for head in [snake["body"][0]]]
        game_state["killer_near"] = killers

    def crowded_rank(p):
        cells = [q 
            for x in range(game_state["board"]["width"]) 
            for y in range(game_state["board"]["height"]) 
            for q in [(x,y)]
            ]
        layers = [[q for q in cells if distance_pq(p,q) == d] for d in range(21)]
        layers = [layer for layer in layers if len(layer) != 0]
        nlayers = [[p]]
        for layer in layers[1:]:
            nlayers.append(nlayers[-1]+layer)
        elayers = [[q for q in layer if q not in game_state["occupied_cells"][0]] for layer in nlayers]
        watching = [(len(a), len(b)) for a,b in zip(nlayers, elayers)]
        return watching

    def crowded_ranking():
        game_state["crowded_ranking"] = crowded_rank(get_my_head())

    def decision_making():
        game_state["decision_path"] = []
        if len(game_state["others"]) != 1:
            decision_1_v_n()
        else:
            decision_1_v_1()

    def decision_1_v_n():
        #4 aspects consideration
        #allowed move - must satisfy
        #danger rank
        #   trap
        #   dead end
        #   off-border
        #   being chased
        #   crowd danger
        #food rank
        #kill oppotunities
        #basic scheme:
        #allowed --> routine -->avoid danger --> food --> kill oppo
        #log the decision making process

        #no allowed move - die on self
        if len(game_state["allowed_move"]) == 0:
            game_state["next_head_coord"] = game_state["me"]["body"][1]
            return

        #base
        game_state["decision_path"].append("base")
        game_state["next_head_coord"] = game_state["allowed_move"][0]

        #routine
        move = game_state["routine_move"]
        if move in game_state["allowed_move"]:
            if move != game_state["next_head_coord"]:
                game_state["decision_path"].append("routine")
                game_state["next_head_coord"] = move
        
        #danger ranking always exists and not empty at this point
        #and they are already compatible with allowed moves

        def food_decision(passed_moves):
            def food_move(target):
                moves = shortest_path_move(get_my_head(), target)
                moves = [move for move in moves if move in passed_moves]
                if len(moves) != 0:
                    off_border = [move for move in moves if not on_border(move)]
                    if len(off_border) != 0:
                        move = off_border[0]
                    else:
                        move = moves[0]
                    if move != game_state["next_head_coord"]:
                        game_state["decision_path"].append("food")
                        game_state["next_head_coord"] = move

            def get_food(target):
                game_state["food_decision"] = [target]
                if not on_border(target):
                    food_move(target)
                else:
                    #food on border
                    if is_adjacent(get_my_head(), target):
                        if all([d>=6 for _,d,_ in game_state["killer_near"]]):
                            if target != game_state["next_head_coord"]:
                                game_state["decision_path"].append("food")
                                game_state["next_head_coord"] = target
                        else:
                            killers = [killer for killer in game_state["killer_near"] for p,d,L in [killer] if L>len(game_state["me"]["body"])+1]
                            if len(killers) == 0:
                                if target != game_state["next_head_coord"]:
                                    game_state["decision_path"].append("food")
                                    game_state["next_head_coord"] = target
                    else:
                        one_next = [p for p in adj_cells(target) if p not in game_state["occupied_cells"][0] and not on_border(p)]
                        if len(one_next) != 0:
                            food_move(one_next[0])
                        else:
                            food_move(target)

            food_near = [food for food in game_state["food_ranking"] for p,d,ds in [food] if d <= 10]
            my_len = len(game_state["me"]["body"])
            good_food = [(p,d) for food in food_near for p,d,ds in [food] 
                         if all([(d<de) if my_len <= size else (d<=de) for de,size in ds])]
            game_state["food_log"] = [len(game_state["food_ranking"]), len(food_near), len(good_food), food_near[:2]]
            if len(good_food) != 0:
                result = first_group(good_food)
                get_food(result[0])

        def try_kill_decision():
            result = game_state["try_kill"]
            if len(result) == 0:
                return

            result = result[0]
            #no danger in 3 steps
            result = [move for move in result if move in game_state["allowed_move"]]
            if len(result) != 0:
                if game_state["next_head_coord"] not in result:
                    game_state["decision_path"].append("try_kill")
                    game_state["next_head_coord"] = result[0]

        def default_decision_path():

            #happy_path_1
            moves = [move 
                    for move, ranking in game_state["danger_ranking"].items()
                    if 1==1
                    and "collision_1" in ranking
                    and ranking["collision_1"] == 99
                    and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                    and not ranking["trap"]
                    ]

            if len(moves) != 0:
                game_state["decision_path"].append("happy_path_1")
                off_border = [p for p in moves if not on_border(p)]
                if len(off_border) != 0:
                    if game_state["next_head_coord"] not in off_border:
                        game_state["decision_path"].append("off_border")
                        game_state["next_head_coord"] = off_border[0]
                else:
                    if game_state["next_head_coord"] not in moves:
                        game_state["decision_path"].append("on_border")
                        game_state["next_head_coord"] = moves[0]

                #food and try_kill only happen in the happy path 1
                food_decision(moves)
                try_kill_decision()
                return

            #happy_path_2
            moves = [move 
                    for move, ranking in game_state["danger_ranking"].items()
                    if 1==1
                    and "collision_2" in ranking
                    and ranking["collision_2"] == 99
                    and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                    and not ranking["trap"]
                    ]

            if len(moves) != 0:
                game_state["decision_path"].append("happy_path_2")
                off_border = [p for p in moves if not on_border(p)]
                if len(off_border) != 0:
                    if game_state["next_head_coord"] not in off_border:
                        game_state["decision_path"].append("off_border")
                        game_state["next_head_coord"] = off_border[0]
                else:
                    if game_state["next_head_coord"] not in moves:
                        game_state["decision_path"].append("on_border")
                        game_state["next_head_coord"] = moves[0]
                return

            #unhappy_path
            #not taking dead_end and trap, take collision risk
            moves = [item 
                        for item in game_state["danger_ranking"].items()
                        for move, ranking in [item]
                        if (1==1
                        and "collision_1" in ranking
                        and "collision_2" in ranking
                        and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                        and not ranking["trap"]
                    ) ]
            #let's try taking risk fast, if passed hopefully danger is dropped
            if len(moves) != 0:
                game_state["decision_path"].append("take_collision")
                #remove on border
                off_border = [(move, ranking) for move, ranking in moves if not on_border(move)]
                if len(off_border) != 0:
                    moves = [(move, ranking["collision_2"]) for move, ranking in off_border]
                else:
                    moves = [(move, ranking["collision_2"]) for move, ranking in moves]
                moves = first_group(moves)
                if game_state["next_head_coord"] not in moves:
                    game_state["next_head_coord"] = moves[0]
                return

        default_decision_path()


    def decision_1_v_1():

        #no allowed move - die on self
        if len(game_state["allowed_move"]) == 0:
            game_state["next_head_coord"] = game_state["me"]["body"][1]
            return

        #base
        game_state["decision_path"].append("base")
        game_state["next_head_coord"] = game_state["allowed_move"][0]

        #routine
        move = game_state["routine_move"]
        if move in game_state["allowed_move"]:
            if move != game_state["next_head_coord"]:
                game_state["decision_path"].append("routine")
                game_state["next_head_coord"] = move
        
        #danger ranking always exists and not empty at this point
        #and they are already compatible with allowed moves

        def food_decision(passed_moves):
            def food_move(target):
                moves = shortest_path_move(get_my_head(), target)
                moves = [move for move in moves if move in passed_moves]
                if len(moves) != 0:
                    off_border = [move for move in moves if not on_border(move)]
                    if len(off_border) != 0:
                        moves = off_border
                    moves = prefer_straight(moves)
                    move = moves[0]
                    if move != game_state["next_head_coord"]:
                        game_state["decision_path"].append("food")
                        game_state["next_head_coord"] = move

            def get_food(target):
                game_state["food_decision"] = [target]
                if not on_border(target):
                    food_move(target)
                else:
                    #food on border
                    if is_adjacent(get_my_head(), target):
                        if all([d>=6 for _,d,_ in game_state["killer_near"]]):
                            if target != game_state["next_head_coord"]:
                                game_state["decision_path"].append("food")
                                game_state["next_head_coord"] = target
                        else:
                            killers = [killer for killer in game_state["killer_near"] for p,d,L in [killer] if L>len(game_state["me"]["body"])+1]
                            if len(killers) == 0:
                                if target != game_state["next_head_coord"]:
                                    game_state["decision_path"].append("food")
                                    game_state["next_head_coord"] = target
                    else:
                        one_next = [p for p in adj_cells(target) if p not in game_state["occupied_cells"][0] and not on_border(p)]
                        if len(one_next) != 0:
                            food_move(one_next[0])
                        else:
                            food_move(target)

            food_near = [food for food in game_state["food_ranking"] for p,d,ds in [food] if d <= 10]
            my_len = len(game_state["me"]["body"])
            good_food = [(p,d) for food in food_near for p,d,ds in [food] 
                         if all([(d<de) if my_len <= size else (d<=de) for de,size in ds])]
            game_state["food_log"] = [len(game_state["food_ranking"]), len(food_near), len(good_food), food_near[:2]]
            if len(good_food) != 0:
                result = first_group(good_food)
                get_food(result[0])

        def try_kill_decision():
            result = game_state["try_kill"]
            if len(result) == 0:
                return

            result = result[0]
            #no danger in 3 steps
            result = [move for move in result if move in game_state["allowed_move"]]
            if len(result) != 0:
                if game_state["next_head_coord"] not in result:
                    game_state["decision_path"].append("try_kill")
                    game_state["next_head_coord"] = result[0]

        def be_careful_choices():
            ab = game_state["allowed_move"]
            if len(ab) != 2:
                return
            a = game_state["next_head_coord"]
            snake_head = game_state["others"][0]["body"][0]
            occupied = game_state["occupied_cells"][0]
            snake_allowed_move = [p for p in adj_cells(snake_head) if p not in occupied]
            cn = len(path_connected(a))
            if any([2*x <= cn and x+10 <= cn for p in snake_allowed_move for x in [len(path_connected(a, occupied+[p]))]]):
                #a is sensitive
                game_state["decision_path"].append("enemy_cut")
                game_state["next_head_coord"] = [b for b in ab if b != a][0]
                return
            if cn <= 10:
                #dead end
                game_state["decision_path"].append("dead_end")
                game_state["next_head_coord"] = [b for b in ab if b != a][0]
                return

        def prefer_straight(moves):
            moves = [(move, 0 if get_adjacent_dir(get_my_head(), move) == get_adjacent_dir(get_my_neck(), get_my_head()) else 1) for move in moves]
            moves = first_group(moves)
            return moves

        def my_snake_bigger():
            my_body = game_state["me"]["body"]
            my_head = my_body[0]
            my_neck = my_body[1]
            my_tail = my_body[-1]
            me_to_my_tail = path_distance_pq(my_head, my_tail)
            if me_to_my_tail == 999:
                return False
            snake_head = game_state["others"][0]["body"][0]
            other_to_my_tail = path_distance_pq(snake_head, my_tail)
            if me_to_my_tail < other_to_my_tail:
                if len(game_state["food_ranking"]) != 0:
                    foods = game_state["food_ranking"]
                    min_d = min([d for _,d,_ in foods])
                    foods = [food for food in game_state["food_ranking"] for p,d,ds in [food] if d == min_d and d <= 3]
                    #foods = [food for food in foods for p,d,ds in [food] if d == min_d]
                    #foods = [food for food in foods for p,d,ds in [food] if path_distance_pq(my_head, p)+path_distance_pq(p, my_tail) <= other_to_my_tail]
                    if len(foods) != 0:
                        food,_,_ = foods[0]
                        moves = shortest_path_move(my_head, food)
                        if len(moves) != 0:
                            moves = prefer_straight(moves)
                            game_state["decision_path"].append("food")
                            game_state["next_head_coord"] = moves[0]
                            be_careful_choices()
                            return True
            if me_to_my_tail > 1 or game_state["me"]["health"] != 100:
                moves = shortest_path_move(my_head, my_tail)
                if len(moves) != 0:
                    moves = [(move, 0 if get_adjacent_dir(my_head, move) == get_adjacent_dir(my_neck, my_head) else 1) for move in moves]
                    moves = first_group(moves)
                    game_state["decision_path"].append("my_tail")
                    game_state["next_head_coord"] = moves[0]
                    be_careful_choices()
                    return True
            return False

        def default_decision_path():

            #happy_path_1
            moves = [move 
                    for move, ranking in game_state["danger_ranking"].items()
                    if 1==1
                    and "collision_1" in ranking
                    and ranking["collision_1"] == 99
                    and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                    and not ranking["trap"]
                    #and not all([d == 999 for d in ranking["tail_connect"]])
                    ]

            if len(moves) != 0:
                game_state["decision_path"].append("happy_path_1")
                off_border = [p for p in moves if not on_border(p)]
                if len(off_border) != 0:
                    if game_state["next_head_coord"] not in off_border:
                        game_state["decision_path"].append("off_border")
                        game_state["next_head_coord"] = off_border[0]
                else:
                    if game_state["next_head_coord"] not in moves:
                        game_state["decision_path"].append("on_border")
                        game_state["next_head_coord"] = moves[0]

                #food and try_kill only happen in the happy path 1
                food_decision(moves)
                try_kill_decision()
                return

            #happy_path_2
            moves = [move 
                    for move, ranking in game_state["danger_ranking"].items()
                    if 1==1
                    and "collision_2" in ranking
                    and ranking["collision_2"] == 99
                    and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                    and not ranking["trap"]
                    #and not all([d == 999 for d in ranking["tail_connect"]])
                    ]

            if len(moves) != 0:
                game_state["decision_path"].append("happy_path_2")
                off_border = [p for p in moves if not on_border(p)]
                if len(off_border) != 0:
                    if game_state["next_head_coord"] not in off_border:
                        game_state["decision_path"].append("off_border")
                        game_state["next_head_coord"] = off_border[0]
                else:
                    if game_state["next_head_coord"] not in moves:
                        game_state["decision_path"].append("on_border")
                        game_state["next_head_coord"] = moves[0]
                return

            #unhappy_path
            #not taking dead_end and trap, take collision risk
            moves = [item 
                        for item in game_state["danger_ranking"].items()
                        for move, ranking in [item]
                        if (1==1
                        and "collision_1" in ranking
                        and "collision_2" in ranking
                        and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                        and not ranking["trap"]
                        #and not all([d == 999 for d in ranking["tail_connect"]])
                    ) ]
            #let's try taking risk fast, if passed hopefully danger is dropped
            if len(moves) != 0:
                game_state["decision_path"].append("take_collision")
                #remove on border
                off_border = [(move, ranking) for move, ranking in moves if not on_border(move)]
                if len(off_border) != 0:
                    moves = [(move, ranking["collision_2"]) for move, ranking in off_border]
                else:
                    moves = [(move, ranking["collision_2"]) for move, ranking in moves]
                moves = first_group(moves)
                if game_state["next_head_coord"] not in moves:
                    game_state["next_head_coord"] = moves[0]
                return


        if len(game_state["me"]["body"]) > len(game_state["others"][0]["body"]) and len(game_state["me"]["body"]) >= 15:
            if my_snake_bigger():
                return



        default_decision_path()


    def logging():
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

        log = game_state["logging"]
        log["board"] = log_board
        log["move"] = game_state["next_move"]
        log["routine_move"] = game_state["routine_move"]
        log["allowed_move"] = game_state["allowed_move"]
        log["danger_ranking"] = game_state["danger_ranking"]
        log["decision_path"] = game_state["decision_path"]
        log["food_decision"] = game_state.get("food_decision", [])
        time_diff = game_state["end_time"] - game_state["start_time"]
        log["time"] = f"{time_diff:.3f}s"
        print(game_state["logging"])


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

    def path_distance_pq(p, q):
        occuppied = game_state["occupied_cells"][0]
        #remove q from occupied otherwise there is no path
        occuppied = [p for p in occuppied if p != q]

        connected = [set([p])]
        layer = set([q for q in adj_cells(p) if q not in occuppied])
        while len(layer) != 0:
            connected.append(layer)
            layer = set([x for q in layer for x in adj_cells(q) if x not in occuppied and x not in connected[-2]])
        for i,layer in enumerate(connected):
            if q in layer:
                return i
        return 999

    def path_connected(p, occuppied=None):
        if occuppied is None:
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
        if game_state["turn"] >= 3:
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
        if game_state["turn"] >= 3:
            result = [(0 if get_adjacent_dir(my_head, move) == get_adjacent_dir(my_neck, my_head) else 1, move) for move in result]
            result = sorted(result)
            result = [move for rank, move in result]
        return result

    def chasing_tail():
        #this is only used in 1v1 case
        result_me = chasing_my_tail()
        result_other = chasing_other_tail(game_state["others"][0])
        game_state["chasing_tail"] = {
            "me": result_me,
            "other": result_other,
        }
        if len(result_me) != 0:
            return result_me
        return result_other


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

    def get_my_neck() -> typing.Tuple:
        return game_state["me"]["body"][1]

    def get_my_tail() -> typing.Tuple:
        return game_state["me"]["body"][-1]

    def get_coord(items: typing.List) -> typing.List:
        return [(c["x"], c["y"]) for c in items]

#############################################
# end of utility functions
#############################################


    def experiment_condition():
        if len(game_state["others"]) != 1: return False
        if game_state["others"][0]["name"] not in (
            "Snakeformatika",
            #"Frank The Tank",
        ): 
            return False
        return True
    
    initialization()
    if not experiment_condition(): return False
    game_state["logging"]["version"] = "Experiment"

    #main
    main()

    #return {"move": game_state["next_move"]}
    return True

