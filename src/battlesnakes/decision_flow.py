import time
import sqlite3
import random
import math

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

            (avoid_single_collision_dead),
            avoid_next_step_no_move,
            avoid_suppressed_single_collision,

            (immediate_kill_oppotunity),
            (prefer_not(entering_danger(immediate_kill_situation))),

            (split_avoid_confinement),

            (type_1_collision),
 
            #looks not useful, disable it
            #(cond(g.me.length >= 7)(avoid_serious_cut_danger)),

            (prefer_not(entering_danger(trap_kill_situation))),

            (collision_cut_oppotunity),

            (suppressed_chasing_kill_oppotunity),
            #(trap_kill_oppotunity),

            (prefer_not(entering_danger(suppressed_chasing_kill_situation))),
            (prefer_not(entering_danger(border_confront_kill_situation))),

            (make_forming_trap),
            (type_2_collision),

            avoid_border_type_1_collision,

            #two step collision mean crowded, don't go
            (cond(len(g.others) > 1)(avoid_two_step_collision)),

            (cond(g.me.length >= 10)(split_choice)),

            (cut_kill_oppotunity),
            general_suppressed_chasing_kill_oppotunity,

            #cond(g.me.length >= 12)(par([ split_choice, collision_take_risk, ])),
            (attack_vulnerables),
            border_confront_kill_oppotunity,
            general_confront_kill_oppotunity,


            partial_cut_oppotunity,

            #(cond(g.me.length >= 12)(split_choice)),
            (cond(len(g.others) == 1)(split_choice)),

            cond(g.me.health < 20)(get_food),

            # par([
            #     cond(len(g.others) == 1 and g.me.length > g.other.length)(longer_push),
            #     cond(len(g.others) == 1 and g.me.length > g.other.length)(chase_other_tail),
            #     (wayout),
            # ]),
            #cond(len(g.others) == 1 and g.me.length > g.other.length)(par([ longer_push, (chase_other_tail), ])),

            (wayout),

            cond(len(g.others) == 1 and g.me.length > g.other.length)(longer_push),
            cond(len(g.others) == 1 and g.me.length > g.other.length)(longer_push_territory),
            cond(len(g.others) == 1 and g.me.length > g.other.length)(chase_my_tail),

            (cond(g.me.length > 8)(avoid_next_step_confinement)),
            avoid_two_snake_trap,
            #(cond(10 <= g.me.length < 12)(split_choice)),
            #cond(7 <= g.me.length <= 9)(collision_take_risk),
            (cond(g.me.length <= 10)(multi_step_collision)),

            (cond(len(g.others) == 1 and g.me.length >= g.other.length)(avoid_cornered_bordered)),
            cond(g.me.length <= 6)(short_avoid_corner),

            (type_2_collision_equal_length),

            attack_vulnerables_lower_priority,
            cond(len(g.others) > 1)(attempt_border_kill),

            #(cond(7 <= g.me.length < 10)(split_choice)),
            cond(g.me.length < 10)(split_choice),

            #cond(len(g.others) == 1 and g.me.length > g.other.length)(push),
            cond(len(g.others) > 1)(push_2),
            cond(len(g.others) > 1)(confront_push_4),
            cond(len(g.others) > 1)(corner_push),
            #cond(len(g.others) == 1 and g.me.length > 20)(gain_territory),

            #try disable this
            #cond(len(g.others) == 1 and g.me.length > g.other.length)(chase_to_the_end),

            #these are effective in killing the only other
            #cond(len(g.others) == 1 and g.me.length > g.other.length)(par([longer_push, chase_other_tail])),

            (cond(g.me.length <= 6)(killer_near_prefer_away_border)),


            #try to reproduce this effect earlier when I'm longer than local target
            cond(len(g.others) > 1 and g.me.length >= 12)(local_chasing),

            #cond(g.me.length >= 35)(chase_my_tail),
            avoid_next_step_suppressed,

            split_choice_2,

            (get_food),

            (cond(g.me.length <= 12)(multi_step_collision)),

            cond(len(g.others) == 1 and g.me.length < g.other.length)(shorter_direct_connect),
            move_close_to_open_space,

            #do split choice again with lower priority, no length condition
            #split_choice_2,

            (cond(g.me.length >= 12)(confined_follow_tail)),

            #disable equal_push and shorter_push
            #cond(len(g.others) == 1 and g.me.length == g.other.length)(equal_push),
            #cond(len(g.others) == 1 and g.me.length < g.other.length)(shorter_push),

            #cond(len(g.others) == 1 and g.me.length > g.other.length)(border_go_up),
            cond(len(g.others) == 1 and g.me.length < g.other.length)(border_go_up),
            #cond(len(g.others) == 1 and g.me.length <= g.other.length)(chase_my_tail_body),
            (cond(g.me.length <= 15)(avoid_single_move)),
            (cond(g.me.length >= 10)(prefer_less_split)),
            (cond(g.me.length <= 16)(prefer_away_border)),
            (split_choice_2),

            avoid_equal_collision,
            (avoid_single_move),

            #this is not accurate, so put in very low priority
            #(cond(g.me.length < 10 and len(g.others) >= 2)(prefer_open_space)),

            prefer(is_straight),
            #take_random,

            id,
        ])(moves)

    def decision():

        #estimated 5-step occupied cells
        g.occupied_cells = [
            occupied_cells(step)
            for step in range(1,11)
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

    def avoid_border_type_1_collision(moves):
        if not on_border(g.me.head): return
        if len(moves) != 2: return
        snakes = [snake for snake in g.others if distance_pq(snake.head, g.me.head) == 4 and path_distance_pq(snake.head, g.me.head) == 4]
        if len(snakes) != 1: return
        snake = take_first(snakes)
        if snake.length <= g.me.length: return
        danger_move = [a for a in moves if on_border(a) for b in snake.allowed_moves if distance_vector_abs(a,b) in [(0,2), (2,0)] and not on_border(b)]
        if len(danger_move) == 0: return
        moves = [a for a in moves if a not in danger_move]
        if len(moves) != 0:
            g.decision_path.append("avoid border type 1 collision")
            return moves

    def avoid_next_step_suppressed(moves):
        if not on_border(g.me.head): return
        snakes = [snake for snake in g.others if distance_pq(snake.head, g.me.head) == 4 and path_distance_pq(snake.head, g.me.head) == 4]
        if len(snakes) != 1: return
        snake = take_first(snakes)
        if snake.length > g.me.length: return
        if distance_vector_abs(g.me.head, snake.head) not in [(1,3), (3,1)]: return
        border_move = [a for a in moves if on_border(a)]
        if len(border_move) == 0: return
        border_move = take_first(border_move)
        if distance_vector_abs(border_move, snake.head) not in [(1,2), (2,1)]: return
        moves = [a for a in moves if a != border_move]
        if len(moves) != 0:
            g.decision_path.append("avoid next step suppressed")
            return moves

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

    def short_avoid_corner(moves):
        killers = [snake for snake in g.others if distance_pq(snake.head, g.me.head) <= 4 and snake.length >= g.me.length+2]
        if len(killers) == 0: return
        corners = [a for a in moves if sum(distance_to_border(a)) <= 1]
        if len(corners) != 0:
            moves = [a for a in moves if a not in corners]
            if len(moves) != 0:
                g.decision_path.append("avoid cornered moves")
                return moves

    def avoid_cornered_bordered(moves):
        #only one opponent
        if sum(distance_to_border(g.me.head)) <= 1:
            if 4 <= distance_pq(g.me.head, g.other.head) <= 8:
                if path_distance_pq(g.me.head, g.other.head) == distance_pq(g.me.head, g.other.head):
                    g.decision_path.append("avoid cornered bordered")
                    return prefer_not(on_border)(moves)
        elif sum(distance_to_border(g.me.head)) <= 2:
            if distance_pq(g.me.head, g.other.head) <= 6:
                if path_distance_pq(g.me.head, g.other.head) == distance_pq(g.me.head, g.other.head):
                    g.decision_path.append("avoid cornered bordered")
                    #return prefer_by_rank(lambda a: min(distance_vector_abs(a, g.other.head)))(moves)
                    return prefer_by_rank(lambda a: path_distance_pq(a, g.other.head))(moves)

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
        if ngroup == 1: return
        return prefer_not(serious_cut_danger_a)(moves)
        #return prefer(no_cut_danger_a(strict=False))(moves)

    def coming_to_each_other(snake: Snake, snake2: Snake):
        if distance_pq(snake.head, snake2.head) != path_distance_pq(snake.head, snake2.head): return False
        return coming_to(snake, snake2.head) and coming_to(snake2, snake.head)

    def longer_push_territory(moves):
        if not path_connected(g.other.head, g.me.head): return
        push_move = prefer_by_score(lambda a: len(new_territory(a)))(moves)
        other_move = [a for a in moves if a not in push_move]
        if len(other_move) != 0:
            g.decision_path.append("1v1 longer push territory")
            return push_move

    def longer_push(moves):
        #assume 1v1
        #if not coming_to_each_other(g.me, g.other): return
        #if not coming_to(g.other, g.me.head): return
        if not path_distance_pq(g.other.head, g.me.head) == distance_pq(g.other.head, g.me.head): return
        if distance_vector_abs(g.me.head, g.other.head) == (1,1): return
 
        g.decision_path.append("1v1 longer push")
        return par([
            push_2,
            prefer_by_score(lambda a: len(new_territory(a))),
        ])(moves)

    def new_territory(a):
        territory = g.me.territory
        territory_border = [p for p in territory if len([q for q in adj_cells(p) if q not in territory and q not in g.occupied_cells[0] and q != g.me.head]) != 0]
        lost = [p for p in territory_border if path_distance_pq(a, p) > path_distance_pq(g.me.head, p)]
        gain = [q for p in territory_border if path_distance_pq(a, p) < path_distance_pq(g.me.head, p)
                for q in adj_cells(p) if q not in territory and q not in g.occupied_cells[0] and q != g.me.head]
        new_territory = list(set([p for p in territory if p not in lost] + gain))
        return new_territory

    def move_close_to_open_space2(moves):
        if len(moves) != 3: return
        ngroup = move_connected_group(moves)
        if ngroup != 1: return
        c = take_first([a for a in moves if is_straight(a)])
        a,b = [a for a in moves if a != c]
        territory = g.me.territory
        occupied = complement(territory) + [c]
        if path_connected(a,b, occupied): return
        g.decision_path.append("move close to open space")
        return prefer_by_score(lambda a: len(path_connected_set(a, occupied)))([a,b])

    def is_connected_piece_terminal(a, piece):
        if len(piece) == 1: return True
        nabors = [b for b in piece if b != a and (is_adjacent(a, b) or distance_vector_abs(a, b) == (1,1))]
        return len(nabors) == 1

    def cosine_angle(s1, s2, s3):
        #s1, s2, s3 are sides length
        #find angle between s1 and s2
        if s1 == 0 or s2 == 0: return 0
        cos_angle = (s1**2 + s2**2 - s3**2) / (2 * s1 * s2)
        return cos_angle

    def shorter_direct_connect(moves):
        #used in 1v1 and shorter
        if path_distance_pq(g.other.head, g.me.head) != distance_pq(g.other.head, g.me.head): return
        ngroup = move_connected_group(moves)
        if ngroup != 1: return

        territory_border = [a for a in g.me.territory for p in adj_cells(a) if p not in g.me.territory and p not in g.occupied_cells[0]]
        territory_border = sorted(list(set(territory_border)))
        if len(territory_border) == 0: return
        pieces = connected_pieces(territory_border)
        if len(pieces) != 1: return
        piece = take_first(pieces)

        terminals = [a for a in piece if is_connected_piece_terminal(a, piece)]
        if len(terminals) == 0: return
        target_terminal = prefer_by_score(lambda a: path_distance_pq(a, g.me.head))(terminals)
        target_terminal = take_first(target_terminal)
        terminal_moves = shortest_path_move(g.me.head, target_terminal)
        if len(terminal_moves) == 1:
            return terminal_moves
        x0,y0 = g.me.head
        x1,y1 = target_terminal
        v1 = (x0,y1)
        v2 = (x1,y0)
        v1_path = [(x0,y) for y in irange(y0, y1)] + [(x,y1) for x in irange(x0, x1)]
        v2_path = [(x1,y) for y in irange(y0, y1)] + [(x,y0) for x in irange(x0, x1)]
        occupied_v1 = g.occupied_cells[0] + v1_path
        occupied_v2 = g.occupied_cells[0] + v2_path
        other_space_v1 = path_connected_set(g.other.head, occupied_v1)
        other_space_v2 = path_connected_set(g.other.head, occupied_v2)
        if len(other_space_v1) < len(other_space_v2):
            preferred_v = v1
        else:
            preferred_v = v2
        path_moves = shortest_path_move(g.me.head, preferred_v)
        terminal_moves = [a for a in terminal_moves if a in path_moves]
        if len(terminal_moves) != 0:
            g.decision_path.append(f"move close to open space {target_terminal} via {preferred_v}")
            return terminal_moves

        """
        length_other_head_to_terminal = math.sqrt((x1 - g.other.head[0])**2 + (y1 - g.other.head[1])**2)
        length_other_head_to_v1 = math.sqrt((v1[0] - g.other.head[0])**2 + (v1[1] - g.other.head[1])**2)
        length_other_head_to_v2 = math.sqrt((v2[0] - g.other.head[0])**2 + (v2[1] - g.other.head[1])**2)
        length_terminal_to_v1 = math.sqrt((x1 - v1[0])**2 + (y1 - v1[1])**2)
        length_terminal_to_v2 = math.sqrt((x1 - v2[0])**2 + (y1 - v2[1])**2)

        if abs(length_other_head_to_v1 - (length_other_head_to_terminal + length_terminal_to_v1)) < 0.1:
            v2_moves = shortest_path_move(g.me.head, v2)
            terminal_moves = [a for a in terminal_moves if a in v2_moves]
            if len(terminal_moves) != 0:
                g.decision_path.append(f"move close to open space {target_terminal} via v2")
                return terminal_moves
        elif abs(length_other_head_to_v2 - (length_other_head_to_terminal + length_terminal_to_v2)) < 0.1:
            v1_moves = shortest_path_move(g.me.head, v1)
            terminal_moves = [a for a in terminal_moves if a in v1_moves]
            if len(terminal_moves) != 0:
                g.decision_path.append(f"move close to open space {target_terminal} via v1")
                return terminal_moves
        else:
            #prefer v to terminal that is more perpendicular to other head to terminal line
            cos1 = cosine_angle(length_other_head_to_terminal, length_terminal_to_v1, length_other_head_to_v1)
            cos2 = cosine_angle(length_other_head_to_terminal, length_terminal_to_v2, length_other_head_to_v2)
            cos1 = abs(cos1)
            cos2 = abs(cos2)
            if cos1 < cos2:
                v1_moves = shortest_path_move(g.me.head, v1)
                terminal_moves = [a for a in terminal_moves if a in v1_moves]
                if len(terminal_moves) != 0:
                    g.decision_path.append(f"move close to open space {target_terminal} via v1 prefer")
                    return terminal_moves
            else:
                v2_moves = shortest_path_move(g.me.head, v2)
                terminal_moves = [a for a in terminal_moves if a in v2_moves]
                if len(terminal_moves) != 0:
                    g.decision_path.append(f"move close to open space {target_terminal} via v2 prefer")
                    return terminal_moves
        """

    def move_close_to_open_space(moves):
        killers = [snake for snake in g.others if snake.length > g.me.length and path_distance_pq(snake.head, g.me.head) <= 6]
        if len(killers) == 0: return

        ngroup = move_connected_group(moves)
        if ngroup != 1: return

        territory_border = [a for a in g.me.territory for p in adj_cells(a) if p not in g.me.territory and p not in g.occupied_cells[0]]
        territory_border = sorted(list(set(territory_border)))
        if len(territory_border) == 0: return
        pieces = connected_pieces(territory_border)
        if len(pieces) != 1: return
        piece = take_first(pieces)

        terminals = [a for a in piece if is_connected_piece_terminal(a, piece)]
        if len(terminals) == 0: return
        target_terminal = prefer_by_score(lambda a: path_distance_pq(a, g.me.head))(terminals)
        target_terminal = take_first(target_terminal)
        terminal_moves = shortest_path_move(g.me.head, target_terminal)
        terminal_moves = [a for a in moves if a in terminal_moves]
        if len(terminal_moves) != 0:
            g.decision_path.append(f"move close to open space {target_terminal}")
            return terminal_moves

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
        killers = [snake for snake in g.others if snake.length > g.me.length 
                   and path_distance_pq(snake.head, g.me.head) <= 4
                   and (not on_border(snake.head) or min(distance_vector_abs(g.me.head, snake.head)) != 0)
                   ]
        if len(killers) != 0:
            if len(killers) == 1:
                g.decision_path.append("killer near prefer away border")
                return prefer_not(lambda a: on_border(a))(moves)

        if on_border(g.me.head) and on_border(g.me.neck):
            killer6 = [snake for snake in g.others if snake.length >= g.me.length+2 
                    and path_distance_pq(snake.head, g.me.head, g.occupied_cells[1]) == 6
                    and not on_border(snake.head)
                    and not off_border_1(snake.head)
                    ]
            if len(killer6) != 0:
                return prefer_not(on_border)(moves)
        
    def avoid_equal_collision(moves):
        equal_collision = [a for a in moves if any([a in snake.allowed_moves and snake.length == g.me.length for snake in g.others])]
        if len(equal_collision) != 0:
            moves = [a for a in moves if a not in equal_collision]
            if len(moves) != 0:
                g.decision_path.append("avoid equal collision")
                return moves

    def prefer_away_border(moves):
        return prefer_by_score(lambda a: min(*distance_to_border(a), 2))(moves)

    def avoid_single_move(moves):
        single_move = []
        for a in moves:
            me2 = possible_next_state(g.me, a)
            if len(me2.allowed_moves) <= 1:
                single_move.append(a)
        if len(single_move) != 0:
            moves = [a for a in moves if a not in single_move]
            if len(moves) != 0:
                g.decision_path.append("avoid next step single move")
                return moves

    def prefer_less_split(moves):
        def next_ngroup(a):
            me2 = possible_next_state(g.me, a)
            ngroup = move_connected_group(me2.allowed_moves, g.occupied_cells[0]+[a])
            if ngroup is None:
                return 999
            return ngroup
        splits = [a for a in moves if next_ngroup(a) > 1 and not any([a != snake.tail for snake in g.snakes])]
        if len(splits) != 0:
            moves = [a for a in moves if a not in splits]
            if len(moves) != 0:
                g.decision_path.append("prefer less split")
                return moves

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
        #food_near = [f for f in g.food if distance_pq(f, g.me.head) <= 8 and distance_to_border(f) != (0,0)]
        food_near = [f for f in g.food if f in g.me.territory and distance_to_border(f) != (0,0)]

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

        if is_adjacent(g.me.head, food_target):
            if food_target in moves:
                g.decision_path.append("next to food")
                return [food_target]

        if g.me.length <= 10:
            if on_border(food_target):
                food_nabor = [a for a in adj_cells(food_target) if on_border(a)]
                food_nabor = [a for a in food_nabor if path_distance_pq(g.me.head, a) < path_distance_pq(g.me.head, food_target)]
                if len(food_nabor) != 0:
                    food_nabor = take_first(food_nabor)
                    food_moves = shortest_path_move(g.me.head, food_nabor)

                    moves = [a for a in moves if a in food_moves]
                    if len(moves) != 0:
                        g.decision_path.append(f"get food {food_target}")
                        return moves

            food_moves = shortest_path_move(g.me.head, food_target)
            moves = [a for a in moves if a in food_moves]
            if len(moves) != 0:
                g.decision_path.append(f"get food {food_target}")
                return moves

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

    def chase_my_tail_1(moves):
        if on_border(g.me.tail): return
        if is_adjacent(g.me.head, g.me.tail):
            if g.me.tail in moves:
                g.decision_path.append("chase my tail")
                return [g.me.tail]

    def chase_my_tail_2(moves):
        if on_border(g.me.tail): return
        if path_distance_pq(g.me.head, g.me.tail) == 2:
            tail_move = shortest_path_move(g.me.head, g.me.tail)
            moves = [a for a in moves if a in tail_move]
            if len(moves) != 0:
                food_move = [a for a in moves if a in g.food]
                if len(food_move) != 0:
                    g.decision_path.append("chase my tail food1")
                    return food_move
                g.decision_path.append("chase my tail")
                return moves
    
    def chase_my_tail_body2(moves):
        chase_points = [(i,c, p, path_distance_pq(g.me.head, p), g.me.length-i-1) 
                        for i,c in enumerate(g.me.body) 
                        if c != g.me.head and c != g.me.tail
                        and not on_border(c)
                        and path_connected(g.me.head, c)
                        for p in adj_cells(c) if p in g.me.territory
                        ]
        chase_points = [info for info in chase_points for i,c,p,d,t in [info] if (d-t) <= 1]
        if len(chase_points) == 0: return

        i,c,p,d,t = take_first(prefer_by_score(lambda a: (a[3]-a[4]))(chase_points))

        if abs(d-t) <= 1:
            tail_move = shortest_path_move(g.me.head, p)
            moves = [a for a in moves if a in tail_move]
            if len(moves) != 0:
                g.decision_path.append(f"chase my tail via body {c} direct")
                return moves
        detour_move = [a for a in moves if a not in shortest_path_move(g.me.head, p)]
        if len(detour_move) != 0:
            g.decision_path.append(f"chase my tail via body {c} detour")
            return detour_move

    def chase_my_tail_body(moves):
        chase_points = [(i,c, p, path_distance_pq(g.me.head, p), g.me.length-i-1) 
                        for i,c in enumerate(g.me.body) 
                        if c != g.me.head and c != g.me.tail
                        and not on_border(c)
                        and path_connected(g.me.head, c)
                        for p in adj_cells(c) if p in g.me.territory
                        ]
        chase_points = [info for info in chase_points for i,c,p,d,t in [info] if (d-t) <= -2]
        if len(chase_points) == 0: return

        i,c,p,d,t = take_first(prefer_by_score(lambda a: (a[3]-a[4]))(chase_points))

        detour_move = [a for a in moves if a not in shortest_path_move(g.me.head, p)]
        if len(detour_move) != 0:
            g.decision_path.append(f"chase my tail via body {c} detour")
            return detour_move

    def chase_my_tail(moves):
        return par([
            chase_my_tail_1,
            chase_my_tail_2,
            chase_my_tail_body,
        ])(moves)
        # return par([
        #     cond(g.me.health < 50)(food1),
        #     tail_move(g.me.tail),
        # ])(moves)

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

    def local_chasing(moves):
        snakes = [snake for snake in g.others if distance_pq(snake.head, g.me.head) <= 6]
        if len(snakes) != 1: return
        target = take_first(snakes)
        if target.length >= g.me.length: return

        def push(moves):
            if sum(distance_to_border(g.me.head)) < sum(distance_to_border(target.head)): return
            if distance_pq(g.me.head, target.head) != path_distance_pq(g.me.head, target.head): return
            if not coming_to_each_other(g.me, target): return
            push_move = [a for a in moves if distance_pq(a, target.head) < distance_pq(g.me.head, target.head)]
            if len(push_move) != 0:
                g.decision_path.append("local push")
                return push_move

        def chase_old(moves):
            if path_distance_pq(g.me.head, target.tail) > 8: return

            if is_adjacent(g.me.head, target.tail):
                #don't follow too close
                tail_move = [a for a in moves if path_connected(a, target.tail)]
                if len(tail_move) != 0:
                    g.decision_path.append("local chase detour")
                    return tail_move
            else:
                if path_distance_pq(g.me.head, target.tail) < path_distance_pq(target.head, target.tail):
                    tail_move = shortest_path_move(g.me.head, target.tail)
                    tail_move = [a for a in moves if a in tail_move]
                    if len(tail_move) != 0:
                        g.decision_path.append("local chase")
                        return tail_move

        def chase(moves):
            g.target_snake = target
            return chase_target_tail(moves)

        #push or chase
        return par([
            push,
            chase,
        ])(moves)

    def adjacent_chasing(moves):
        target = g.target_snake
        if is_adjacent(g.me.head, target.tail):
            #don't follow too close
            tail_move = [a for a in moves if path_connected(a, target.tail) and distance_vector_abs(a, target.tail) == (1,1)]
            if len(tail_move) != 0:
                g.decision_path.append("chase other tail detour")
                return tail_move
            """
            path_2 = grow_path(target.head, 2)[2]
            if any([len([f for f in path if f in g.food]) >= 1 for path in path_2]):
                tail_move = [a for a in moves if path_connected(a, target.tail) and distance_vector_abs(a, target.tail) == (1,1)]
                if len(tail_move) != 0:
                    g.decision_path.append("chase other tail detour")
                    return tail_move
            else:
                if target.tail in moves:
                    g.decision_path.append("chase other tail direct")
                    return [target.tail]
            """

    def distance_2_chasing(moves):
        target = g.target_snake
        if path_distance_pq(g.me.head, target.tail) in [2,3]:
            path_3 = grow_path(target.head, 3)[3]
            if not any([len([f for f in path if f in g.food]) >= 2 for path in path_3]):
                tail_move = shortest_path_move(g.me.head, target.tail)
                moves = [a for a in moves if a in tail_move
                         and len([b for b in adj_cells(a) if b not in g.occupied_cells[1]]) != 1
                         ]
                if len(moves) != 0:
                    g.decision_path.append("chase other tail direct")
                    return moves

    def body_chasing(moves):
        target = g.target_snake
        if path_distance_pq(g.me.head, target.tail) <= 2: return

        chasing_info = [(i,c,p, path_distance_pq(g.me.head, p), target.length-i-1) 
                        for i,c in enumerate(target.body)
                        if c != target.head and c not in target.body[-3:]
                        #and path_distance_pq(g.me.head, c) == distance_pq(g.me.head, c) 
                        for p in adj_cells(c) if p in g.me.territory
                        ]
        #distance within 4
        chasing_info = [info for info in chasing_info for i,c,p,d,t in [info] if abs(d-t) <= 3]
        if len(chasing_info) == 0: return
        chasing_info = prefer_by_rank(lambda a: abs(a[3]-a[4]))(chasing_info)
        chasing_info = prefer_by_score(lambda a: a[0])(chasing_info)
        i, c, p, d, t = take_first(chasing_info)
        if path_distance_pq(g.me.head, p) > 5: return

        tail_move = shortest_path_move(g.me.head, p)
        if t > d:
            #detour
            moves = [a for a in moves if a not in tail_move]
            if len(tail_move) == 1:
                moves = [a for a in moves if a not in tail_move and distance_vector_abs(a, take_first(tail_move)) == (1,1)]
            if len(moves) != 0:
                g.decision_path.append(f"chase other tail via {c} detour")
                return moves
        else:
            moves = [a for a in moves if a in tail_move]
            if len(moves) != 0:
                g.decision_path.append(f"chase other tail via {c}")
                return moves

    def chase_single_move_length(moves):
        #unfinished
        ngroup = move_connected_group(moves)
        if ngroup == 1: return
        chase_move = [a for a in moves if path_connected(a, g.other.tail)]
        if len(chase_move) != 1: return
        chase_move = take_first(chase_move)
        occupied = complement(g.me.territory)
        aset = path_connected_set(chase_move, occupied)
        aset_trimmed = trim_aset(aset, chase_move)

    def chase_target_tail(moves):
        return par([
            adjacent_chasing,
            (distance_2_chasing),
            (body_chasing),
        ])(moves)

    def chase_other_tail(moves):
        g.target_snake = g.other
        return chase_target_tail(moves)

    def confront_push_4(moves):
        snakes = [snake for snake in g.others 
                  if distance_vector_abs(g.me.head, snake.head) in [(0,4), (4,0)]
                    and snake.length < g.me.length
                    and on_border(snake.head)
                    and path_distance_pq(snake.head, g.me.head) == 4
                  ]
        if len(snakes) != 1: return
        snake = take_first(snakes)
        others = [s for s in g.others if s.name != snake.name]
        if any([distance_pq(s.head, snake.head) <= 4 for s in others]): return
        if any([distance_pq(s.head, g.me.head) <= 4 for s in others]): return
        snake_move = [a for a in snake.allowed_moves if not on_border(a)]
        if len(snake_move) != 1: return
        snake_move = take_first(snake_move)
        snake_move_ab = [a for a in adj_cells(snake_move) if off_border_1(a)]
        if len(snake_move_ab) != 2: return
        occupied = complement(snake.territory)+[snake_move]
        if not all([len(path_connected_set(a, occupied)) <= snake.length for a in snake_move_ab]): return
        push_move = [a for a in moves if distance_vector_abs(a, snake_move) in [(0,2), (2,0)]]
        if len(push_move) != 0:
            g.decision_path.append("confront push 4")
            return push_move

    def corner_push(moves):
        snakes = [snake for snake in g.others if sum(distance_to_border(snake.head)) <= 1 and snake.length < g.me.length]
        if len(snakes) == 0: return
        snake = take_first(snakes)
        if distance_pq(snake.head, g.me.head) != 4: return
        if path_distance_pq(snake.head, g.me.head) != 4: return
        if len(snake.allowed_moves) != 2: return

        snake_move = [a for a in snake.allowed_moves if not on_border(a)]
        if len(snake_move) != 1: return
        snake_move = take_first(snake_move)

        if distance_vector_abs(g.me.head, snake.head) in [(1,3), (3,1)]:
            if distance_vector_abs(snake_move, g.me.head) in [(1,2), (2,1)]:
                push_move = [a for a in moves if distance_vector_abs(a, snake_move) == (1,1)]
                if len(push_move) != 0:
                    g.decision_path.append("corner push")
                    return push_move
            if distance_vector_abs(snake_move, g.me.head) in [(0,3), (3,0)]:
                push_move = [a for a in moves if distance_vector_abs(a, snake_move) in [(0,2), (2,0)]]
                if len(push_move) == 0: return
                push_move = take_first(push_move)
                push_move_next_step = [a for a in adj_cells(push_move) if get_adjacent_dir(push_move, a) == get_adjacent_dir(snake.head, snake_move)]
                if len(push_move_next_step) != 1: return
                push_move_next_step = take_first(push_move_next_step)
                if push_move_next_step in g.occupied_cells[1]: return
                g.decision_path.append("corner push")
                return [push_move]
        if distance_vector_abs(g.me.head, snake.head) == (2,2):
            push_move = [a for a in moves if distance_vector_abs(a, snake_move) in [(1,1)]]
            if len(push_move) != 0:
                g.decision_path.append("corner push")
                return push_move

    def push_2(moves):
        if not all([g.me.length > snake.length for snake in g.others]): return
        snakes = [snake for snake in g.others if distance_vector_abs(g.me.head, snake.head) in [(0,2), (2,0)]]
        if len(snakes) != 1: return
        snake = take_first(snakes)

        collision = [a for a in adj_cells(g.me.head) if a in adj_cells(snake.head)]
        collision = take_first(collision)
        if collision not in moves: return

        #don't push from border to center
        #if min(distance_to_border(g.me.head)) >= 2:
        if sum(distance_to_border(g.me.head)) > sum(distance_to_border(snake.head)):
            if collision in moves:
                g.decision_path.append("longer confront push")
                return [collision]
        else:
            #parallel push

            if get_adjacent_dir(snake.neck, snake.head) == get_adjacent_dir(snake.head, collision):
                pass
            else:
                parallel_push = [a for a in moves if distance_vector_abs(a, snake.head) in [(1,2), (2,1)]]
                parallel_push = [a for a in parallel_push if get_adjacent_dir(g.me.head, a) == get_adjacent_dir(snake.neck, snake.head)]
                if len(parallel_push) != 1: return
                parallel_push = take_first(parallel_push)
                snake_move = [a for a in snake.allowed_moves if distance_vector_abs(a, collision) == (1,1)]
                if len(snake_move) == 0: return
                g.decision_path.append("parallel push")
                return [parallel_push]


    def coming_push(moves):
        if coming_to(g.me, g.other.head) and coming_to(g.other, g.me.head):
            if distance_pq(g.me.head, g.other.head) == 4:
                moves = [a for a in moves if distance_pq(a, g.other.head) < distance_pq(g.me.head, g.other.head)]
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
    
    def push(moves):
        return par([
            push_2,
            (push_4),
        ])(moves)

    def equal_push(moves):
        if g.me.length != g.other.length: return
        if distance_pq(g.me.head, g.other.head) != path_distance_pq(g.me.head, g.other.head): return
        if not coming_to_each_other(g.me, g.other): return

        def distance_rank(p):
            x,y = p
            return x**2 + y**2

        avoids = [a for a in moves if a in g.other.allowed_moves]
        push_move = [a for a in moves if a not in avoids]
        if len(push_move) != 0:
            g.decision_path.append("equal push")
            #return prefer_by_rank(lambda a: distance_rank(distance_vector_abs(a, g.other.head)))(push_move)
            return prefer_by_score(lambda a: len(new_territory(a)))(push_move)

    def shorter_push(moves):
        if g.me.length >= g.other.length: return
        if distance_pq(g.me.head, g.other.head) != path_distance_pq(g.me.head, g.other.head): return
        #if not coming_to_each_other(g.me, g.other): return

        def distance_rank(p):
            x,y = p
            return x**2 + y**2

        if any([
            sum(distance_to_border(g.me.head)) > sum(distance_to_border(g.other.head)),
            min(distance_vector_abs(g.me.head, g.other.head)) == 0 and get_adjacent_dir(g.me.neck, g.me.head) != get_adjacent_dir(g.other.neck, g.other.head)
        ]):
            avoids = [a for a in moves if a in g.other.allowed_moves or any([distance_vector_abs(a,b) == (1,1) for b in g.other.allowed_moves])]
            push_move = [a for a in moves if a not in avoids]
            if len(push_move) != 0:
                g.decision_path.append("short push")
                #return prefer_by_rank(lambda a: distance_rank(distance_vector_abs(a, g.other.head)))(push_move)
                return prefer_by_score(lambda a: len(new_territory(a)))(push_move)


    def collision_score(a, consider_equal=True):
        killers = [snake for snake in g.others if snake.length > g.me.length if distance_pq(snake.head, g.me.head) <= 8]
        nonkillers = [snake for snake in g.others if snake.length == g.me.length if distance_pq(snake.head, g.me.head) <= 8]
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

    def avoid_two_step_collision(moves):
        for snake in g.snakes:
            snake.head_paths = grow_path(snake.head, 5)

        two_step_collision = [a for a in moves if collision_score(a, consider_equal=False) == 2]
        if len(two_step_collision) != 0:
            moves = [a for a in moves if a not in two_step_collision]
            if len(moves) != 0:
                g.decision_path.append("avoid two step collision")
                return moves

    def multi_step_collision(moves):
        for snake in g.snakes:
            snake.head_paths = grow_path(snake.head, 5)

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

    def collision_wayout_11(avoid):

        cut_set = [p for a in g.me.territory for p in adj_cells(a) if p not in g.me.territory and p in g.me.head_space]
        cut_set = sorted(list(set(cut_set)))

        #has wayout
        if not cut_set_connected(cut_set): return True
        if cut_set_dim(cut_set) >= 2: return True

        #check wayout
        #consider this later
        #in type-2 collision case, you don't have the full g.me.territory to wiggle

        if any([snake.tail in g.me.territory for snake in g.snakes]):
            return True

        aset = sorted(list(set(g.me.territory)))

        adjacent_indexes = [i
                for i,c in enumerate(g.me.body)
                for p in adj_cells(c) if p in g.me.territory
                ]

        if len(adjacent_indexes) == 0: return False

        max_index = max(adjacent_indexes)
        wayout_point = g.me.body[max_index]
        wayout_length = g.me.length - max_index - 1
        if len(cut_set) >= 5 and len(cut_set) >= len(aset) * 0.4:
            if wayout_length <= len(cut_set):
                return False
        oset = trim_aset(aset, g.me.head, wayout_point)
        if wayout_length <= len(oset): 
            return True

        return False

    def type_2_collision_equal_length(moves):
        nonkillers = [snake for snake in g.others if snake.length == g.me.length and distance_vector_abs(g.me.head, snake.head) == (1,1)]
        if len(nonkillers) != 1: return
        nonkiller = take_first(nonkillers)

        if len(moves) != 3: return

        avoid = take_first([a for a in moves if not is_adjacent(a, nonkiller.head)])
        middle = take_first([a for a in moves if distance_vector_abs(a, avoid) == (1,1)])
        collision = take_first([a for a in moves if a not in [avoid, middle]])
        if sum(distance_to_border(avoid)) <= 3:
            g.decision_path.append("type 2 collision equal length take risk")
            return [middle, collision]
        g.decision_path.append(f"type 2 collision take equal length avoid point {avoid}")
        return [avoid]

    def type_2_collision(moves):

        killers = [snake for snake in g.others if snake.length > g.me.length and distance_vector_abs(g.me.head, snake.head) == (1,1)]
        nonkillers = [snake for snake in g.others if snake.length == g.me.length and distance_vector_abs(g.me.head, snake.head) == (1,1)]
        if len(killers) == 0 and len(nonkillers) == 0: return

        if len(killers) > 1:
            avoid = [a for a in moves if not any([is_adjacent(a, killer.head) for killer in killers])]
            if len(avoid) != 0:
                g.decision_path.append("multiple killers take avoid point")
                return avoid

        if len(killers) != 1: return
        killer = take_first(killers)

        for i in range(1):
            if len(moves) != 2: continue
            avoid = [a for a in moves if not is_adjacent(a, killer.head)]
            if len(avoid) != 0:
                g.decision_path.append("type 2 collision take avoid point")
                return avoid
            #if len(killer.allowed_moves) != 3: continue
            border_move = [a for a in moves if on_border(a)]
            if len(border_move) != 0:
                g.decision_path.append("type 2 collision take border risk")
                return border_move
            killer_other_move = [a for a in killer.allowed_moves if a not in moves]
            if len(killer_other_move) != 1: continue
            killer_other_move = take_first(killer_other_move)
            risk_move = [a for a in moves if distance_vector_abs(a, killer_other_move) != (1,1)]
            if len(risk_move) != 1: continue
            g.decision_path.append("take risk so that killer can no longer chase")
            return risk_move

        if len(moves) != 3: return

        avoid = ([a for a in moves if not is_adjacent(a, killer.head)])
        if len(avoid) == 0: return
        avoid = take_first(avoid)
        middle = ([a for a in moves if distance_vector_abs(a, avoid) == (1,1)])
        if len(middle) == 0: return
        middle = take_first(middle)
        collision = ([a for a in moves if a != avoid and a != middle])
        if len(collision) == 0: return
        collision = take_first(collision)

        if len(g.others) > 1 and path_distance_pq(avoid, g.me.tail) <= 2:
            g.decision_path.append("collision type 2 take avoid point loop tail")
            return [avoid]

        if len(g.others) > 1 and sum(distance_to_border(avoid)) <= 2:
            g.decision_path.append("collision type 2 take risk")
            return prefer_by_rank(lambda a: sum(distance_to_border(a)))([collision, middle])

        cut_set = [p for a in g.me.territory for p in adj_cells(a) if p not in g.me.territory and p in g.me.head_space]
        cut_set = sorted(list(set(cut_set)))

        #has wayout
        if not cut_set_connected(cut_set): 
            g.decision_path.append("collision type 2 take avoid point")
            return [avoid]

        if cut_set_dim(cut_set) >= 2:
            g.decision_path.append("collision type 2 take avoid point")
            return [avoid]

        if any([snake.tail in g.me.territory for snake in g.snakes]):
            g.decision_path.append("collision type 2 take avoid point")
            return [avoid]

        aset = sorted(list(set(g.me.territory)))
        #aset = path_connected_set(avoid, g.occupied_cells[1])

        """
        if len(aset) <= 2:
            g.decision_path.append("collision type 2 take risk")
            return [collision]
        """

        if len(aset) >= g.me.length:
            g.decision_path.append("collision type 2 take avoid point")
            return [avoid]

        if any([snake.tail in aset for snake in g.snakes]):
            g.decision_path.append("collision type 2 take avoid point - tail")
            return [avoid]

        if any([any([is_adjacent(snake.tail, a) for a in aset]) and snake.tail not in cut_set for snake in g.snakes if snake.health == 100]):
            g.decision_path.append("collision type 2 take avoid point - tail")
            return [avoid]

        adjacent_indexes = [i
                for i,c in enumerate(g.me.body) if c != g.me.head and c != g.me.tail
                for p in adj_cells(c) if p in aset 
                #and p != avoid
                ]

        if len(adjacent_indexes) == 0:
            g.decision_path.append("collision type 2 take risk")
            return [collision]

        max_index = max(adjacent_indexes)
        wayout_point = g.me.body[max_index]
        wayout_length = g.me.length - max_index - 1

        oset = trim_aset(aset, g.me.head, wayout_point)
        if wayout_length <= len(oset): 
            g.decision_path.append("collision type 2 take avoid point")
            return [avoid]

        if len(g.others) == 1 and len(cut_set) >= 5 and len(cut_set) >= len(aset) * 0.4:
            if wayout_length <= len(cut_set):
                g.decision_path.append("collision type 2 take risk")
                return [collision]

        #if len(g.others) > 1 and g.me.length >= 10 and all([g.me.length <= snake.length for snake in g.others]):
        if len(g.others) > 1 and g.me.length >= 10:
            if len(oset) < wayout_length:
                g.decision_path.append("collision type 2 take risk")
                return [collision]

        if len(g.others) > 1 and len(oset) >= 2:
            g.decision_path.append("collision type 2 take avoid point")
            return [avoid]

        if len(g.others) == 1 and len(oset) < wayout_length:
            g.decision_path.append("collision type 2 take risk")
            return [collision]

    def split_choice_2(moves):
        return seq([
            split_avoid_preliminary_trap,
            #(avoid_static_confinement),
            multistep_terrritories(1),

            par([
                split_choose_spacious,
                split_choose_my_tail,
                (split_choose_other_tail),
                (split_choose_more_space),
                #(split_prefer_diagonal_cut_set),
            ]),
        ])(moves)

    def split_self_confinement(a):
        #occupied = complement(g.me.territory)
        occupied = g.occupied_cells[1]
        aset = path_connected_set(a, occupied)
        aset = sorted(list(set(aset)))
        #self confined
        if not all([p in g.me.body for a in aset for p in adj_cells(a) if p not in aset]): return False

        wayout_point = has_wayout_on_myself2(aset, a)
        return wayout_point is None

    def split_avoid_confinement(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 2: return
        confined_moves = [a for a in moves if split_self_confinement(a)]
        if len(confined_moves) != 0:
            moves = [a for a in moves if a not in confined_moves]
            if len(moves) != 0:
                g.decision_path.append("split avoid self confined moves")
                return moves

    def split_choice(moves):
        ngroup = move_connected_group(moves)
        if ngroup == 1:
            return

        if ngroup == 3:
            if path_connected(g.me.head, g.me.tail):
                return shortest_path_move(g.me.head, g.me.tail)
            else:
                snakes = [snake for snake in g.others if path_connected(g.me.head, snake.tail)]
                if len(snakes) != 0:
                    snake = take_first(snakes)
                    return shortest_path_move(g.me.head, snake.tail)
            return prefer_by_score(lambda a: len(path_connected_set(a)))(moves)
        
        ok_set = [a for a in moves if combined_wayout(a)]
        if len(ok_set) != 0 and len(ok_set) != len(moves):
            g.decision_path.append("split choice")
            return ok_set

    def move_space(a, occupied=None):
        if occupied is None:
            occupied = complement(g.me.territory)
        if a in occupied:
            return []
        return path_connected_set(a, occupied)

    def split_choose_spacious(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 2: return
        occupied = complement(g.me.territory2)+[a for a in g.me.allowed_moves if a not in moves]
        spacious_move = [a for a in moves if len(move_space(a, occupied)) >= 0.8 * g.me.length]
        not_spacious_move = [a for a in moves if a not in spacious_move]
        if len(not_spacious_move) != 0:
            moves = [a for a in moves if a not in not_spacious_move]
            if len(moves) != 0:
                g.decision_path.append("split2 choose spacious")
                return moves

    def split_choose_my_tail(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 2: return
        def has_my_tail(a):
            aset = path_connected_set(a, complement(g.me.territory2)+[a for a in g.me.allowed_moves if a not in moves])
            if g.me.tail in aset:
                return True
            if g.me.health == 100:
                if any([is_adjacent(g.me.tail, a) for a in aset]):
                    return True
            return False
        moves = [a for a in moves if has_my_tail(a)]
        if len(moves) != 0:
            g.decision_path.append("split2 choose my tail")
            return moves

    def split_choose_other_tail(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 2: return
        def has_other_tail(a):
            aset = path_connected_set(a, complement(g.me.territory2)+[a for a in g.me.allowed_moves if a not in moves])
            if any([snake.tail in aset for snake in g.others]):
                return True
            if any([is_adjacent(snake.tail, a) for snake in g.others if snake.health == 100 for a in aset]):
                return True
            return False
        moves = [a for a in moves if has_other_tail(a)]
        if len(moves) != 0:
            g.decision_path.append("split2 choose other tail")
            return moves

    def split_choose_more_space(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 2: return
        #occupied = complement(g.me.territory)+[a for a in g.me.allowed_moves if a not in moves]
        occupied = complement(g.me.territory2)+[a for a in g.me.allowed_moves if a not in moves]
        space_move =  prefer_by_score(lambda a: len(move_space(a, occupied)))(moves)
        less_space = [a for a in moves if a not in space_move]
        if len(less_space) != 0:
            moves = [a for a in moves if a not in less_space]
            if len(moves) != 0:
                g.decision_path.append("split2 choose more space")
                return moves
 
    def split_prefer_diagonal_cut_set(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 2: return
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

    def split_avoid_preliminary_trap(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 2: return
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
        others = [snake for snake in g.others if snake.head != killer.head]
        danger_set = []
        for a in moves:
            me2 = possible_next_state(g.me, a)
            for b in killer.allowed_moves:

                #if b in moves and killer.length <= g.me.length: continue
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
                if any([snake.body[-2] in oset for snake in others]): continue

                #trimmed
                indexes = [i for i,c in enumerate(me2.body) if c != me2.tail and any([p in oset for p in adj_cells(c)])]
                #indexes = [i for i,c in enumerate(me2.body) if c != me2.tail for p in adj_cells(c) if p in oset ]

                if len(indexes) == 0: continue
                max_index = max(indexes)
                wayout_point = me2.body[max_index]
                wayout_length = me2.length - max_index -1
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

        """
        if len(cut_set) != 0:
            future_tail = g.me.body[-1-len(cut_set)]
            if any([p in g.me.territory for p in adj_cells(future_tail)]):
                return
        """

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
                        for p in adj_cells(c) if p in aset and p != a
                        ]
        if len(adjacent_indexes) == 0: return
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
                    for i,c in enumerate(snake.body) if i != snake.length-1 #don't count tail
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
        
        if len(g.me.territory) <= 5 and not any([a in g.me.territory for a in g.food]):
            if path_distance_pq(g.me.head, wayout_point) >= g.me.wayout_length + 1:
                g.decision_path.append("go direct to wayout")
                return shortest_path_move(g.me.head, wayout_point)

        if path_distance_pq(g.me.head, wayout_point) >= g.me.wayout_length + 3:
            g.decision_path.append("wayout path long enough to go direct")
            return shortest_path_move(g.me.head, wayout_point)

        g.decision_path.append("meander")
        return prefer_less_next_moves(
            prefer_by_score(lambda a: path_distance_pq(a, wayout_point))(moves_in_territory)
        )

    def prefer_less_next_moves(moves):
        def n_next_moves(a):
            occupied = complement(g.me.territory)
            next_moves = [p for p in adj_cells(a) if p not in occupied]
            return len(next_moves)
        return prefer_by_rank(n_next_moves)(moves)

    def move_connected_group(moves, occupied=None):
        if occupied is None:
            #tail -1 will not split routes
            occupied = g.occupied_cells[1]

        if len(moves) == 1:
            return 1
        if len(moves) == 2:
            a,b = moves
            if distance_vector_abs(a,b) == (1,1):
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

        rects = []

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
            oset = sorted(list(set(oset)))
            if any([snake.tail in oset for snake in g.snakes]): continue
            if any([any([is_adjacent(snake.tail, a) for a in oset]) for snake in g.snakes if snake.health == 100]): continue

            v2 = [p for p in [(x0,y1), (x1,y0)] if min(distance_vector_abs(g.me.head, p)) == 0]
            v2 = take_first(v2)

            #path to v via v2
            path_1 = [(x,y) for x0,y0 in [g.me.head] for x1,y1 in [v2] for x in irange(x0,x1) for y in irange(y0,y1)]
            path_2 = [(x,y) for x0,y0 in [v2] for x1,y1 in [v] for x in irange(x0,x1) for y in irange(y0,y1)]
            path = path_1 + path_2
            path = [p for p in path if p != v]
            path = sorted(list(set(path)))
            #path must touch target territory
            if not any([q in oset for p in path for q in adj_cells(p)]):
                continue

            room = len(oset)
            oset = trim_aset(oset, target.head, target.head)
            if len(oset) > target.length * 1.1:
                continue

            if path_distance_pq(g.me.head, v) != distance_pq(g.me.head, v):
                continue

            rects.append((rect, room, v, v2))

        if len(rects) == 0: return

        rect, n, v, v2 = take_first(prefer_by_rank(lambda a: a[1])(rects))

        g.decision_path.append(f"go cut to {v}")
        cut_moves = shortest_path_move(g.me.head, v)
        cut_moves = prefer_by_rank(lambda a: distance_pq(a, target.head))(cut_moves)
        cut_moves = prefer_by_rank(lambda a: distance_pq(a, v2))(cut_moves)
        return cut_moves

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

    def attempt_border_kill(moves):
        border_snakes = [snake for snake in g.others 
                         if snake.length < g.me.length 
                         and on_border(snake.head) 
                         and distance_pq(snake.head, g.me.head) <= 6
                         and not on_border(snake.neck)
                         ]
        if len(border_snakes) != 1: return
        snake = take_first(border_snakes)
        ab = [p for p in adj_cells(snake.head) if on_border(p)]
        a = [p for p in ab if p in snake.territory]
        if len(a) != 1: return
        a = take_first(a)
        aset = path_connected_set(a, complement(snake.territory))
        kill_position = [a for p in aset for a in adj_cells(p) if a in g.me.territory]
        kill_position = list(set(kill_position))
        if len(kill_position) == 0: return
        kill_position = prefer_by_rank(lambda a: path_distance_pq(g.me.head, a))(kill_position)
        kill_position = take_first(kill_position)
        kill_move = shortest_path_move(g.me.head, kill_position)
        kill_move = [a for a in moves if a in kill_move]
        if len(kill_move) != 0:
            g.decision_path.append("border kill attempt")
            return kill_move

        border_snakes = sorted(border_snakes, key=lambda s: distance_pq(s.head, g.me.head))
        snake = take_first(border_snakes)
        attack_moves = [a for a in moves if distance_pq(a, snake.head) < distance_pq(g.me.head, snake.head)]
        if len(attack_moves) != 0:
            g.decision_path.append("border kill opportunity")
            return attack_moves

    def attack_vulnerables_lower_priority(moves):
        vul = [snake for snake in g.vulnerables if snake.length < g.me.length and distance_pq(snake.head, g.me.head) <= 4]
        if len(vul) == 0: return

        vul = take_first(vul)
        vul2 = vul.vulnerable_emerge
        if vul.vulnerable_steps > 2: return
        if sum(distance_to_border(vul2.head)) > 2: return

        #push it
        moves = [a for a in moves if distance_pq(a, vul2.head) < distance_pq(g.me.head, vul2.head)]
        if len(moves) != 0:
            g.decision_path.append("vulnerable snake is near and cornered try kill it")
            return moves

    def attack_vulnerables(moves):
        for snake in g.vulnerables:
            g.target_snake = snake
            if snake.dead:
                g.decision_path.append("vulnerable target evolve dead")
                #return [g.me.next.head]
                return
            if g.me.length <= snake.length:
                g.decision_path.append("vulnerable but I'm short")
                return
            if g.me.length > snake.length:
                result = par([
                    attack_vulnerables_equal_distance,
                    (attack_vulnerables_distance_2),
                    attack_vulnerables_path_distance_2,
                    #disable this
                    #(attack_vulnerables_distance_4),
                    (attack_vulnerables_distance_excess),
                    (attack_vulnerables_negative_distance),
                ])(moves)
                if result is not None:
                    return result

    def attack_vulnerables_negative_distance(moves):
        snake = g.target_snake
        snake2: Snake = snake.vulnerable_emerge
        if path_distance_pq(g.me.head, snake2.head) < snake.vulnerable_steps:
            attack_move = shortest_path_move(g.me.head, snake2.head)
            attack_move = [a for a in moves if a in attack_move]
            if len(attack_move) != 0:
                g.decision_path.append("attack vulnerables negative distance")
                return attack_move

    def attack_vulnerables_distance_excess(moves):
        snake = g.target_snake
        snake2: Snake = snake.vulnerable_emerge
        if not on_border(snake2.head): return
        attack_point = [p for a in adj_cells(snake2.head) if not on_border(a) for p in adj_cells(a) if p != snake2.head and distance_vector_abs(p, snake2.head) != (1,1)]
        if len(attack_point) != 1: return
        attack_point = take_first(attack_point)
        if path_distance_pq(g.me.head, attack_point) < snake.vulnerable_steps:
            meander = [a for a in moves if a not in shortest_path_move(g.me.head, attack_point)]
            if len(meander) != 0:
                g.decision_path.append("attack vulnerable take meander")
                return meander

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
                if len(attack_point) != 0:
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
                if any([on_border(c) for c in g.me.body if c != g.me.head]):
                    #trap is done
                    continue
                if on_border(g.me.head):
                    #trap just made, don't go back
                    if len(moves) != 2: continue
                    if not all([on_border(a) for a in moves ]): continue
                    moves = [a for a in moves if not path_connected(a, snake.head)]
                    if len(moves) != 0:
                        g.decision_path.append(f"avoid going back after trap kill {snake.name}")
                        return moves
                trap_kill = [a for a in moves if on_border(a)]
                if len(trap_kill) != 0:
                    g.decision_path.append(f"make trap kill {snake.name}")
                    return trap_kill
                preserve_trap = [a for a in moves if off_border_1(a)]
                if len(preserve_trap) != 0:
                    g.decision_path.append(f"preserve trap kill {snake.name}")
                    return preserve_trap

    def trap_kill_situation(killer: Snake, target: Snake):
        for i,c in enumerate(killer.body):
            if c in killer.body[-1:]: continue
            if c == killer.head: continue
            if not is_adjacent(target.head, c): continue
            if not on_border(target.head): continue
            if on_border(c): continue
            b = killer.body[i-1]
            if get_adjacent_dir(c, b) == get_adjacent_dir(target.neck, target.head):
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
        target_contact_point = target_point_0
        killer_catch_point = [a for a in adj_cells(killer_point_0) if is_adjacent(a, target_point_0)]
        if len(killer_catch_point) != 1: return False
        killer_catch_point = take_first(killer_catch_point)

        for step in range(11):
            #killer_block_point = [a for a in adj_cells(killer_catch_point) if off_border_1(a) and is_adjacent(a, target_taken_point)]
            killer_block_point = [a for a in adj_cells(killer_catch_point) if a != target_contact_point and a in adj_cells(target_taken_point)]
            if len(killer_block_point) != 1: return False
            killer_block_point = take_first(killer_block_point)
            if killer_block_point in killer.body:
                index = take_first([i for i in range(killer.length) if killer.body[i] == killer_block_point])
                if killer.length - index > 3+step:
                    #killer path is blocked
                    return False

            target_contact_point = target_taken_point
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
            if sum(distance_to_border(g.me.head)) < sum(distance_to_border(snake.head)): continue
            g.decision_path.append("general suppressed chasing")
            return [collision]

    def suppressed_chasing_kill_oppotunity(moves):
        for snake in g.others:
            if suppressed_chasing_kill_situation(g.me, snake):
                kill_moves = [a for a in moves if a in snake.allowed_moves]
                if len(kill_moves) != 0:
                    g.decision_path.append(f"chasing kill {snake.name}")
                    return kill_moves

    def suppressed_chasing_kill_situation(killer: Snake, target: Snake):
        if distance_pq(killer.head, target.head) != 2: return False
        if killer.length <= target.length: return False
        if not on_border(target.head): return False
        if on_border(killer.head): return False
        if len(target.allowed_moves) != 2: return False
        a,b = target.allowed_moves
        if distance_vector_abs(a, b) != (1,1): return False
        collision_points = [a for a in killer.allowed_moves if a in target.allowed_moves]
        if len(collision_points) != 1: return False
        if len([snake for snake in g.snakes 
                    if snake.head != killer.head and snake.head != target.head
                    and snake.length >= killer.length 
                    and take_first(collision_points) in snake.allowed_moves
                    ]) != 0: 
            return False

        target_head = target.head
        target_neck = target.neck
        killer_head = killer.head

        for step in range(11):
            new_target_head = [a for a in adj_cells(target_head) if get_adjacent_dir(target_head, a) == get_adjacent_dir(target_neck, target_head)]
            new_killer_head = [a for a in adj_cells(killer_head) if get_adjacent_dir(killer_head, a) == get_adjacent_dir(target_neck, target_head)]
            if len(new_killer_head) == 0: return False
            new_killer_head = take_first(new_killer_head)
            if new_killer_head in g.occupied_cells[step]: return False
            if len(new_target_head) == 0: return True
            new_target_head = take_first(new_target_head)
            if new_target_head in g.occupied_cells[step]: return True
            target_neck = target_head
            target_head = new_target_head
            killer_head = new_killer_head

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
        avoid = take_first([a for a in snake.allowed_moves if a not in collision])
        snake2 = possible_next_state(snake, avoid)
        c = take_first([a for a in snake.allowed_moves if distance_vector_abs(a, avoid) == (1,1)])
        me2 = possible_next_state(g.me, c)
        k = take_first([a for a in snake.allowed_moves if a not in [avoid, c]])
        others = [possible_next_state(s, take_first(s.allowed_moves)) for s in g.others if s.head != snake.head and len(s.allowed_moves) != 0]

        hypothetic_development_territories([me2]+[snake2]+others)
        if preliminary_cut_kill_situation(me2, snake2):
            g.decision_path.append(f"try collision cut kill {c}")
            return [c]

    def trim_aset(aset, a, b=None):
        #aset is a path connected set
        #a is the entry point and a point inside aset
        #b is the exit point and is a border point - so not in aset
        #b2 = take_first([p for p in adj_cells(b) if p in aset]) if b else a
        b2 = a
        if b is not None:
            x = [p for p in adj_cells(b) if p in aset]
            if len(x) != 0:
                b2 = take_first(x)
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
            if any([snake.body[-2] in aset for snake in g.snakes]):
                return True
            #if any([p in aset for snake in g.snakes if snake.health == 100 for p in adj_cells(snake.tail)]): return True

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
            good = len(aset) >= g.me.length * factor
            return good
        return fn

    def cut_set_connected(cut_set):
        #check if cut_set is connected - no hole to escape
        #and put cut_set in line order

        cut_set = sorted(list(set(cut_set)))

        if len(cut_set) <= 1: return True

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

    def connected_to(one, cut_set):
        result = [one]
        for a in cut_set:
            if a == one: continue
            if any([is_adjacent(a, p) for p in result]):
                result.append(a)
                continue
            if any([distance_vector_abs(a, p) == (1,1) for p in result]):
                result.append(a)
                continue
        return sorted(result)

    def connected_pieces(cut_set):
        one_set = connected_to(take_first(cut_set), cut_set)
        rest_set = [a for a in cut_set if a not in one_set]
        if len(rest_set) == 0:
            return [one_set]
        return [one_set] + connected_pieces(rest_set)

    def partial_cut_oppotunity(moves):
        #choose a target
        for snake in g.others:
            cut_set = [p for a in snake.territory for p in adj_cells(a) if p not in snake.territory and p not in g.occupied_cells[0]]
            cut_set = sorted(list(set(cut_set)))
            if len(cut_set) == 0: continue
            cut_set_pieces = connected_pieces(cut_set)
            if len(cut_set_pieces) !=2: continue
            if max([len(piece) for piece in cut_set_pieces]) > 3: continue
            piece = [piece for piece in cut_set_pieces if any([a in g.me.territory for a in piece])]
            if len(piece) == 0: continue
            piece = take_first(piece)
            if len(piece) > 2: continue
            if len(piece) == 1:
                cut_point = take_first(piece)
                cut_move = shortest_path_move(g.me.head, cut_point)
                moves = [a for a in moves if a in cut_move]
                if len(moves) != 0:
                    g.decision_path.append(f"partial cut {snake.name} {piece}")
                    return moves
            elif len(piece) == 2:
                a,b = piece
                if distance_vector_abs(a,b) == (1,1):
                    c = [p for p in adj_cells(a) if p in adj_cells(b) and p in g.me.territory]
                    if len(c) != 0:
                        cut_point = take_first(c)
                        cut_move = shortest_path_move(g.me.head, cut_point)
                        moves = [a for a in moves if a in cut_move]
                        if len(moves) != 0:
                            g.decision_path.append(f"partial cut {snake.name} {piece}")
                            return moves

    def preliminary_cut_kill_situation(killer: Snake, target: Snake):

        #target is too short - cut kill is not reliable
        if target.length < 7:
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
                    if len(cut_set) == 0: break
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
        oset = sorted(list(set(oset)))

        if len(oset) == 0:
            g.decision_path.append("cut case collision 2")
            return False

        #no tails
        if any([snake.tail in oset for snake in g.snakes]):
            return False

        #trimmed
        #oset = trim_aset(oset, target.head, target.head)
        #don't trim
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

        #if target oset is bordered by more than killer and target body then no case
        if len(g.snakes) > 2:
            oset_border = [q for p in oset for q in adj_cells(p) if q not in oset]
            oset_border = sorted(list(set(oset_border)))
            others = [snake for snake in g.snakes if snake.name not in [killer.name, target.name]]
            if any([a in snake.body for a in oset_border for snake in others]):
                return False

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

    def multistep_terrritories(step):
        def fn(moves):
            occupied = g.occupied_cells[step]
            snakes = g.snakes
            for snake in snakes:
                layers = path_connected_layers(snake.head, occupied)
                snake.cell_distance2 = {p:i for i,layer in enumerate(layers) for p in layer}
                snake.head_space2 = [p for layer in layers for p in layer if p != snake.head]
            for snake in snakes:
                others = [s for s in snakes if snake.head != s.head]
                snake.territory2 = [p for p in snake.head_space2
                                if all([
                                    snake.cell_distance2[p] < other.cell_distance2.get(p, 999) 
                                    if snake.length < other.length else
                                    snake.cell_distance2[p] <= other.cell_distance2.get(p, 999) 
                                        for other in others])
                                ]
        return fn

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

    def take_random(moves):
        g.decision_path.append("take random")
        return [random.choice(moves)]

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

    g.log["module"] = "decision_flow - github"
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

    if log: 
        #print(g.log)
        print(str(g.log).encode('ascii', 'ignore').decode())

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
    log = {'id': 'df01485a-c992-4a29-bdca-a61c9f464476', 'turn': 261, 'me': {'name': 'mark_snake', 'health': 92, 'length': 17, 'body': [(1, 10), (2, 10), (3, 10), (4, 10), (4, 9), (3, 9), (2, 9), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), (2, 2), (1, 2), (1, 1), (0, 1)], 'id': 'gs_dCDyvvCVhYDBFMHptbHy6JRd'}, 'others': [{'name': 'Geriatric Jagwire', 'health': 98, 'length': 17, 'body': [(7, 8), (7, 9), (7, 10), (6, 10), (6, 9), (5, 9), (5, 8), (4, 8), (3, 8), (3, 7), (3, 6), (4, 6), (5, 6), (5, 5), (5, 4), (6, 4), (6, 3)], 'id': 'gs_KqCh7YpBMFr9hMcmWtHXFQMW'}], 'food': [(7, 0), (6, 8)], 'module': 'decision_flow', 'decision_path': ['1v1'], 'next_coord': (0, 10), 'next_move': 'left', 'time': '0.028s'}
    log = {'id': 'ee292417-b52a-45f3-8bfe-915bae73d17f', 'turn': 93, 'me': {'name': 'mark_snake', 'health': 61, 'length': 6, 'body': [(6, 3), (5, 3), (5, 2), (4, 2), (3, 2), (3, 3)], 'id': 'gs_B3Fp3YXtbMyYwHdb4Whc4YJ4'}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 79, 'length': 10, 'body': [(5, 4), (4, 4), (4, 5), (3, 5), (3, 6), (3, 7), (4, 7), (5, 7), (5, 8), (5, 9)], 'id': 'gs_QyfvTd4kGWbhgj9xFbvPDrvK'}, {'name': 'Copy of snake2_v3_FINAL_final(1)', 'health': 94, 'length': 13, 'body': [(8, 7), (9, 7), (10, 7), (10, 8), (10, 9), (10, 10), (9, 10), (9, 9), (9, 8), (8, 8), (7, 8), (7, 7), (6, 7)], 'id': 'gs_4fJcMTtGyjq4yYh3qSkYDMTY'}, {'name': 'soma-mini v1[standard]', 'health': 92, 'length': 6, 'body': [(10, 1), (10, 0), (9, 0), (8, 0), (8, 1), (8, 2)], 'id': 'gs_p6YQCYvrjCkpG3tTGrgjdpKR'}], 'food': [(7, 4), (0, 9), (10, 6)], 'module': 'decision_flow', 'decision_path': ['1vn', "vulnerable snakes: [('Copy of snake2_v3_FINAL_final(1)', 1, (8, 6))]", 'avoid single collision [(6, 4)]', "vulnerable but I'm short", 'go to open space (4, 2)'], 'next_coord': (6, 2), 'next_move': 'down', 'time': '0.150s'}
    log = {'id': '98ec9e82-2459-41b2-b254-fa695ab3624b', 'turn': 301, 'me': {'name': 'mark_snake', 'health': 98, 'length': 20, 'body': [(0, 7), (0, 8), (0, 9), (1, 9), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (9, 9), (8, 9), (7, 9), (6, 9), (5, 9)], 'id': 'gs_QR86mpbW3hq4fTMctHPkYM8D'}, 'others': [{'name': 'SmartyRat', 'health': 88, 'length': 13, 'body': [(2, 7), (2, 8), (3, 8), (3, 7), (3, 6), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5)], 'id': 'gs_kJh3K4WyHVy4Yyyg3gSBxkxb'}], 'food': [(6, 0), (0, 2), (0, 1), (8, 0), (5, 0), (9, 3), (2, 3), (6, 4), (8, 3), (4, 1), (5, 1), (4, 0), (9, 1), (10, 0)], 'module': 'decision_flow', 'decision_path': ['1v1', 'general suppressed chasing'], 'next_coord': (1, 7), 'next_move': 'right', 'time': '0.012s'}
    log = {'id': '31c90869-ac37-4835-a99e-d5e81ec7ff99', 'turn': 114, 'me': {'name': 'mark_snake', 'health': 95, 'length': 12, 'body': [(5, 1), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (1, 1), (1, 2), (2, 2), (3, 2), (4, 2), (4, 1)], 'id': 'gs_Q9FcBYYfww4BdfFvBDPJHtKP'}, 'others': [{'name': 'SmartyRat', 'health': 66, 'length': 5, 'body': [(5, 7), (4, 7), (4, 8), (5, 8), (6, 8)], 'id': 'gs_M8qrBWPDMXChSFGfFjrKdGXX'}, {'name': 'Game of Chicken', 'health': 83, 'length': 9, 'body': [(8, 6), (8, 7), (8, 8), (7, 8), (7, 9), (7, 10), (8, 10), (9, 10), (9, 9)], 'id': 'gs_KtfvHJ9BRhjTBKrbQJC8WjhH'}, {'name': 'Red Yarn', 'health': 98, 'length': 13, 'body': [(5, 3), (6, 3), (6, 4), (5, 4), (4, 4), (3, 4), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (7, 6), (7, 7)], 'id': 'gs_k96D6qpq4Q33S7PfyprjcvBH'}], 'food': [(3, 1)], 'module': 'decision_flow', 'decision_path': ['1vn', 'avoid single collision [(5, 2)]', 'split choice'], 'next_coord': (4, 1), 'next_move': 'left', 'time': '0.006s'}
    log = {'id': '29db6122-577b-47c2-a425-355227330e54', 'turn': 59, 'me': {'name': 'mark_snake', 'health': 88, 'length': 9, 'body': [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8)], 'id': 'gs_PVqtKwmHyfvKKWqDxXMJSRBf'}, 'others': [{'name': 'SmartyRat', 'health': 41, 'length': 3, 'body': [(4, 9), (4, 10), (3, 10)], 'id': 'gs_CQKBGVb8Pd69qd6Mrw7MJT3V'}, {'name': 'go-st', 'health': 66, 'length': 6, 'body': [(8, 5), (8, 4), (7, 4), (6, 4), (5, 4), (5, 5)], 'id': 'gs_pYCdJBPqdd4g8T7tQrwb9xHB'}, {'name': 'Cutiee', 'health': 91, 'length': 10, 'body': [(0, 3), (0, 4), (0, 5), (1, 5), (1, 4), (1, 3), (2, 3), (2, 2), (2, 1), (2, 0)], 'id': 'gs_K9pcVQwJMryWydJRhBPrVc6F'}], 'food': [(4, 0), (6, 9)], 'module': 'decision_flow', 'decision_path': ['1vn', "vulnerable snakes: [('Cutiee', 1, (0, 2))]", "vulnerable but I'm short", 'partial cut Cutiee ✨ [(1, 0), (2, 1)]'], 'next_coord': (2, 0), 'next_move': 'left', 'time': '0.011s'}
    log = {'id': '58c85cc4-5132-415c-8d24-dcd1e3031413', 'turn': 101, 'me': {'name': 'mark_snake', 'health': 69, 'length': 7, 'body': [(8, 5), (7, 5), (7, 6), (7, 7), (6, 7), (6, 6), (6, 5)], 'id': 'gs_9xfpvRdCgg3KBwM9XTwtdMxG'}, 'others': [{'name': 'Game of Chicken', 'health': 98, 'length': 11, 'body': [(8, 9), (7, 9), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (0, 7)], 'id': 'gs_8hSGQR4Cy96FxdT4J7GPRcfS'}, {'name': 'Cutiee', 'health': 96, 'length': 16, 'body': [(4, 1), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3), (0, 3), (0, 4), (0, 5), (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (5, 5)], 'id': 'gs_jW3P8GmhdSMQvcKBPDJtHSpM'}, {'name': 'Spaceheater', 'health': 47, 'length': 8, 'body': [(7, 4), (7, 3), (7, 2), (8, 2), (8, 1), (9, 1), (9, 2), (10, 2)], 'id': 'gs_gFF9k8wSgFvmkt4myTFQXPhc'}], 'food': [(9, 5), (8, 3)], 'module': 'decision_flow', 'decision_path': ['1vn', 'avoid single collision [(8, 4)]'], 'next_coord': (8, 6), 'next_move': 'up', 'time': '0.039s'}
    log = {'id': '7ec16231-8599-443a-8e4a-d831c5089f71', 'turn': 181, 'me': {'name': 'mark_snake', 'health': 81, 'length': 12, 'body': [(4, 5), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (9, 5), (8, 5), (7, 5), (6, 5), (6, 4)], 'id': 'gs_KMSjQTvg6wM9V4hrTpRBgVRW'}, 'others': [{'name': 'go-st', 'health': 62, 'length': 12, 'body': [(6, 1), (6, 2), (7, 2), (7, 3), (7, 4), (8, 4), (8, 3), (9, 3), (10, 3), (10, 2), (10, 1), (9, 1)], 'id': 'gs_MBmvbP7BW4VSCFqHCddTQhbF'}, {'name': 'ich heisse marvin', 'health': 99, 'length': 13, 'body': [(2, 7), (2, 8), (3, 8), (4, 8), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (8, 8), (8, 7), (7, 7), (6, 7)], 'id': 'gs_9GDxFvBMvwwCTJWbxjB8jJQd'}, {'name': '@~~~~@', 'health': 92, 'length': 16, 'body': [(5, 4), (5, 3), (4, 3), (3, 3), (3, 2), (3, 1), (2, 1), (2, 0), (1, 0), (1, 1), (1, 2), (2, 2), (2, 3), (2, 4), (3, 4), (3, 5)], 'id': 'gs_KVwRDtMf7FpY4R9f9mHjfPdQ'}], 'food': [(0, 7), (1, 5)], 'module': 'decision_flow', 'decision_path': ['1vn', 'avoid two step collision'], 'next_coord': (4, 4), 'next_move': 'down', 'time': '0.011s'}
    log = {'id': 'd40f57cc-4f44-40bb-80a0-a1ec543b39d9', 'turn': 108, 'me': {'name': 'mark_snake', 'health': 67, 'length': 10, 'body': [(1, 5), (1, 4), (1, 3), (1, 2), (2, 2), (2, 1), (3, 1), (3, 2), (3, 3), (3, 4)], 'id': 'gs_Qbtt4c9wvvMDCVKcMT6CfQ94'}, 'others': [{'name': 'Lancer', 'health': 98, 'length': 13, 'body': [(6, 2), (6, 3), (7, 3), (7, 4), (7, 5), (8, 5), (9, 5), (10, 5), (10, 4), (10, 3), (10, 2), (10, 1), (9, 1)], 'id': 'gs_KfbHjv9gSmTRMHJp4tT4rRCR'}, {'name': 'go-st', 'health': 86, 'length': 11, 'body': [(4, 6), (5, 6), (6, 6), (6, 7), (7, 7), (8, 7), (8, 8), (8, 9), (7, 9), (6, 9), (5, 9)], 'id': 'gs_8QgFTWhDTSSfctGbwyYKwDvb'}, {'name': 'soma-mini v1[standard]', 'health': 83, 'length': 8, 'body': [(4, 4), (5, 4), (5, 3), (5, 2), (5, 1), (5, 0), (4, 0), (4, 1)], 'id': 'gs_qxrybVrGYtrGHm3VfyXXDwc6'}], 'food': [(3, 5), (10, 6)], 'module': 'decision_flow - github', 'decision_path': ['1vn'], 'next_coord': (2, 5), 'next_move': 'right', 'time': '0.041s'}
    log = {'id': 'c30f7bab-0842-4b0c-b7dc-5f3cab6c9549', 'turn': 101, 'me': {'name': 'mark_snake', 'health': 90, 'length': 8, 'body': [(3, 6), (3, 7), (2, 7), (2, 8), (3, 8), (4, 8), (5, 8), (5, 7)], 'id': 'gs_RXybRyPjC3rC9XWQYqvbxHBB'}, 'others': [{'name': 'Wim HU', 'health': 92, 'length': 10, 'body': [(5, 6), (6, 6), (6, 7), (6, 8), (7, 8), (7, 7), (7, 6), (7, 5), (7, 4), (8, 4)], 'id': 'gs_xj9kk6JB6hKhpmxMhYDPGVX8'}, {'name': 'Lancer', 'health': 86, 'length': 11, 'body': [(1, 10), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (7, 10), (6, 10), (5, 10)], 'id': 'gs_4Vg49FvSptwG7BYS6494HJCG'}, {'name': 'Cutiee', 'health': 76, 'length': 13, 'body': [(0, 5), (1, 5), (2, 5), (3, 5), (3, 4), (3, 3), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (7, 3), (6, 3)], 'id': 'gs_yRRjWQWrwW4Qq6GPcyDBj6SW'}], 'food': [(2, 1)], 'module': 'decision_flow - github', 'decision_path': ['1vn'], 'next_coord': (4, 6), 'next_move': 'right', 'time': '0.001s'}
    log = {'id': 'b4043864-5a79-4cc2-968c-c4bef3fee2a2', 'turn': 99, 'me': {'name': 'mark_snake', 'health': 100, 'length': 8, 'body': [(8, 9), (7, 9), (6, 9), (5, 9), (4, 9), (4, 8), (4, 7), (4, 7)], 'id': 'gs_9pXffyjrCPMSrc7V3chDRMBC'}, 'others': [{'name': 'Kakemonsteret-v2', 'health': 86, 'length': 10, 'body': [(8, 1), (8, 2), (9, 2), (9, 1), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4)], 'id': 'gs_FjxMHBy3cgFDG4XmQrpxSjvP'}, {'name': 'snakey_wakey', 'health': 93, 'length': 13, 'body': [(9, 8), (9, 7), (9, 6), (9, 5), (9, 4), (9, 3), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (7, 7), (6, 7)], 'id': 'gs_36dhvhYr9YPDVVjkjxFKqJVM'}, {'name': 'Wim HU', 'health': 66, 'length': 9, 'body': [(3, 0), (4, 0), (4, 1), (5, 1), (6, 1), (7, 1), (7, 2), (7, 3), (7, 4)], 'id': 'gs_jM7XBvVmpVdwvGmQhSbW8pG8'}], 'food': [(4, 10)], 'module': 'decision_flow - github', 'decision_path': ['1vn', "vulnerable snakes: [('Kakemonsteret-v2', 5, (5, 0))]", 'collision type 2 take risk'], 'next_coord': (8, 8), 'next_move': 'down', 'time': '0.009s'}
    log = {'id': 'b514f9e2-2fce-44e8-b45c-396049a7eba6', 'turn': 125, 'me': {'name': 'mark_snake', 'health': 44, 'length': 7, 'body': [(5, 6), (5, 5), (5, 4), (5, 3), (6, 3), (6, 4), (6, 5)], 'id': 'gs_KcWKrKqrv3mSyHx4WR38KtW7'}, 'others': [{'name': 'FerralSnake-standard', 'health': 96, 'length': 12, 'body': [(6, 7), (6, 8), (6, 9), (6, 10), (5, 10), (5, 9), (4, 9), (3, 9), (3, 8), (3, 7), (4, 7), (4, 8)], 'id': 'gs_pp99xQ7QWm9ypwQ9WF3pWGc7'}, {'name': 'FIA', 'health': 99, 'length': 14, 'body': [(1, 6), (1, 5), (1, 4), (2, 4), (3, 4), (3, 5), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0), (3, 0), (2, 0)], 'id': 'gs_d3S77kc9PDWrVPBCDtyf6kdD'}], 'food': [(0, 0), (2, 10), (0, 7), (0, 6)], 'module': 'decision_flow - github', 'decision_path': ['1vn', 'collision type 2 take risk'], 'next_coord': (6, 6), 'next_move': 'right', 'time': '0.005s'}
    log = {'id': '3e891171-1325-4162-aed2-caeb2fb7e06d', 'turn': 113, 'me': {'name': 'mark_snake', 'health': 82, 'length': 8, 'body': [(3, 8), (4, 8), (5, 8), (5, 7), (4, 7), (4, 6), (5, 6), (6, 6)], 'id': 'gs_4SSD4PGKMkBgwpvwkDQpD87S'}, 'others': [{'name': 'go-st', 'health': 46, 'length': 9, 'body': [(4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (8, 8), (8, 7), (8, 6), (8, 5)], 'id': 'gs_PMBWGHJjhYkDy3Gk96HBwccW'}, {'name': 'ich heisse marvin', 'health': 100, 'length': 11, 'body': [(1, 8), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), (2, 2), (3, 2), (3, 3), (3, 3)], 'id': 'gs_mq8dD4MMDchPTDJMrbMf7F7X'}, {'name': 'Red Yarn', 'health': 92, 'length': 13, 'body': [(4, 5), (4, 4), (4, 3), (5, 3), (5, 2), (5, 1), (5, 0), (6, 0), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4)], 'id': 'gs_cDQJcfhbcwxqyKMwcQKPMXgX'}], 'food': [(0, 6), (1, 2)], 'module': 'decision_flow - github', 'decision_path': ['1vn'], 'next_coord': (3, 9), 'next_move': 'up', 'time': '0.003s'}
    log = {'id': 'fd5a7d2e-a6b8-41c3-8955-9d0d1864305d', 'turn': 291, 'me': {'name': 'mark_snake', 'health': 99, 'length': 24, 'body': [(8, 3), (8, 2), (7, 2), (6, 2), (5, 2), (4, 2), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (2, 10), (2, 9), (2, 8), (2, 7), (2, 6), (2, 5), (1, 5), (0, 5), (0, 4)], 'id': 'gs_YQchRBqkmK8vSwF9wdf3cjXc'}, 'others': [{'name': 'Cutiee ✨', 'health': 95, 'length': 23, 'body': [(7, 6), (7, 5), (8, 5), (9, 5), (9, 6), (9, 7), (9, 8), (8, 8), (7, 8), (7, 9), (8, 9), (8, 10), (7, 10), (6, 10), (5, 10), (5, 9), (4, 9), (4, 8), (4, 7), (4, 6), (4, 5), (4, 4), (5, 4)], 'id': 'gs_67dbkKV6xxDGBhFJfWQhF3Tb'}], 'food': [(0, 6)], 'module': 'decision_flow - github', 'decision_path': ['1v1', 'preliminary cut kill target: Cutiee ✨', 'go cut to (5, 4)'], 'next_coord': (8, 4), 'next_move': 'up', 'time': '0.014s'}
    log = {'id': 'fd5a7d2e-a6b8-41c3-8955-9d0d1864305d', 'turn': 292, 'me': {'name': 'mark_snake', 'health': 98, 'length': 24, 'body': [(8, 4), (8, 3), (8, 2), (7, 2), (6, 2), (5, 2), (4, 2), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (2, 10), (2, 9), (2, 8), (2, 7), (2, 6), (2, 5), (1, 5), (0, 5)], 'id': 'gs_YQchRBqkmK8vSwF9wdf3cjXc'}, 'others': [{'name': 'Cutiee ✨', 'health': 94, 'length': 23, 'body': [(6, 6), (7, 6), (7, 5), (8, 5), (9, 5), (9, 6), (9, 7), (9, 8), (8, 8), (7, 8), (7, 9), (8, 9), (8, 10), (7, 10), (6, 10), (5, 10), (5, 9), (4, 9), (4, 8), (4, 7), (4, 6), (4, 5), (4, 4)], 'id': 'gs_67dbkKV6xxDGBhFJfWQhF3Tb'}], 'food': [(0, 6)], 'module': 'decision_flow - github', 'decision_path': ['1v1', '1v1 longer push'], 'next_coord': (7, 4), 'next_move': 'left', 'time': '0.013s'}
    log = {'id': 'a3a78d3f-bf5a-47c6-a4ae-986fb159fe54', 'turn': 35, 'me': {'name': 'mark_snake', 'health': 69, 'length': 4, 'body': [(8, 9), (8, 8), (8, 7), (8, 6)], 'id': 'gs_qQwxYTyxkCRbgbphFcpfY7TY'}, 'others': [{'name': 'Frank The Tank', 'health': 73, 'length': 5, 'body': [(4, 9), (3, 9), (3, 8), (4, 8), (5, 8)], 'id': 'gs_MKD93HC9w6hvkS3jR39rbWvY'}, {'name': 'ich heisse marvin', 'health': 84, 'length': 7, 'body': [(1, 6), (2, 6), (3, 6), (3, 5), (3, 4), (3, 3), (2, 3)], 'id': 'gs_fGymXcF4ySXDrx6RcH39JfkH'}, {'name': 'mark_snake_test GREEN', 'health': 67, 'length': 4, 'body': [(6, 3), (6, 2), (7, 2), (8, 2)], 'id': 'gs_hkQ3BF7fkSmTpvxpt6QcpqTS'}], 'food': [(0, 10), (4, 10), (8, 10)], 'module': 'decision_flow - github', 'decision_path': ['1vn', 'killer near prefer away border', 'split2 choose my tail', 'split2 choose my tail'], 'next_coord': (9, 9), 'next_move': 'right', 'time': '0.093s'}





    game_state = init_from_log(log)
    self_name = "mark_snake_test GREEN"
    #game_state = init_from_db_log(id, turn, self_name)
    #game_state = init_from_game_engine_log(log, "mark_snake_test GREEN")
    main(game_state, log=True, log_db=False)
