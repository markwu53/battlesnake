from itertools import product, groupby
import snake_utility
from snake_utility import *
import math

game_state = None

def rank_a_move(a):
    my_tail = get_my_tail()
    other_tail = game_state["others"][0]["body"][-1]
    cut_info = game_state["danger_ranking"][a]["cut_info"]
    rank = 1

    if len(cut_info) == 0:
        #no cut
        if path_connected(a, my_tail):
            #a is good
            rank = 1
        elif path_connected(a, other_tail):
            #a is good
            rank = 2
        else:
            #a static dead end
            rank = 5
    else:
        if path_connected(a, my_tail):
            rank = 3
        elif path_connected(a, other_tail):
            rank = 4
        else:
            rank = 5
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

    store_enemy_possible_paths()
    abc = game_state["allowed_move"]
    for a in abc:
        game_state["danger_ranking"][a]["cut_info"] = enemy_possible_cut_path(a)
        game_state["danger_ranking"][a]["rank_1v1"] = rank_a_move(a)

    my_head = get_my_head()
    my_tail = get_my_tail()
    other_tail = game_state["others"][0]["body"][-1]

    abc = [(a, game_state["danger_ranking"][a]["rank_1v1"]) for a in abc]
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

    else:
        #rank = 5
        find_wayout(best)

def rank_again(a):
    #a is in a confined space
    #can't see my tail or other tail
    cut_info = game_state["danger_ranking"][a]["cut_info"]
    nspace = game_state["danger_ranking"][a]["dead_end"]
    my_length = len(game_state["me"]["body"])
    rank5 = 1
    if len(cut_info) == 0:
        #no cut
        if nspace >= my_length + 5:
            #space big enough
            rank5 = 1
        else:
            rank5 = 8
    else:
        cut_path, cut_space = cut_info[0]
        if cut_space >= my_length + 5:
            #cut but space is big enough
            rank5 = 2
        else:
            rank5 = 9
    return rank5

def static_wayout(a):
    max_index = max([i for i,cell in enumerate(game_state["me"]["body"])
        if path_connected(a, cell) ])
    confined_set = path_connected_set(a)
    foods = len([f for f in game_state["food"] if f in confined_set])
    wayout_length = len(game_state["me"]["body"]) - max_index + len(foods) -1
    if len(confined_set) < wayout_length:
        #no wayout
        pass
    else:
        pass

def find_wayout(abc):
    game_state["decision_path"].append(f"wayout")
    for a in abc:
        game_state["danger_ranking"][a]["rank5"] = rank_again(a)
    abc = [(a, game_state["danger_ranking"][a]["rank5"]) for a in abc]
    best_rank = min([rank for a, rank in abc])
    best = [a for a, rank in abc if rank == best_rank]
    if best_rank in (1,2):
        game_state["decision_path"].append(f"spacious")
        game_state["next_head_coord"] = best[0]
    elif best_rank == 8:
        #static confined space
        occupied = game_state["occupied"][0]



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

def enemy_snake_danger_paths(nstep=5):
    #5 step enemy move

    snake_head = game_state["others"][0]["body"][0]
    my_head = get_my_head()
    occupied = game_state["occupied_cells"][0]

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

    #paths with same end point will have same effect - this is wrong
    #in each layer (paths with same length), group by end point
    snake_paths = [[list(paths)[0] 
                    for endpoint, paths in groupby(sorted(layer, key=lambda path: path[-1]), key=lambda path: path[-1])]
                    for layer in snake_paths]

    #flatten it
    snake_paths = [path for layer in snake_paths for path in layer]
    #game_state["logging"]["danger_path"] = snake_paths
    return snake_paths

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
                    and nhead not in game_state["occupied"][ilayer] 
                 ]
        layers.append(layer)
    game_state["enemy_paths"] = layers

def enemy_possible_cut_path(a, nstep=5, max_paths=200):
    occ = game_state["occupied"]
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

