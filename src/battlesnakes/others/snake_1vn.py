
import snake_utility
from snake_utility import *

game_state = None


def decision_1_v_n():
    global game_state
    game_state = snake_utility.game_state

    #4 aspects consideration
    #allowed move - must satisfy
    #danger rank
    #   trap
    #   dead end
    #   off-border
    #   being chased
    #   crowd danger
    #food rank
    #kill oppotunities
    #basic scheme:
    #allowed --> routine -->avoid danger --> food --> kill oppo
    #log the decision making process

    #no allowed move - die on self
    if len(game_state["allowed_move"]) == 0:
        game_state["next_head_coord"] = game_state["me"]["body"][1]
        return

    #base
    game_state["decision_path"].append("base")
    game_state["next_head_coord"] = game_state["allowed_move"][0]

    #routine
    move = game_state["routine_move"]
    if move in game_state["allowed_move"]:
        if move != game_state["next_head_coord"]:
            game_state["decision_path"].append("routine")
            game_state["next_head_coord"] = move
    
    #danger ranking always exists and not empty at this point
    #and they are already compatible with allowed moves

    def food_decision(passed_moves):
        def food_move(target):
            moves = shortest_path_move(get_my_head(), target)
            moves = [move for move in moves if move in passed_moves]
            if len(moves) != 0:
                off_border = [move for move in moves if not on_border(move)]
                if len(off_border) != 0:
                    move = off_border[0]
                else:
                    move = moves[0]
                if move != game_state["next_head_coord"]:
                    game_state["decision_path"].append("food")
                    game_state["next_head_coord"] = move

        def get_food(target):
            game_state["food_decision"] = [target]
            if not on_border(target):
                food_move(target)
            else:
                #food on border
                if is_adjacent(get_my_head(), target):
                    if all([d>=6 for _,d,_ in game_state["killer_near"]]):
                        if target != game_state["next_head_coord"]:
                            game_state["decision_path"].append("food")
                            game_state["next_head_coord"] = target
                    else:
                        killers = [killer for killer in game_state["killer_near"] for p,d,L in [killer] if L>len(game_state["me"]["body"])+1]
                        if len(killers) == 0:
                            if target != game_state["next_head_coord"]:
                                game_state["decision_path"].append("food")
                                game_state["next_head_coord"] = target
                else:
                    one_next = [p for p in adj_cells(target) if p not in game_state["occupied_cells"][0] and not on_border(p)]
                    if len(one_next) != 0:
                        food_move(one_next[0])
                    else:
                        food_move(target)

        food_near = [food for food in game_state["food_ranking"] for p,d,ds in [food] if d <= 10]
        my_len = len(game_state["me"]["body"])
        good_food = [(p,d) for food in food_near for p,d,ds in [food] 
                        if all([(d<de) if my_len <= size else (d<=de) for de,size in ds])]
        game_state["food_log"] = [len(game_state["food_ranking"]), len(food_near), len(good_food), food_near[:2]]
        if len(good_food) != 0:
            result = first_group(good_food)
            get_food(result[0])

    def try_kill_decision():
        result = game_state["try_kill"]
        if len(result) == 0:
            return

        result = result[0]
        #no danger in 3 steps
        result = [move for move in result if move in game_state["allowed_move"]]
        if len(result) != 0:
            if game_state["next_head_coord"] not in result:
                game_state["decision_path"].append("try_kill")
                game_state["next_head_coord"] = result[0]

    def default_decision_path():

        #happy_path_1
        moves = [move 
                for move, ranking in game_state["danger_ranking"].items()
                if 1==1
                and "collision_1" in ranking
                and ranking["collision_1"] == 99
                and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                and not ranking["trap"]
                ]

        if len(moves) != 0:
            game_state["decision_path"].append("happy_path_1")
            off_border = [p for p in moves if not on_border(p)]
            if len(off_border) != 0:
                if game_state["next_head_coord"] not in off_border:
                    game_state["decision_path"].append("off_border")
                    game_state["next_head_coord"] = off_border[0]
            else:
                if game_state["next_head_coord"] not in moves:
                    game_state["decision_path"].append("on_border")
                    game_state["next_head_coord"] = moves[0]

            #food and try_kill only happen in the happy path 1
            food_decision(moves)
            try_kill_decision()
            return

        #happy_path_2
        moves = [move 
                for move, ranking in game_state["danger_ranking"].items()
                if 1==1
                and "collision_2" in ranking
                and ranking["collision_2"] == 99
                and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                and not ranking["trap"]
                ]

        if len(moves) != 0:
            game_state["decision_path"].append("happy_path_2")
            off_border = [p for p in moves if not on_border(p)]
            if len(off_border) != 0:
                if game_state["next_head_coord"] not in off_border:
                    game_state["decision_path"].append("off_border")
                    game_state["next_head_coord"] = off_border[0]
            else:
                if game_state["next_head_coord"] not in moves:
                    game_state["decision_path"].append("on_border")
                    game_state["next_head_coord"] = moves[0]
            return

        #unhappy_path
        #not taking dead_end and trap, take collision risk
        moves = [item 
                    for item in game_state["danger_ranking"].items()
                    for move, ranking in [item]
                    if (1==1
                    and "collision_1" in ranking
                    and "collision_2" in ranking
                    and ranking["dead_end"] >=  len(game_state["me"]["body"]) *2 //3
                    and not ranking["trap"]
                ) ]
        #let's try taking risk fast, if passed hopefully danger is dropped
        if len(moves) != 0:
            game_state["decision_path"].append("take_collision")
            #remove on border
            off_border = [(move, ranking) for move, ranking in moves if not on_border(move)]
            if len(off_border) != 0:
                moves = [(move, ranking["collision_2"]) for move, ranking in off_border]
            else:
                moves = [(move, ranking["collision_2"]) for move, ranking in moves]
            moves = first_group(moves)
            if game_state["next_head_coord"] not in moves:
                game_state["next_head_coord"] = moves[0]
            return

    default_decision_path()
