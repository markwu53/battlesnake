from itertools import product, groupby
import snake_utility
from snake_utility import *

game_state = None

def decision_1_v_1():

    global game_state
    game_state = snake_utility.game_state

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

    def enemy_snake_danger_paths():

        snake_head = game_state["others"][0]["body"][0]
        my_head = get_my_head()
        occupied = game_state["occupied_cells"][0]

        #5 step enemy move
        nstep = 5
        snake_connected_layers = path_connected_layers(snake_head)
        my_connected_layers = path_connected_layers(my_head)
        my_connected_dict = {c:i for i,layers in enumerate(my_connected_layers) for c in layers}

        #path must in every step shorter than mine otherwise won't be danger
        snake_paths = [
            layer if i == 0 else
            [c for c in layer if c in my_connected_dict and i+2 <= my_connected_dict[c]] 
                for i,layer in enumerate(snake_connected_layers) if i <= nstep]
        snake_paths = [layer for layer in snake_paths if len(layer) != 0]
        #5 layers each layer has paths all with same length
        #path must connected
        snake_paths = [[path for path in product(*snake_paths[:i+2]) 
                        if len(path) > 1 and all([is_adjacent(a,b) for a,b in zip(path[:-1], path[1:])])]
                        for i in range(nstep) ]
        #end point must cut an area
        snake_paths = [[path for path in layer for p in [path[-1]]
                        for occ in [[q for q in occupied if q != snake_head]]
                        if on_border(p)
                        or any([is_adjacent(p, c) for c in occ])
                        or any([distance_pq(p,c) == 2 and len([q for q in adj_cells(p) if q in adj_cells(c)]) == 2 for c in occ])
                        ] for layer in snake_paths if len(layer) != 0]
        #paths with same end point will have same effect
        #in each layer (paths with same length), group by end point
        snake_paths = [[list(paths)[0] 
                        for endpoint, paths in groupby(sorted(layer, key=lambda path: path[-1]), key=lambda path: path[-1])]
                        for layer in snake_paths]
        #flatten it
        snake_paths = [path for layer in snake_paths for path in layer]
        #game_state["logging"]["danger_path"] = snake_paths
        return snake_paths

    def be_careful_choices():
        abc = game_state["allowed_move"]
        if len(abc) <= 1:
            return
        if len(abc) == 3:
            #3 choices
            a,b,c = abc
            ab = path_distance_pq(a, b)
            ac = path_distance_pq(a, c)
            bc = path_distance_pq(b, c)
            if len([d for d in [ab, ac, bc] if d == 2]) == 2:
                #all connected
                return

        #otherwise, we need to check

        occupied = game_state["occupied_cells"][0]
        snake_paths = enemy_snake_danger_paths()

        my_head = get_my_head()
        my_tail = get_my_tail()
        other_tail = game_state["others"][0]["body"][-1]
        to_my_tail = path_distance_pq(my_head, my_tail)
        to_other_tail = path_distance_pq(my_head, other_tail)
        for a in abc: 
            cuts = [ (len(path_connected_set(a, occupied+list(path))), path_distance_pq(my_head, path[-1])) for path in snake_paths ]
            if len(cuts) != 0:
                cut_space, cut_distance = sorted(cuts)[0]
            else:
                cut_space, cut_distance = 999, 999
            game_state["danger_ranking"][a]["cut_space"] = cut_space
            game_state["danger_ranking"][a]["cut_distance"] = cut_distance
        
        #now I have the following information of an allowed move:
        #1. path connected distance to my tail
        #2. path connected distance to other tail
        #3. original connected space
        #4. possible cut space
        #5. cut point distance
        #I will use these to determine a best move

        a = game_state["next_head_coord"]
        r = game_state["danger_ranking"][a]
        if r["dead_end"] - r["cut_space"] < 6:
            return
        if to_my_tail < r["cut_distance"] or to_other_tail < r["cut_distance"]:
            return
        
        abc = [x for x in abc if x != a]
        game_state["next_head_coord"] = abc[0]

        """
        moves = [a for a in abc if a not in sensitive_to_cut and a not in dead_end]
        if len(moves) == 0:
            #find a way out
            return
        if game_state["next_head_coord"] in moves:
            return
        game_state["decision_path"].append("cut or dead_end")
        game_state["next_head_coord"] = moves[0]
        """

    def prefer_straight(moves):
        if game_state["turn"] >= 3:
            moves = [(move, 0 if get_adjacent_dir(get_my_head(), move) == get_adjacent_dir(get_my_neck(), get_my_head()) else 1) for move in moves]
            moves = first_group(moves)
        return moves

    def my_snake_bigger():
        my_body = game_state["me"]["body"]
        my_head = my_body[0]
        my_neck = my_body[1]
        my_tail = my_body[-1]
        me_to_my_tail = path_distance_pq(my_head, my_tail)
        #if me_to_my_tail == 999: return False
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
        if not is_adjacent(my_head, my_tail) or game_state["me"]["health"] != 100:
            moves = shortest_path_move(my_head, my_tail)
            if len(moves) != 0:
                moves = prefer_straight(moves)
                game_state["decision_path"].append("my_tail")
                game_state["next_head_coord"] = moves[0]
                be_careful_choices()
                return True
            else:
                #I can't see my tail
                #in this case, I can either chase the other's tail, 
                # or calculate a path that I can walk and wait until my tail reappear
                other_tail = game_state["others"][0]["body"][-1]
                if not is_adjacent(my_head, other_tail) or game_state["others"][0]["health"] != 100:
                    moves = shortest_path_move(my_head, other_tail)
                    if len(moves) != 0:
                        moves = prefer_straight(moves)
                        game_state["decision_path"].append("other_tail")
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
