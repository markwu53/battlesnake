from itertools import product, groupby
import snake_utility
from snake_utility import *
import math

game_state = None

def get_food(moves):
    #something wrong deploy again
    pass

def my_snake_bigger():
    global game_state
    game_state = snake_utility.game_state

    store_enemy_possible_paths()

    my_head = get_my_head()
    my_tail = get_my_tail()
    other_head = game_state["others"][0]["body"][0]
    other_tail = game_state["others"][0]["body"][-1]

    r = game_state["danger_ranking"]
    abc = game_state["allowed_move"]
    for a in abc:
        r[a]["cut_info"] = enemy_possible_cut_path(a)
        r[a]["see_my_tail"] = path_connected(a, my_tail)
        r[a]["see_other_head"] = path_connected(a, other_head)
        r[a]["see_other_tail"] = path_connected(a, other_tail)


    #################################
    # can see tail either no cut or after cut
    #################################

    #category - no cut, can see my tail
    moves = [a for a in abc if len(r[a]["cut_info"]) == 0 and r[a]["see_my_tail"]]
    if len(moves) != 0:
        game_state["decision_path"].append("no_cut my_tail")
        if game_state["next_head_coord"] not in moves:
            game_state["next_head_coord"] = moves[0]
        get_food(moves)
        return
    
    #category - no cut, can see other tail
    moves = [a for a in abc if len(r[a]["cut_info"]) == 0 and r[a]["see_other_tail"]]
    if len(moves) != 0:
        game_state["decision_path"].append("no_cut other_tail")
        if game_state["next_head_coord"] not in moves:
            game_state["next_head_coord"] = moves[0]
        get_food(moves)
        return

    #category - has cut, can see my tail
    moves = [a for a in abc
             for cut_info in [r[a]["cut_info"]]
             for cut_path, nspace in cut_info
             for occupied in [game_state["occupied_cells"][0]+cut_path[1:]]
             if len(cut_info) == 1
             and path_connected(a, my_tail, occupied)
             ]
    if len(moves) != 0:
        game_state["decision_path"].append("has_cut my_tail")
        if game_state["next_head_coord"] not in moves:
            game_state["next_head_coord"] = moves[0]
        get_food(moves)
        return

    #category - has cut, can see other tail
    moves = [a for a in abc
             for cut_info in [r[a]["cut_info"]]
             for cut_path, nspace in cut_info
             for occupied in [game_state["occupied_cells"][0]+cut_path[1:]]
             if len(cut_info) == 1
             and path_connected(a, other_tail, occupied)
             ]
    if len(moves) != 0:
        game_state["decision_path"].append("has_cut other_tail")
        if game_state["next_head_coord"] not in moves:
            game_state["next_head_coord"] = moves[0]
        get_food(moves)
        return

    #################################
    # no tail
    #################################

    #category - can't see any tail, no cut, confined space has enough room
    moves = [a for a in abc 
             if len(r[a]["cut_info"]) == 0
             and r[a]["dead_end"] >= len(game_state["me"]["body"]) *3 //2
             ]
    if len(moves) != 0:
        game_state["decision_path"].append("static spacious")
        if game_state["next_head_coord"] not in moves:
            game_state["next_head_coord"] = moves[0]
        #get_food(moves)
        return

    #category - can't see any tail, has cut, cut space has enough room
    moves = [a for a in abc
             for cut_info in [r[a]["cut_info"]]
             for cut_path, nspace in cut_info
             if len(cut_info) == 1
             and nspace >= len(game_state["me"]["body"]) *3 //2
             ]
    if len(moves) != 0:
        game_state["decision_path"].append("has_cut spacious")
        if game_state["next_head_coord"] not in moves:
            game_state["next_head_coord"] = moves[0]
        #get_food(moves)
        return

    #################################
    # limited space - find a wayout
    #################################

    for a in abc:
        wayout = {}

        occupied = game_state["occupied_cells"][0]
        confined_space = path_connected_set(a, occupied)
        if len(r[a]["cut_info"]) == 1:
            cut_path, nspace = r[a]["cut_info"][0]
            occupied += cut_path[1:]
            confined_space = path_connected_set(a, occupied)
        wayout["confined_food"] = [f for f in game_state["food"] if f in confined_space]

        wayout["me"] = {}
        my_body = game_state["me"]["body"]
        my_index = max([i for i,cell in enumerate(my_body) if path_connected(a, cell, occupied)])
        wayout["me"]["point"] = my_body[my_index]
        wayout["me"]["needed_steps"] = len(my_body) - my_index-1
        wayout["me"]["direct_distance"] = path_distance_pq(a, wayout["me"]["point"])

        wayout["other"] = {}
        other_body = game_state["others"][0]["body"]
        #this can be empty
        other_connected_body = [i for i,cell in enumerate(other_body) if path_connected(a, cell, occupied)]
        wayout["other"]["connected"] = len(other_connected_body) != 0
        if wayout["other"]["connected"]:
            other_index = max(other_connected_body)
            wayout["other"]["point"] = other_body[other_index]
            wayout["other"]["needed_steps"] = len(other_body) - other_index-1
            wayout["other"]["direct_distance"] = path_distance_pq(a, wayout["other"]["point"])

        r[a]["wayout"] = wayout

    #category - simple wayout: long enough path towards wayout
    moves = [a for a in abc
             for way in [r[a]["wayout"]["me"]]
             if way["direct_distance"] >= way["needed_steps"]
             ]
    if len(moves) != 0:
        game_state["decision_path"].append("simple_wayout me")
        if game_state["next_head_coord"] not in moves:
            game_state["next_head_coord"] = moves[0]
        return

    moves = [a for a in abc
             for way in [r[a]["wayout"]["other"]]
             if way["connected"] and way["direct_distance"] >= way["needed_steps"]
             ]
    if len(moves) != 0:
        game_state["decision_path"].append("simple_wayout other")
        if game_state["next_head_coord"] not in moves:
            game_state["next_head_coord"] = moves[0]
        return

    #no simple wayout, need to calculate a path long enough towards wayout
    #first remove no hope ones
    #sort by most hopeful one
    #go one by one return on first success to avoid costly calculation
    nohope = [a for a in abc 
                  for me in [r[a]["wayout"]["me"]] 
                  for other in [r[a]["wayout"]["other"]] 
                  for food in [r[a]["wayout"]["confined_food"]]
                  if len(r[a]["cut_info"]) == 0
                  and not other["connected"]
                  and r[a]["dead_end"]-len(food) < me["needed_steps"]
                  ]
    nohope2 = [a for a in abc 
                  for me in [r[a]["wayout"]["me"]] 
                  for other in [r[a]["wayout"]["other"]] 
                  for food in [r[a]["wayout"]["confined_food"]]
                  if len(r[a]["cut_info"]) == 0
                  and other["connected"]
                  and r[a]["dead_end"]-len(food) < me["needed_steps"]
                  and r[a]["dead_end"]-len(food) < other["needed_steps"]
                  ]
    hopeful = [a for a in abc if a not in nohope and a not in nohope2]

    #category - static, only me
    moves = [a for a in hopeful
                  for other in [r[a]["wayout"]["other"]] 
                  if len(r[a]["cut_info"]) == 0 
                  and not other["connected"]
                  ]
    moves = sorted(moves, key=lambda a: path_distance_pq(a, r[a]["wayout"]["me"]["point"]), reverse=True)
    for a in moves:
        wayout_point = r[a]["wayout"]["me"]["point"]
        needed_length = r[a]["wayout"]["me"]["needed_steps"]+1
        #this is a costly calculation:
        if exist_long_enough_path(a, wayout_point, needed_length):
            #a is good
            game_state["decision_path"].append("myself search_wayout")
            game_state["next_head_coord"] = a
            return

    #category - static, connected to both
    moves = [a for a in hopeful
                  for other in [r[a]["wayout"]["other"]] 
                  if len(r[a]["cut_info"]) == 0 
                  and other["connected"]
                  ]
    for a in moves:
        if r[a]["wayout"]["me"]["needed_steps"] <= r[a]["wayout"]["other"]["needed_steps"]:
            if exist_long_enough_path(a, r[a]["wayout"]["me"]["point"], r[a]["wayout"]["me"]["needed_steps"]+1):
                game_state["decision_path"].append("both me search_wayout")
                game_state["next_head_coord"] = a
                return
        else:
            if exist_long_enough_path(a, r[a]["wayout"]["other"]["point"], r[a]["wayout"]["other"]["needed_steps"]+1):
                game_state["decision_path"].append("both other search_wayout")
                game_state["next_head_coord"] = a
                return

    #category - has cut, search wayout
    moves = [a for a in hopeful if len(r[a]["cut_info"]) == 1 ]
    for a in moves:
        cut_path, nspace = r[a]["cut_info"][0]
        occupied = game_state["occupied_cells"][0]+cut_path[1:]
        if r[a]["wayout"]["me"]["needed_steps"] <= r[a]["wayout"]["other"]["needed_steps"]:
            if exist_long_enough_path(a, r[a]["wayout"]["me"]["point"], r[a]["wayout"]["me"]["needed_steps"]+1, occupied):
                game_state["decision_path"].append("cut me search_wayout")
                game_state["next_head_coord"] = a
                return
        else:
            if exist_long_enough_path(a, r[a]["wayout"]["other"]["point"], r[a]["wayout"]["other"]["needed_steps"]+1, occupied):
                game_state["decision_path"].append("cut other search_wayout")
                game_state["next_head_coord"] = a
                return

    ##############################################################

def get_food2():

    my_head = get_my_head()
    best = []
    target = game_state["food"][0]

    #get food
    food = [f for f in game_state["food"] if path_connected(my_head, f)]

    if len(food) != 0:
        food1 = [f for f in food if is_adjacent(my_head, f)]
        if len(food1) != 0:
            moves = [a for a in food1 if a in best]
            if len(moves) != 0:
                game_state["decision_path"].append("food1")
                game_state["next_head_coord"] = moves[0]
        else:
            food2 = [f for f in food if path_distance_pq(my_head, f) == 2 and not is_adjacent(f, get_my_neck())]
            if len(food2) != 0:
                food_target = food2[0]
                moves = shortest_path_move(my_head, food_target)
                moves = [move for move in moves if move in best]
                if len(moves) != 0:
                    game_state["decision_path"].append(f"food2: {food_target}")
                    game_state["next_head_coord"] = moves[0]
            else:
                food = [(f, (
                    path_distance_pq(my_head, f),
                    path_distance_pq(my_head, target),
                    path_distance_pq(f, target),
                )) for f in food]
                food = [(f, 
                        #(my_head, food, target) should form a triangle
                        #and we want food should roughly on the path to target
                        #this is calculated by sine of the angle
                        math.sqrt((hp-a)*(hp-b)*(hp-c)*hp)*2/(a*b)) for f, sides in food for a,b,c in [sides] for hp in [(a+b+c)/2] 
                        if 1==1
                        and a == distance_pq(my_head, f)
                        and b == distance_pq(my_head, target)
                        and c == distance_pq(f, target)
                        and a<=b
                        and a+b > c
                        and a+c > b
                        and b+c > a
                        ]
                if len(food) != 0:
                    food = sorted(food, key=lambda f: f[1])
                    food_target, sine = food[0]
                    moves = shortest_path_move(my_head, food_target)
                    moves = [move for move in moves if move in best]
                    if len(moves) != 0:
                        game_state["decision_path"].append(f"food: {food_target}")
                        game_state["next_head_coord"] = moves[0]

def exist_long_enough_path(a, b, needed_length, occupied=None):
    if occupied is None:
        occupied = game_state["occupied_cells"][0]
    r = game_state["danger_ranking"][a]
    occupied = [p for p in occupied if p != b]
    layers = []
    layer = [[a]]
    foods = r["wayout"]["confined_food"]
    while len(layer) != 0:
        layers.append(layer)
        layer = [path+[p] for layer in layers for path in layer for end in [path[-1]] for p in adj_cells(end)
                 if p not in path and p not in occupied]
    for layer in layers:
        for path in layer:
            if path[-1] != b: continue
            if len(path) < needed_length: continue
            f = [p for p in foods if p in path]
            if len(path) - len(f) >= needed_length:
                return True
    return False

def store_enemy_possible_paths(nstep=5, max_paths=200):
    #calculate enemy snake possible path
    #assuming my snake static
    #limit nstep or a fix number of total paths
    snake_head = game_state["others"][0]["body"][0]
    layers = [[[snake_head]]]
    for ilayer in range(nstep):
        if sum([len(layer) for layer in layers]) > max_paths: break
        layer = [npath
                 for path in layers[-1] 
                 for head in [path[-1]] 
                 for nhead in adj_cells(head)
                 for npath in [ path+[nhead] ]
                 if nhead not in path 
                    and nhead not in game_state["occupied_cells"][ilayer] 
                 ]
        layers.append(layer)
    game_state["enemy_paths"] = layers

def enemy_possible_cut_path(a, nstep=5, max_paths=200):
    occ = game_state["occupied_cells"]
    n_original_space = game_state["danger_ranking"][a]["dead_end"]
    #layers = enemy_possible_paths(nstep, max_paths)

    #stored once
    layers = game_state["enemy_paths"]

    cut_paths = []
    for layer in layers:
        for path in layer:
            #1. must cut an area
            #2. new head can't expose in the cut space - assuming my snake is bigger
            #3. if exposed it must be shorter than the distance for my head
            occupied = occ[len(path)-2]+path[1:]
            cut_space = path_connected_set(a, occupied)
            n_cut_space = len(cut_space)
            n_orig = n_original_space-len(path)+1
            if n_orig <= 0:
                continue
            if n_cut_space / n_orig > 0.4:
                #not a substantial cut
                continue
            if len(path) > path_distance_pq(a, path[-1]):
                #enemy head doesn't reach the cut point earlier than I
                #so won't be a danger assuming I'm bigger
                continue

            #my_new_tail = game_state["me"]["body"][-len(path)]
            #enemy_new_tail = game_state["others"][0]["body"][-len(path)]
            #if path_connected(a, my_new_tail): continue
            #if path_connected(a, enemy_new_tail): continue

            cut_paths.append((path, n_cut_space))

    if len(cut_paths) != 0:
        min_cut_space = min([n for path, n in cut_paths])
        cut_paths = [path for path, n in cut_paths if n == min_cut_space]
        cut_paths = [(path, len(path)) for path in cut_paths]
        min_cut_length = min([n for path, n in cut_paths])
        cut_paths = [path for path, n in cut_paths if n == min_cut_length]
        cut_path = cut_paths[0]
        return [(cut_path, min_cut_space)]
    return []

def test_init_game():
    snake_utility.game_state = {}
    snake_utility.game_state["board"] = {}
    snake_utility.game_state["board"]["width"] = 11
    snake_utility.game_state["board"]["height"] = 11

def test_path(p=None, nstep=None):
    if p is None: p = (5,5)
    if nstep is None: nstep = 5
    layers = [[[p]]]
    for ilayer in range(nstep):
        layer = [npath
                 for path in layers[-1] 
                 for end in [path[-1]] 
                 for p in adj_cells(end)
                 for npath in [ path+[p] ]
                 if p not in path ]
        layers.append(layer)
    paths = [path for layer in layers for path in layer]
    print(len(paths))
    for layer in layers: print(len(layer))

def run():
    test_init_game()
    test_path()

if __name__ == "__main__":
    run()

