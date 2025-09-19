import time

class Snake:
    def __init__(self, name, body, health):
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
        return {k: self.__dict__[k] for k in ["name", "health", "length", "body", ]}
    def copy(self):
        snake = Snake(self.name, [c for c in self.body], self.health)
        snake.allowed_moves = [a for a in self.allowed_moves]
        snake.territory = [a for a in self.territory]
        snake.head_space = [a for a in self.head_space]

class GameTurn:
    def __init__(self):
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

def main(game_state, log=True):

    ######################################################
    # "global" variable
    ######################################################

    g = GameTurn()

    ######################################################

    def ________DECISION_LOGIC________():
        return

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

        moves = (seq([
            (some_calculations),
            (avoid_single_collision_dead),
            (kill_oppotunities),
            (avoid_danger),
            (reward),
            (other_considerations),

            #seq can return None,
            #the main decision seq must return something
            id,
        ]))(g.me.allowed_moves)

        g.next_coord = take_first(moves)

    def ____TERRITORIES____():
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

    def ____KILL_OPPOTUNITIES____():
        return

    def kill_oppotunities(moves):
        return cases([
            (cond(immediate_kill_oppotunity())(prefer(immediate_kill_move))),
            collision_cut_oppotunity,
            (cond(suppressed_chasing_kill_oppotunity())(prefer_suppressed_chasing_kill_move)),
            general_confront_kill_try,
            cond(border_confront_kill_oppotunity())(prefer(general_confront_kill_move)),
            (cond(trap_kill_oppotunity())(cases([
                prefer(trap_kill_move, "trap kill"),
                prefer(off_border_1, "trap preserve"),
            ]))),
            (make_forming_trap),
            (attack_vulnerables),
            (cut_kill_oppotunity2),
        ])(moves)

    def attack_vulnerables_equal_distance(moves):
        snake = g.target_snake
        snake2: Snake = snake.vulnerable_emerge
        if path_distance_pq(g.me.head, snake2.head) == snake.vulnerable_steps:
            attack_move = shortest_path_move(g.me.head, snake2.head)
            attack_move = [a for a in moves if a in attack_move]
            if len(attack_move) != 0:
                g.decision_path.append("attack vulnerables equal distance")
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
                attack_points = [a for a in attack_points if path_distance_pq(g.me.head, a) == snake.vulnerable_steps+4]
                attack_points = [a for a in attack_points if coming_to(snake2, a)]
                if len(attack_points) != 0:
                    attack_point = take_first(attack_points)
                    attack_move = shortest_path_move(g.me.head, attack_point)
                    attack_move = [a for a in moves if a in attack_move]
                    if len(attack_move) != 0:
                        g.decision_path.append("attack vulnerables")
                        return attack_move

    def attack_vulnerables(moves):
        for snake in g.vulnerables:
            if g.me.length > snake.length:
                g.target_snake = snake
                result = cases([
                    attack_vulnerables_equal_distance,
                    attack_vulnerables_distance_2,
                    attack_vulnerables_path_distance_2,
                    (attack_vulnerables_distance_4),
                ])(moves)
                if result is not None:
                    return result

    def coming_to(snake: Snake, p):
        straight = [a for a in snake.allowed_moves if get_adjacent_dir(snake.head, a) == get_adjacent_dir(snake.neck, snake.head)]
        if len(straight) == 1:
            straight = take_first(straight)
            return distance_pq(straight, p) < distance_pq(snake.head, p)
        return False

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

    def vulnerable_snakes(moves):
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

    def no_cut_danger_a(a, territory=None):
        if territory is None:
            territory = g.me.territory
        occupied = complement(territory)
        if a in occupied:
            return False
        aset = path_connected_set(a, occupied)

        #cut tail is not reliable
        #if any([p in aset or snake.tail in aset for snake in g.snakes for p in adj_cells(snake.tail)]):
        if any([snake.tail in aset for snake in g.snakes]):
            return True
        if any([p in aset for snake in g.snakes if snake.health == 100 for p in adj_cells(snake.tail)]):
            return True
        aset = trim_aset(aset, a)
        return len(aset) >= g.me.length * 1.1

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
        others = [possible_next_state(s, take_first(s.allowed_moves)) for s in g.others if s.head != snake.head]

        for m in collision:
            me2 = possible_next_state(g.me, m)
            hypothetic_development_territories([me2]+[snake2]+others)
            if preliminary_cut_kill_situation2(me2, snake2):
                if no_cut_danger_a(m):
                    g.decision_path.append(f"try collision cut kill {m}")
                    return [m]

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

    def preliminary_cut_kill_situation2(killer: Snake, target: Snake):

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

    def cut_kill_target2():
        #get the first target
        for snake in g.others:
            if preliminary_cut_kill_situation2(g.me, snake):
                g.target_snake = snake
                return True
        return False

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

    def cut_kill_oppotunity2(moves):
        if not cut_kill_target2():
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
            cells = [(x,y) for x in irange(x0, x1) for y in irange(y0, y1)]

            #select the rectangle in the correct direction
            if any([p in cells for p in target.territory]): continue

            occupied = list(set(g.occupied_cells[0]+cells))
            oset = path_connected_set(target.head, occupied)
            oset = [p for p in oset if p != target.head]
            if any([snake.tail in oset for snake in g.snakes]):
                continue
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

    def trap_kill_move(a):
        if on_border(a):
            if not is_adjacent(a, g.target_snake.head):
                return True
            if g.me.length > g.target_snake.length:
                return True
        return False

    def trap_kill_oppotunity():
        for snake in g.others:
            if trap_kill_situation(g.me, snake):
                g.target_snake = snake
                return True
        return False

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

    def general_confront_kill_try(moves):
        if general_confront_kill_oppotunity():
            for a in moves:
                if general_confront_kill_move(a):
                    if len([snake for snake in g.others if is_adjacent(a, snake.head) and snake.length > g.me.length]) == 0:
                        return [a]

    def general_confront_kill_move(a):
        if len(g.target_snake.allowed_moves) != 2:
            return False
        b = [p for p in g.target_snake.allowed_moves if get_adjacent_dir(g.target_snake.head, p) != get_adjacent_dir(g.target_snake.neck, g.target_snake.head)]
        b = take_first(b)
        return distance_vector_abs(a, b) == (1,1)

    def general_confront_kill_oppotunity():
        for snake in g.others:
            if general_confront_kill_situation(g.me, snake):
                g.target_snake = snake
                return True
        return False

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

    def border_confront_kill_oppotunity():
        for snake in g.others:
            if border_confront_kill_situation(g.me, snake):
                g.target_snake = snake
                return True
        return False

    def border_confront_kill_situation(killer: Snake, target: Snake):
        return all([
            distance_pq(killer.head, target.head) == 4,
            killer.length > target.length,
            on_border(target.head),
            not on_border(killer.head),
            not off_border_1(killer.head),
            distance_vector_abs(killer.head, target.head) in [(2,2), (1,3), (3,1)],
            path_distance_pq(killer.head, target.head) == 4,
            all([distance_pq(a, killer.head) == 3 for a in target.allowed_moves]),
            any([distance_vector_abs(a, target.head) in [(1,2), (2,1)] for a in killer.allowed_moves]),
        ])

    def prefer_suppressed_chasing_kill_move(moves):
        for a in moves:
            if suppressed_chasing_kill_move(a):
                target = g.target_snake
                aset = path_connected_set(a, g.occupied_cells[0])
                if len(aset) > len(target.territory):
                    g.decision_path.append(f"chasing kill '{target.name}'")
                    return [a]

    def suppressed_chasing_kill_move(a):
        return a in g.me.allowed_moves and a in g.target_snake.allowed_moves

    def suppressed_chasing_kill_oppotunity():
        for snake in g.others:
            if suppressed_chasing_kill_situation(g.me, snake):
                g.target_snake = snake
                return True
        return False

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
                                        return True
        return False

    def immediate_kill_move(a):
        if is_adjacent(a, g.target_snake.head):
            g.decision_path.append("immediate kill")
            return True
        return False

    def immediate_kill_oppotunity():
        for snake in g.others:
            if immediate_kill_situation(g.me, snake):
                g.target_snake = snake
                return True
        return False

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

    def forming_trap_situation(killer: Snake, target: Snake):
        return all([
            distance_pq(killer.head, target.head) == 2,
            killer.length <= target.length,
            on_border(target.head),
            distance_vector_abs(killer.head, target.head) == (1,1),
            all([is_adjacent(a, killer.head) for a in target.allowed_moves]),
            len([a for a in killer.allowed_moves if off_border_1(a) and distance_pq(a, target.head) == 3]) == 1,
        ])

    def make_forming_trap(moves):
        for snake in g.others:
            if distance_vector_abs(g.me.head, snake.head) == (2,2):
                for a in g.me.allowed_moves:
                    for b in snake.allowed_moves:
                        me2 = possible_next_state(g.me, a)
                        snake2 = possible_next_state(snake, b)
                        if forming_trap_situation(me2, snake2):
                            return [a]

    def ____AVOID_DANGER____():
        return

    def message_step(message):
        def fn(moves):
            if isinstance(message, str):
                print(message)
                return
            #assume a function
            print(message(moves))
        return fn

    def avoid_danger(moves):
        return seq([
            (avoid_next_step_no_move),
            (wayout),
            (avoid_suppressed_single_collision),
            (prefer_not(entering_danger(immediate_kill_situation))),
            (prefer_not(entering_danger(suppressed_chasing_kill_situation))),
            (prefer_not(entering_danger(border_confront_kill_situation))),
            (prefer_not(entering_danger(trap_kill_situation))),
            (avoid_single_collision),
            #(prefer_not(entering_danger(confine_kill_situation))),
            (cond(g.me.length > 8)(avoid_next_step_confinement)),
            (cond(g.me.length >= 10)(split_choice)),
            (cond(g.me.length <= 10)(multi_step_collision)),
        ])(moves)

    def avoid_single_collision_dead(moves):
        snakes = [snake for snake in g.others if snake.length >= g.me.length and distance_pq(snake.head, g.me.head) == 2]
        if len(snakes) != 0:
            dead_moves = [a for a in moves if any([is_adjacent(a, snake.head) and len(snake.allowed_moves) == 1 for snake in snakes])]
            moves = [a for a in moves if a not in dead_moves]
            if len(moves) != 0:
                return moves

    def avoid_next_step_no_move(moves):
        no_move = [a for a in moves if len([p for p in adj_cells(a) if p not in g.occupied_cells[1]]) == 0]
        if len(no_move) != 0:
            g.decision_path.append(f"avoid next step no move {no_move}")
            moves = [a for a in moves if a not in no_move]
            if len(moves) != 0:
                return moves

    def avoid_next_step_confinement(moves):
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
                if len(cut_set) > 2: continue
                if len(cut_set) == 2:
                    if not cut_set_connected(cut_set): continue
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

    def possible_next_state(snake, a):
        ns = Snake(
            snake.name, [a]+snake.body[:-1], snake.health-1
        ) if a not in g.food else Snake(
            snake.name, [a]+snake.body[:-1]+[snake.body[-2]], 100
        )
        ns.allowed_moves = [a for a in adj_cells(ns.head) if a not in g.occupied_cells[1]]
        return ns

    def suppressed_single_collision(killer: Snake, target: Snake):
        if len(target.allowed_moves) == 2:
            if killer.length > target.length:
                if len([a for a in target.allowed_moves if a in killer.allowed_moves]) == 1:
                    a,b = target.allowed_moves
                    if path_distance_pq(a, b) == 2:
                        return True
        return False

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

    def single_collision(killer: Snake, target: Snake):
        return all([
            len(target.allowed_moves) == 3,
            killer.length > target.length,
            len([a for a in target.allowed_moves if a in killer.allowed_moves]) == 1,
        ])

    def avoid_single_collision(moves):
        avoid = [a 
                 for snake in g.others if single_collision(snake, g.me) 
                 for a in moves if is_adjacent(a, snake.head) 
                 ]
        if len(avoid) != 0:
            g.decision_path.append(f"avoid single collision {avoid}")
            moves = [a for a in moves if a not in avoid]
            if len(moves) != 0:
                return moves

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

    def at_corner(p):
        distv = distance_to_border(p)
        return sum(distv) <= 2

    def ____SPLIT_CHOICES____():
        return

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
        
        g.decision_path.append("try split choice")
        #ngroup == 2
        return cases([
            (check_confinement),
            (check_wayout),
            (collision_take_risk),
            seq([
                avoid_preliminary_trap,
                avoid_static_confinement,
                prefer_diagonal_cut_set,
                more_space,
            ]),
        ])(moves)

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

    def check_wayout(moves):
        ok_set = []

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

        for a in moves:
            if has_wayout(a):
                ok_set.append(a)
        if len(ok_set) != 0:
            return ok_set
        g.decision_path.append("split fail wayout check")

    def check_confinement(moves):
        ok_set = [a for a in moves if no_cut_danger_a(a)]
        if len(ok_set) != 0:
            return ok_set
        g.decision_path.append("split fail confinement check")

    def more_space(moves):
        def move_space(a):
            if a not in g.me.territory:
                return []
            return path_connected_set(a, complement(g.me.territory))
        return prefer_by_score(lambda a: len(move_space(a)))(moves)
 
    def ____WAYOUT____():
        pass

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
        if len(cut_set) != 0:
            future_tail = g.me.body[-1-len(cut_set)]
            if any([p in g.me.territory for p in adj_cells(future_tail)]):
                return

        #wayout spacious
        if len(g.me.territory) >= g.me.length * 1.1:
            return

        g.decision_path.append("try wayout")

        return cases([
            (wayout_myself),
            wayout_on_others,
        ])(moves)

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

        if len(aset) <= 5:
            if len(aset) >= wayout_length:
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

    def wayout_myself(moves):
        wayout_point = has_wayout_on_myself(g.me.territory)
        if wayout_point is not None:
            return wayout_to(wayout_point, moves)

    def wayout_on_others(moves):
        wayout_point = has_wayout_on_others(g.me.territory)
        if wayout_point is not None:
            return wayout_to(wayout_point, moves)

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
    
    def ____GET_FOOD____():
        pass

    def reward(moves):
        return cases([
            cond(len(g.others) == 1 and g.me.length > g.other.length)(push),
            cond(g.me.length >= 35)(chase_tail),
            (get_food),
            #chase_tail,
        ])(moves)

    def push(moves):
        def push_2(moves):
            if distance_pq(g.me.head, g.other.head) == 2:
                if distance_vector_abs(g.me.head, g.other.head) != (1,1):
                    collision = [a for a in adj_cells(g.me.head) if a in adj_cells(g.other.head)]
                    collision = take_first(collision)
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
                    return cases([
                        coming_push,
                        center_push,
                    ])(moves)
     
        return cases([
            push_2,
            push_4,
        ])(moves)

    def chase_tail(moves):
        return cases([
            chase_my_tail,
            chase_other_tail,
        ])(moves)

    def chase_my_tail(moves):
        return cases([
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
        pass

    def get_food(moves):
        food_near = [f for f in g.food if distance_pq(f, g.me.head) <= 8]
        food_good = [f for f in food_near 
                     if path_connected(f, g.me.head) 
                     and all([path_distance_pq(f, g.me.head) < path_distance_pq(f, snake.head) if snake.length >= g.me.length 
                     else path_distance_pq(f, g.me.head) <= path_distance_pq(f, snake.head)
                              for snake in g.others])]
        if len(food_good) == 0:
            return

        food_better = prefer_by_rank(lambda f: path_distance_pq(f, g.me.head))(food_good)
        food_target = take_first(food_better)

        if g.me.length <= 10:
            food_moves = shortest_path_move(g.me.head, food_target)
            g.decision_path.append(f"get food {food_target}")
            return prefer_yes(lambda a: a in food_moves)(moves)

        if on_border(food_target):
            #if food target is on border, need to access it from certain direction
            if is_adjacent(g.me.head, food_target):
                g.decision_path.append(f"get food {food_target}")
                return [food_target]
            food_and_nabor = [a for a in adj_cells(food_target) if on_border(a)] + [food_target]
            food_and_nabor = [a for a in food_and_nabor if a not in g.occupied_cells[0]]
            food_access = prefer_by_rank(lambda a: path_distance_pq(g.me.head, a))(food_and_nabor)
            food_access = take_first(food_access)
            food_moves = shortest_path_move(g.me.head, food_access)
            g.decision_path.append(f"get food {food_target} via {food_access}")
            return prefer_yes(lambda a: a in food_moves)(moves)

        food_moves = shortest_path_move(g.me.head, food_target)
        g.decision_path.append(f"get food {food_target}")
        return prefer_yes(lambda a: a in food_moves)(moves)

    def ____OTHER_CONSIDERATIONS____():
        pass

    def other_considerations(moves):
        return seq([
            multi_step_collision,
            (cond(g.me.length >= 10)(prefer_less_split)),
            #cond(len(g.others) >= 2)(split_prefer_open_space),
            #cond(g.me.length <= 8)(prefer_more_next_moves),
            cond(g.me.length <= 16)(prefer_away_border),
            cond(g.me.length < 10 and len(g.others) >= 2)(prefer_open_space),
            (prefer_straight),
        ])(moves)

    def prefer_less_split(moves):
        def next_ngroup(a):
            me2 = possible_next_state(g.me, a)
            ngroup = move_connected_group(me2.allowed_moves, g.occupied_cells[0]+[a])
            if ngroup is None:
                return 999
            return ngroup
        return prefer_by_rank(next_ngroup)(moves)

    def prefer_away_border(moves):
        return prefer_by_score(lambda a: min(*distance_to_border(a), 2))(moves)

    def split_prefer_open_space(moves):
        ngroup = move_connected_group(moves)
        if ngroup > 1:
            return prefer_open_space(moves)

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

    def cases(fs):
        def fn(moves):
            if len(moves) <= 1:
                return moves
            for f in fs:
                result = f(moves)
                if result is not None:
                    return result
        return fn

    def timeit(fname):
        def fn(f):
            def action(moves):
                start_time = time.time()
                result = f(moves)
                end_time = time.time()
                print(f"{fname}: {end_time-start_time:.3f}s")
                return result
            return action
        return fn

    def seq2(fs):
        def fn(moves):
            for f in fs:
                if len(moves) <= 1:
                    return moves
                result = f(moves)
                if result is not None:
                    moves = result
            return moves
        return fn

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

    def cond(*pred):
        def fn(f):
            def fc(moves):
                if all(pred):
                    return f(moves)
            return fc
        return fn

    def take_first(moves):
        try:
            assert(len(moves) != 0)
        except AssertionError:
            turn = g.state["turn"]
            id = g.state["game"]["id"]
            print(f"id: {id}, TURN: {turn}")
            raise AssertionError
        return moves[0]

    def score_more_next_move(p):
        moves = [a for a in adj_cells(p) if a not in g.occupied_cells[1]]
        return len(moves)

    def score_more_room(p):
        cells = path_connected_set(p)
        return len(cells)

    def prefer_by_rank(rank):
        def fn(moves):
            moves = [(a, rank(a)) for a in moves]
            moves = first_group(moves)
            return moves
        return fn

    def prefer_yes(check):
        return prefer_by_rank(lambda a: 0 if check(a) else 1)

    def prefer_no(check):
        return prefer_yes(lambda a: not check(a))

    def prefer_in(aset):
        return prefer_yes(lambda a: a in aset)
    
    def prefer_not_in(aset):
        return prefer_no(lambda a: a in aset)

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

    def choose(check):
        def fn(moves):
            yes = [a for a in moves if check(a)]
            no = [a for a in moves if a not in yes]
            if len(yes) != 0 and len(no) != 0:
                return yes
        return fn

    def avoid(check, message=None):
        def fn(moves):
            yes = [a for a in moves if check(a)]
            no = [a for a in moves if a not in yes]
            if len(yes) != 0 and len(no) != 0:
                return no
            if len(no) == 0 and message is not None:
                g.decision_path.append(f"avoid {message} fail")
        return fn

    def prefer_by_score(score):
        def fn(moves):
            moves = [(a, score(a)) for a in moves]
            moves = first_group(moves, reverse=True)
            return moves
        return fn

    def prefer_less_next_moves(moves):
        def n_next_moves(a):
            next_moves = [p for p in adj_cells(a) if p not in g.occupied_cells[1]]
            return len(next_moves)
        return prefer_by_rank(n_next_moves)(moves)

    def prefer_more_next_moves(moves):
        def n_next_moves(a):
            next_moves = [p for p in adj_cells(a) if p not in g.occupied_cells[1]]
            return len(next_moves)
        return prefer_by_score(n_next_moves)(moves)

    def prefer_straight(moves):
        return prefer_yes(is_straight)(moves)

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

    def ________GAME_ENTRY________():
        pass

    def init_game(game_state):
        g.state = game_state
        g.turn = game_state["turn"]

        g.snakes = [
            Snake(
                name = snake["name"],
                body = get_coord(snake["body"]),
                health = snake["health"],
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
            #"mark_snake",
            "mark_snake_test RED",
            "mark_snake_test BLUE",
            "mark_snake_test GREEN",
            "mark_snake_test YELLOW",
        ]:
            return True
        return False

    

    ######################################################
    # main process
    ######################################################

    init_game(game_state)
    if not entry_condition(): return False

    g.log["module"] = "simp"
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
            "name": snake["name"],
            "health": snake["health"],
            "body": reverse_coord(snake["body"]),
        } for snake in log["others"] ]
    me = [ {
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
    log = {'id': '4c5fa55e-5147-425c-8a96-72e441f13321', 'turn': 128, 'me': {'name': 'mark_snake', 'health': 66, 'length': 10, 'body': [(8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (4, 9)]}, 'others': [{'name': 'conesnake', 'health': 89, 'length': 6, 'body': [(10, 0), (9, 0), (9, 1), (9, 2), (10, 2), (10, 1)]}, {'name': 'Natterlie', 'health': 91, 'length': 13, 'body': [(6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (2, 3), (3, 3), (3, 4), (2, 4), (1, 4), (1, 5), (1, 6), (1, 7)]}, {'name': 'Red Yarn', 'health': 72, 'length': 12, 'body': [(8, 2), (8, 1), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (6, 7), (5, 7), (4, 7)]}], 'food': [(6, 1)], 'module': 'simp', 'decision_path': ['1vn', "vulnerable snakes: [('conesnake', 2, (10, 2)), ('Red Yarn', 2, (9, 3))]", 'attack vulnerables distance 2'], 'next_coord': (8, 3), 'next_move': 'down', 'time': '0.006s'}
    log = {'id': 'e1704880-1bfc-4e55-9b7d-cbccaefb4d96', 'turn': 86, 'me': {'name': 'mark_snake', 'health': 99, 'length': 13, 'body': [(10, 4), (10, 3), (9, 3), (8, 3), (7, 3), (6, 3), (6, 4), (6, 5), (5, 5), (4, 5), (3, 5), (3, 6), (3, 7)]}, 'others': [{'name': 'slieks', 'health': 88, 'length': 8, 'body': [(6, 6), (5, 6), (5, 7), (6, 7), (7, 7), (8, 7), (8, 6), (9, 6)]}, {'name': 'ich heisse marvin', 'health': 69, 'length': 8, 'body': [(3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (7, 0), (6, 0), (5, 0)]}, {'name': 'Spaceheater', 'health': 58, 'length': 6, 'body': [(2, 8), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3)]}], 'food': [(8, 1), (4, 2), (4, 6)], 'module': 'simp', 'decision_path': ['1vn', "vulnerable snakes: [('slieks', 1, (7, 6))]"], 'next_coord': (9, 4), 'next_move': 'left', 'time': '0.021s'}
    log = {'id': 'e1704880-1bfc-4e55-9b7d-cbccaefb4d96', 'turn': 87, 'me': {'name': 'mark_snake', 'health': 98, 'length': 13, 'body': [(9, 4), (10, 4), (10, 3), (9, 3), (8, 3), (7, 3), (6, 3), (6, 4), (6, 5), (5, 5), (4, 5), (3, 5), (3, 6)]}, 'others': [{'name': 'slieks', 'health': 87, 'length': 8, 'body': [(7, 6), (6, 6), (5, 6), (5, 7), (6, 7), (7, 7), (8, 7), (8, 6)]}, {'name': 'ich heisse marvin', 'health': 68, 'length': 8, 'body': [(3, 2), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (7, 0), (6, 0)]}, {'name': 'Spaceheater', 'health': 57, 'length': 6, 'body': [(3, 8), (2, 8), (2, 7), (2, 6), (2, 5), (2, 4)]}], 'food': [(8, 1), (4, 2), (4, 6)], 'module': 'simp', 'decision_path': ['1vn'], 'next_coord': (8, 4), 'next_move': 'left', 'time': '0.005s'}
    log = {'id': 'faaa4285-f09f-4179-8c1c-6367e212405b', 'turn': 120, 'nalive': 2, 'snakes': [{'name': 'mark_snake_test RED', 'health': 99, 'length': 19, 'alive': True, 'delay': 8, 'body': [(3, 5), (3, 4), (4, 4), (4, 3), (4, 2), (4, 1), (5, 1), (6, 1), (7, 1), (7, 2), (7, 3), (8, 3), (9, 3), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8)]}, {'name': 'mark_snake_test GREEN', 'health': 89, 'length': 16, 'alive': True, 'delay': 26, 'body': [(4, 6), (3, 6), (3, 7), (3, 8), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (7, 8), (6, 8), (6, 7), (7, 7), (7, 6), (7, 5), (6, 5)]}], 'food': [(8, 1)]}
    log = {'id': 'b7c66d53-c7bb-4593-8d13-7c4ca3310b69', 'turn': 372, 'me': {'name': 'mark_snake', 'health': 86, 'length': 38, 'body': [(3, 5), (3, 4), (2, 4), (1, 4), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, 10), (2, 10), (2, 9), (1, 9), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (5, 9), (4, 9), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (9, 9), (9, 8), (9, 7), (9, 6), (9, 5), (8, 5), (8, 6), (8, 7), (8, 8), (7, 8)]}, 'others': [{'name': 'conesnake', 'health': 92, 'length': 14, 'body': [(5, 5), (5, 4), (5, 3), (5, 2), (5, 1), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (10, 1), (10, 2), (10, 3)]}], 'food': [(4, 0), (6, 3), (1, 2), (1, 5), (1, 7)], 'module': 'simp', 'decision_path': ['1v1', 'try wayout'], 'next_coord': (2, 5), 'next_move': 'left', 'time': '0.006s'}
    log = {'id': '9283b907-2cee-4fee-99ff-d3693d9ce0bc', 'turn': 312, 'me': {'name': 'mark_snake', 'health': 86, 'length': 28, 'body': [(4, 10), (5, 10), (6, 10), (6, 9), (7, 9), (8, 9), (9, 9), (9, 8), (10, 8), (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (10, 2), (9, 2), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (7, 7), (6, 7), (5, 7), (4, 7), (3, 7), (2, 7)]}, 'others': [{'name': 'Spaceheater', 'health': 80, 'length': 16, 'body': [(2, 6), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (0, 10), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5)]}], 'food': [(6, 0), (9, 10), (1, 4)], 'module': 'simp', 'decision_path': ['1v1', 'coming push'], 'next_coord': (3, 10), 'next_move': 'left', 'time': '0.011s'}
    log = {'id': '1708325b-2260-4862-a088-2021c35fc97e', 'turn': 176, 'me': {'name': 'mark_snake', 'health': 98, 'length': 16, 'body': [(8, 6), (9, 6), (9, 7), (9, 8), (9, 9), (8, 9), (7, 9), (6, 9), (6, 8), (7, 8), (8, 8), (8, 7), (7, 7), (6, 7), (5, 7), (4, 7)]}, 'others': [{'name': '@~~~~@', 'health': 89, 'length': 18, 'body': [(6, 4), (7, 4), (7, 3), (6, 3), (6, 2), (5, 2), (5, 3), (4, 3), (3, 3), (3, 2), (2, 2), (1, 2), (1, 3), (2, 3), (2, 4), (2, 5), (3, 5), (3, 4)]}], 'food': [(5, 0), (2, 6)], 'module': 'simp', 'decision_path': ['1v1'], 'next_coord': (7, 6), 'next_move': 'left', 'time': '0.013s'}
    log = {'id': 'ca149b53-e520-4465-b816-b23781ae3f6a', 'turn': 192, 'me': {'name': 'mark_snake', 'health': 91, 'length': 16, 'body': [(8, 4), (8, 5), (8, 6), (8, 7), (7, 7), (6, 7), (5, 7), (5, 8), (6, 8), (7, 8), (8, 8), (8, 9), (8, 10), (7, 10), (6, 10), (5, 10)]}, 'others': [{'name': 'slieks', 'health': 87, 'length': 11, 'body': [(9, 1), (8, 1), (7, 1), (6, 1), (6, 0), (5, 0), (5, 1), (5, 2), (6, 2), (7, 2), (8, 2)]}, {'name': '@~~~~@', 'health': 93, 'length': 15, 'body': [(2, 6), (2, 7), (3, 7), (4, 7), (4, 6), (3, 6), (3, 5), (3, 4), (4, 4), (5, 4), (6, 4), (6, 3), (5, 3), (4, 3), (4, 2)]}], 'food': [(10, 10), (0, 3)], 'module': 'simp', 'decision_path': ['1vn', 'preliminary cut kill target: slieks', 'get food (10, 10)'], 'next_coord': (9, 4), 'next_move': 'right', 'time': '0.029s'}
    log = {'id': '93c8893b-34b7-41da-bbe3-256ebef5ed93', 'turn': 245, 'me': {'name': 'mark_snake', 'health': 100, 'length': 25, 'body': [(3, 2), (4, 2), (4, 3), (5, 3), (6, 3), (7, 3), (7, 2), (6, 2), (6, 1), (7, 1), (8, 1), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (8, 6), (7, 6), (6, 6), (5, 6), (5, 7), (6, 7), (6, 8), (6, 8)]}, 'others': [{'name': 'Prüzze v2', 'health': 85, 'length': 21, 'body': [(6, 9), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (2, 9), (1, 9), (0, 9), (0, 8), (1, 8), (2, 8), (3, 8), (3, 9), (4, 9), (5, 9), (5, 8), (4, 8), (4, 7), (3, 7), (3, 6)]}], 'food': [(10, 4)], 'module': 'simp', 'decision_path': ['1v1', "vulnerable snakes: [('Prüzze v2', 1, (7, 9))]", 'preliminary cut kill target: Prüzze v2', 'go cut to (5, 0)'], 'next_coord': (3, 1), 'next_move': 'down', 'time': '0.027s'}
    log = {'id': '6326f66f-6a8b-4624-b947-8540bbe9ba68', 'turn': 245, 'me': {'name': 'mark_snake', 'health': 97, 'length': 21, 'body': [(7, 2), (7, 3), (7, 4), (8, 4), (8, 3), (9, 3), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (9, 7), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8), (3, 9), (3, 10)]}, 'others': [{'name': 'Prüzze v2', 'health': 91, 'length': 18, 'body': [(2, 7), (2, 6), (2, 5), (1, 5), (1, 4), (2, 4), (2, 3), (2, 2), (2, 1), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (4, 6), (4, 5), (4, 4)]}], 'food': [(1, 1), (10, 1)], 'module': 'simp', 'decision_path': ['1v1', 'get food (10, 1)'], 'next_coord': (7, 1), 'next_move': 'down', 'time': '0.029s'}
    log = {'id': '3fc9ea8b-d67d-441f-89c3-fca6edb01cef', 'turn': 256, 'me': {'name': 'mark_snake', 'health': 57, 'length': 24, 'body': [(1, 1), (2, 1), (3, 1), (4, 1), (4, 2), (3, 2), (2, 2), (1, 2), (0, 2), (0, 3), (0, 4), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (4, 4), (5, 4), (5, 5), (5, 6), (5, 7), (6, 7), (6, 8), (5, 8)]}, 'others': [{'name': 'Prüzze v2', 'health': 75, 'length': 17, 'body': [(7, 5), (7, 4), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0), (7, 0), (7, 1), (8, 1), (9, 1), (9, 2), (8, 2), (7, 2), (7, 3), (8, 3), (8, 4)]}], 'food': [(10, 0), (10, 8), (9, 0), (10, 9)], 'module': 'simp', 'decision_path': ['1v1', 'try wayout'], 'next_coord': (0, 1), 'next_move': 'left', 'time': '0.003s'}
    log = {'id': '3fc9ea8b-d67d-441f-89c3-fca6edb01cef', 'turn': 255, 'me': {'name': 'mark_snake', 'health': 58, 'length': 24, 'body': [(2, 1), (3, 1), (4, 1), (4, 2), (3, 2), (2, 2), (1, 2), (0, 2), (0, 3), (0, 4), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (4, 4), (5, 4), (5, 5), (5, 6), (5, 7), (6, 7), (6, 8), (5, 8), (4, 8)]}, 'others': [{'name': 'Prüzze v2', 'health': 76, 'length': 17, 'body': [(7, 4), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0), (7, 0), (7, 1), (8, 1), (9, 1), (9, 2), (8, 2), (7, 2), (7, 3), (8, 3), (8, 4), (8, 5)]}], 'food': [(10, 0), (10, 8), (9, 0), (10, 9)], 'module': 'simp', 'decision_path': ['1v1', "vulnerable snakes: [('Prüzze v2', 1, (7, 5))]", 'try wayout'], 'next_coord': (1, 1), 'next_move': 'left', 'time': '0.002s'}
    log = {'id': '395aaee6-9c72-4921-b6bc-4ad8e3b5925f', 'turn': 122, 'me': {'name': 'mark_snake', 'health': 94, 'length': 12, 'body': [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, 0), (6, 0), (6, 1), (6, 2), (7, 2), (8, 2), (8, 3)]}, 'others': [{'name': 'Geriatric Jagwire', 'health': 85, 'length': 12, 'body': [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (6, 4), (5, 4), (5, 5), (4, 5), (4, 6), (5, 6)]}], 'food': [(0, 8), (0, 2)], 'module': 'simp', 'decision_path': ['1v1', 'apparently cut is done', 'try wayout'], 'next_coord': (1, 0), 'next_move': 'down', 'time': '0.021s'}
    log = {'id': 'ad5c44ea-805a-441d-8645-ad336340c304', 'turn': 311, 'me': {'name': 'mark_snake', 'health': 83, 'length': 29, 'body': [(1, 4), (1, 3), (1, 2), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 7), (4, 7), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (0, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9)]}, 'others': [{'name': 'Natterlie', 'health': 86, 'length': 24, 'body': [(7, 0), (7, 1), (8, 1), (8, 2), (7, 2), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (5, 6), (4, 6), (3, 6), (3, 5), (4, 5), (4, 4), (4, 3), (5, 3), (5, 2), (4, 2), (4, 1), (3, 1), (2, 1), (1, 1)]}], 'food': [(3, 2)], 'module': 'simp', 'decision_path': ['1v1', 'avoid next step confinement [(1, 5)]'], 'next_coord': (0, 4), 'next_move': 'left', 'time': '0.007s'} 
    log = {'id': 'ad5c44ea-805a-441d-8645-ad336340c304', 'turn': 309, 'me': {'name': 'mark_snake', 'health': 85, 'length': 29, 'body': [(1, 2), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 7), (4, 7), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (0, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (10, 8), (10, 7)]}, 'others': [{'name': 'Natterlie', 'health': 88, 'length': 24, 'body': [(8, 1), (8, 2), (7, 2), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (5, 6), (4, 6), (3, 6), (3, 5), (4, 5), (4, 4), (4, 3), (5, 3), (5, 2), (4, 2), (4, 1), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2)]}], 'food': [(3, 2)], 'module': 'simp', 'decision_path': ['1v1'], 'next_coord': (1, 3), 'next_move': 'up', 'time': '0.006s'}
    log = {'id': 'ad5c44ea-805a-441d-8645-ad336340c304', 'turn': 300, 'me': {'name': 'mark_snake', 'health': 94, 'length': 29, 'body': [(4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (0, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (10, 8), (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (10, 2), (10, 1), (9, 1), (9, 2), (9, 3)]}, 'others': [{'name': 'Natterlie', 'health': 97, 'length': 24, 'body': [(4, 6), (3, 6), (3, 5), (4, 5), (4, 4), (4, 3), (5, 3), (5, 2), (4, 2), (4, 1), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 7), (1, 6), (1, 5), (1, 4)]}], 'food': [(3, 2)], 'module': 'simp', 'decision_path': ['1v1', 'get food (3, 2)'], 'next_coord': (4, 7), 'next_move': 'down', 'time': '0.028s'}



    game_state = init_from_log(log)
    #game_state = init_from_game_engine_log(log, "mark_snake_test GREEN")
    main(game_state)

