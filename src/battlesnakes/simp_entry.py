import time
from simp_util import *

g = None

def main(game_state):
    global g
    init_game(game_state)
    g = game_state["you"]["var"]
    if not entry_condition(): return False

    g.log["module"] = "simp"
    start_time = time.time()
    #g.e.localtime = time.localtime()

    decision()
    g.state["next_move"] = get_adjacent_dir(g.me.head, g.next_coord)

    #g.log["decision_support"] = {k:v for k,v in g.e.__dict__.items() if v is not None}
    g.log["decision_path"] = g.decision_path
    g.log["next_coord"] = g.next_coord
    g.log["next_move"] = g.state["next_move"]

    end_time = time.time()
    g.log["time"] = f"{end_time-start_time:.3f}s"

    print(g.log)
    return True

def entry_condition():
    return True
    if len(g.snakes) == 1:
        return True
    if len(g.snakes) > 1:
        if all([snake.name == "mark_snake" for snake in g.others]):
            return True
    print("not in this module")
    return False

def decision():
    #estimated 5-step occupied cells
    g.x.occupied_cells = [
        occupied_cells(step)
        for step in [1,2,3,4,5]
    ]
    g.x.allowed_moves = [a for a in adj_cells(g.me.head) if a not in g.x.occupied_cells[0]]

    if len(g.x.allowed_moves) == 0:
        #no allowed moves, die on myself
        g.next_coord = g.me.neck
        return
    
    if len(g.x.allowed_moves) == 1:
        #no choice
        g.next_coord = g.x.allowed_moves[0]
        return

    if len(g.others) == 0:
        #win
        g.next_coord = g.x.allowed_moves[0]
        return

    #allowed_moves must be 2 or 3
    moves = sequential([
        kill_oppotunities,
        avoid_danger,
        get_food,
        other_considerations,
    ])(g.x.allowed_moves)
    g.next_coord = take_first(moves)

def kill_oppotunities(moves):
    return cases([
        collision_kill,
    ])(moves)

def collision_kill(moves):
    others = [snake for snake in g.others if snake.length < g.me.length]
    others = [snake for snake in others if distance_pq(snake.head, g.me.head) == 2]

def avoid_danger(moves):
    return sequential([
        collision_danger,
    ])(moves)

def collision_danger(moves):
    killers = [snake for snake in g.others if snake.length > g.me.length]
    nonkillers = [snake for snake in g.others if snake.length == g.me.length]
    killer_collision_points = [a for a in moves for snake in killers if is_adjacent(a, snake.head)]
    nonkiller_collision_points = [a for a in moves for snake in nonkillers if is_adjacent(a, snake.head)]
    return prefer_no(lambda a: a in nonkiller_collision_points)(
        prefer_no(lambda a: a in killer_collision_points)(moves))

def get_food(moves):
    food_near = [f for f in g.food if distance_pq(f, g.me.head) <= 8]
    food_good = [f for f in food_near if path_connected(f, g.me.head) and all([path_distance_pq(f, g.me.head) < path_distance_pq(f, snake.head) for snake in g.others])]
    if len(food_good) != 0:
        food_better = prefer_by_rank(lambda f: path_distance_pq(f, g.me.head))(food_good)
        food_target = take_first(food_better)
        food_moves = shortest_path_move(g.me.head, food_target)
        return prefer_yes(lambda a: a in food_moves)(moves)

def other_considerations(moves):
    pass

######################################################
# testing
######################################################

def init_from_log(log):

    others = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
            "id": snake.get("id", ""),
        } for snake in log["others"] ]
    me = [ {
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
            "id": snake.get("id", ""),
        } for snake in [log["me"]] ][0]

    game_state = {
        "game": {
                "id": log["id"]
            },
        "turn": log["turn"],
        "you": me,
        "board": {
                "width": 11,
                "height": 11,
                "snakes": [me, *others],
                "food": reverse_coord(log["food"]),
            },
    }
    return game_state

def run():
    log = {'id': '49650c4c-8b0b-40a8-be5a-4312fe526212', 'turn': 104, 'me': {'name': 'mark_snake', 'health': 94, 'body': [(9, 3), (9, 2), (10, 2), (10, 1), (9, 1), (8, 1), (7, 1), (7, 2), (7, 3)]}, 'others': [{'name': 'Frank The Tank', 'health': 100, 'body': [(8, 4), (7, 4), (6, 4), (6, 5), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (9, 9)]}, {'name': 'Kakemonsteret-v2', 'health': 92, 'body': [(3, 3), (3, 2), (2, 2), (2, 1), (2, 0), (1, 0), (1, 1), (1, 2), (1, 3), (2, 3), (2, 4), (1, 4), (1, 5)]}], 'food': [(10, 7)], 'experiment': 'Yes', 'decision_path': ['avoid collision'], 'next_coord': (10, 3), 'next_move': 'right', 'time': '0.001s'}
    log = {'id': 'ef5ac3ef-96d7-420a-8fa6-83f795f281b8', 'turn': 236, 'me': {'name': 'mark_snake', 'health': 89, 'body': [(1, 3), (2, 3), (2, 2), (3, 2), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (9, 8), (9, 9), (8, 9), (8, 10), (7, 10)]}, 'others': [{'name': 'Wim HU [dev]', 'health': 90, 'body': [(1, 5), (1, 4), (2, 4), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (0, 4)]}, {'name': 'Kakemonsteret-v2', 'health': 94, 'body': [(5, 5), (5, 4), (5, 3), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (5, 7), (5, 6), (6, 6), (7, 6), (7, 5), (7, 4), (7, 3), (8, 3), (8, 4)]}], 'food': [(9, 10)], 'experiment': 'Yes', 'decision_path': ['consider wayout', 'wayout point far enough', 'go to open space'], 'next_coord': (1, 2), 'next_move': 'down', 'time': '0.001s'}
    log = {'id': '3104d1b4-d02b-44ac-8cde-510183de0b65', 'turn': 85, 'me': {'name': 'mark_snake', 'health': 88, 'body': [(6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (5, 10), (5, 9)]}, 'others': [{'name': 'Wim HU [dev]', 'health': 100, 'body': [(4, 1), (3, 1), (2, 1), (1, 1), (1, 2), (1, 2)]}, {'name': 'Frank The Tank', 'health': 100, 'body': [(3, 4), (3, 5), (3, 6), (2, 6), (2, 5), (2, 4), (2, 3), (3, 3), (3, 2), (4, 2), (4, 2)]}, {'name': 'Kakemonsteret-v2', 'health': 84, 'body': [(7, 2), (8, 2), (8, 1), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6)]}], 'food': [(10, 8)], 'experiment': 'Yes', 'decision_path': ['split choice', 'no confinement - need further consideration'], 'next_coord': (5, 3), 'next_move': 'left', 'time': '0.002s'}
    log = {'id': '94700155-0f20-482a-b882-0267239a9a0c', 'turn': 210, 'me': {'name': 'mark_snake', 'health': 87, 'body': [(4, 6), (4, 5), (4, 4), (5, 4), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (7, 8), (8, 8), (8, 9)]}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 97, 'body': [(8, 0), (7, 0), (7, 1), (7, 2), (7, 3), (8, 3), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (10, 8), (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (10, 2), (10, 1), (10, 0), (9, 0)]}, {'name': 'snakey_wakey', 'health': 90, 'body': [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (2, 2), (3, 2), (3, 3), (3, 4), (3, 5), (2, 5), (1, 5), (1, 4), (1, 3)]}, {'name': 'soma-mini v1[standard]', 'health': 84, 'body': [(4, 8), (4, 9), (3, 9), (2, 9), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (1, 7), (2, 7), (3, 7)]}], 'food': [(0, 2), (6, 9), (2, 3)], 'module': 'functional2', 'decision_path': ['avoid collision'], 'next_coord': (5, 6), 'next_move': 'right', 'time': '0.005s'}
    log = {'id': '0d7da7b2-c47e-435c-b80d-f48b7e5f66bc', 'turn': 115, 'me': {'name': 'mark_snake', 'health': 96, 'body': [(0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (1, 3), (1, 4), (1, 5), (1, 6), (2, 6), (2, 5), (2, 4), (2, 3)]}, 'others': [{'name': 'Würmchen', 'health': 15, 'body': [(8, 1), (8, 2), (8, 3), (7, 3), (6, 3), (6, 2)]}, {'name': 'snakey_wakey', 'health': 91, 'body': [(3, 4), (3, 5), (3, 6), (3, 7), (4, 7), (4, 6), (5, 6), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5)]}, {'name': 'Wim HU', 'health': 84, 'body': [(3, 8), (4, 8), (4, 9), (5, 9), (6, 9), (6, 8), (6, 7), (7, 7), (8, 7), (8, 6), (9, 6), (9, 7)]}], 'food': [(7, 2), (4, 2)], 'module': 'functional2', 'decision_path': [], 'next_coord': (1, 7), 'next_move': 'right', 'time': '0.002s'}
    log = {'id': '3c112738-4775-4965-9d95-b7a53108fa6e', 'turn': 29, 'me': {'name': 'mark_snake', 'health': 79, 'body': [(7, 6), (7, 5), (7, 4), (7, 3), (7, 2)]}, 'others': [{'name': 'FerralSnake-standard', 'health': 97, 'body': [(5, 8), (6, 8), (6, 9), (6, 10), (5, 10)]}, {'name': 'Wim HU', 'health': 83, 'body': [(3, 4), (3, 3), (3, 2), (3, 1), (3, 0)]}, {'name': 'suboptimal', 'health': 96, 'body': [(7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (9, 9), (9, 8), (9, 7)]}], 'food': [(4, 4), (5, 7), (3, 9)], 'module': 'functional2', 'decision_path': ['go to open space (5, 5)'], 'next_coord': (6, 6), 'next_move': 'left', 'time': '0.068s'}
    log = {'id': '7a0129ad-a8ea-427f-869c-a8281d54fcec', 'turn': 153, 'me': {'name': 'mark_snake', 'health': 89, 'body': [(4, 9), (4, 10), (5, 10), (6, 10), (6, 9), (7, 9), (7, 8), (6, 8), (5, 8), (5, 7), (6, 7), (7, 7), (7, 6), (6, 6), (5, 6), (4, 6)]}, 'others': [{'name': 'FerralSnake-standard', 'health': 73, 'body': [(2, 3), (2, 4), (3, 4), (3, 3), (4, 3), (4, 4), (5, 4), (5, 3), (5, 2)]}, {'name': 'rustiger', 'health': 82, 'body': [(10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (8, 10), (8, 9), (9, 9), (9, 8), (9, 7), (9, 6), (9, 5), (8, 5), (7, 5)]}, {'name': 'Snakeformatika', 'health': 96, 'body': [(2, 7), (2, 6), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (2, 10), (1, 10)]}], 'food': [(8, 6), (9, 2)], 'module': 'functional2', 'decision_path': ["don't go in trap [(4, 8)]"], 'next_coord': (5, 9), 'next_move': 'right', 'time': '0.000s'}
    log = {'id': '27f2baaf-30e2-4314-8173-b5fbe5cc403b', 'turn': 52, 'me': {'name': 'mark_snake', 'health': 52, 'body': [(9, 7), (10, 7), (10, 8), (9, 8)]}, 'others': [{'name': 'snakey_wakey', 'health': 90, 'body': [(1, 7), (2, 7), (3, 7), (3, 6), (4, 6), (4, 5), (4, 4), (4, 3), (5, 3), (6, 3)]}, {'name': 'Snakeformatika', 'health': 92, 'body': [(0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, 10)]}, {'name': 'Hovering Hobbs', 'health': 88, 'body': [(7, 5), (7, 6), (7, 7), (7, 8), (6, 8), (5, 8)]}], 'food': [(6, 1), (0, 3), (10, 6)], 'module': 'functional2', 'decision_path': ['killer near', 'go to food'], 'next_coord': (9, 6), 'next_move': 'down', 'time': '0.010s'}
    log = {'id': '06c3573a-c6b9-45c2-b5f0-8505719d89fc', 'turn': 130, 'me': {'name': 'mark_snake', 'health': 93, 'body': [(9, 1), (8, 1), (7, 1), (6, 1), (5, 1), (5, 0), (4, 0), (3, 0), (3, 1), (2, 1)]}, 'others': [{'name': 'snakey_wakey', 'health': 59, 'body': [(7, 3), (6, 3), (5, 3), (4, 3), (4, 4), (4, 5), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6)]}, {'name': 'rustiger', 'health': 96, 'body': [(1, 3), (1, 2), (2, 2), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8)]}], 'food': [(5, 10), (8, 0)], 'module': 'functional2', 'decision_path': ['killer near', 'go to food'], 'next_coord': (9, 0), 'next_move': 'down', 'time': '0.008s'}
    log = {'id': 'cca6536b-7bd7-4438-9a43-9aa493fd9fb4', 'turn': 72, 'me': {'name': 'mark_snake', 'health': 99, 'body': [(1, 7), (0, 7), (0, 6), (0, 5), (1, 5), (1, 6)]}, 'others': [{'name': 'Fairy Rust', 'health': 100, 'body': [(4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (9, 9), (10, 9), (10, 8), (10, 7), (9, 7), (9, 7)]}, {'name': 'MattIPv6', 'health': 76, 'body': [(4, 8), (4, 7), (4, 6), (4, 5), (4, 4), (5, 4), (6, 4)]}, {'name': 'Beholder', 'health': 95, 'body': [(3, 5), (2, 5), (2, 4), (3, 4), (3, 3), (3, 2), (2, 2), (2, 1)]}], 'food': [(0, 2)], 'module': 'functional2', 'decision_path': ['killer near'], 'next_coord': (1, 8), 'next_move': 'up', 'time': '0.178s'}

    game_state = init_from_log(log)
    main(game_state)

if __name__ == "__main__":
    run()
