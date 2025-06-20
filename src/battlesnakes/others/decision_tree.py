import time
from others.decision_tree_text import algorithm 
import others.utility_functions
from others.utility_functions import *

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
    dt["env_lt8_enemy_far?"].gather_info = lambda: env.update({"env_lt8_enemy_far?": distance_pq(my_head, other_head) > 8})
    
    def env_lt8_food_1():
        adjacent_food = [f for f in board["food"] if is_adjacent(f, my_head)]
        if len(adjacent_food) != 0:
            env["adjacent_food"] = adjacent_food
            env["env_lt8_food_1?"] = True
        env["env_lt8_food_1?"] = False

    dt["env_lt8_food_1?"].gather_info = env_lt8_food_1

    def eat():
        moves = env["adjacent_food"]
        moves = prefer_straight(moves)
        env["move"] = moves[0]

    dt["eat!"].gather_info = eat

    def env_food_near():
        food_near = [f for f in board["food"] if distance_pq(f, my_head) <= 8]
        food_near = [(f, d) for f in food_near for d in [path_distance_pq(f, my_head)] if d <= 8]
        if len(food_near) != 0:
            env["food_near"] = first_group(food_near)
            env["env_food_near?"] = True
        env["env_food_near?"] = False

    dt["env_food_near?"].gather_info = env_food_near

    def prefer_straight(moves):
        if game_state["turn"] <= 3:
            return moves
        moves = [(move, 0 if get_adjacent_dir(my_head, move) == get_adjacent_dir(my_neck, my_head) else 1) for move in moves]
        moves = first_group(moves)
        return moves

    def prefer_more_next_moves(moves):
        moves = [(move, len([p for p in adj_cells(move) if p not in game_state["occupied_cells"][0]])) for move in moves]
        moves = first_group(moves, reverse=True)
        return moves

    def goto_food():
        food_target = env["food_near"][0]
        moves = shortest_path_move(my_head, food_target)
        moves = prefer_straight(moves)
        env["move"] = moves[0]

    dt["goto_food!"].gather_info = goto_food

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
    others.utility_functions.game_state = state
    game_state = state
    game_state["logger"] = {}
    logger = game_state["logger"]
    board = {
        "id": game_state["game"]["id"],
        "turn": game_state["turn"],
        "me": {
            "name": game_state["you"]["name"],
            "health": game_state["you"]["health"],
            "body": get_coord(game_state["you"]["body"]),
        },
        "others": [
            {
                "name": snake["name"],
                "health": snake["health"],
                "body": get_coord(snake["body"]),
            }
            for snake in game_state["board"]["snakes"]
            if snake["id"] != game_state["you"]["id"]
        ],
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
    return None

def test_run():
    state = init_from_log()
    special_experimenting_code(state)

if __name__ == "__main__":
    test_run()
