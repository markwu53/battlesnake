import time
from decision_tree_text import algorithm 
import snake_utility as ut
from snake_utility import *

game_state = None
logger = None
board = None


def experiment_condition():
    if len(board["others"]) != 1: return False
    if board["others"][0]["name"] not in (
        "Snakeformatika",
        #"Wim HU [dev]",
        #"Frank The Tank",

    ): 
        return False
    return True

#experimental code entry point
def special_experimenting_code(game_state):
    initialize_game_state(game_state)
    if not experiment_condition(): return False

    logger["experiment"] = True
    game_state["start_time"] = time.time()
    decision()
    logger["env"] = game_state["env"]
    game_state["end_time"] = time.time()
    time_diff = game_state["end_time"] - game_state["start_time"]
    logger["time"] = f"{time_diff:.3f}s"
    print(logger)

    game_state["next_move"] = get_next_move(get_my_head(), game_state["next_head_coord"])
    return True

def filling_decision_functions():
    my_head = get_my_head()
    my_neck = get_my_neck()
    my_tail = get_my_tail()
    other_head = board["others"][0]["body"][0]
    other_tail = board["others"][0]["body"][-1]

    game_state["env"] = {}

    dt = game_state["decision_tree"]
    env = game_state["env"]

    dt["env_1_vs_1?"].gather_info = lambda: env.update({"env_1_vs_1?": len(board["others"]) == 1})
    dt["env_mine_bigger?"].gather_info = lambda: env.update({"env_mine_bigger?": (1==1
        and len(board["me"]["body"]) > len(board["others"][0]["body"])
        and len(board["me"]["body"]) >= 15
    )})
    dt["env_less_than_8?"].gather_info = lambda: env.update({"env_less_than_8?": len(board["me"]["body"]) < 8})
    dt["env_lt8_smaller?"].gather_info = lambda: env.update({"env_lt8_smaller?": len(board["me"]["body"]) < len(board["others"][0]["body"])})
    dt["env_lt8_enemy_far?"].gather_info = lambda: env.update({"env_lt8_enemy_far?": distance_pq(my_head, other_head) > 6})
    
    def env_lt8_food_1():
        adjacent_food = [f for f in board["food"] if is_adjacent(f, my_head)]
        if len(adjacent_food) != 0:
            env["adjacent_food"] = adjacent_food
            env["env_lt8_food_1?"] = True
        else:
            env["env_lt8_food_1?"] = False

    dt["env_lt8_food_1?"].gather_info = env_lt8_food_1

    def eat():
        moves = env["adjacent_food"]
        moves = prefer_straight(moves)
        env["move"] = moves[0]

    dt["eat!"].gather_info = eat

    def env_food_near():
        food_near = [f for f in board["food"] if distance_pq(f, my_head) <= 8]
        if len(food_near) != 0:
            env["food_near"] = food_near
            env["env_food_near?"] = True
        else:
            env["env_food_near?"] = False

    dt["env_food_near?"].gather_info = env_food_near

    def env_food_closer():
        food_near = env["food_near"]
        food_closer = [f for f in food_near if path_distance_pq(my_head, f) < path_distance_pq(other_head, f)]
        if len(food_closer) != 0:
            env["food_closer"] = food_closer
            env["env_food_closer?"] = True
        else:
            env["env_food_closer?"] = False

    dt["env_food_closer?"].gather_info = env_food_closer

    def goto_food():
        food_closer = env["food_closer"]
        food_closer = [(f, path_distance_pq(my_head, f)) for f in food_closer]
        foods = first_group(food_closer)
        food_target = foods[0]
        moves = shortest_path_move(my_head, food_target)
        moves = prefer_straight(moves)
        env["move"] = moves[0]

    dt["goto_food!"].gather_info = goto_food

    def goto_food2():
        food_near = env["food_near"]
        other_rank = [(f, path_distance_pq(other_head, f)) for f in food_near]
        other_first_group = first_group(other_rank)
        my_food = [f for f in food_near if f not in other_first_group]
        if len(my_food) != 0:
            env["my_food"] = my_food
            my_rank = [(f, path_distance_pq(my_head, f)) for f in my_food]
            my_first_group = first_group(my_rank)
            food_target = my_first_group[0]
        else:
            food_target = food_near[0]
        env["food_target"] = food_target
        moves = shortest_path_move(my_head, food_target)
        moves = prefer_straight(moves)
        env["move"] = moves[0]

    dt["goto_food2!"].gather_info = goto_food2

    def routine_move():
        moves = game_state["node"].moves
        moves = prefer_more_next_moves(moves)
        moves = prefer_straight(moves)
        env["move"] = moves[0]

    dt["routine_move!"].gather_info = routine_move

def assemble_decision_tree():

    nodes = {}
    game_state["decision_tree"] = nodes
    rules = algorithm.split("\n")
    rules = [r.strip() for r in rules if len(r.strip()) > 0]
    rules = [r for r in rules if not r.startswith("#")]
    rules = [r.split("=") for r in rules]
    rules = [(a.strip(),b.strip()) for a, b in rules]
    #for rule in rules: print(rule)
    root = None
    for a, b in rules:
        if b in nodes: continue
        nodes[b] = Node(b)

        if b.startswith("env_"):
            nodes[b].question = lambda a, key=b: game_state["env"][key]
        elif "?" in b:
            #regular question
            pass
        elif "!" in b:
            #this is a terminal node
            #the question MUST have exactly one yes answer
            nodes[b].question = lambda a: a == game_state["env"]["move"]
        else:
            nodes[b].question = lambda a: True #pass through
    for a, b in rules:
        if "+" in a:
            a = a.replace("+", "?")
            nodes[a].yes = nodes[b]
        elif "-" in a:
            a = a.replace("-", "?")
            nodes[a].no = nodes[b]
        elif a == "BEGIN":
            game_state["decision_root"] = nodes[b]
        else:
            nodes[a].yes = nodes[b]
            nodes[a].no = nodes[b]

    filling_decision_functions()

def decision():
    assemble_decision_tree()

    #estimated 5-step occupied cells
    game_state["occupied_cells"] = [
        occupied_cells(step)
        for step in [1,2,3,4,5]
    ]

    my_head = get_my_head()
    my_neck = get_my_neck()

    allowed_moves = [p for p in adj_cells(my_head) if p not in game_state["occupied_cells"][0]]
    logger["allowed_moves"] = allowed_moves

    if len(allowed_moves) == 0:
        #no moves available, die on myself
        game_state["next_head_coord"] = my_neck
        return
    
    if len(allowed_moves) == 1:
        game_state["next_head_coord"] = allowed_moves[0]
        return
    
    #2 or 3 choices
    node = game_state["decision_root"]
    node.moves = allowed_moves
    logger["decision_path"] = []

    while True:
        game_state["node"] = node
        node.gather_info()
        yes_group = [a for a in node.moves if node.question(a)]
        if len(yes_group) == 1:
            logger["decision_path"].append(f"{node.question_description}")
            game_state["next_head_coord"] = yes_group[0]
            return
        if len(yes_group) > 1:
            logger["decision_path"].append(f"{node.question_description}: Y")
            node = node.yes
            node.moves = yes_group
        else:
            logger["decision_path"].append(f"{node.question_description}: N")
            moves = node.moves
            node = node.no
            node.moves = moves

def prefer_straight(moves):
    if game_state["turn"] <= 3:
        return moves
    moves = [(move, 0 if get_adjacent_dir(get_my_head(), move) == get_adjacent_dir(get_my_neck(), get_my_head()) else 1) for move in moves]
    moves = first_group(moves)
    return moves

def prefer_more_next_moves(moves):
    moves = [(move, len([p for p in adj_cells(move) if p not in game_state["occupied_cells"][0]])) for move in moves]
    moves = first_group(moves, reverse=True)
    return moves

def nothing():
    # Placeholder for a function that does nothing
    pass

class Node:
    def __init__(self, question_description):
        self.question_description = question_description
        self.gather_info = nothing
        self.question = None
        self.yes = None
        self.no = None
        self.moves = None

def initialize_game_state(state):
    global game_state, logger, board
    ut.game_state = state
    game_state = state
    game_state["logger"] = {}
    logger = game_state["logger"]
    me = {
            "name": game_state["you"]["name"],
            "health": game_state["you"]["health"],
            "body": get_coord(game_state["you"]["body"]),
        }
    snakes = [
            {
                "name": snake["name"],
                "health": snake["health"],
                "body": get_coord(snake["body"]),
            }
            for snake in game_state["board"]["snakes"]
        ]
    others = [snake for snake in snakes if snake["body"][0] != me["body"][0]]
    board = {
        "id": game_state["game"]["id"],
        "turn": game_state["turn"],
        "me": me,
        "others": others,
        "food": get_coord(game_state["board"]["food"]),
    }
    logger["board"] = board
    game_state["me"] = board["me"]
    game_state["others"] = board["others"]
    game_state["snakes"] = [board["me"], *board["others"]]


###########################################
# test
###########################################

def init_from_log():
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 16, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(9, 7), (9, 6), (8, 6), (8, 5), (8, 4)]}, 'others': [{'name': 'Snakeformatika', 'health': 98, 'body': [(6, 6), (6, 7), (7, 7), (7, 6), (7, 5), (7, 4)]}], 'food': [(3, 5), (0, 0)]}, 'experiment': True, 'allowed_moves': [(10, 7), (8, 7), (9, 8)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: Y', 'env_lt8_enemy_far?: N', 'env_lt8_food_1?: N', 'env_food_near?: N', 'routine_move!'], 'time': '0.000s'}
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 3, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(0, 3), (0, 4), (1, 4), (1, 5)]}, 'others': [{'name': 'Snakeformatika', 'health': 99, 'body': [(4, 9), (4, 10), (5, 10), (5, 9)]}], 'food': [(5, 5), (8, 3)]}, 'experiment': True, 'allowed_moves': [(1, 3), (0, 2)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: N', 'env_food_near?: Y', 'goto_food!'], 'time': '0.002s'}
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 7, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(4, 3), (3, 3), (2, 3), (1, 3)]}, 'others': [{'name': 'Snakeformatika', 'health': 95, 'body': [(5, 6), (5, 7), (5, 8), (4, 8)]}], 'food': [(5, 5), (8, 3)]}, 'experiment': True, 'allowed_moves': [(5, 3), (4, 4), (4, 2)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: N', 'env_food_near?: Y', 'goto_food!'], 'time': '0.002s'}
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 8, 'me': {'name': 'mark_snake', 'health': 94, 'body': [(5, 3), (4, 3), (3, 3), (2, 3)]}, 'others': [{'name': 'Snakeformatika', 'health': 100, 'body': [(5, 5), (5, 6), (5, 7), (5, 8), (5, 8)]}], 'food': [(8, 3)]}, 'experiment': True, 'allowed_moves': [(6, 3), (5, 4), (5, 2)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: Y', 'env_lt8_enemy_far?: N', 'env_lt8_food_1?: N', 'env_food_near?: Y', 'goto_food!'], 'time': '0.002s'}
    board = log["board"]
    game_state = {}
    game_state["turn"] = board["turn"]
    game_state["game"] = {}
    game_state["game"]["id"] = board["id"]
    game_state["board"] = {}
    game_state["board"]["width"] = 11
    game_state["board"]["height"] = 11
    game_state["you"] = {}
    game_state["you"]["name"] = board["me"]["name"]
    game_state["you"]["health"] = board["me"]["health"]
    game_state["you"]["body"] = [{"x": x, "y": y} for x,y in board["me"]["body"]]
    others = [
        {
            "name": snake["name"],
            "health": snake["health"],
            "body": [{"x": x, "y": y} for x,y in snake["body"]]
        } for snake in board["others"]
    ]
    game_state["board"]["snakes"] = [game_state["you"], *others]
    game_state["board"]["food"] = [{"x": x, "y": y} for x,y in board["food"]]
    return game_state

def test_run():
    state = init_from_log()
    special_experimenting_code(state)

if __name__ == "__main__":
    test_run()
