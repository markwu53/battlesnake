from itertools import product, groupby
import snake_utility
from snake_utility import *

game_state = None

def my_snake_bigger():
    global game_state
    game_state = snake_utility.game_state

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

