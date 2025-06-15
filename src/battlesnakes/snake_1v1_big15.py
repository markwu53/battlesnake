from itertools import product, groupby
import snake_utility
from snake_utility import *
import math

game_state = None

def has_cut(a):
    r = game_state["danger_ranking"][a]
    if r["cut_space"] == 999:
        return False
    if r["dead_end"] - r["cut_space"] < len(r["cut_path"])+2:
        #cut not effective
        return False
    return True

def rank_a_move(a):
    my_head = get_my_head()
    my_tail = get_my_tail()
    other_tail = game_state["others"][0]["body"][-1]
    r = game_state["danger_ranking"][a]
    rank = 1
    if not has_cut(a):
        if path_distance_pq(a, my_tail) < 999:
            rank = 1
        elif path_distance_pq(a, other_tail) < 999:
            rank = 2
        else:
            #need calculate a wayout
            rank = 5
    else:
        cut_point = r["cut_point"]
        if path_distance_pq(a, my_tail) < path_distance_pq(a, cut_point):
            rank = 3
        elif path_distance_pq(a, other_tail) < path_distance_pq(a, cut_point):
            rank = 4
        else:
            #dangerous, probably too late
            rank = 9
    return rank

def my_snake_bigger():
    global game_state
    game_state = snake_utility.game_state

    #chase my tail first
    #if not, chase other tail
    #in the route, get food if near
    #consider possible cut and dead end

    #1. no cut and can see tail
    #2. cut not effective - still can see tail
    #3. no cut but dead end but can calculate a way out

    get_cut_info()

    my_head = get_my_head()
    my_tail = get_my_tail()
    other_tail = game_state["others"][0]["body"][-1]

    abc = game_state["allowed_move"]
    abc = [(a, rank_a_move(a)) for a in abc]
    best_rank = min([rank for a, rank in abc])
    best = [a for a, rank in abc if rank == best_rank]
    target = None
    if best_rank in (1,2,3,4):
        if best_rank in (1,3):
            game_state["decision_path"].append("my_tail")
            target = my_tail
        elif best_rank in (2,4):
            game_state["decision_path"].append("other_tail")
            target = other_tail

        moves = shortest_path_move(my_head, target)
        if len(moves) != 0:
            game_state["next_head_coord"] = moves[0]

        food = game_state["food"]
        food1 = [f for f in food if is_adjacent(my_head, f)]
        if len(food1) != 0:
            moves = [a for a in best if a in food1]
            if len(moves) != 0:
                game_state["decision_path"].append("food1")
                game_state["next_head_coord"] = moves[0]
        else:
            food = [f for f in food if path_distance_pq(my_head, f) == 2 and not is_adjacent(f, get_my_neck())]
            if len(food) != 0:
                food_target = food[0]
                moves = shortest_path_move(my_head, food_target)
                moves = [move for move in best]
                if len(moves) != 0:
                    game_state["decision_path"].append(f"food: {food_target}")
                    game_state["next_head_coord"] = moves[0]
            else:

                food = [f for f in food if path_connected(my_head, f)]
                if len(food) != 0:
                    food = [(f, (
                        path_distance_pq(my_head, f),
                        path_distance_pq(my_head, target),
                        path_distance_pq(f, target),
                    )) for f in food]
                    food = [(f, math.sqrt((hp-a)*(hp-b)*(hp-c)*hp)*2/(a*b)) for f, sides in food for a,b,c in [sides] for hp in [(a+b+c)/2] 
                            if a<=b
                            and a+b > c
                            and a+c > b
                            and b+c > a
                            ]
                    if len(food) != 0:
                        food = sorted(food, key=lambda f: f[1])
                        food_target = food[0][0]
                        moves = shortest_path_move(my_head, food_target)
                        moves = [move for move in best]
                        if len(moves) != 0:
                            game_state["decision_path"].append(f"food: {food_target}")
                            game_state["next_head_coord"] = moves[0]

    else:
        #rank = 5
        #rank = 9
        game_state["decision_path"].append(f"rank:{best_rank}")
        game_state["next_head_coord"] = best[0]
    
    return True

def get_cut_info():
    snake_paths = enemy_snake_danger_paths()

    occupied = game_state["occupied_cells"][0]
    my_head = get_my_head()
    my_tail = get_my_tail()
    for a in game_state["allowed_move"]: 
        cuts = [ (len(path_connected_set(a, occupied+list(path))), path[-1], path) for path in snake_paths ]
        if len(cuts) != 0:
            cut_space, cut_point, cut_path = sorted(cuts)[0]
        else:
            cut_space, cut_point, cut_path = 999, 999, tuple()
        game_state["danger_ranking"][a]["cut_space"] = cut_space
        game_state["danger_ranking"][a]["cut_point"] = cut_point
        game_state["danger_ranking"][a]["cut_path"] = cut_path

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

