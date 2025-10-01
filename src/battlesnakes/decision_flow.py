import time
import sqlite3

class Snake:
    def __init__(self, name, body, health, id=None):
        self.id = id
        self.name = name
        self.body = body
        self.health = health
        self.length = len(body)
        self.head = body[0]
        self.neck = body[1]
        self.tail = body[-1]
        self.allowed_moves = None
        self.ngroup = None
        self.territory = None
        self.head_space = None
        self.cut_set = None
        self.cut_space = None
        self.next = None
    def dict(self):
        return {k: self.__dict__[k] for k in ["name", "health", "length", "body", "id", ]}
    def copy(self):
        snake = Snake(self.name, [c for c in self.body], self.health)
        snake.allowed_moves = [a for a in self.allowed_moves]
        snake.territory = [a for a in self.territory]
        snake.head_space = [a for a in self.head_space]
    def set_id(self, id):
        self.id = id
        return self

class GameTurn:
    def __init__(self):
        self.id = None
        self.state = None
        self.me: Snake = None
        self.other: Snake = None
        self.others: list[Snake] = None
        self.snakes: list[Snake] = None
        self.food = None
        self.next_coord = None
        self.occupied_cells = None
        self.log = {}
        self.decision_path = []
        self.target_snake: Snake = None
        self.max_cut_length = 8
        self.turn = None
        self.vulnerables = []

def main(game_state, log=True, log_db=False):

    ######################################################
    # "global" variable
    ######################################################

    g = GameTurn()

    ######################################################

    def ________DECISION_LOGIC________():
        return

    def decision_flow(moves):
        return seq([
            some_calculations,

            avoid_single_collision_dead,
            avoid_next_step_no_move,
            avoid_suppressed_single_collision,

            (immediate_kill_oppotunity),
            (prefer_not(entering_danger(immediate_kill_situation))),

            type_1_collision,
            (cond(g.me.length >= 7)(avoid_serious_cut_danger)),
            (collision_cut_oppotunity),

            #(par([
            
            #this need some avoid first
            suppressed_chasing_kill_oppotunity,
            (trap_kill_oppotunity),

            #])),

            (wayout),

            (prefer_not(entering_danger(suppressed_chasing_kill_situation))),
            (prefer_not(entering_danger(border_confront_kill_situation))),
            (prefer_not(entering_danger(trap_kill_situation))),

            (make_forming_trap),
            (cut_kill_oppotunity),
            general_suppressed_chasing_kill_oppotunity,

            #cond(g.me.length >= 12)(par([ split_choice, collision_take_risk, ])),
            (type_2_collision),

            (attack_vulnerables),
            border_confront_kill_oppotunity,
            general_confront_kill_oppotunity,
            (cond(g.me.length >= 12)(split_choice)),

            (cond(g.me.length > 8)(avoid_next_step_confinement)),
            avoid_two_snake_trap,
            (cond(g.me.length >= 10)(split_choice)),
            cond(7 <= g.me.length <= 9)(collision_take_risk),
            (cond(g.me.length <= 10)(multi_step_collision)),

            cond(len(g.others) == 1 and g.me.length >= g.other.length)(avoid_cornered_bordered),


            cond(g.me.health < 20)(get_food),

            seq([ (split_choice), split_choice_2, ]),

            cond(len(g.others) == 1 and g.me.length > g.other.length)(push),
            (corner_push),
            cond(len(g.others) == 1 and g.me.length > 20)(gain_territory),
            cond(g.me.length >= 35)(chase_my_tail),

            (cond(7 <= g.me.length <= 10)(split_choice)),
            cond(g.me.length <= 10)(killer_near_prefer_away_border),
            cond(len(g.others) == 1 and g.me.length > g.other.length)(chase_to_the_end),
            cond(len(g.others) == 1 and g.me.length >= 10)(prefer_more_territory),
            cond(len(g.others) == 1 and g.me.length > g.other.length)(chase_other_tail),

            (get_food),

            (cond(g.me.length <= 12)(multi_step_collision)),

            #do split choice again with lower priority, no length condition
            seq([ (split_choice), split_choice_2, ]),

            (cond(g.me.length >= 12)(confined_follow_tail)),

            #cond(len(g.others) == 1 and g.me.length > g.other.length)(border_go_up),
            cond(len(g.others) == 1 and g.me.length < g.other.length)(border_go_up),
            (cond(g.me.length >= 10)(prefer_less_split)),
            (cond(g.me.length <= 16)(prefer_away_border)),

            seq([ (split_choice), split_choice_2, ]),

            cond(g.me.length < 10 and len(g.others) >= 2)(prefer_open_space),
            prefer(is_straight),

            id,
        ])(moves)

    def decision():

        #estimated 5-step occupied cells
        g.occupied_cells = [
            occupied_cells(step)
            for step in [1,2,3,4,5]
        ]
        for snake in g.snakes:
            snake.allowed_moves = [a for a in adj_cells(snake.head) if a not in g.occupied_cells[0]]
 
        if g.turn < 1:
            g.next_coord = take_first(g.me.allowed_moves)
            return

        if len(g.me.allowed_moves) == 0:
            #no allowed moves, die on myself
            g.next_coord = g.me.neck
            return
 
        if len(g.me.allowed_moves) == 1:
            #no choice
            g.next_coord = g.me.allowed_moves[0]
            return

        if len(g.others) == 0:
            #win
            g.next_coord = g.me.allowed_moves[0]
            return

        #allowed_moves must be 2 or 3
        moves = decision_flow(g.me.allowed_moves)

        g.next_coord = take_first(moves)

    def message(msg):
        def fn(moves):
            print(msg, moves)
        return fn

    def self_wayout_calculations(snake: Snake):
        oset = snake.territory
        indexes = [i for i,c in enumerate(snake.body) if c != snake.tail and any([p in oset for p in adj_cells(c)])]
        max_index = max(indexes)
        wayout_point = snake.body[max_index]
        wayout_length = snake.length - max_index -1
        oset = trim_aset(oset, snake.head, wayout_point)
        return (oset, wayout_point, wayout_length)

    def chase_to_the_end(moves):
        if distance_vector_abs(g.me.head, g.other.head) != (1,1): return
        if not is_adjacent(g.me.head, g.other.neck): return
        moves = [a for a in moves if is_adjacent(a, g.other.head)]
        if len(moves) != 0:
            g.decision_path.append("chase to the end")
            return moves

    def gain_territory(moves):
        #len(g.others) == 1 and g.me.length > 20
        other_ngroup = move_connected_group(g.other.allowed_moves)
        if other_ngroup != 1:
            return
        oset = sorted(g.other.territory)
        trimmed_oset, wayout_point, wayout_length = self_wayout_calculations(g.other)

        #I want to gain territory, or sequeeze opponent territory at the same time
        #I don't know how to do that exactly
        #but it should have the following properties:
        #1. My snake should move on a loop route
        #2. The route may be a rectanglar shape
        #3. The route should have one side close to opponent territory
        #4. The side should touch both borders so that the opponent cannot go around it
        #5. Case when I am shorter than the opponent, then the loop should have a direction 
        # that when I go on the side close to the opponent, it should have the same direction 
        # as the opponent head direction, and I am in front of the opponent head so that it cannot kill me.
        #6. Case when I am longer than the opponent, then the loop should have a direction
        # that when I go on the side close to the opponent, it should have the opposite direction
        # as the opponent head direction, so that when I go on the side I have a chance to head-to-head kill the opponent.
        #7, The loop may not be closed.
        #8. Case when I am shorter than the opponent, the open side should be away from the opponent territory, 
        # at that time, I should be walking on the side close to the opponent territory.
        #9. Case when I am longer than the opponent, 
        # I haven't had idea whether the open side should be close or away from the opponent territory.
        #10. I want the side of the loop that is close to the opponent territory to be able to push down 
        # to the opponent territory, so that I can gain more and more territory. 
        # The push down may not be a straight line, but it can be a zig-zag line. 
        # So the whole loop may not be a rectangle. 
        # My purpose is to gain more and more territory from the opponent with the most efficient route.


    def avoid_cornered_bordered(moves):
        #only one opponent
        if sum(distance_to_border(g.me.head)) <= 1:
            if distance_pq(g.me.head, g.other.head) <= 8:
                if path_distance_pq(g.me.head, g.other.head) == distance_pq(g.me.head, g.other.head):
                    g.decision_path.append("avoid cornered bordered")
                    return prefer_not(on_border)(moves)
        if sum(distance_to_border(g.me.head)) <= 2:
            if distance_pq(g.me.head, g.other.head) <= 6:
                if path_distance_pq(g.me.head, g.other.head) == distance_pq(g.me.head, g.other.head):
                    g.decision_path.append("avoid cornered bordered")
                    return prefer_by_rank(lambda a: min(distance_vector_abs(a, g.other.head)))(moves)

    def border_go_up(moves):
        if not on_border(g.me.head): return
        if not on_border(g.me.neck): return
        border_distance_2 = max(distance_to_border(g.me.head))
        if border_distance_2 < 2: return
        distance = distance_pq(g.me.head, g.other.head)
        if distance > 8: return
        if path_distance_pq(g.me.head, g.other.head) != distance: return
        if distance == 8:
            if distance_vector_abs(g.me.head, g.other.head) not in [(4,4), (3,5), (5,3)]: 
                return
        danger = [a for a in moves if on_border(a)]
        if len(danger) == 0: return
        danger = take_first(danger)
        if distance_pq(danger, g.other.head) != distance-1: return
        goup = [a for a in moves if not on_border(a)]
        if len(goup) != 0:
            g.decision_path.append("border go up")
            return goup

    def avoid_serious_cut_danger(moves):
        #serious cut danger consideration is to done before kill oppotunity
        #it must be very serious
        #so serious that we abort the kill oppotunity
        #I'll define it as territory is less than or equal to 2
        ngroup = move_connected_group(moves)
        if ngroup > 1: return
        return prefer_not(serious_cut_danger_a)(moves)
        #return prefer(no_cut_danger_a(strict=False))(moves)

    def coming_to_each_other(snake: Snake, snake2: Snake):
        if distance_pq(snake.head, snake2.head) != path_distance_pq(snake.head, snake2.head): return False
        if not any([distance_pq(a, snake2.head) < distance_pq(snake.head, snake2.head) for a in snake.allowed_moves]): return False
        if not any([distance_pq(a, snake.head) < distance_pq(snake.head, snake2.head) for a in snake2.allowed_moves]): return False
        return True

    def prefer_more_territory(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 1: return
        if distance_pq(g.me.head, g.other.head) != path_distance_pq(g.me.head, g.other.head): return
        if coming_to_each_other(g.me, g.other) and distance_pq(g.me.head, g.other.head) == 4 and g.me.length < g.other.length: return
        g.decision_path.append("prefer more territory")
        return prefer_by_score(lambda a: len(new_territory(a)))(moves)

    def new_territory(a):
        territory = g.me.territory
        territory_border = [p for p in territory if len([q for q in adj_cells(p) if q not in territory and q not in g.occupied_cells[0] and q != g.me.head]) != 0]
        lost = [p for p in territory_border if path_distance_pq(a, p) > path_distance_pq(g.me.head, p)]
        gain = [q for p in territory_border if path_distance_pq(a, p) < path_distance_pq(g.me.head, p)
                for q in adj_cells(p) if q not in territory and q not in g.occupied_cells[0] and q != g.me.head]
        new_territory = list(set([p for p in territory if p not in lost] + gain))
        return new_territory

    def prefer_open_space(moves):
        aset = path_connected_set(g.me.head)
        killers = [snake for snake in g.others if snake.length > g.me.length]
        nonkillers = [snake for snake in g.others if snake.length <= g.me.length]
        aset = [a for a in aset 
        if all([path_distance_pq(a, g.me.head) < path_distance_pq(a, snake.head) for snake in killers])
        #and all([path_distance_pq(a, g.me.head) <= path_distance_pq(a, snake.head) for snake in nonkillers])
        ]
        nset = len(aset)
        center = int(round(sum([x for x,y in aset])/nset, 0)), int(round(sum([y for x,y in aset])/nset, 0))
        if distance_pq(center, g.me.head) >= 2:
            g.decision_path.append(f"go to open space {center}")
            return prefer_by_rank(lambda a: distance_pq(a, center))(moves)

    def killer_near_prefer_away_border(moves):
        killers = [snake for snake in g.others if snake.length >= g.me.length+2 and path_distance_pq(snake.head, g.me.head) == 2]
        if len(killers) != 0:
            return prefer_not(lambda a: on_border(a) or off_border_1(a))(moves)

    def prefer_away_border(moves):
        return prefer_by_score(lambda a: min(*distance_to_border(a), 2))(moves)

    def prefer_less_split(moves):
        def next_ngroup(a):
            me2 = possible_next_state(g.me, a)
            ngroup = move_connected_group(me2.allowed_moves, g.occupied_cells[0]+[a])
            if ngroup is None:
                return 999
            return ngroup
        return prefer_by_rank(next_ngroup)(moves)

    def corner_danger_food(f):
        if g.me.length >= 15:
            return False
        if not at_corner(f):
            return False
        if sum(distance_to_border(f)) <= 1:
            if distance_pq(f, g.me.head) <= 8:
                if len([snake for snake in g.others if distance_pq(snake.head, f) <= 8 and snake.length >= g.me.length+2]) != 0:
                    return True
        return False

    def get_food(moves):
        food_near = [f for f in g.food if distance_pq(f, g.me.head) <= 8]
        food_good = [f for f in food_near 
                     if path_connected(f, g.me.head) 
                     and all([path_distance_pq(f, g.me.head) < path_distance_pq(f, snake.head) if snake.length >= g.me.length 
                     else path_distance_pq(f, g.me.head) <= path_distance_pq(f, snake.head)
                              for snake in g.others])]
        food_good = [f for f in food_good if not corner_danger_food(f)]
        if len(food_good) == 0:
            return

        food_better = prefer_by_rank(lambda f: path_distance_pq(f, g.me.head))(food_good)
        food_target = take_first(food_better)

        if g.me.length <= 10:
            food_moves = shortest_path_move(g.me.head, food_target)
            g.decision_path.append(f"get food {food_target}")
            return prefer(lambda a: a in food_moves)(moves)

        if is_adjacent(g.me.head, food_target):
            g.decision_path.append("next to food")
            return [food_target]

        def food_space(a):
            occupied = g.occupied_cells[1]+[a]
            food_set = path_connected_set(food_target, occupied)
            return len(food_set)

        if on_border(food_target):
            if distance_vector_abs(g.me.head, food_target) == (1,1):
                food_moves = [a for a in moves if is_adjacent(a, food_target)]
                if len(food_moves) == 1:
                    return food_moves
                g.decision_path.append("choose food path")
                return prefer_by_score(food_space)(food_moves)

        food_moves = shortest_path_move(g.me.head, food_target)
        food_moves = [a for a in moves if a in food_moves]
        if len(food_moves) != 0:
            g.decision_path.append(f"get food {food_target}")
            return prefer(lambda a: a in food_moves)(moves)

    def confined_follow_tail(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 1:
            return
        if any([path_connected(g.me.head, snake.head) for snake in g.others]):
            #confined
            return
        tails = [snake.tail for snake in g.snakes if snake.tail in g.me.territory]
        if len(tails) == 0:
            return
        tail = take_first(tails)
        tail_moves = shortest_path_move(g.me.head, tail)
        tail_moves = [a for a in moves if a in tail_moves]
        if len(tail_moves) != 0:
            return tail_moves

    def chase_my_tail(moves):
        return par([
            food1,
            tail_move(g.me.tail),
        ])(moves)

    def food1(moves):
        tail_moves = shortest_path_move(g.me.head, g.me.tail)
        food1 = [a for a in moves if a in g.food]
        if len(food1) != 0:
            food_and_tail = [a for a in food1 if a in tail_moves]
            if len(food_and_tail) != 0:
                return food_and_tail
            food_tail_connect = [a for a in food1 if any([path_connected(a, p) for p in tail_moves])]
            if len(food_tail_connect) != 0:
                g.decision_path.append("detour get food1")
                return food_tail_connect

    def tail_move(tail):
        def fn(moves):
            tail_moves = shortest_path_move(g.me.head, tail)
            if len(tail_moves) != 0:
                moves = [a for a in moves if a in tail_moves]
                if len(moves) != 0:
                    g.decision_path.append(f"chase tail {tail}")
                    return moves
        return fn

    def chase_other_tail(moves):
        if is_adjacent(g.me.head, g.other.tail):
            #don't follow too close
            tail_move = [a for a in moves if path_connected(a, g.other.tail)]
            if len(tail_move) != 0:
                g.decision_path.append("chase other tail detour")
                return tail_move
        else:
            tail_move = shortest_path_move(g.me.head, g.other.tail)
            tail_move = [a for a in moves if a in tail_move]
            if len(tail_move) != 0:
                g.decision_path.append("chase other tail")
                return tail_move

    def corner_push(moves):
        snakes = [snake for snake in g.others if sum(distance_to_border(snake.head)) <= 1 and snake.length < g.me.length]
        if len(snakes) != 0:
            snake = take_first(snakes)
            if distance_pq(snake.head, g.me.head) == 4:
                if len(snake.allowed_moves) == 2:
                    snake_move = [a for a in snake.allowed_moves if not on_border(a)]
                    if len(snake_move) == 1:
                        snake_move = take_first(snake_move)
                        if distance_vector_abs(g.me.head, snake.head) in [(1,3), (3,1)]:
                            if distance_vector_abs(snake_move, g.me.head) in [(1,2), (2,1)]:
                                push_move = [a for a in moves if distance_vector_abs(a, snake_move) == (1,1)]
                                if len(push_move) != 0:
                                    g.decision_path.append("corner push")
                                    return push_move
                            if distance_vector_abs(snake_move, g.me.head) in [(0,3), (3,0)]:
                                push_move = [a for a in moves if distance_vector_abs(a, snake_move) in [(0,2), (2,0)]]
                                if len(push_move) != 0:
                                    g.decision_path.append("corner push")
                                    return push_move
                        if distance_vector_abs(g.me.head, snake.head) == (2,2):
                            push_move = [a for a in moves if distance_vector_abs(a, snake_move) in [(1,1)]]
                            if len(push_move) != 0:
                                g.decision_path.append("corner push")
                                return push_move

    def push(moves):
        def push_2(moves):
            if distance_pq(g.me.head, g.other.head) == 2:
                if distance_vector_abs(g.me.head, g.other.head) != (1,1):
                    collision = [a for a in adj_cells(g.me.head) if a in adj_cells(g.other.head)]
                    collision = take_first(collision)
                    if collision not in moves: return

                    #don't push from border to center
                    #if min(distance_to_border(g.me.head)) >= 2:
                    if sum(distance_to_border(g.me.head)) > sum(distance_to_border(g.other.head)):
                        if collision in moves:
                            g.decision_path.append("longer confront push")
                            return [collision]
                    else:
                        #parallel push
                        parallel_push = [a for a in moves if distance_vector_abs(a, g.other.head) in [(1,2), (2,1)]]
                        if len(parallel_push) != 0:
                            g.decision_path.append("parallel push")
                            return parallel_push

        def coming_push(moves):
            if coming_to(g.me, g.other.head) and coming_to(g.other, g.me.head):
                if distance_pq(g.me.head, g.other.head) == 4:
                    moves = [a for a in moves if distance_pq(a, g.other.head) < distance_pq(g.me.head, g.other.head)]
                    print(moves)
                    if len(moves) != 0:
                        g.decision_path.append("coming push")
                        return moves
                if distance_pq(g.me.head, g.other.head) == 6:
                    if distance_vector_abs(g.me.head, g.other.head) in [(2,4), (4,2), (3,3)]:
                        moves = [a for a in moves if distance_vector_abs(a, g.other.head) in [(2,3), (3,2)]]
                        if len(moves) != 0:
                            g.decision_path.append("coming push")
                            return moves

        def center_push(moves):
            if min(distance_to_border(g.me.head)) >= 2:
                if coming_to(g.me, g.other.head):
                    near_moves = [a for a in g.other.allowed_moves if distance_pq(a, g.me.head) < distance_pq(g.other.head, g.me.head)]
                    if len(near_moves) == 1:
                        near_move = take_first(near_moves)
                        moves = [a for a in moves if distance_vector_abs(a, near_move) in [(1,1), (2,2)]]
                        if len(moves) != 0:
                            g.decision_path.append("center push")
                            return moves

        def push_4(moves):
            if distance_pq(g.me.head, g.other.head) in [4,6]:
                if path_distance_pq(g.me.head, g.other.head) == distance_pq(g.me.head, g.other.head):
                    return par([
                        coming_push,
                        center_push,
                    ])(moves)
    
        return par([
            push_2,
            (push_4),
        ])(moves)

    def multi_step_collision(moves):
        killers = [snake for snake in g.others if snake.length > g.me.length if distance_pq(snake.head, g.me.head) <= 8]
        nonkillers = [snake for snake in g.others if snake.length == g.me.length if distance_pq(snake.head, g.me.head) <= 8]
        for snake in g.snakes:
            snake.head_paths = grow_path(snake.head, 5)

        def collision_score(a, consider_equal=True):
            def path_collision_score(apath):
                length = len(apath)
                if length == 5:
                    return 999
                if len(g.me.head_paths) <= length:
                    return length - 1
                snakes = (killers+nonkillers) if length <= (3 if consider_equal else 2) else killers
                if apath[-1] in [ path[-1]
                    for snake in snakes if len(snake.head_paths) >= length
                    for path in snake.head_paths[length-1]
                ]:
                    return length - 1
                npaths = [path for path in g.me.head_paths[length] if path[:length] == apath ]
                if len(npaths) == 0:
                    return length - 1
                return max([path_collision_score(path) for path in npaths])
            return path_collision_score([g.me.head, a])

        move_score = [(a, collision_score(a, consider_equal=False)) for a in moves]
        low_score = [(a, score) for a, score in move_score if score < 999]
        score_999 = [a for a, score in move_score if score == 999]
        danger_1 = [a for a, score in move_score if score == 1]
        collisions = [a for a in danger_1 if any([is_adjacent(a, snake.head) for snake in g.others if snake.length >= g.me.length])]
        if len(low_score) != 0:
            g.decision_path.append(f"multi-step collision {low_score}")
        if len(score_999) == 0:
            if len(collisions) != 0:
                equal_collision = [p for p in collisions if all([snake.length == g.me.length for snake in g.others if is_adjacent(p, snake.head)])]
                if len(equal_collision) != 0:
                    g.decision_path.append("take equal collision")
                    return equal_collision
                if on_border(g.me.head) or off_border_1(g.me.head) or at_corner(g.me.head):
                    if len(collisions) == 2:
                        g.decision_path.append("too close to corner - take risk")
                        return collisions
        max_score = [a for a, score in move_score if score == max([score for a, score in move_score])]
        return max_score

    def grow_path(head, steps):
        layers = [[[head]]]
        for i in range(steps):
            layer = [ path+[nhead]
                for path in layers[-1]
                for end in [path[-1]]
                for nhead in adj_cells(end)
                if nhead not in path
                and nhead not in g.occupied_cells[i]
            ]
            layers.append(layer)
        return layers

    def at_corner(p):
        distv = distance_to_border(p)
        return sum(distv) <= 2

    def avoid_two_snake_trap(moves):
        def config_11(moves):
            snakes = [snake for snake in g.others if distance_vector_abs(snake.head, g.me.head) == (1,1)]
            if len(snakes) != 2:
                return
            snake1, snake2 = snakes
            if distance_vector_abs(snake1.head, snake2.head) not in [(0,2), (2,0)]:
                return
            danger = [a for a in moves if a in snake1.allowed_moves and a in snake2.allowed_moves]
            if len(danger) == 0:
                return
            danger = take_first(danger)
            if all([any([get_adjacent_dir(snake.head, a) == get_adjacent_dir(g.me.head, danger) for a in snake.allowed_moves]) for snake in snakes]):
                moves = [a for a in moves if a != danger]
                if len(moves) != 0:
                    g.decision_path.append("avoid two-snake trap")
                    return moves

        def config_10(moves):
            if len(g.me.allowed_moves) != 3: return
            snakes = [snake for snake in g.others if distance_vector_abs(snake.head, g.me.head) == (1,1)]
            if len(snakes) != 1: return
            one = take_first(snakes)
            snakes = [snake for snake in g.others if distance_vector_abs(snake.head, g.me.head) in [(0,2), (2,0)]]
            if len(snakes) != 1: return
            two = take_first(snakes)
            if two.length <= g.me.length: return
            if distance_vector_abs(one.head, two.head) not in [(1,3), (3,1)]: return
            single_collision = ([a for a in moves if is_adjacent(a, two.head)])
            if len(single_collision) != 1: return
            single_collision = take_first(single_collision)
            type_2_collision = [a for a in moves if is_adjacent(a, one.head)]
            if len(type_2_collision) != 2: return
            avoid = take_first([a for a in type_2_collision if distance_vector_abs(a, single_collision) != (1,1)])
            g.decision_path.append("avoid two-snake trap")
            return [avoid]

        return par([
            config_11,
            config_10,
        ])(moves)

    def collision_wayout(avoid):
        cut_set = [p for a in g.me.territory for p in adj_cells(a) if p not in g.me.territory and p in g.me.head_space]
        cut_set = sorted(list(set(cut_set)))

        #check wayout
        #consider this later
        #in type-2 collision case, you don't have the full g.me.territory to wiggle

        if any([snake.tail in g.me.territory for snake in g.snakes]):
            return True

        for snake in g.snakes:
            adjacent_indexes = [i
                    for i,c in enumerate(snake.body)
                    for p in adj_cells(c) if p in g.me.territory
                    ]
            if len(adjacent_indexes) == 0: continue
            max_index = max(adjacent_indexes)
            wayout_point = g.me.body[max_index]
            wayout_length = snake.length - max_index - 1
            aset = g.me.territory
            if len(cut_set) >= 5 and len(cut_set) >= len(aset) * 0.4:
                if wayout_length <= len(cut_set):
                    return False
            aset = trim_aset(aset, g.me.head, wayout_point)
            if wayout_length <= len(aset): 
                return True

        return False

    def type_2_collision(moves):

        killers = [snake for snake in g.others if snake.length > g.me.length and distance_vector_abs(g.me.head, snake.head) == (1,1)]
        nonkillers = [snake for snake in g.others if snake.length == g.me.length and distance_vector_abs(g.me.head, snake.head) == (1,1)]
        if len(killers) == 0 and len(nonkillers) == 0: return

        if len(killers) != 1: return
        killer = take_first(killers)

        if len(moves) != 3: return

        avoid = take_first([a for a in moves if not is_adjacent(a, killer.head)])
        middle = take_first([a for a in moves if distance_vector_abs(a, avoid) == (1,1)])
        collision = take_first([a for a in moves if a not in [avoid, middle]])
        if collision_wayout(avoid):
            g.decision_path.append(f"type 2 collision take avoid point {avoid}")
            return [avoid]
        else:
            g.decision_path.append("type 2 collision take risk")
            return [collision]

    def split_choice_2(moves):
        ngroup = move_connected_group(moves)
        if ngroup == 1:
            return

        #split choice doesn't consider type-2 collision
        type_2_collision = [snake for snake in g.others if snake.length > g.me.length and distance_vector_abs(snake.head, g.me.head) == (1,1) and len([a for a in g.me.allowed_moves if a in snake.allowed_moves]) == 2]
        if len(type_2_collision) != 0: return

        if ngroup == 3:
            if path_connected(g.me.head, g.me.tail):
                return shortest_path_move(g.me.head, g.me.tail)
            else:
                snakes = [snake for snake in g.others if path_connected(g.me.head, snake.tail)]
                if len(snakes) != 0:
                    snake = take_first(snakes)
                    return shortest_path_move(g.me.head, snake.tail)
            return prefer_by_score(lambda a: len(path_connected_set(a)))(moves)
        
        g.decision_path.append("split choice 2")
        return seq([
                avoid_preliminary_trap,
                avoid_static_confinement,
                more_space,
                (prefer_diagonal_cut_set),
        ])(moves)

    def split_choice(moves):
        ngroup = move_connected_group(moves)
        if ngroup == 1:
            return

        #split choice doesn't consider type-2 collision
        type_2_collision = [snake for snake in g.others if snake.length > g.me.length and distance_vector_abs(snake.head, g.me.head) == (1,1) and len([a for a in g.me.allowed_moves if a in snake.allowed_moves]) == 2]
        if len(type_2_collision) != 0: return

        if ngroup == 3:
            if path_connected(g.me.head, g.me.tail):
                return shortest_path_move(g.me.head, g.me.tail)
            else:
                snakes = [snake for snake in g.others if path_connected(g.me.head, snake.tail)]
                if len(snakes) != 0:
                    snake = take_first(snakes)
                    return shortest_path_move(g.me.head, snake.tail)
            return prefer_by_score(lambda a: len(path_connected_set(a)))(moves)
        
        g.decision_path.append("try split choice")
        #ngroup == 2
        
        ok_set = [a for a in moves if combined_wayout(a)]
        if len(ok_set) != 0:
            return ok_set

    def more_space(moves):
        def move_space(a):
            if a not in g.me.territory:
                return []
            return path_connected_set(a, complement(g.me.territory))
        return prefer_by_score(lambda a: len(move_space(a)))(moves)
 
    def prefer_diagonal_cut_set(moves):
        ok_set = []
        occupied = complement(g.me.territory)
        for a in moves:
            aset = path_connected_set(a, occupied)
            cut_set = [q for p in aset for q in adj_cells(p) if q not in g.occupied_cells[0] and q not in aset]
            if len(cut_set) == 0: continue
            cut_set = sorted(cut_set)
            x0, y0 = cut_set[0]
            x1, y1 = cut_set[-1]
            dx = abs(x0-x1)
            dy = abs(y0-y1)
            dd = abs(dx-dy)
            if len(cut_set) >= 3 and dd <= 1:
                ok_set.append(a)
        if len(ok_set) != 0:
            return ok_set

    def avoid_static_confinement(moves):
        ok_set = []
        occupied = complement(g.me.head_space)
        occupied2 = complement(g.me.territory)
        for a in moves:
            aset = path_connected_set(a, occupied)
            aset2 = path_connected_set(a, occupied2)
            if len(aset) != len(aset2):
                #not a static confinement
                ok_set.append(a)
        if len(ok_set) != 0:
            return ok_set

    def avoid_preliminary_trap(moves):
        danger_set = []
        for snake in g.others:
            if len(snake.allowed_moves) != 0:
                for a in moves:
                    snake2 = possible_next_state(snake, take_first(snake.allowed_moves))
                    me2 = possible_next_state(g.me, a)
                    if preliminary_trap(snake2, me2):
                        danger_set.append(a)
        ok_set = [a for a in moves if a not in danger_set]
        if len(danger_set) != 0:
            g.decision_path.append("avoid preliminary trap")
        if len(ok_set) != 0:
            return ok_set

    def preliminary_trap(killer: Snake, target: Snake):
        for i,c in enumerate(killer.body):
            if c in killer.body[-2:]: continue
            if c == killer.head: continue
            if not is_adjacent(target.head, c): continue
            if not on_border(target.head): continue
            if on_border(c): continue
            b = killer.body[i-1]
            if get_adjacent_dir(c, b) == get_adjacent_dir(target.neck, target.head):
                return True
        return False

    def collision_take_risk(moves):
        if len(g.me.allowed_moves) != 3:
            return
        snakes = [snake for snake in g.others if distance_vector_abs(snake.head, g.me.head) == (1,1) and snake.length > g.me.length]
        if len(snakes) != 1:
            return
        snake = take_first(snakes)
        collision = [a for a in g.me.allowed_moves if a in snake.allowed_moves]
        if len(collision) != 2:
            return
        avoid_point = take_first([a for a in g.me.allowed_moves if a not in collision])
        risk = [a for a in moves if a in collision and distance_vector_abs(a, avoid_point) != (1,1)]
        g.decision_path.append("take risk")
        return risk

    def has_wayout(a):
        occupied = complement(g.me.territory)
        if a in occupied:
            return False
        aset = path_connected_set(a, occupied)
        wayout_point = has_wayout_on_myself2(aset, a)
        if wayout_point is not None:
            return True
        wayout_point = has_wayout_on_others2(aset, a)
        if wayout_point is not None:
            return True
        return False

    def check_wayout(moves):
        ok_set = []

        for a in moves:
            if has_wayout(a):
                ok_set.append(a)
        if len(ok_set) != 0:
            return ok_set
        g.decision_path.append("split fail wayout check")

    def check_confinement(moves):
        ok_set = [a for a in moves if no_cut_danger_a(strict=True)(a)]
        if len(ok_set) != 0:
            return ok_set
        g.decision_path.append("split fail confinement check")

    def check_confinement_again(moves):
        ok_set = [a for a in moves if no_cut_danger_a(strict=False)(a)]
        if len(ok_set) != 0:
            return ok_set
        g.decision_path.append("split fail confinement check")

    def combined_wayout(a):
        if no_cut_danger_a(strict=True)(a):
            return True
        if has_wayout(a):
            return True
        return False

    def avoid_next_step_confinement(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 1:
            return

        distances = [(snake, path_distance_pq(snake.head, g.me.head)) for snake in g.others]
        min_dist = min([dist for snake, dist in distances])
        if min_dist == 999:
            return
        killer = take_first([snake for snake, dist in distances if dist == min_dist])
        danger_set = []
        for a in moves:
            me2 = possible_next_state(g.me, a)
            for b in killer.allowed_moves:
                if b == a: continue
                snake2 = possible_next_state(killer, b)
                hypothetic_development_territories([snake2, me2])
                cut_set = [p
                            for a in me2.territory
                            for p in adj_cells(a)
                            if p in me2.head_space and p not in me2.territory
                    ] if snake2.length > me2.length else [a
                            for a in snake2.territory
                            for p in adj_cells(a)
                            if p in me2.head_space and p not in snake2.territory
                            ]
                cut_set = sorted(list(set(cut_set)))

                #if len(cut_set) == 0: continue
                #if len(cut_set) > 2: continue
                #if len(cut_set) == 2:
                    #if not cut_set_connected(cut_set): continue
                if cut_set_too_thick(cut_set): continue

                occupied = [p for snake in [me2, snake2] for p in snake.body[:-1]]+g.occupied_cells[1]+cut_set
                occupied = list(set(occupied))
                oset = path_connected_set(me2.head, occupied)
                oset = sorted([p for p in oset if p != me2.head])

                #no tails
                if any([snake.tail in oset for snake in [me2, snake2]]): continue

                #trimmed
                indexes = [i for i,c in enumerate(g.me.body) if c != g.me.head and c != g.me.tail and any([p in oset for p in adj_cells(c)])]
                if len(indexes) == 0: continue
                max_index = max(indexes)
                wayout_point = g.me.body[max_index]
                wayout_length = g.me.length - max_index -1
                oset = trim_aset(oset, me2.head, wayout_point)
                if len(oset) >= wayout_length: continue

                danger_set.append(a)
                #only need one killer move to make me confined
                break

        if len(danger_set) != 0:
            g.decision_path.append(f"avoid next step confinement {danger_set}")
            moves = [a for a in moves if a not in danger_set]
            if len(moves) != 0:
                return moves

    def cut_set_too_thick(cut_set):
        if len(cut_set) <= 2:
            return False
        min_x = min([x for x,y in cut_set])
        max_x = max([x for x,y in cut_set])
        if max_x - min_x < 2:
            return False
        min_y = min([y for x,y in cut_set])
        max_y = min([y for x,y in cut_set])
        if max_y - min_y < 2:
            return False
        return True

    def type_1_collision(moves):
        avoid = [a 
                 for snake in g.others if single_collision(snake, g.me) 
                 for a in moves if is_adjacent(a, snake.head) 
                 ]
        if len(avoid) != 0:
            g.decision_path.append(f"avoid single collision {avoid}")
            moves = [a for a in moves if a not in avoid]
            if len(moves) != 0:
                return moves

    def single_collision(killer: Snake, target: Snake):
        return all([
            len(target.allowed_moves) == 3,
            killer.length > target.length,
            len([a for a in target.allowed_moves if a in killer.allowed_moves]) == 1,
        ])

    def entering_danger(danger):
        def fn(a):
            for snake in g.others:
                for b in snake.allowed_moves:
                    me2 = possible_next_state(g.me, a)
                    snake2 = possible_next_state(snake, b)
                    if danger(snake2, me2):
                        return True
            return False
        return fn

    def avoid_suppressed_single_collision(moves):
        avoid = [a 
                 for snake in g.others if suppressed_single_collision(snake, g.me) 
                 for a in moves if is_adjacent(a, snake.head) 
                 ]
        if len(avoid) != 0:
            g.decision_path.append(f"avoid suppressed single collision {avoid}")
            moves = [a for a in moves if a not in avoid]
            if len(moves) != 0:
                return moves

    def suppressed_single_collision(killer: Snake, target: Snake):
        if len(target.allowed_moves) == 2:
            if killer.length > target.length:
                if len([a for a in target.allowed_moves if a in killer.allowed_moves]) == 1:
                    a,b = target.allowed_moves
                    if distance_vector_abs(a, b) == (1,1):
                        return True
        return False

    def wayout(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 1:
            return

        cut_set = [p for a in g.me.territory for p in adj_cells(a)
                    if p in g.me.head_space and p not in g.me.territory ] 
        cut_set = sorted(list(set(cut_set)))
 
        #only consider one-point cut
        #when cut is too far in the future, don't over optimize it
        if len(cut_set) > 1: return

        if len(cut_set) > 2:
            #if cut_set too long, don't consider cut danger
            return
        
        if len(cut_set) == 2:
            #if cust_set not "connected", no cut danger
            a,b = cut_set
            if not any([
                is_adjacent(a, b),
                distance_vector_abs(a, b) == (1,1),
            ]):
                return
   
        #tail
        if any([snake.tail in g.me.territory for snake in g.snakes]):
            return
        if any([snake.health == 100 and any([is_adjacent(snake.tail, a) for a in g.me.territory]) for snake in g.snakes]):
            return
        if len(cut_set) != 0:
            future_tail = g.me.body[-1-len(cut_set)]
            if any([p in g.me.territory for p in adj_cells(future_tail)]):
                return

        #wayout spacious
        if len(g.me.territory) >= g.me.length * 1.1:
            return

        g.decision_path.append("try wayout")

        return par([
            (wayout_myself),
            wayout_on_others,
        ])(moves)

    def wayout_myself(moves):
        wayout_point = has_wayout_on_myself(g.me.territory)
        if wayout_point is not None:
            return wayout_to(wayout_point, moves)

    def wayout_on_others(moves):
        wayout_point = has_wayout_on_others(g.me.territory)
        if wayout_point is not None:
            return wayout_to(wayout_point, moves)

    def has_wayout_on_myself(territory):
        adjacent_indexes = [i
                        for i,c in enumerate(g.me.body) if c != g.me.head
                        for p in adj_cells(c) if p in territory
                        ]
        if len(adjacent_indexes) == 0:
            return
        max_index = max(adjacent_indexes)
        wayout_length = g.me.length - max_index - 1
        wayout_point = g.me.body[max_index]
        aset = trim_aset(g.me.territory, g.me.head, wayout_point)
        if len(aset) >= wayout_length:
            g.me.wayout_length = wayout_length
            return wayout_point

    def has_wayout_on_others(territory):
        wayout_choices = []
        for snake in g.others:
            adjacent_indexes = [i
                    for i,c in enumerate(snake.body)
                    for p in adj_cells(c) if p in territory
                    ]
            if len(adjacent_indexes) == 0: continue
            max_index = max(adjacent_indexes)
            wayout_length = snake.length - max_index - 1
            wayout_point = snake.body[max_index]
            wayout_choices.append((snake, max_index, wayout_length, wayout_point))
        if len(wayout_choices) == 0:
            return
        min_wayout_length = min([wayout_length for a,b, wayout_length, c in wayout_choices])
        choice = [(a,b, wayout_length, c) for a,b, wayout_length, c in wayout_choices if wayout_length == min_wayout_length]
        a,b,wayout_length, wayout_point = take_first(choice)
        g.me.wayout_length = wayout_length
        return wayout_point

    def has_wayout_on_myself2(aset, a):
        adjacent_indexes = [i
                        for i,c in enumerate(g.me.body) if c != g.me.head and c != g.me.tail
                        for p in adj_cells(c) if p in aset
                        ]
        if len(adjacent_indexes) == 0:
            return
        max_index = max(adjacent_indexes)
        wayout_length = g.me.length - max_index - 1
        wayout_point = g.me.body[max_index]

        aset = trim_aset(aset, a, wayout_point)
        aset_food = [f for f in g.food if f in aset]

        if len(aset) <= 5:
            if len(aset) >= wayout_length + len(aset_food):
                return wayout_point
        else:
            if len(aset) >= wayout_length * 1.1:
                return wayout_point

    def has_wayout_on_others2(aset, a):
        wayout_choices = []
        for snake in g.others:
            adjacent_indexes = [i
                    for i,c in enumerate(snake.body)
                    for p in adj_cells(c) if p in aset
                    ]
            if len(adjacent_indexes) == 0: continue
            max_index = max(adjacent_indexes)
            wayout_length = snake.length - max_index - 1
            wayout_point = snake.body[max_index]
            wayout_choices.append((snake, max_index, wayout_length, wayout_point))
        if len(wayout_choices) == 0:
            return
        min_wayout_length = min([wayout_length for a,b, wayout_length, c in wayout_choices])
        choice = [(a,b, wayout_length, c) for a,b, wayout_length, c in wayout_choices if wayout_length == min_wayout_length]
        snake,max_index,wayout_length, wayout_point = take_first(choice)

        aset = trim_aset(aset, a, wayout_point)
        if len(aset) <= 5:
            if len(aset) >= wayout_length:
                return wayout_point
        else:
            if len(aset) >= wayout_length * 1.1:
                return wayout_point

    def wayout_to(wayout_point, moves):
        moves_in_territory = [a for a in moves if a in g.me.territory and path_connected(a, wayout_point)]
        if len(moves_in_territory) == 0:
            return moves
        if len(moves_in_territory) == 1:
            return moves_in_territory
        
        if path_distance_pq(g.me.head, wayout_point) >= g.me.wayout_length + 3:
            g.decision_path.append("wayout path long enough to go direct")
            return shortest_path_move(g.me.head, wayout_point)

        g.decision_path.append("meander")
        return prefer_less_next_moves(
            prefer_by_score(lambda a: path_distance_pq(a, wayout_point))(moves_in_territory)
        )

    def prefer_less_next_moves(moves):
        def n_next_moves(a):
            next_moves = [p for p in adj_cells(a) if p not in g.occupied_cells[1]]
            return len(next_moves)
        return prefer_by_rank(n_next_moves)(moves)

    def move_connected_group(moves, occupied=None):
        if occupied is None:
            occupied = g.occupied_cells[0]

        if len(moves) == 1:
            return 1
        if len(moves) == 2:
            a,b = moves
            distv = distance_vector_abs(a,b)
            if distv == (1,1):
                if not all([p in occupied for p in adj_cells(a) if p in adj_cells(b)]):
                    return 1
            return 2
        if len(moves) == 3:
            c = take_first([a for a in moves if len([b for b in moves if b != a and distance_vector_abs(a,b) == (1,1)]) == 2])
            a,b = [a for a in moves if a != c]
            ac = not all([p in occupied for p in adj_cells(a) if p in adj_cells(c)])
            bc = not all([p in occupied for p in adj_cells(b) if p in adj_cells(c)])
            if ac and bc:
                return 1
            if ac and not bc:
                return 2
            if not ac and bc:
                return 2
            return 3

    def avoid_next_step_no_move(moves):
        no_move = [a for a in moves if len([p for p in adj_cells(a) if p not in g.occupied_cells[1]]) == 0]
        if len(no_move) != 0:
            g.decision_path.append(f"avoid next step no move {no_move}")
            moves = [a for a in moves if a not in no_move]
            if len(moves) != 0:
                return moves

    def cut_kill_target():
        #get the first target
        for snake in g.others:
            if preliminary_cut_kill_situation(g.me, snake):
                g.target_snake = snake
                return True
        return False

    def cut_kill_oppotunity(moves):
        if not cut_kill_target():
            return

        #passed preliminary cut kill check - have a target and a cut_set
        #I'll take a path (cut_path) so that the target is blocked from escaping
        #the cut_path should pass cut_set
        #the cut_path should be as short as possible
        #the cut_path should be reachable from my head - straight or rectangular
        #the cut_path should come back so that I myself is not confined

        #algorithm description
        #find a *good* rectangle with one cut_set cell as a corner and my head on a side
        #the cut_path will be the border of the rectangle
        #good - the resulting cut space is small enough so that the target will likely die
        
        cut_set = g.target_snake.cut_set
        target = g.target_snake

        for v,rect in [(v, rect) for v in cut_set for rect in cut_rectangles(v)]:
            (x0,y0), (x1,y1) = rect

            #not a rectangle
            if x0 == x1 or y0 == y1: continue

            #my head cannot be the other corner
            if g.me.head == (x1,y1): continue

            #if min(distance_vector_abs(g.me.head, v)) != 0: continue

            cells = [(x,y) for x in irange(x0, x1) for y in irange(y0, y1)]

            #select the rectangle in the correct direction
            if any([p in cells for p in target.territory]): continue

            occupied = list(set(g.occupied_cells[0]+cells))
            oset = path_connected_set(target.head, occupied)
            oset = [p for p in oset if p != target.head]
            if any([snake.tail in oset for snake in g.snakes]): continue
            if any([any([is_adjacent(snake.tail, a) for a in oset]) for snake in g.snakes if snake.health == 100]): continue

            oset = trim_aset(oset, target.head, target.head)
            if len(oset) > target.length * 1.1:
                continue

            if path_distance_pq(g.me.head, v) != distance_pq(g.me.head, v):
                continue

            v2 = [p for p in [(x0,y1), (x1,y0)] if min(distance_vector_abs(g.me.head, p)) == 0]
            v2 = take_first(v2)

            g.decision_path.append(f"go cut to {(x0,y0)}")
            cut_moves = shortest_path_move(g.me.head, v)
            cut_moves = prefer_by_rank(lambda a: distance_pq(a, target.head))(cut_moves)
            cut_moves = prefer_by_rank(lambda a: distance_pq(a, v2))(cut_moves)
            return cut_moves

        g.decision_path.append("no cut path")

    def irange(a, b):
        return list([a] if a == b else range(a, b+1) if a < b else range(a,b-1,-1,))

    def cut_rectangles(v):
        width = g.state["board"]["width"]
        height = g.state["board"]["height"]

        x0,y0 = v
        x1,y1 = g.me.head

        rectangles = [
            [v, (0,y1)], 
            [v, (width-1,y1)],
        ] if x0 == x1 else [
            [v, (x1,0)], 
            [v, (x1,height-1)],
        ] if y0 == y1 else [
            [v, (x1, 0 if y1 < y0 else height-1)],
            [v, (0 if x1 < x0 else width-1, y1)],
        ]
        return rectangles

    def attack_vulnerables(moves):
        for snake in g.vulnerables:
            g.target_snake = snake
            if g.me.length <= snake.length:
                snake2: Snake = snake.vulnerable_emerge
                if snake.dead:
                    g.decision_path.append("vulnerable target evolve dead")
                    return [g.me.next.head]
                if path_distance_pq(g.me.head, snake2.head) < snake.vulnerable_steps:
                    attack_move = shortest_path_move(g.me.head, snake2.head)
                    attack_move = [a for a in moves if a in attack_move]
                    if len(attack_move) != 0:
                        g.decision_path.append("attack vulnerables less distance")
                        return attack_move
            if g.me.length > snake.length:
                result = par([
                    attack_vulnerables_equal_distance,
                    attack_vulnerables_distance_2,
                    attack_vulnerables_path_distance_2,
                    (attack_vulnerables_distance_4),
                ])(moves)
                if result is not None:
                    return result

    def attack_vulnerables_equal_distance(moves):
        snake = g.target_snake
        snake2: Snake = snake.vulnerable_emerge
        if path_distance_pq(g.me.head, snake2.head) <= snake.vulnerable_steps:
            attack_move = shortest_path_move(g.me.head, snake2.head)
            attack_move = [a for a in moves if a in attack_move]
            if len(attack_move) != 0:
                g.decision_path.append("attack vulnerables less or equal distance")
                return attack_move

    def attack_vulnerables_path_distance_2(moves):
        snake = g.target_snake
        snake2: Snake = snake.vulnerable_emerge

        if path_distance_pq(g.me.head, snake2.head) == snake.vulnerable_steps + 2:
            if on_border(snake2.head):
                attack_point = [q 
                                for p in adj_cells(snake2.head) if not on_border(p) 
                                for q in adj_cells(p) if distance_vector_abs(q, snake2.head) in [(0,2), (2,0)]]
                attack_point = take_first(attack_point)
                if path_distance_pq(g.me.head, attack_point) == snake.vulnerable_steps:
                    attack_move = shortest_path_move(g.me.head, attack_point)
                    attack_move = [a for a in moves if a in attack_move]
                    if len(attack_move) != 0:
                        g.decision_path.append("attack vulnerables path distance 2")
                        return attack_move

    def attack_vulnerables_distance_2(moves):
        snake = g.target_snake
        snake2: Snake = snake.vulnerable_emerge

        if distance_pq(g.me.head, snake2.head) == snake.vulnerable_steps + 2:
            if on_border(snake2.head):
                attack_point = [q 
                                for p in adj_cells(snake2.head) if not on_border(p) 
                                for q in adj_cells(p) if distance_vector_abs(q, snake2.head) in [(0,2), (2,0)]]
                attack_point = take_first(attack_point)
                if path_distance_pq(g.me.head, attack_point) == snake.vulnerable_steps:
                    attack_move = shortest_path_move(g.me.head, attack_point)
                    attack_move = [a for a in moves if a in attack_move]
                    if len(attack_move) != 0:
                        g.decision_path.append("attack vulnerables distance 2")
                        return attack_move

    def attack_vulnerables_distance_4(moves):
        snake = g.target_snake
        snake2: Snake = snake.vulnerable_emerge

        if distance_pq(g.me.head, snake2.head) == snake.vulnerable_steps + 4:
            if on_border(snake2.head):
                attack_points = [a for a in board_cells() if distance_vector_abs(a, snake2.head) in [(2,2), (1,3), (3,1)]]
                attack_points = [a for a in attack_points if not off_border_1(a) and path_connected(a, g.me.head)]
                attack_points = [a for a in attack_points if path_distance_pq(g.me.head, a) == snake.vulnerable_steps]
                attack_points = [a for a in attack_points if coming_to(snake2, a)]
                if len(attack_points) != 0:
                    attack_point = take_first(attack_points)
                    attack_move = shortest_path_move(g.me.head, attack_point)
                    attack_move = [a for a in moves if a in attack_move]
                    if len(attack_move) != 0:
                        g.decision_path.append("attack vulnerables")
                        return attack_move

    def coming_to(snake: Snake, p):
        straight = [a for a in snake.allowed_moves if get_adjacent_dir(snake.head, a) == get_adjacent_dir(snake.neck, snake.head)]
        if len(straight) == 1:
            straight = take_first(straight)
            return distance_pq(straight, p) < distance_pq(snake.head, p)
        return False

    def make_forming_trap(moves):
        for snake in g.others:
            if distance_vector_abs(g.me.head, snake.head) == (1,1):
                if forming_trap_situation(g.me, snake):
                    trap_move = [a for a in moves if off_border_1(a) and distance_pq(a, snake.head) == 3]
                    if len(trap_move) != 0:
                        g.decision_path.append("forming trap")
                        return trap_move
            if distance_vector_abs(g.me.head, snake.head) == (2,2):
                for a in g.me.allowed_moves:
                    for b in snake.allowed_moves:
                        me2 = possible_next_state(g.me, a)
                        snake2 = possible_next_state(snake, b)
                        if forming_trap_situation(me2, snake2):
                            g.decision_path.append("make forming trap")
                            return [a]

    def forming_trap_situation(killer: Snake, target: Snake):
        return all([
            distance_pq(killer.head, target.head) == 2,
            killer.length <= target.length,
            on_border(target.head),
            distance_vector_abs(killer.head, target.head) == (1,1),
            all([is_adjacent(a, killer.head) for a in target.allowed_moves]),
            len([a for a in killer.allowed_moves if off_border_1(a) and distance_pq(a, target.head) == 3]) == 1,
        ])

    def trap_kill_oppotunity(moves):
        for snake in g.others:
            if trap_kill_situation(g.me, snake):
                trap_kill = [a for a in moves if on_border(a)]
                if len(trap_kill) != 0:
                    g.decision_path.append(f"make trap kill {snake.name}")
                    return trap_kill
                preserve_trap = [a for a in moves if off_border_1(a)]
                if len(preserve_trap) != 0:
                    g.decision_path.append(f"preserve trap kill {snake.name}")
                    return preserve_trap

    def trap_kill_situation(killer: Snake, target: Snake):
        if off_border_1(killer.head):
            for i,c in enumerate(killer.body):
                if c in killer.body[-2:]: continue
                if c == killer.head: continue
                if not is_adjacent(target.head, c): continue
                if not on_border(target.head): continue
                if on_border(c): continue
                b = killer.body[i-1]
                if get_adjacent_dir(c, b) == get_adjacent_dir(target.neck, target.head):
                    if not any([on_border(killer.body[j]) for j in range(i)]):
                        #an open trap
                        return True
        return False

    def border_confront_kill_oppotunity(moves):
        for snake in g.others:
            if border_confront_kill_situation(g.me, snake):
                g.target_snake = snake
                kill_moves = [a for a in moves if confront_kill_move(a)]
                if len(kill_moves) != 0:
                    g.decision_path.append(f"border confront kill {snake.name}")
                    return kill_moves

    def border_confront_kill_situation(killer: Snake, target: Snake):
        if not all([
            distance_pq(killer.head, target.head) == 4,
            killer.length > target.length,
            on_border(target.head),
            not on_border(killer.head),
            not off_border_1(killer.head),
            distance_vector_abs(killer.head, target.head) in [(2,2), (1,3), (3,1)],
            path_distance_pq(killer.head, target.head) == 4,
            all([distance_pq(a, killer.head) == 3 for a in target.allowed_moves]),
            any([distance_vector_abs(a, target.head) in [(1,2), (2,1)] for a in killer.allowed_moves]),
        ]):
            return False

        #check if killer kill-path is blocked
        target_point_0 = [a for a in target.allowed_moves if on_border(a)]
        if len(target_point_0) != 1: return False
        target_point_0 = take_first(target_point_0)
        killer_point_0 = [a for a in killer.allowed_moves if distance_vector_abs(a, target_point_0) in [(0,2), (2,0)]]
        if len(killer_point_0) != 1: return False
        killer_point_0 = take_first(killer_point_0)

        target_taken_point = [a for a in adj_cells(target_point_0) if on_border(a) and a != target.head]
        if len(target_taken_point) == 0:
            #target die first
            return True
        target_taken_point = take_first(target_taken_point)
        killer_catch_point = [a for a in adj_cells(killer_point_0) if is_adjacent(a, target_point_0)]
        if len(killer_catch_point) != 1: return False
        killer_catch_point = take_first(killer_catch_point)

        for step in range(11):
            killer_block_point = [a for a in adj_cells(killer_catch_point) if off_border_1(a) and is_adjacent(a, target_taken_point)]
            if len(killer_block_point) != 1: return False
            killer_block_point = take_first(killer_block_point)
            if killer_block_point in killer.body:
                index = take_first([i for i in range(killer.length) if killer.body[i] == killer_block_point])
                if killer.length - index > 3+step:
                    #killer path is blocked
                    return False

            target_taken_point = [a for a in adj_cells(target_taken_point) if on_border(a) and not is_adjacent(a, killer_catch_point)]
            if len(target_taken_point) == 0:
                #target die first
                return True
            target_taken_point = take_first(target_taken_point)
            killer_catch_point = killer_block_point

        return True

    def confront_kill_move(a):
        if len(g.target_snake.allowed_moves) != 2:
            return False
        b = [p for p in g.target_snake.allowed_moves if get_adjacent_dir(g.target_snake.head, p) != get_adjacent_dir(g.target_snake.neck, g.target_snake.head)]
        b = take_first(b)
        return distance_vector_abs(a, b) == (1,1)

    def general_confront_kill_oppotunity(moves):
        for snake in g.others:
            if general_confront_kill_situation(g.me, snake):
                g.target_snake = snake
                kill_moves = [a for a in moves if confront_kill_move(a)]
                if len(kill_moves) != 0:
                    g.decision_path.append(f"general confront kill {snake.name}")
                    return kill_moves

    def general_confront_kill_situation(killer: Snake, target: Snake):
        if all([
            distance_pq(killer.head, target.head) == 4,
            killer.length > target.length,
            len(target.allowed_moves) == 2,
            distance_vector_abs(killer.head, target.head) in [(2,2), (1,3), (3,1)],
            path_distance_pq(killer.head, target.head) == 4,
            all([distance_pq(a, killer.head) == 3 for a in target.allowed_moves]),
            any([distance_vector_abs(a, target.head) in [(1,2), (2,1)] for a in killer.allowed_moves]),
        ]):
            a,b = target.allowed_moves
            if distance_vector_abs(a,b) == (1,1):
                return True
        return False

    def general_suppressed_chasing_kill_oppotunity(moves):
        for snake in g.others:
            if g.me.length <= snake.length: continue
            if len(snake.allowed_moves) != 2: continue
            if distance_pq(g.me.head, snake.head) != 2: continue
            if distance_vector_abs(g.me.head, snake.head) not in [(0,2), (2,0)]: continue
            collision = [a for a in moves if a in snake.allowed_moves]
            if len(collision) != 1: continue
            collision = take_first(collision)
            b = take_first([a for a in snake.allowed_moves if a != collision])
            if get_adjacent_dir(snake.neck, snake.head) != get_adjacent_dir(snake.head, b): continue
            if path_distance_pq(b, collision) != 2: continue
            g.decision_path.append("general suppressed chasing")
            return [collision]

    def suppressed_chasing_kill_oppotunity(moves):
        for snake in g.others:
            if suppressed_chasing_kill_situation(g.me, snake):
                kill_moves = [a for a in moves if a in g.target_snake.allowed_moves]
                if len(kill_moves) != 0:
                    g.decision_path.append(f"chasing kill '{snake.name}'")
                    return kill_moves

    def suppressed_chasing_kill_situation(killer: Snake, target: Snake):
        if distance_pq(killer.head, target.head) == 2:
            if killer.length > target.length:
                if on_border(target.head):
                    if not on_border(killer.head):
                        if len(target.allowed_moves) == 2:
                            a,b = target.allowed_moves
                            if distance_vector_abs(a, b) == (1,1):
                                collision_points = [a for a in killer.allowed_moves if a in target.allowed_moves]
                                if len(collision_points) == 1:
                                    if len([snake for snake in g.snakes 
                                                if snake.name != killer.name and snake.name != target.name
                                                and snake.length >= killer.length 
                                                and take_first(collision_points) in snake.allowed_moves
                                                ]) == 0:
                                        g.target_snake = target
                                        return True
        return False

    def collision_cut_oppotunity(moves):
        snakes = [snake for snake in g.others if distance_vector_abs(g.me.head, snake.head) == (1,1) and g.me.length > snake.length]
        if len(snakes) == 0:
            return
        snakes = [snake for snake in snakes if len([a for a in moves if a in snake.allowed_moves]) == 2]
        if len(snakes) == 0:
            return
        snakes = [snake for snake in snakes if len(snake.allowed_moves) == 3]
        if len(snakes) != 1:
            return

        snake = take_first(snakes)
        collision = [a for a in moves if a in snake.allowed_moves]
        c = take_first([c for c in snake.allowed_moves if c not in collision])
        snake2 = possible_next_state(snake, c)
        others = [possible_next_state(s, take_first(s.allowed_moves)) for s in g.others if s.head != snake.head and len(s.allowed_moves) != 0]

        for m in collision:
            me2 = possible_next_state(g.me, m)
            hypothetic_development_territories([me2]+[snake2]+others)
            if preliminary_cut_kill_situation(me2, snake2):
                g.decision_path.append(f"try collision cut kill {m}")
                return [m]

    def trim_aset(aset, a, b=None):
        #aset is a path connected set
        #a is the entry point and a point inside aset
        #b is the exit point and is a border point - so not in aset
        b2 = take_first([p for p in adj_cells(b) if p in aset]) if b else a
        while True:
            trim_set = [p for p in aset if p != a and p != b2 and len([q for q in adj_cells(p) if q in list(aset)+[a]]) == 1]
            if len(trim_set) == 0:
                break
            aset = [p for p in aset if p not in trim_set]
        return aset

    def cut_set_dim(cset):
        if len(cset) == 0:
            return 0
        min_x = min([x for x,y in cset])
        max_x = max([x for x,y in cset])
        min_y = min([y for x,y in cset])
        max_y = max([y for x,y in cset])
        return min(max_x - min_x +1, max_y - min_y +1)

    def serious_cut_danger_a(a):
        if any([a == snake.tail for snake in g.snakes]):
            return False
        occupied = complement(g.me.territory)
        if a in occupied:
            return False
        aset = path_connected_set(a, occupied)
        aset = sorted(aset)
        if len(aset) <= 2:
            g.decision_path.append(f"avoid serious cut danger {a}")
            return True
        return False

    def no_cut_danger_a(strict):
        def fn(a):
            occupied = complement(g.me.territory)
            if a in occupied:
                return False
            aset = path_connected_set(a, occupied)
            aset = sorted(aset)

            #cut tail is not reliable
            #if any([p in aset or snake.tail in aset for snake in g.snakes for p in adj_cells(snake.tail)]):
            if any([snake.tail in aset for snake in g.snakes]):
                return True
            if any([p in aset for snake in g.snakes if snake.health == 100 for p in adj_cells(snake.tail)]):
                return True

            cut_set = [q for p in aset for q in adj_cells(p) if q not in g.me.territory and q not in g.occupied_cells[0]]
            cut_set = sorted(list(set(cut_set)))
            cut_set_dimension = cut_set_dim(cut_set)
            if strict:
                if cut_set_dimension >= 3:
                    return True
            else:
                if cut_set_dimension >= 2:
                    return True

            aset = trim_aset(aset, a)

            factor = 1.1 if strict else 0.3
            return len(aset) >= g.me.length * factor
        return fn

    def cut_set_connected(cut_set):
        #check if cut_set is connected - no hole to escape
        #and put cut_set in line order

        cut_set = sorted(list(set(cut_set)))

        if len(cut_set) == 1: return True

        def connected(a, b):
            return is_adjacent(a, b) or distance_vector_abs(a,b) == (1,1)

        cut_set_adjacency = [(a, [b for b in cut_set if connected(a, b)]) for a in cut_set ]
        cut_set_adj_number = [(a, nb) for a,b in cut_set_adjacency for nb in [len(b)]]
        terminals = [(a,nb) for a,nb in cut_set_adj_number if nb == 1]
        if len(terminals) != 2:
            return False
        inner = [(a,nb) for a,nb in cut_set_adj_number if nb == 2]
        if len(terminals)+len(inner) != len(cut_set):
            return False

        #sort cut_set in place by connection
        cut_set_copy = [a for a in cut_set]
        start = take_first(sorted([a for a,nb in terminals]))
        for i in range(len(cut_set)):
            if i == 0:
                cut_set[0] = start
                continue
            a = cut_set[i-1]
            b = [b for b in cut_set_copy if b not in cut_set[:i] and connected(a, b)]
            if len(b) != 1: 
                g.decision_path.append(f"anomaly cut_set {cut_set}")
                return False
            b = take_first(b)
            cut_set[i] = b

        return True

    def preliminary_cut_kill_situation(killer: Snake, target: Snake):

        #target is too short - cut kill is not reliable
        if target.length < 10:
            return False

        #cut_set is the set that killer will take to block target from escaping
        #it's on the border of either the killer or target territory depending on who is longer
        cut_set = [p
                    for a in target.territory
                    for p in adj_cells(a)
                    if p in target.head_space and p not in target.territory
            ] if killer.length > target.length else [a
                    for a in killer.territory
                    for p in adj_cells(a)
                    if p in target.head_space and p not in killer.territory
                       ]
 
        #chasing cut need add the collision point in cut_set
        if distance_vector_abs(killer.head, target.head) == (1,1):
            if killer.length > target.length:
                cut_set += [a for a in killer.allowed_moves if a in target.allowed_moves]

        cut_set = sorted(list(set(cut_set)))

        if len(cut_set) != 0:
            if any([a for a in cut_set if not path_connected(killer.head, a)]):
                return False
            if any([path_distance_pq(a, target.head) < path_distance_pq(a, killer.head) for a in cut_set]):
                return False

        if killer.length <= target.length:
            if len(cut_set) == 1:
                #grow back
                while True:
                    if len(cut_set) == 0: 
                        g.decision_path.append("apparently cut is done")
                        break
                    cut_point = take_first(cut_set)
                    new_cut_set = [p for p in adj_cells(cut_point) 
                            if p in killer.territory
                            and path_distance_pq(target.head, p) > path_distance_pq(target.head, cut_point)
                            ]
                    if len(new_cut_set) > 1: break
                    cut_set = new_cut_set

        #if the target has multiple place to escape then don't do it
        if not cut_set_connected(cut_set): return False

        #cut is done
        if len(cut_set) == 0: return False

        # if len(cut_set) != 0:
        #     if min([path_distance_pq(killer.head, a) for a in cut_set]) > 2: return False

        if cut_set_dim(cut_set) >= 3:
            return False

        occupied = g.occupied_cells[0]+cut_set
        oset = path_connected_set(target.head, occupied)
        oset = [p for p in oset if p != target.head]

        if len(oset) == 0:
            g.decision_path.append("cut case collision 2")
            return False

        #no tails
        if any([snake.tail in oset for snake in g.snakes]):
            return False

        #trimmed
        oset = trim_aset(oset, target.head, target.head)
        if len(oset) >= target.length * 1.1:
            return False

        occupied_border = [p for p in g.occupied_cells[0] if any([a in oset for a in adj_cells(p)])]
        if any([snake.tail in occupied_border for snake in g.snakes]):
            #snake tail just on occupied border
            return False
        
        if any([a in occupied_border for snake in g.snakes for a in adj_cells(snake.tail)]):
            #snake tail is adjacent to occupied border
            return False

        #cut_set can be long
        #if len(cut_set) > 4: return False

        target.cut_set = cut_set
        g.decision_path.append(f"preliminary cut kill target: {target.name}")
        return True

    def possible_next_state(snake, a):
        ns = Snake(
            snake.name, [a]+snake.body[:-1], snake.health-1
        ) if a not in g.food else Snake(
            snake.name, [a]+snake.body[:-1]+[snake.body[-2]], 100
        )
        ns.allowed_moves = [a for a in adj_cells(ns.head) if a not in g.occupied_cells[1]]
        return ns

    def avoid_single_collision_dead(moves):
        snakes = [snake for snake in g.others if snake.length >= g.me.length and distance_pq(snake.head, g.me.head) == 2]
        if len(snakes) != 0:
            dead_moves = [a for a in moves if any([is_adjacent(a, snake.head) and len(snake.allowed_moves) == 1 for snake in snakes])]
            moves = [a for a in moves if a not in dead_moves]
            if len(moves) != 0:
                return moves

    def immediate_kill_oppotunity(moves):
        for snake in g.others:
            if immediate_kill_situation(g.me, snake):
                kill_moves = [a for a in moves if is_adjacent(a, snake.head)]
                if len(kill_moves) != 0:
                    g.decision_path.append("immediate kill")
                    return kill_moves

    def immediate_kill_situation(killer: Snake, target: Snake):
        if distance_pq(killer.head, target.head) == 2:
            if len(target.allowed_moves) == 1:
                collision_point = take_first(target.allowed_moves)
                if collision_point in killer.allowed_moves:
                    if killer.length > target.length:
                        others = [snake for snake in g.snakes if snake.head not in [killer.head, target.head]]
                        others = [snake for snake in others if is_adjacent(collision_point, snake.head)]
                        others = [snake for snake in others if snake.length >= killer.length]
                        if len(others) == 0:
                            return True
        return False

    def ____SOME_CALCULATIONS____():
        return

    def some_calculations(moves):
        return seq([
            territories,
            number_of_snakes,
            vulnerable_snakes,
        ])(moves)

    def number_of_snakes(moves):
        if len(g.others) == 1:
            g.other = take_first(g.others)

    def territories(moves):
        hypothetic_development_territories(g.snakes)

    def hypothetic_development_territories(snakes):
        occupied = [p for snake in snakes for p in snake.body[:-1]]
        for snake in snakes:
            layers = path_connected_layers(snake.head, occupied)
            snake.cell_distance = {p:i for i,layer in enumerate(layers) for p in layer}
            snake.head_space = [p for layer in layers for p in layer if p != snake.head]
        for snake in snakes:
            others = [s for s in snakes if snake.head != s.head]
            snake.territory = [p for p in snake.head_space
                               if all([
                                   snake.cell_distance[p] < other.cell_distance.get(p, 999) 
                                   if snake.length < other.length else
                                   snake.cell_distance[p] <= other.cell_distance.get(p, 999) 
                                       for other in others])
                               ]

    def vulnerable_snakes2(moves):
        targets = [snake for snake in g.others if len(snake.allowed_moves) == 1]
        if len(targets) == 0:
            return

        snakes = g.snakes
        while True:
            one_step_world(snakes)
            snakes = [snake.next for snake in snakes if snake.next is not None]
            remain = [snake for snake in snakes if len(snake.allowed_moves) == 1 and snake.name != g.me.name]
            if len(remain) == 0: break

        for snake in targets:
            snake.vulnerable_steps = 1
            snake.dead = False
            ns = snake
            while True:
                ns = ns.next
                if ns is None:
                    snake.dead = True
                    break
                if len(ns.allowed_moves) > 1:
                    snake.vulnerable_emerge = ns
                    break
                snake.vulnerable_steps += 1
        
        vulnerables = [snake for snake in targets if not snake.dead]
        g.decision_path.append(f"vulnerable snakes: {[(snake.name, snake.vulnerable_steps, snake.vulnerable_emerge.head) for snake in vulnerables]}")
        g.vulnerables = vulnerables

    def vulnerable_snakes(moves):
        #count dead development as vulnerable
        targets = [snake for snake in g.others if len(snake.allowed_moves) == 1]
        if len(targets) == 0:
            return

        snakes = g.snakes
        while True:
            one_step_world(snakes)
            snakes = [snake.next for snake in snakes if snake.next is not None]
            remain = [snake for snake in snakes if len(snake.allowed_moves) == 1 and snake.name != g.me.name]
            if len(remain) == 0: break

        for snake in targets:
            snake.vulnerable_steps = 1
            snake.dead = False
            ns = snake
            while True:
                ns2 = ns.next
                if ns2 is None:
                    snake.dead = True
                    if len(ns.allowed_moves) == 0:
                        snake.vulnerable_emerge = ns
                    else:
                        snake.vulnerable_emerge = possible_next_state(ns, take_first(ns.allowed_moves))
                    break
                if len(ns2.allowed_moves) > 1:
                    snake.vulnerable_emerge = ns2
                    break
                snake.vulnerable_steps += 1
                ns = ns2
        
        vulnerables = [snake for snake in targets]
        g.decision_path.append(f"vulnerable snakes: {[(snake.name, snake.vulnerable_steps, snake.vulnerable_emerge.head) for snake in vulnerables]}")
        g.vulnerables = vulnerables

    def one_step_world(snakes):
        occupied = [p for snake in snakes for p in snake.body[:-1]]

        #longer one choose move first
        snakes.sort(key=lambda s: s.length, reverse=True)
        for snake in snakes:
            allowed_moves = [a for a in adj_cells(snake.head) if pos_on_board(a) and a not in occupied]
            if len(allowed_moves) == 0:
                continue
            a = take_first(allowed_moves)
            snake.next = Snake(
                snake.name, [a]+snake.body[:-1], snake.health-1
            ) if a not in g.food else Snake(
                snake.name, [a]+snake.body[:-1]+[snake.body[-2]], 100
            )
            occupied.append(a)

        #resolve dead
        ns = [snake.next for snake in snakes if snake.next is not None]
        occupied = [p for snake in ns for p in snake.body[:-1]]
        for snake in ns:
            snake.allowed_moves = [a for a in adj_cells(snake.head) if pos_on_board(a) and a not in occupied]

    ######################################################
    # utility functions
    ######################################################

    def ________UTILITY_FUNCTIONS________():
        pass

    def get_coord(ds):
        return [(d["x"], d["y"]) for d in ds]

    def get_adjacent_dir(p, q):
        x,y = p
        nx,ny = q
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    def is_opposite_dir(dir1, dir2):
        if dir1 == "up" and dir2 == "down":
            return True
        if dir1 == "down" and dir2 == "up":
            return True
        if dir1 == "left" and dir2 == "right":
            return True
        if dir1 == "right" and dir2 == "left":
            return True
        return False

    def is_perpendicular_dir(dir1, dir2):
        if dir1 == "up" and dir2 in ["left", "right"]:
            return True
        if dir1 == "down" and dir2 in ["left", "right"]:
            return True
        if dir1 == "left" and dir2 in ["up", "down"]:
            return True
        if dir1 == "right" and dir2 in ["up", "down"]:
            return True
        return False

    def get_next_move(head_coord, next_head_coord):
        return get_adjacent_dir(head_coord, next_head_coord)

    def pos_on_board(pos):
        x,y = pos
        if x < 0:
            return False
        if y < 0:
            return False
        if x >= g.state["board"]["width"]:
            return False
        if y >= g.state["board"]["height"]:
            return False
        return True

    def on_border(p):
        x,y = p
        if x == 0 or x == g.state["board"]["width"]-1:
            return True
        if y == 0 or y == g.state["board"]["height"]-1:
            return True
        return False

    def off_border_1(p):
        return not on_border(p) and any([on_border(q) for q in adj_cells(p)])

    def adj_cells(pos):
        x,y = pos
        moves = [(1,0), (-1,0), (0,1), (0,-1)]
        npos = [(a+x,b+y) for a,b in moves]
        npos = [p for p in npos if pos_on_board(p)]
        return npos

    def occupied_cells(step):
        #not including head
        #assuming no die
        #assuming no eating food
        #if eating food it will be more
        sbody = []
        for s in g.snakes:
            body = s.body
            # if s.health == 100:
                #eat food, tail will not move in the next step
                # body = body + [body[-1]]
            sbody.append(body[:-step])
        cells = [c for s in sbody for c in s]
        return cells

    def distance_pq(p, q):
        x1,y1 = p
        x2,y2 = q
        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def is_adjacent(p, q):
        return distance_pq(p, q) == 1

    def distance_to_border(p):
        x,y = p
        dx = min([x, g.state["board"]["width"]-x-1])
        dy = min([y, g.state["board"]["height"]-y-1])
        return (dx, dy)

    def distance_vector_abs(p, q):
        x1,y1 = p
        x2,y2 = q
        dx,dy = x2-x1, y2-y1
        return (abs(dx), abs(dy))

    def get_dir_number(p, q):
        assert(is_adjacent(p, q))
        x1,y1 = p
        x2,y2 = q
        dx,dy = x2-x1,y2-y1
        dir_dict = {dir:i for i, dir in enumerate(g.dir_order)}
        return dir_dict[(dx,dy)]

    def add_coord(p, dq):
        x,y = p
        dx,dy = dq
        return (x+dx, y+dy)

    def minus(dq):
        dx,dy = dq
        return (-dx, -dy)

    def is_straight(p):
        return get_adjacent_dir(g.me.head, p) == get_adjacent_dir(g.me.neck, g.me.head)

    ######################################################

    def path_distance_pq(p, q, occupied=None):
        if occupied is None:
            occupied = g.occupied_cells[0]
        #remove q from occupied otherwise there is no path
        occupied = [p for p in occupied if p != q]
        layers = path_connected_layers(p, occupied)
        for i,layer in enumerate(layers):
            if q in layer:
                return i
        return 999

    def path_connected_layers(p, occupied=None):
        if occupied is None:
            occupied = g.occupied_cells[0]
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
            occupied = g.occupied_cells[0]
        layers = path_connected_layers(p, occupied)
        return set([q for layer in layers for q in layer])

    def path_connected(p, q, occupied=None):
        if occupied is None:
            occupied = g.occupied_cells[0]
        occupied = [x for x in occupied if x != q]
        return q in path_connected_set(p, occupied)

    def shortest_path_move(p, q, occupied=None):
        if is_adjacent(p, q):
            return [q]
        if occupied is None:
            occupied = g.occupied_cells[0]
        occupied = [c for c in occupied if c != q]
        if q in path_connected_set(p, occupied):
            dist = path_distance_pq(p, q, occupied)
            layers = path_connected_layers(p, occupied)
            if len(layers) > 1:
                result = [x for x in layers[1] if path_distance_pq(x, q, occupied) == dist-1]
                return result
        return []

    ######################################################

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
        
    def prefer_by_rank(rank):
        def fn(moves):
            moves = [(a, rank(a)) for a in moves]
            moves = first_group(moves)
            return moves
        return fn

    def prefer_by_score(score):
        def fn(moves):
            moves = [(a, score(a)) for a in moves]
            moves = first_group(moves, reverse=True)
            return moves
        return fn

    def prefer(check, message=None):
        def fn(moves):
            good = [a for a in moves if check(a)]
            if message is not None:
                if isinstance(message, str):
                    g.decision_path.append(message)
                else:
                    #message must be a function
                    g.decision_path.append(message(moves, good))
            if len(good) != 0:
                return good
        return fn

    def prefer_not(check, message=None):
        return prefer(lambda a: not check(a), message)

    def take_first(moves):
        try:
            assert(len(moves) != 0)
        except AssertionError:
            turn = g.state["turn"]
            id = g.state["game"]["id"]
            print(f"id: {id}, TURN: {turn}")
            raise AssertionError
        return moves[0]

    def seq(fs):
        #seq takes in moves and process by fs sequentially
        #seq can return None if all f return None
        def fn(moves):
            result = None
            for f in fs:
                input = result or moves
                if len(input) > 1:
                    output = f(input)
                    if output is not None:
                        result = output
            return result
        return fn

    def par(fs):
        def fn(moves):
            if len(moves) > 1:
                for f in fs:
                    result = f(moves)
                    if result is not None:
                        return result
        return fn

    def cond(*pred):
        def fn(f):
            def fc(moves):
                if all(pred):
                    return f(moves)
            return fc
        return fn

    def id(moves):
        return moves

    def print_before(f):
        def fn(moves):
            print(moves)
            moves = f(moves)
            return moves
        return fn

    def print_after(f):
        def fn(moves):
            moves = f(moves)
            print(moves)
            return moves
        return fn

    def log_print(anything=None):
        turn = g.state["turn"]
        id = g.state["game"]["id"]
        print(f"MARK_EXCEPTION, TURN: {turn}, id: {id}, {anything}")

    def board_cells():
        return [(x,y)
            for x in range(g.state["board"]["width"])
            for y in range(g.state["board"]["height"])
            ]

    def complement(aset):
        return [p for p in board_cells() if p not in aset]

    def ________DB_UTILS________():
        return

    def init_db():
        db_conn = sqlite3.connect("/project/src/battlesnakes/my_database.db")
        cursor = db_conn.cursor()
        sql = """
        insert into game_turn (game_id, game_turn, food, insert_date) values (?, ?, ?, ?)
        """
        cursor.execute(sql, (g.state["game"]["id"], g.turn, "[(3, 2)]", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        sql_snake = """
        insert into snake (snake_id, name, health, body, game_id, game_turn) values (?, ?, ?, ?, ?, ?)
        """
        snakes = [(snake.id, snake.name, snake.health, str(snake.body), g.state["game"]["id"], g.turn) for snake in g.snakes]
        cursor.executemany(sql_snake, snakes)
        db_conn.commit()
        db_conn.close()

    def ________GAME_ENTRY________():
        return

    def init_game(game_state):
        g.state = game_state
        g.id = game_state["game"]["id"]
        g.turn = game_state["turn"]

        g.snakes = [
            Snake(
                name = snake["name"],
                body = get_coord(snake["body"]),
                health = snake["health"],
                id = snake["id"]
            )
            for snake in game_state["board"]["snakes"]
        ]
        g.me = [snake for snake in g.snakes for c in [game_state["you"]["body"][0]] if snake.head == (c["x"], c["y"])][0]
        g.others = [snake for snake in g.snakes if snake.head != g.me.head]

        if len(g.others) == 0:
            g.decision_path.append("only myself")
        elif len(g.others) == 1:
            g.decision_path.append("1v1")
            g.other = g.others[0]
        else:
            g.decision_path.append("1vn")

        g.food = get_coord(game_state["board"]["food"])

        g.log["id"] = game_state["game"]["id"]
        g.log["turn"] = game_state["turn"]
        g.log["me"] = g.me.dict()
        g.log["others"] = [snake.dict() for snake in g.others]
        g.log["food"] = g.food
        
    def entry_condition():
        if g.me.name in [
            "mark_snake",
            #"mark_snake_test RED",
            #"mark_snake_test BLUE",
            #"mark_snake_test GREEN",
            #"mark_snake_test YELLOW",
        ]:
            return True
        return False

    

    ######################################################
    # main process
    ######################################################

    init_game(game_state)
    if not entry_condition(): return False

    if log_db:
        init_db()

    g.log["module"] = "decision_flow"
    start_time = time.time()
    #g.e.localtime = time.localtime()

    decision()
    next_move = get_adjacent_dir(g.me.head, g.next_coord)

    #g.log["decision_support"] = {k:v for k,v in g.e.__dict__.items() if v is not None}
    g.log["decision_path"] = g.decision_path
    g.log["next_coord"] = g.next_coord
    g.log["next_move"] = next_move

    end_time = time.time()
    g.log["time"] = f"{end_time-start_time:.3f}s"

    if log: print(g.log)

    game_state["next_move"] = next_move
    return True

######################################################
# testing
######################################################

def ________TESTING________():
    pass

def reverse_coord(cs):
    return [{"x":x, "y":y} for x,y in cs]

def init_from_log(log):
    others = [ {
            "id": snake.get("id", None),
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
        } for snake in log["others"] ]
    me = [ {
            "id": snake.get("id", None),
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
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

def init_from_game_engine_log(log, name):
    snakes = [{
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
        } for snake in log["snakes"] if snake["alive"] ]
    me = [snake for snake in snakes if snake["name"] == name][0]
    others = [snake for snake in snakes if snake["name"] != name]
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

if __name__ == "__main__":
    log = {'id': '8a9d84d5-7772-4cad-a11d-46bb267c82c6', 'turn': 96, 'me': {'name': 'mark_snake', 'health': 94, 'length': 13, 'body': [(2, 4), (2, 5), (2, 6), (1, 6), (1, 7), (1, 8), (1, 9), (2, 9), (2, 8), (2, 7), (3, 7), (3, 8), (4, 8)], 'id': 'gs_wHbPdYHY94vfhhFXFDBTdKwW'}, 'others': [{'name': 'SmartyRat', 'health': 65, 'length': 6, 'body': [(3, 3), (2, 3), (1, 3), (1, 2), (1, 1), (2, 1)], 'id': 'gs_8vr638rWhtKC9YtVWfXtXgCB'}, {'name': 'do you have any games on your phone', 'health': 35, 'length': 8, 'body': [(5, 5), (4, 5), (3, 5), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)], 'id': 'gs_TPdjXcq8GMQFGPHyrVpP4Frb'}, {'name': 'ich heisse marvin', 'health': 60, 'length': 9, 'body': [(7, 5), (6, 5), (6, 4), (6, 3), (6, 2), (5, 2), (5, 3), (4, 3), (4, 4)], 'id': 'gs_37xx8yB9xvgD6qB9vqjbP9xB'}], 'food': [(10, 8), (10, 4)], 'module': 'decision_flow', 'decision_path': ['1vn', 'vulnerable snakes: []', 'try split choice', 'try split choice', 'try split choice', 'split choice 2'], 'next_coord': (1, 4), 'next_move': 'left', 'time': '0.014s'}
    log = {'id': '96c04d34-ada9-4212-9e7a-93430fdf6885', 'turn': 83, 'me': {'name': 'mark_snake', 'health': 89, 'length': 10, 'body': [(6, 7), (6, 8), (6, 9), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (9, 9)], 'id': 'gs_4mftRpgm8Kd7t9jdjcjdySxc'}, 'others': [{'name': 'Rusty the Hungry Sneke', 'health': 82, 'length': 9, 'body': [(4, 1), (5, 1), (6, 1), (7, 1), (7, 2), (6, 2), (5, 2), (5, 3), (4, 3)], 'id': 'gs_rYPSCXMyWTjfbMgfWJkbgfmY'}, {'name': 'do you have any games on your phone', 'health': 100, 'length': 11, 'body': [(8, 5), (8, 4), (9, 4), (10, 4), (10, 3), (9, 3), (8, 3), (7, 3), (7, 4), (7, 5), (7, 5)], 'id': 'gs_QrMWQSw7TVR9jfVxRjQTV7P8'}], 'food': [(10, 7)], 'module': 'decision_flow', 'decision_path': ['1vn'], 'next_coord': (7, 7), 'next_move': 'right', 'time': '0.042s'}
    log = {'id': '0e781286-af92-457c-964a-f5248b0f56e6', 'turn': 260, 'me': {'name': 'mark_snake', 'health': 97, 'length': 28, 'body': [(4, 10), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (8, 8), (9, 8), (10, 8), (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (9, 3), (8, 3), (7, 3), (6, 3), (6, 4), (7, 4), (8, 4), (9, 4), (9, 5), (9, 6), (8, 6), (7, 6), (7, 5), (6, 5)], 'id': 'gs_QXc3wjyGQdQmfRXjrM8rVPKF'}, 'others': [{'name': 'Red Yarn', 'health': 50, 'length': 26, 'body': [(2, 10), (2, 9), (1, 9), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, 8), (3, 8), (4, 8), (4, 7), (4, 6), (4, 5)], 'id': 'gs_FkxcwvWSkkgrHkjPvhw6DwK7'}], 'food': [(1, 0)], 'module': 'decision_flow', 'decision_path': ['1v1', 'try split choice', 'try split choice', 'longer confront push'], 'next_coord': (3, 10), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': 'da6f4fde-ad76-4f71-85e7-c42e6b01a0e5', 'turn': 211, 'me': {'name': 'mark_snake', 'health': 83, 'length': 16, 'body': [(7, 6), (6, 6), (6, 5), (6, 4), (6, 3), (7, 3), (7, 2), (7, 1), (7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (1, 1)], 'id': 'gs_48bxwk36rFGcFYyhvBpRGSvF'}, 'others': [{'name': 'mark_snake_test GREEN', 'health': 85, 'length': 18, 'body': [(8, 1), (8, 0), (9, 0), (10, 0), (10, 1), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (8, 9), (7, 9), (7, 8), (7, 7)], 'id': 'gs_QJVHjVD377tf67XYRvyrBVQK'}], 'food': [(4, 3), (10, 3), (3, 9)], 'module': 'decision_flow', 'decision_path': ['1v1', "vulnerable snakes: [('mark_snake_test GREEN', 3, (8, 4))]", 'preliminary cut kill target: mark_snake_test GREEN', 'no cut path', 'prefer more territory'], 'next_coord': (7, 5), 'next_move': 'down', 'time': '0.024s'}
    log = {'id': 'da6f4fde-ad76-4f71-85e7-c42e6b01a0e5', 'turn': 207, 'me': {'name': 'mark_snake', 'health': 87, 'length': 16, 'body': [(6, 3), (7, 3), (7, 2), (7, 1), (7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (1, 1), (0, 1), (0, 2), (1, 2), (2, 2)], 'id': 'gs_48bxwk36rFGcFYyhvBpRGSvF'}, 'others': [{'name': 'mark_snake_test GREEN', 'health': 89, 'length': 18, 'body': [(10, 1), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (8, 9), (7, 9), (7, 8), (7, 7), (7, 6), (7, 5), (7, 4), (6, 4)], 'id': 'gs_QJVHjVD377tf67XYRvyrBVQK'}], 'food': [(4, 3), (10, 3), (3, 9)], 'module': 'decision_flow', 'decision_path': ['1v1', 'preliminary cut kill target: mark_snake_test GREEN', 'go cut to (6, 10)'], 'next_coord': (6, 4), 'next_move': 'up', 'time': '0.035s'}
    log = {'id': 'da6f4fde-ad76-4f71-85e7-c42e6b01a0e5', 'turn': 208, 'me': {'name': 'mark_snake', 'health': 87, 'length': 16, 'body': [(6,4), (6, 3), (7, 3), (7, 2), (7, 1), (7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (1, 1), (0, 1), (0, 2), (1, 2)], 'id': 'gs_48bxwk36rFGcFYyhvBpRGSvF'}, 'others': [{'name': 'mark_snake_test GREEN', 'health': 89, 'length': 18, 'body': [(10,0), (10, 1), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (8, 9), (7, 9), (7, 8), (7, 7), (7, 6), (7, 5), (7, 4)], 'id': 'gs_QJVHjVD377tf67XYRvyrBVQK'}], 'food': [(4, 3), (10, 3), (3, 9)], 'module': 'decision_flow', 'decision_path': ['1v1', 'preliminary cut kill target: mark_snake_test GREEN', 'go cut to (6, 10)'], 'next_coord': (6, 4), 'next_move': 'up', 'time': '0.035s'}
    log = {'id': '1fea05a2-e488-4054-bac1-54237d5b2ec1', 'turn': 113, 'me': {'name': 'mark_snake', 'health': 100, 'length': 8, 'body': [(3, 0), (3, 1), (4, 1), (5, 1), (5, 2), (4, 2), (3, 2), (3, 2)], 'id': 'gs_xxRDYHPYFfSpcQjc8qxmPhv9'}, 'others': [{'name': 'Wim HU', 'health': 92, 'length': 9, 'body': [(3, 10), (2, 10), (1, 10), (0, 10), (0, 9), (0, 8), (1, 8), (2, 8), (2, 9)], 'id': 'gs_Jt3ffmc6QbVgJDbbWf44FbdD'}, {'name': 'do you have any games on your phone', 'health': 88, 'length': 10, 'body': [(5, 8), (5, 7), (5, 6), (5, 5), (6, 5), (6, 6), (6, 7), (6, 8), (7, 8), (8, 8)], 'id': 'gs_kRrT8wH3GWbdgCSMhPKTCFd6'}, {'name': 'Red Yarn', 'health': 96, 'length': 13, 'body': [(0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 7), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), (3, 3), (4, 3)], 'id': 'gs_4wJ4vW9drkXkXwDMkPyhVXXc'}], 'food': [(3, 4)], 'module': 'decision_flow', 'decision_path': ['1vn', 'preliminary cut kill target: Red Yarn', 'go cut to (1, 0)'], 'next_coord': (2, 0), 'next_move': 'left', 'time': '0.015s'}
    log = {'id': 'b84320c0-29f7-4a0e-be8a-53b0afd1a87a', 'turn': 345, 'me': {'name': 'mark_snake', 'health': 94, 'length': 25, 'body': [(4, 3), (4, 2), (4, 1), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, 10), (2, 10), (2, 9), (2, 8), (1, 8), (1, 7), (1, 6), (2, 6), (2, 7)], 'id': 'gs_XXxRwpGgdwCyBfwm6myrX4y7'}, 'others': [{'name': 'Red Yarn', 'health': 98, 'length': 28, 'body': [(7, 4), (8, 4), (9, 4), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (3, 9), (3, 8), (4, 8), (5, 8), (6, 8), (6, 7), (5, 7), (5, 6), (6, 6), (6, 5), (5, 5)], 'id': 'gs_9CVWJTpr6TXwmwBv43yHR7T9'}], 'food': [(7, 0), (1, 0), (2, 0), (4, 0), (8, 3), (10, 0), (8, 7), (6, 9), (8, 6), (3, 2)], 'module': 'decision_flow', 'decision_path': ['1v1', 'prefer more territory'], 'next_coord': (5, 3), 'next_move': 'right', 'time': '0.040s'}
    log = {'id': 'a440265c-5bff-4336-823e-896553f72cdd', 'turn': 96, 'me': {'name': 'mark_snake', 'health': 96, 'length': 10, 'body': [(8, 8), (8, 9), (9, 9), (10, 9), (10, 10), (9, 10), (8, 10), (7, 10), (6, 10), (5, 10)], 'id': 'gs_qqXchRTrcg4pTjH934V8qFMF'}, 'others': [{'name': 'snakey_wakey', 'health': 90, 'length': 13, 'body': [(7, 5), (7, 4), (7, 3), (6, 3), (6, 4), (6, 5), (5, 5), (4, 5), (4, 6), (3, 6), (3, 7), (4, 7), (5, 7)], 'id': 'gs_jJM3Bffmp7DchQHFjXRym8x3'}, {'name': 'go-st', 'health': 64, 'length': 9, 'body': [(3, 1), (4, 1), (5, 1), (5, 2), (4, 2), (3, 2), (2, 2), (2, 3), (2, 4)], 'id': 'gs_Yp7Y8M3brb7Wg8kKpjM9W7Jb'}], 'food': [(9, 5), (9, 1)], 'module': 'decision_flow', 'decision_path': ['1vn', 'avoid next step confinement [(9, 8)]'], 'next_coord': (8, 7), 'next_move': 'down', 'time': '0.031s'}
    log = {'id': 'ba22b52d-9cc0-4b99-b593-ee28c7a1e071', 'turn': 31, 'me': {'name': 'mark_snake', 'health': 91, 'length': 7, 'body': [(5, 6), (5, 5), (5, 4), (5, 3), (5, 2), (5, 1), (5, 0)], 'id': 'gs_q8rtSS3pkDvHYyGQV7xbP6JV'}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 97, 'length': 5, 'body': [(3, 10), (2, 10), (1, 10), (0, 10), (0, 9)], 'id': 'gs_ttvvQbCyphTX6PDmHwwWKWRV'}, {'name': 'do you have any games on your phone', 'health': 88, 'length': 5, 'body': [(2, 3), (3, 3), (3, 2), (2, 2), (1, 2)], 'id': 'gs_bSCPxpFVy9JpbQvWTDKDq8BF'}, {'name': 'Copy of snake2_v3_FINAL_final(1)', 'health': 94, 'length': 7, 'body': [(3, 6), (2, 6), (1, 6), (1, 5), (2, 5), (3, 5), (4, 5)], 'id': 'gs_xPdyx3pJYFH7drQywFGm6b7H'}], 'food': [(9, 10)], 'module': 'decision_flow', 'decision_path': ['1vn', 'general suppressed chasing'], 'next_coord': (4, 6), 'next_move': 'left', 'time': '0.016s'}
    log = {'id': '0e274666-e215-4f69-b763-f77a35d3ca8b', 'turn': 100, 'me': {'name': 'mark_snake', 'health': 87, 'length': 11, 'body': [(5, 9), (4, 9), (3, 9), (2, 9), (1, 9), (1, 8), (1, 7), (1, 6), (2, 6), (3, 6), (3, 7)], 'id': 'gs_FJS6VYm4vgk7RVxXPvPXKHB7'}, 'others': [{'name': 'snakey_wakey', 'health': 95, 'length': 13, 'body': [(6, 8), (7, 8), (8, 8), (9, 8), (9, 7), (9, 6), (8, 6), (8, 5), (8, 4), (7, 4), (7, 5), (6, 5), (6, 6)], 'id': 'gs_DjSdWYHy8G8CCdGRYHXxBXmF'}, {'name': 'Snakeformatika', 'health': 97, 'length': 6, 'body': [(10, 0), (9, 0), (9, 1), (9, 2), (9, 3), (10, 3)], 'id': 'gs_dft6M9WpvpDT6RddTg6Bg7Rb'}, {'name': 'Lancer', 'health': 91, 'length': 13, 'body': [(6, 0), (7, 0), (7, 1), (7, 2), (6, 2), (6, 1), (5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (3, 4), (3, 5)], 'id': 'gs_JTMKYGdKyHVT9HdpSyXF9SrK'}], 'food': [(2, 3), (7, 7)], 'module': 'decision_flow', 'decision_path': ['1vn', "vulnerable snakes: [('Snakeformatika', 2, (10, 2)), ('Lancer', 2, (4, 0))]", 'type 2 collision take risk'], 'next_coord': (5, 8), 'next_move': 'down', 'time': '0.013s'}
    log = {'id': 'be0b4f67-f2be-4599-b78b-ab36eafed702', 'turn': 80, 'me': {'name': 'mark_snake', 'health': 100, 'length': 10, 'body': [(7, 3), (7, 2), (7, 1), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 2)], 'id': 'gs_QTQwpJ3j4qPQcwDbPB3jQctY'}, 'others': [{'name': 'Fairy Rust', 'health': 22, 'length': 4, 'body': [(10, 4), (10, 5), (9, 5), (9, 6)], 'id': 'gs_pffBcbyvTjKCtcQT8XY8WHMb'}, {'name': 'Raptor', 'health': 96, 'length': 11, 'body': [(8, 4), (8, 5), (8, 6), (8, 7), (7, 7), (6, 7), (5, 7), (5, 6), (5, 5), (5, 4), (4, 4)], 'id': 'gs_w9WTgkyMgByDSvcydcdBXpbV'}, {'name': 'the evening and the morning', 'health': 95, 'length': 7, 'body': [(1, 3), (2, 3), (2, 4), (2, 5), (3, 5), (3, 4), (3, 3)], 'id': 'gs_qMb4thHWdMyYYHW6S4cXbxC9'}], 'food': [(0, 7), (9, 8)], 'module': 'decision_flow', 'decision_path': ['1vn', 'general confront kill Fairy Rust'], 'next_coord': (8, 3), 'next_move': 'right', 'time': '0.002s'}
    log = {'id': '374faffd-25a9-46d9-ac71-c3693eb28b5e', 'turn': 306, 'me': {'name': 'mark_snake', 'health': 89, 'length': 25, 'body': [(5, 1), (5, 2), (5, 3), (5, 4), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0)], 'id': 'gs_X4cpphwS8wrhWVxcvvrg79hG'}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 100, 'length': 25, 'body': [(6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (9, 5), (9, 4), (9, 3), (9, 2), (9, 1), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (7, 8), (7, 8)], 'id': 'gs_TcFVJpRM4M6tftxrx9VMpC63'}], 'food': [(0, 10)], 'module': 'decision_flow', 'decision_path': ['1v1', 'try split choice', 'try split choice', 'try split choice', 'split choice 2'], 'next_coord': (6, 1), 'next_move': 'right', 'time': '0.017s'}
    log = {'id': '59f9f779-3e31-4013-ae0a-b1136299549d', 'turn': 156, 'me': {'name': 'mark_snake', 'health': 95, 'length': 13, 'body': [(3, 1), (4, 1), (5, 1), (6, 1), (6, 2), (6, 3), (7, 3), (8, 3), (8, 2), (8, 1), (9, 1), (9, 2), (9, 3)], 'id': 'gs_4mHfV6hgjbwYvty8t6XHgc7P'}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 89, 'length': 18, 'body': [(2, 8), (2, 7), (1, 7), (1, 8), (1, 9), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (1, 5), (1, 6), (2, 6), (2, 5), (3, 5), (4, 5)], 'id': 'gs_cYcpFtjYKtGKJfpk3YbxJbW6'}, {'name': 'Wim HU', 'health': 60, 'length': 9, 'body': [(10, 10), (9, 10), (8, 10), (7, 10), (7, 9), (6, 9), (5, 9), (5, 8), (5, 7)], 'id': 'gs_hYCpWWgQMqMbMqbBRCKMXhKH'}, {'name': 'Red Yarn', 'health': 85, 'length': 9, 'body': [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (4, 3), (3, 3), (2, 3), (1, 3)], 'id': 'gs_6HdfPYQYtT8FyXWccQjHJdBC'}], 'food': [(3, 0)], 'module': 'decision_flow', 'decision_path': ['1vn', "vulnerable snakes: [('Wim HU', 1, (10, 9)), ('Red Yarn', 1, (0, 3))]", 'next to food'], 'next_coord': (3, 0), 'next_move': 'down', 'time': '0.029s'}
    log = {'id': '6fc4271f-bb0c-4733-9996-c0d1060d6fb2', 'turn': 191, 'me': {'name': 'mark_snake', 'health': 97, 'length': 18, 'body': [(8, 7), (8, 6), (8, 5), (7, 5), (7, 4), (7, 3), (7, 2), (7, 1), (7, 0), (6, 0), (5, 0), (4, 0), (4, 1), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2)], 'id': 'gs_XGJRhK3BThtQgTrdXxdSxrjC'}, 'others': [{'name': 'Copy of snake2_v3_FINAL_final(1)', 'health': 99, 'length': 27, 'body': [(7, 8), (7, 9), (8, 9), (8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (2, 9), (2, 8), (2, 7), (2, 6), (2, 5), (1, 5), (0, 5), (0, 4), (1, 4), (2, 4), (3, 4), (3, 5), (3, 6), (3, 7), (4, 7), (4, 6), (4, 5)], 'id': 'gs_dWywbCbyTQpbT3QJPmSTFgBT'}], 'food': [(0, 10), (9, 7), (8, 1), (10, 0)], 'module': 'decision_flow', 'decision_path': ['1v1', 'type 2 collision take risk'], 'next_coord': (7, 7), 'next_move': 'left', 'time': '0.005s'}




    game_state = init_from_log(log)
    self_name = "mark_snake_test GREEN"
    #game_state = init_from_db_log(id, turn, self_name)
    #game_state = init_from_game_engine_log(log, "mark_snake_test GREEN")
    main(game_state, log=True, log_db=False)

