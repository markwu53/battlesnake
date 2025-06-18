import typing
import time
from itertools import product, groupby
import snake_utility
from snake_utility import *
from snake_1v1 import decision_1_v_1
from snake_1vn import decision_1_v_n

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

#def move(game_state: typing.Dict) -> typing.Dict:
def special_experimenting_code(game_state):
    snake_utility.game_state = game_state

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
            connected = path_connected_set(p)
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



    def logging():
        log_board = {
            "id": game_state["game"]["id"],
            "turn": game_state["turn"],
            "me": {
                "name": game_state["me"]["name"],
                "length": len(game_state["me"]["body"]),
                "head": game_state["me"]["body"][0],
                "health": game_state["me"]["health"],
                "body": game_state["me"]["body"],
            },
            "others": [ {
                "name": snake["name"],
                "length": len(snake["body"]),
                "head": snake["body"][0],
                "health": snake["health"],
                "body": snake["body"],
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


def test_init_game():
    log = {'version': 'Experiment', 'board': {'id': 'f555bfef-d447-46ab-8fa7-08f8181fe2be', 'turn': 355, 'me': {
        'name': 'mark_snake', 'length': 29, 'head': (6, 1), 'health': 97, 
        'body': [(6, 1), (7, 1), (7, 2), (6, 2), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (9, 9), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8), (3, 7), (3, 6)]}, 
        'others': [{'name': 'Snakeformatika', 'length': 26, 'head': (2, 9), 'health': 89, 'body': [(2, 9), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), (2, 2), (1, 2), (1, 3), (1, 4), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (8, 1), (9, 1)]}]}, 'move': 'left', 'routine_move': (5, 1), 'allowed_move': [(5, 1)], 'danger_ranking': {(5, 1): {'collision_1': 99, 'collision_2': 99, 'trap': True, 'dead_end': 21, 'cut_info': [([(2, 9), (3, 9)], 21)], 'see_my_tail': True, 'see_other_head': False, 'see_other_tail': False, 'allowed_moves': 1}}, 'decision_path': ['base', 'has_cut my_tail'], 'food_decision': [], 'time': '0.026s'}
    log = {'version': 'Experiment', 'board': {'id': 'f555bfef-d447-46ab-8fa7-08f8181fe2be', 
                                              'turn': 356, 'me': {
        'name': 'mark_snake', 'length': 29, 'head': (6, 1), 'health': 96, 
        'body': [(5, 1), (6, 1), (7, 1), (7, 2), (6, 2), (5, 2), (5, 3), (5, 4), (5, 5), 
                 (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (10, 7), (10, 8), (10, 9), 
                 (10, 10), (9, 10), (9, 9), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8), (3, 7), ]}, 
        'others': [{'name': 'Snakeformatika', 'length': 26, 'head': (2, 9), 'health': 88, 
                    'body': [(1, 9), (2, 9), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), 
                             (2, 2), (1, 2), (1, 3), (1, 4), (0, 4), (0, 3), (0, 2), (0, 1), 
                             (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (8, 1), ]}]}, 'move': 'left', 'routine_move': (5, 1), 'allowed_move': [(5, 1)], 'danger_ranking': {(5, 1): {'collision_1': 99, 'collision_2': 99, 'trap': True, 'dead_end': 21, 'cut_info': [([(2, 9), (3, 9)], 21)], 'see_my_tail': True, 'see_other_head': False, 'see_other_tail': False, 'allowed_moves': 1}}, 
                    'decision_path': ['base', 'has_cut my_tail'], 'food_decision': [], 'time': '0.026s'}
    log = {'version': 'Experiment', 'board': {'id': 'f555bfef-d447-46ab-8fa7-08f8181fe2be', 
                                              'turn': 357, 'me': {
        'name': 'mark_snake', 'length': 29, 'head': (6, 1), 'health': 95, 
        'body': [(4, 1), (5, 1), (6, 1), (7, 1), (7, 2), (6, 2), (5, 2), (5, 3), (5, 4), (5, 5), 
                 (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (10, 7), (10, 8), (10, 9), 
                 (10, 10), (9, 10), (9, 9), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8), ]}, 
        'others': [{'name': 'Snakeformatika', 'length': 26, 'head': (2, 9), 'health': 87, 
                    'body': [(1, 10), (1, 9), (2, 9), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), 
                             (2, 2), (1, 2), (1, 3), (1, 4), (0, 4), (0, 3), (0, 2), (0, 1), 
                             (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), ]}]}, 'move': 'left', 'routine_move': (5, 1), 'allowed_move': [(5, 1)], 'danger_ranking': {(5, 1): {'collision_1': 99, 'collision_2': 99, 'trap': True, 'dead_end': 21, 'cut_info': [([(2, 9), (3, 9)], 21)], 'see_my_tail': True, 'see_other_head': False, 'see_other_tail': False, 'allowed_moves': 1}}, 
                    'decision_path': ['base', 'has_cut my_tail'], 'food_decision': [], 'time': '0.026s'}
    log2 = {'version': 'Experiment', 'board': {'id': 'f555bfef-d447-46ab-8fa7-08f8181fe2be', 
                                              'turn': 358, 'me': {
        'name': 'mark_snake', 'length': 29, 'head': (6, 1), 'health': 94, 
        'body': [(3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (7, 2), (6, 2), (5, 2), (5, 3), (5, 4), (5, 5), 
                 (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (10, 7), (10, 8), (10, 9), 
                 (10, 10), (9, 10), (9, 9), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), ]}, 
        'others': [{'name': 'Snakeformatika', 'length': 26, 'head': (2, 9), 'health': 86, 
                    'body': [(2, 10), (1, 10), (1, 9), (2, 9), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), 
                             (2, 2), (1, 2), (1, 3), (1, 4), (0, 4), (0, 3), (0, 2), (0, 1), 
                             (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), ]}]}, 'move': 'left', 'routine_move': (5, 1), 'allowed_move': [(5, 1)], 'danger_ranking': {(5, 1): {'collision_1': 99, 'collision_2': 99, 'trap': True, 'dead_end': 21, 'cut_info': [([(2, 9), (3, 9)], 21)], 'see_my_tail': True, 'see_other_head': False, 'see_other_tail': False, 'allowed_moves': 1}}, 
                    'decision_path': ['base', 'has_cut my_tail'], 'food_decision': [], 'time': '0.026s'}
    game_state = {}
    game_state["game"] = {}
    game_state["game"]["id"] = log["board"]["id"]
    game_state["board"] = {}
    game_state["turn"] = log["board"]["turn"]
    game_state["board"]["width"] = 11
    game_state["board"]["height"] = 11

    game_state["you"] = {}
    game_state["you"]["name"] = log["board"]["me"]["name"]
    game_state["you"]["length"] = log["board"]["me"]["length"]
    game_state["you"]["health"] = log["board"]["me"]["health"]
    game_state["you"]["body"] = [{"x":x, "y":y} for x,y in log["board"]["me"]["body"]]

    game_state["board"]["snakes"] = [
        game_state["you"],
        *[ { "name": snake["name"],
                "length": snake["length"],
                "health": snake["health"],
                "body": [{"x": x, "y": y} for x, y in snake["body"]]
            } for snake in log["board"]["others"] ]
    ]
    game_state["board"]["food"] = []
    return game_state

def run():
    game_state = test_init_game()
    special_experimenting_code(game_state)

if __name__ == "__main__":
    run()