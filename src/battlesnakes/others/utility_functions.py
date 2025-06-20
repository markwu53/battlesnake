import typing
import time

game_state = None

#############################################
# utility functions
#############################################

def path_distance_pq(p, q, occupied=None):
    if occupied is None:
        occupied = game_state["occupied_cells"][0]
    #remove q from occupied otherwise there is no path
    occupied = [p for p in occupied if p != q]
    layers = path_connected_layers(p, occupied)
    for i,layer in enumerate(layers):
        if q in layer:
            return i
    return 999

def path_connected_layers(p, occupied=None):
    if occupied is None:
        occupied = game_state["occupied_cells"][0]
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
        occupied = game_state["occupied_cells"][0]
    layers = path_connected_layers(p, occupied)
    return set([q for layer in layers for q in layer])

def path_connected(p, q, occupied=None):
    if occupied is None:
        occupied = game_state["occupied_cells"][0]
    occupied = [x for x in occupied if x != q]
    return q in path_connected_set(p, occupied)

def shortest_path_move(p, q, occupied=None):
    if is_adjacent(p, q):
        return [q]
    if occupied is None:
        occupied = game_state["occupied_cells"][0]
    occupied = [c for c in occupied if c != q]
    if q in path_connected_set(p, occupied):
        dist = path_distance_pq(p, q, occupied)
        layers = path_connected_layers(p, occupied)
        if len(layers) > 1:
            result = [x for x in layers[1] if path_distance_pq(x, q, occupied) == dist-1]
            return result
    return []

def go_straight():
    body = get_coord(game_state["you"]["body"])
    x0,y0 = body[0]
    x1,y1 = body[1]
    x,y = x1-x0, y1-y0
    x,y = -x, -y
    return (x0+x, y0+y)


def prefer_straight(moves):
    if game_state["turn"] >= 3:
        moves = [(move, 0 if get_adjacent_dir(get_my_head(), move) == get_adjacent_dir(get_my_neck(), get_my_head()) else 1) for move in moves]
        moves = first_group(moves)
    return moves

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


#############################################
# end of utility functions
#############################################

def test_run():
    global game_state
    game_state = {}
    game_state["board"] = {}
    game_state["board"]["width"] = 11
    game_state["board"]["height"] = 11
    game_state["occupied_cells"] = [[
        (0,4), (1,4), (2,4), (3,4), (4,4),
        (5,3), (5,2), (5,1), (5,0) 
        ] ]
    a = (0,1)
    layers = []
    occupied = game_state["occupied_cells"][0]
    layer = [[a]]
    start_time = time.time()
    for i in range(100):
        if len(layer) == 0: break 
        #print(i, len(layer))
        layers.append(layer)
        layer = [path+[p] for path in layers[-1] for end in [path[-1]] for p in adj_cells(end) if p not in occupied and p not in path]
    end_time = time.time()
    log_time_diff = end_time - start_time
    log_time_diff = f"time: {log_time_diff:.3f}s"
    print(log_time_diff)
    #for i,layer in enumerate(layers): print(i, len(layer))

    b = (4,3)
    print(b)
    target_paths = [[path for path in layer if path[-1] == b] for layer in layers]
    for i,layer in enumerate(target_paths): print(i, len(layer))
    print()

    b = (4,0)
    print(b)
    target_paths = [[path for path in layer if path[-1] == b] for layer in layers]
    for i,layer in enumerate(target_paths): print(i, len(layer))
    print()

    b = (4,0)
    print(b)
    target_paths = [[path for path in layer if path[-1] == b] for layer in layers]
    for i,layer in enumerate(target_paths): print(i, len(layer))
    print()

if __name__ == "__main__":
    test_run()
