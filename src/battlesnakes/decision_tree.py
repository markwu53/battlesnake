import time
from decision_tree_text import algorithm 
from decision_utility import *
from global_var import game, Node

def experiment_condition():
    if len(game.others) != 1: return False
    if game.others[0]["name"] not in (
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

    game.logger["experiment"] = True
    game.state["start_time"] = time.time()
    assemble_decision_nodes()
    filling_decision_functions()
    decision()
    game.logger["env"] = game.env
    game.state["end_time"] = time.time()
    time_diff = game.state["end_time"] - game.state["start_time"]
    game.logger["time"] = f"{time_diff:.3f}s"
    print(game.logger)

    game.state["next_move"] = get_next_move(game.my_head, game.state["next_head_coord"])
    return True

def filling_decision_functions():
    game.dn["env_1_vs_1?"].gather_info = lambda: game.env.update({"env_1_vs_1?": len(game.board["others"]) == 1})
    game.dn["env_mine_bigger?"].gather_info = lambda: game.env.update({"env_mine_bigger?": (1==1
        and game.my_length > game.other_length
        and game.my_length >= 15
    )})
    game.dn["env_less_than_8?"].gather_info = lambda: game.env.update({"env_less_than_8?": game.my_length < 8})
    game.dn["env_lt8_smaller?"].gather_info = lambda: game.env.update({"env_lt8_smaller?": game.my_length < game.other_length})
    game.dn["env_lt8_len_eq?"].gather_info = lambda: game.env.update({"env_lt8_len_eq?": game.my_length == game.other_length})
    game.dn["env_lt8_enemy_far?"].gather_info = lambda: game.env.update({"env_lt8_enemy_far?": distance_pq(game.my_head, game.other_head) > 6})
    game.dn["env_food_danger_1?"].gather_info = lambda: game.env.update({"env_food_danger_1?": distance_pq(game.my_head, game.other_head) == 2})
    
    def env_food_1():
        adjacent_food = [f for f in game.board["food"] if is_adjacent(f, game.my_head)]
        if len(adjacent_food) != 0:
            game.env["adjacent_food"] = adjacent_food
            game.env["env_food_1?"] = True
        else:
            game.env["env_food_1?"] = False

    game.dn["env_food_1?"].gather_info = env_food_1

    def eat():
        moves = game.env["adjacent_food"]
        moves = prefer_straight(moves)
        game.env["move"] = moves[0]

    game.dn["eat!"].gather_info = eat

    def env_food_near():
        food_near = [f for f in game.board["food"] if distance_pq(f, game.my_head) <= 8]
        if len(food_near) != 0:
            game.env["food_near"] = food_near
            game.env["env_food_near?"] = True
        else:
            game.env["env_food_near?"] = False

    game.dn["env_food_near?"].gather_info = env_food_near

    def env_food_closer():
        food_near = game.env["food_near"]
        food_closer = [f for f in food_near if path_distance_pq(game.my_head, f) < path_distance_pq(game.other_head, f)]
        if len(food_closer) != 0:
            game.env["food_closer"] = food_closer
            game.env["env_food_closer?"] = True
        else:
            game.env["env_food_closer?"] = False

    game.dn["env_food_closer?"].gather_info = env_food_closer

    def env_danger_1():
        if distance_pq(game.my_head, game.other_head) == 2:
            if game.my_length <= game.other_length:
                game.env["env_danger_1?"] = True
                return
        game.env["env_danger_1?"] = True

    game.dn["env_danger_1?"].gather_info = env_danger_1

    def goto_food():
        food_closer = game.env["food_closer"]
        food_closer = [(f, path_distance_pq(game.my_head, f)) for f in food_closer]
        foods = first_group(food_closer)
        food_target = foods[0]
        moves = shortest_path_move(game.my_head, food_target)
        moves = prefer_straight(moves)
        game.env["move"] = moves[0]

    game.dn["goto_food!"].gather_info = goto_food

    def goto_food2():
        food_near = game.env["food_near"]
        other_rank = [(f, path_distance_pq(game.other_head, f)) for f in food_near]
        other_first_group = first_group(other_rank)
        my_food = [f for f in food_near if f not in other_first_group]
        if len(my_food) != 0:
            game.env["my_food"] = my_food
            my_rank = [(f, path_distance_pq(game.my_head, f)) for f in my_food]
            my_first_group = first_group(my_rank)
            food_target = my_first_group[0]
        else:
            food_target = food_near[0]
        game.env["food_target"] = food_target
        moves = shortest_path_move(game.my_head, food_target)
        moves = prefer_straight(moves)
        game.env["move"] = moves[0]

    game.dn["goto_food2!"].gather_info = goto_food2

    def routine_move():
        moves = game.node.moves
        moves = prefer_more_next_moves(moves)
        moves = prefer_straight(moves)
        game.env["move"] = moves[0]

    game.dn["routine_move!"].gather_info = routine_move

def assemble_decision_nodes():

    rules = algorithm.split("\n")
    rules = [r.strip() for r in rules if len(r.strip()) > 0]
    rules = [r for r in rules if not r.startswith("#")]
    rules = [r.split("=") for r in rules]
    rules = [(a.strip(),b.strip()) for a, b in rules]
    #for rule in rules: print(rule)
    root = None
    for a, b in rules:
        if b in game.dn: continue

        #create game.dn
        game.dn[b] = Node(b)

        if b.startswith("env_"):
            game.dn[b].question = lambda a, key=b: game.env[key]
        elif "?" in b:
            #regular question
            pass
        elif "!" in b:
            #this is a terminal node
            #the question MUST have exactly one yes answer
            game.dn[b].question = lambda a: a == game.env["move"]
        else:
            #it's a label not a question
            game.dn[b].question = lambda a: True #pass through
    
    #create tree link
    for a, b in rules:
        if a == "BEGIN":
            game.state["decision_root"] = game.dn[b]
        elif "+" in a:
            a = a.replace("+", "?")
            game.dn[a].yes = game.dn[b]
        elif "-" in a:
            a = a.replace("-", "?")
            game.dn[a].no = game.dn[b]
        else:
            #it's a label not a question
            game.dn[a].yes = game.dn[b]
            game.dn[a].no = game.dn[b]


def decision():

    #estimated 5-step occupied cells
    game.state["occupied_cells"] = [
        occupied_cells(step)
        for step in [1,2,3,4,5]
    ]

    game.my_head = get_my_head()
    my_neck = get_my_neck()

    allowed_moves = [p for p in adj_cells(game.my_head) if p not in game.state["occupied_cells"][0]]
    game.logger["allowed_moves"] = allowed_moves

    if len(allowed_moves) == 0:
        #no moves available, die on myself
        game.state["next_head_coord"] = my_neck
        return
    
    if len(allowed_moves) == 1:
        game.state["next_head_coord"] = allowed_moves[0]
        return
    
    #2 or 3 choices
    node = game.state["decision_root"]
    node.moves = allowed_moves
    game.logger["decision_path"] = []

    while True:
        game.node = node
        node.gather_info()
        print(node.question_description)
        yes_group = [a for a in node.moves if node.question(a)]
        if len(yes_group) == 1:
            game.logger["decision_path"].append(f"{node.question_description}")
            game.state["next_head_coord"] = yes_group[0]
            return
        if len(yes_group) > 1:
            game.logger["decision_path"].append(f"{node.question_description}: Y")
            node = node.yes
            node.moves = yes_group
        else:
            game.logger["decision_path"].append(f"{node.question_description}: N")
            moves = node.moves
            node = node.no
            node.moves = moves

def prefer_straight(moves):
    if game.state["turn"] <= 3:
        return moves
    moves = [(move, 0 if get_adjacent_dir(get_my_head(), move) == get_adjacent_dir(get_my_neck(), get_my_head()) else 1) for move in moves]
    moves = first_group(moves)
    return moves

def prefer_more_next_moves(moves):
    moves = [(move, len([p for p in adj_cells(move) if p not in game.state["occupied_cells"][0]])) for move in moves]
    moves = first_group(moves, reverse=True)
    return moves

def initialize_game_state(state):
    game.state = state
    game.logger = {}
    game.me = {
            "name": game.state["you"]["name"],
            "health": game.state["you"]["health"],
            "body": get_coord(game.state["you"]["body"]),
        }
    game.snakes = [
            {
                "name": snake["name"],
                "health": snake["health"],
                "body": get_coord(snake["body"]),
            }
            for snake in game.state["board"]["snakes"]
        ]
    game.others = [snake for snake in game.snakes if snake["body"][0] != game.me["body"][0]]
    game.board = {
        "id": game.state["game"]["id"],
        "turn": game.state["turn"],
        "me": game.me,
        "others": game.others,
        "food": get_coord(game.state["board"]["food"]),
    }
    game.logger["board"] = game.board
    game.my_head = game.me["body"][0]
    game.my_neck = game.me["body"][1]
    game.my_tail = game.me["body"][-1]
    game.other_head = game.others[0]["body"][0]
    game.other_neck = game.others[0]["body"][1]
    game.other_tail = game.others[0]["body"][-1]
    game.my_length = len(game.me["body"])
    game.other_length = len(game.others[0]["body"])


###########################################
# test
###########################################

def init_from_log():
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 16, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(9, 7), (9, 6), (8, 6), (8, 5), (8, 4)]}, 'others': [{'name': 'Snakeformatika', 'health': 98, 'body': [(6, 6), (6, 7), (7, 7), (7, 6), (7, 5), (7, 4)]}], 'food': [(3, 5), (0, 0)]}, 'experiment': True, 'allowed_moves': [(10, 7), (8, 7), (9, 8)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: Y', 'env_lt8_enemy_far?: N', 'env_lt8_food_1?: N', 'env_food_near?: N', 'routine_move!'], 'time': '0.000s'}
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 3, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(0, 3), (0, 4), (1, 4), (1, 5)]}, 'others': [{'name': 'Snakeformatika', 'health': 99, 'body': [(4, 9), (4, 10), (5, 10), (5, 9)]}], 'food': [(5, 5), (8, 3)]}, 'experiment': True, 'allowed_moves': [(1, 3), (0, 2)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: N', 'env_food_near?: Y', 'goto_food!'], 'time': '0.002s'}
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 7, 'me': {'name': 'mark_snake', 'health': 95, 'body': [(4, 3), (3, 3), (2, 3), (1, 3)]}, 'others': [{'name': 'Snakeformatika', 'health': 95, 'body': [(5, 6), (5, 7), (5, 8), (4, 8)]}], 'food': [(5, 5), (8, 3)]}, 'experiment': True, 'allowed_moves': [(5, 3), (4, 4), (4, 2)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: N', 'env_food_near?: Y', 'goto_food!'], 'time': '0.002s'}
    log = {'board': {'id': '19fa9bec-610a-4fa1-93fb-3e591b305598', 'turn': 8, 'me': {'name': 'mark_snake', 'health': 94, 'body': [(5, 3), (4, 3), (3, 3), (2, 3)]}, 'others': [{'name': 'Snakeformatika', 'health': 100, 'body': [(5, 5), (5, 6), (5, 7), (5, 8), (5, 8)]}], 'food': [(8, 3)]}, 'experiment': True, 'allowed_moves': [(6, 3), (5, 4), (5, 2)], 'decision_path': ['env_1_vs_1?: Y', 'env_mine_bigger?: N', 'env_less_than_8?: Y', 'env_lt8_smaller?: Y', 'env_lt8_enemy_far?: N', 'env_lt8_food_1?: N', 'env_food_near?: Y', 'goto_food!'], 'time': '0.002s'}
    game.board = log["board"]
    game.state = {}
    game.state["turn"] = game.board["turn"]
    game.state["game"] = {}
    game.state["game"]["id"] = game.board["id"]
    game.state["board"] = {}
    game.state["board"]["width"] = 11
    game.state["board"]["height"] = 11
    game.state["you"] = {}
    game.state["you"]["name"] = game.board["me"]["name"]
    game.state["you"]["health"] = game.board["me"]["health"]
    game.state["you"]["body"] = [{"x": x, "y": y} for x,y in game.board["me"]["body"]]
    others = [
        {
            "name": snake["name"],
            "health": snake["health"],
            "body": [{"x": x, "y": y} for x,y in snake["body"]]
        } for snake in game.board["others"]
    ]
    game.state["board"]["snakes"] = [game.state["you"], *others]
    game.state["board"]["food"] = [{"x": x, "y": y} for x,y in game.board["food"]]
    return game.state

def test_run():
    state = init_from_log()
    special_experimenting_code(state)

if __name__ == "__main__":
    test_run()
