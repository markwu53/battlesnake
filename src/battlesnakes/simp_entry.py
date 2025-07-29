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
    def dict(self):
        return {k: self.__dict__[k] for k in ["name", "health", "body", ]}

class DecisionAux:
    def __init__(self):
        self.occupied_cells = None

class Game:
    def __init__(self):
        self.state = None
        self.me = None
        self.others = None
        self.other = None
        self.snakes = None
        self.food = None
        self.next_coord = None
        self.log = {}
        self.decision_path = []
        self.x = DecisionAux()

def main(game_state):

    ######################################################
    # "global" variable
    ######################################################

    g = Game()

    ######################################################

    def ________DECISION_LOGIC________():
        pass

    def decision():
        #estimated 5-step occupied cells
        g.x.occupied_cells = [
            occupied_cells(step)
            for step in [1,2,3,4,5]
        ]
        for snake in g.snakes:
            snake.allowed_moves = [a for a in adj_cells(snake.head) if a not in g.x.occupied_cells[0]]

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

        moves = sequential([
            territories,
            kill_oppotunities,
            #(avoid_danger),
            (single_collision),
            (split_choice),
            killer_near,
            multi_step_collision,
            wayout,
            (get_food),
            other_considerations,
        ])(g.me.allowed_moves)

        g.next_coord = take_first(moves)

    def ____TERRITORIES____():
        pass

    def territories(moves):
        for snake in g.snakes:
            layers = path_connected_layers(snake.head)
            snake.cell_distance = {p:i for i,layer in enumerate(layers) for p in layer}
            snake.head_space = [p for layer in layers for p in layer if p != snake.head]
        for snake in g.snakes:
            others = [s for s in g.snakes if snake.head != s.head]
            snake.territory = [p for p in snake.head_space
                               if all([
                                   snake.cell_distance[p] < other.cell_distance.get(p, 999) 
                                   if snake.length < other.length else
                                   snake.cell_distance[p] <= other.cell_distance.get(p, 999) 
                                       for other in others])
                               ]

    def ____KILL_OPPOTUNITIES____():
        pass

    def kill_oppotunities(moves):
        return cases([
            collision_kill,
            trap_kill,
            contact_kill,
            try_kill_4,
            try_trap_4,
            try_trap_2,
        ])(moves)

    def try_kill_4(moves):
        snakes = [snake for snake in g.others if distance_pq(g.me.head, snake.head) == 4]
        if len(snakes) != 1:
            return

        snake = take_first(snakes)
        if g.me.length <= snake.length:
            #this doesn't belong here
            return

        if not on_border(snake.head):
            return
        if distance_vector_abs(g.me.head, snake.head) not in [(2,2), (1,3), (3,1)]:
            return
        if off_border_1(g.me.head):
            return
        if not all([distance_pq(a, g.me.head) == 3 for a in snake.allowed_moves]):
            return
        
        #coming near
        snake_move = [a for a in snake.allowed_moves if on_border(a)]
        if len(snake_move) != 1:
            return
        snake_move = take_first(snake_move)
        moves = [a for a in moves if distance_vector_abs(a, snake_move) in [(0,2), (2,0)]]
        if len(moves) != 1:
            return
        g.decision_path.append("try kill 4")
        return moves

    def try_trap_2(moves):
        snakes = [snake for snake in g.others if distance_pq(g.me.head, snake.head) == 2]
        if len(snakes) != 1:
            return

        snake = take_first(snakes)
        if g.me.length > snake.length:
            #this doesn't belong here
            return

        if not on_border(snake.head):
            return
        if distance_vector_abs(g.me.head, snake.head) != (1,1):
            return
        if not all([is_adjacent(a, g.me.head) for a in snake.allowed_moves]):
            return
        trap_moves = [a for a in moves if distance_pq(a, snake.head) == 3 and off_border_1(a)]
        if len(trap_moves) != 1:
            return
        trap_move = take_first(trap_moves)
        aset = path_connected_set(trap_move, complement(g.me.territory))
        if len(aset) >= 3 and len(aset) >= g.me.length //2:
            g.decision_path.append("try trap shorter")
            return trap_moves

    def try_trap_4(moves):
        snakes = [snake for snake in g.others if distance_pq(g.me.head, snake.head) == 4]
        if len(snakes) != 1:
            return

        snake = take_first(snakes)
        if g.me.length > snake.length:
            #this doesn't belong here
            return

        if len([snake for snake in g.others if distance_pq(g.me.head, snake.head) == 2]) != 0:
            #no other complications
            return

        if not on_border(snake.head):
            return
        if distance_vector_abs(g.me.head, snake.head) != (2,2):
            return
        if path_distance_pq(g.me.head, snake.head) != 4:
            return
        if not all([distance_pq(a, g.me.head) == 3 for a in snake.allowed_moves]):
            return
        
        #coming near
        snake_moves = [a for a in snake.allowed_moves if on_border(a)]
        if len(snake_moves) != 1:
            return
        snake_move = take_first(snake_moves)
        moves = [a for a in moves if distance_vector_abs(a, snake_move) == (1,1)]
        if len(moves) != 1:
            return
        g.decision_path.append("try trap shorter")
        return moves

        
    def contact_kill(moves):
        if on_border(g.me.head):
            return

        snakes = [snake for snake in g.others 
                  if distance_pq(g.me.head, snake.head) == 2 
                  and snake.length < g.me.length
                  and on_border(snake.head)
                  ]
        if len(snakes) != 1:
            return

        snake = take_first(snakes)
        collision_points = [a for a in moves if is_adjacent(a, snake.head)]
        if len(collision_points) != 1:
            return
        g.decision_path.append(f"contact kill {collision_points}")
        return collision_points

    def trap_kill(moves):
        snake = someone_in_trap()
        if snake is not None:
            kill_moves = [a for a in moves if on_border(a)]
            if len(kill_moves) != 0:
                if g.me.length > snake.length:
                    g.decision_path.append("kill")
                    return kill_moves
                else:
                    kill_moves = [a for a in kill_moves if not is_adjacent(a, snake.head)]
                    if len(kill_moves) != 0:
                        g.decision_path.append("kill")
                        return kill_moves
                    else:
                        g.decision_path.append("keep the trap")
                        return prefer_straight(moves)

    def someone_in_trap():
        if not off_border_1(g.me.head):
            return
        in_trap = False
        for i,c in enumerate(g.me.body):
            if c in g.me.body[-2:]: continue
            for snake in g.others:
                if not is_adjacent(snake.head, c): continue
                if not on_border(snake.head): continue
                if on_border(c): continue
                b = g.me.body[i-1]
                if get_adjacent_dir(c, b) == get_adjacent_dir(snake.neck, snake.head):
                    in_trap = True
                    break
        if not in_trap:
            return
        if any([on_border(g.me.body[j]) for j in range(i)]):
            #already performed kill action
            return
        return snake

    def collision_kill(moves):
        for a in moves:
            snakes = [snake for snake in g.others if is_adjacent(a, snake.head)]
            if not all([snake.length < g.me.length for snake in snakes]): continue
            for snake in snakes:
                if len(snake.allowed_moves) == 1:
                    g.decision_path.append(f"kill! {a}")
                    return [a]

    def ____AVOID_DANGER____():
        pass

    def single_collision(moves):
        def killer_collision(a):
            killers = [snake for snake in g.others if is_adjacent(a, snake.head) and snake.length > g.me.length]
            return len(killers) != 0
        def nonkiller_collision(a):
            nonkillers = [snake for snake in g.others if is_adjacent(a, snake.head) and snake.length == g.me.length]
            return len(nonkillers) != 0
        if move_connected_group(moves) == 1:
            return prefer_no(nonkiller_collision)(
                prefer_no(killer_collision)(moves)
            )

    def grow_path(head, steps):
        layers = [[[head]]]
        for i in range(steps):
            layer = [ path+[nhead]
                for path in layers[-1]
                for end in [path[-1]]
                for nhead in adj_cells(end)
                if nhead not in path
                and nhead not in g.x.occupied_cells[i]
            ]
            layers.append(layer)
        return layers

    def multi_step_collision(moves):
        killers = [snake for snake in g.others if snake.length > g.me.length if distance_pq(snake.head, g.me.head) <= 8]
        nonkillers = [snake for snake in g.others if snake.length == g.me.length if distance_pq(snake.head, g.me.head) <= 8]
        for snake in g.snakes:
            snake.head_paths = grow_path(snake.head, 5)

        def collision_score(a):
            def path_collision_score(apath):
                length = len(apath)
                if length == 5:
                    return 999
                if len(g.me.head_paths) <= length:
                    return length - 1
                snakes = (killers+nonkillers) if length <= 3 else killers
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

        move_score = [(a, collision_score(a)) for a in moves]
        low_score = [(a, score) for a, score in move_score if score < 999]
        score_999 = [a for a, score in move_score if score == 999]
        collisions = [a for a, score in move_score if score == 1]
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
        
    def killer_near(moves):
        return cases([
            me_at_corner,
            no_killer_return,
            multi_killer_near,
            single_killer_near,
        ])(moves)

    def at_corner(p):
        distv = distance_to_border(p)
        return sum(distv) <= 2

    def me_at_corner(moves):
        if at_corner(g.me.head):
            killers = [snake for snake in g.others if snake.length > g.me.length 
                    and path_distance_pq(snake.head, g.me.head) <= 10 ]
            if len(killers) != 0:
                return prefer_no(lambda a: sum(distance_to_border(a)) <= 1)(moves)

    def single_killer_near(moves):
        killers = [snake for snake in g.others if snake.length > g.me.length 
                   if path_distance_pq(snake.head, g.me.head) <= 6 ]
        if len(killers) != 1:
            return

        killer = take_first(killers)
        if killer.length == g.me.length + 1:
            food = [f for f in g.food if distance_pq(f, g.me.head) <= 6]
            if len(food) != 0:
                food_distance = [(f, d) for f in food for d in [path_distance_pq(f, g.me.head)] if d < 999]
                if len(food_distance) != 0:
                    food_distance = prefer_by_rank(lambda f: f[1])(food_distance)
                    food = [f for f,d in food_distance]
                    if any([path_distance_pq(f, g.me.head) < path_distance_pq(f, killer.head) for f in food]):
                        g.decision_path.append("get food and length will be equal")
                        return
        if distance_pq(g.me.head, killer.head) == 6:
            #heading border allowed
            if off_border_1(g.me.head) and not on_border(g.me.neck) and not off_border_1(g.me.neck):
                return
        
        if min(distance_to_border(g.me.head)) <= 1:
            return prefer_no(on_border)(moves)

    def multi_killer_near(moves):
        killers = [snake for snake in g.others if snake.length > g.me.length 
                   if path_distance_pq(snake.head, g.me.head) <= 6 ]
        def move_away_score(a):
            return sum([1 
                        if path_distance_pq(a, snake.head) > path_distance_pq(g.me.head, snake.head)
                        else -1
                        for snake in killers 
                        ])
        if len(killers) >= 2:
            g.decision_path.append(f"multi killer {len(killers)}")
            distv = distance_to_border(g.me.head)
            if min(distv) <= 1:
                return prefer_by_score(move_away_score)(prefer_no(on_border)(moves))
            return prefer_by_score(move_away_score)(moves)

    def no_killer_return(moves):
        killers = [snake for snake in g.others if snake.length > g.me.length if distance_pq(snake.head, g.me.head) <= 6]
        if len(killers) == 0:
            return moves

    def ____SPLIT_CHOICES____():
        pass

    def move_connected_group(moves):
        if len(moves) == 1:
            return 1
        elif len(moves) == 2:
            a,b = moves
            if path_distance_pq(a, b) > 2:
                return 2
            else:
                return 1
        elif len(moves) == 3:
            c = [a for a in moves if is_straight(a)][0]
            a,b = [a for a in moves if a != c]
            ac = path_distance_pq(a, c)
            bc = path_distance_pq(b, c)
            if ac == 2 and bc == 2:
                return 1
            elif ac == 2 or bc == 2:
                return 2
            else:
                return 3

    def split_choice(moves):
        ngroup = move_connected_group(moves)
        if ngroup == 1:
            return
        if ngroup == 3:
            return prefer_by_score(lambda a: len(path_connected_set(a)))(moves)
        
        #ngroup == 2
        return cases([
            two_split_two,
            (three_split_two),
        ])(moves)

    def move_space(a):
        if a not in g.me.territory:
            return []
        return path_connected_set(a, complement(g.me.territory))

    def two_split_two(moves):
        if len(moves) != 2:
            return
        return prefer_by_score(lambda a: len(move_space(a)))(moves)

    def three_split_two(moves):
        if len(moves) != 3:
            return
        return prefer_by_score(lambda a: len(move_space(a)))(moves)

    def ____WAYOUT____():
        pass

    def wayout(moves):
        ngroup = move_connected_group(moves)
        if ngroup != 1:
            return

        return cases([
            wayout_see_one_tail,
        ])(moves)

    def wayout_see_one_tail(moves):
        aset = path_connected_set(g.me.head)
        aset = [p for p in aset if p != g.me.head]
        if len(aset) >= int(g.me.length * 1.2):
            return
        snakes = [snake for snake in g.others if path_connected(g.me.head, snake.tail)]
        if len(snakes) != 1:
            return
        snake = take_first(snakes)
        if snake.length > g.me.length:
            #this case is to prevent a smaller snake try to confine me
            return
        waypoints = [(c,d) 
                     for i,c in enumerate(snake.body) if path_connected(g.me.head, c) 
                     for d in [abs(path_distance_pq(g.me.head, c) + i - snake.length)]
                        ]
        waypoints = [c for c,d in waypoints if d == min([d for c,d in waypoints])]
        waypoint = take_first(waypoints)
        g.decision_path.append(f"wayout tail shortcut {waypoint}")
        return shortest_path_move(g.me.head, waypoint)

    def ____GET_FOOD____():
        pass

    def get_food(moves):
        food_near = [f for f in g.food if distance_pq(f, g.me.head) <= 8]
        food_good = [f for f in food_near if path_connected(f, g.me.head) and all([path_distance_pq(f, g.me.head) < path_distance_pq(f, snake.head) for snake in g.others])]
        if len(food_good) != 0:
            food_better = prefer_by_rank(lambda f: path_distance_pq(f, g.me.head))(food_good)
            food_target = take_first(food_better)
            food_moves = shortest_path_move(g.me.head, food_target)
            return prefer_yes(lambda a: a in food_moves)(moves)

    def ____OTHER_CONSIDERATIONS____():
        pass

    def other_considerations(moves):
        return sequential([
            crowd_prefer_open_space,
            short_prefer,
            prefer_straight,
        ])(moves)

    def short_prefer(moves):
        if g.me.length <= 8:
            return sequential([
                prefer_more_next_moves,
                prefer_away_border,
            ])(moves)

    def prefer_away_border(moves):
        return prefer_by_score(lambda a: min(*distance_to_border(a), 2))(moves)

    def crowd_prefer_open_space(moves):
        if len(g.others) >= 2:
            g.decision_path.append("try to go to open space")
            return split_prefer_open_space(moves)

    def split_prefer_open_space(moves):
        ngroup = move_connected_group(moves)
        if ngroup > 1:
            return prefer_open_space(moves)

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
            occupied = g.x.occupied_cells[0]
        #remove q from occupied otherwise there is no path
        occupied = [p for p in occupied if p != q]
        layers = path_connected_layers(p, occupied)
        for i,layer in enumerate(layers):
            if q in layer:
                return i
        return 999

    def path_connected_layers(p, occupied=None):
        if occupied is None:
            occupied = g.x.occupied_cells[0]
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
            occupied = g.x.occupied_cells[0]
        layers = path_connected_layers(p, occupied)
        return set([q for layer in layers for q in layer])

    def path_connected(p, q, occupied=None):
        if occupied is None:
            occupied = g.x.occupied_cells[0]
        occupied = [x for x in occupied if x != q]
        return q in path_connected_set(p, occupied)

    def shortest_path_move(p, q, occupied=None):
        if is_adjacent(p, q):
            return [q]
        if occupied is None:
            occupied = g.x.occupied_cells[0]
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

    def sequential(fs):
        def fn(moves):
            for f in fs:
                if len(moves) <= 1:
                    return moves
                result = f(moves)
                if result is not None:
                    moves = result
            return moves
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
        moves = [a for a in adj_cells(p) if a not in g.x.occupied_cells[1]]
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

    def prefer_by_score(score):
        def fn(moves):
            moves = [(a, score(a)) for a in moves]
            moves = first_group(moves, reverse=True)
            return moves
        return fn

    def prefer_more_next_moves(moves):
        def n_next_moves(a):
            next_moves = [p for p in adj_cells(a) if p not in g.x.occupied_cells[1]]
            return len(next_moves)
        return prefer_by_score(n_next_moves)(moves)

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

    print(g.log)

    game_state["next_move"] = next_move
    return True

######################################################
# testing
######################################################

def ________TESTING________():
    pass

def init_from_log(log):
    def reverse_coord(cs):
        return [{"x":x, "y":y} for x,y in cs]

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

if __name__ == "__main__":
    log = {'id': '3fbe1c07-e716-43ce-ab37-9fb1e23bd12a', 'turn': 71, 'me': {'name': 'mark_snake_test BLUE', 'health': 92, 'body': [(3, 10), (2, 10), (2, 9), (3, 9), (4, 9), (5, 9), (5, 8), (5, 7)]}, 'others': [{'name': 'the evening and the morning', 'health': 81, 'body': [(7, 2), (7, 3), (8, 3), (8, 4), (9, 4), (10, 4), (10, 5), (10, 6), (10, 7)]}, {'name': 'ich heisse marvin', 'health': 98, 'body': [(2, 3), (2, 2), (3, 2), (3, 3), (3, 4), (4, 4), (5, 4), (6, 4)]}], 'food': [(0, 9), (8, 0)], 'module': 'simp', 'decision_path': ['1vn'], 'next_coord': (4, 10), 'next_move': 'right', 'time': '0.000s'}
    log = {'id': 'ed887488-c738-47de-9721-c07d8f208fbb', 'turn': 155, 'me': {'name': 'mark_snake_test BLUE', 'health': 24, 'body': [(1, 8), (0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (1, 3), (1, 4)]}, 'others': [{'name': 'the evening and the morning', 'health': 99, 'body': [(5, 8), (6, 8), (6, 9), (7, 9), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (9, 9), (9, 8), (9, 7), (10, 7), (10, 6), (9, 6), (9, 5), (8, 5), (8, 4)]}, {'name': 'ich heisse marvin', 'health': 58, 'body': [(6, 5), (5, 5), (5, 4), (5, 3), (4, 3), (3, 3), (3, 4), (3, 5), (2, 5), (2, 6), (3, 6)]}], 'food': [(0, 10)], 'module': 'simp', 'decision_path': ['1vn'], 'next_coord': (1, 9), 'next_move': 'up', 'time': '0.011s'}
    log = {'id': '89064acc-a973-4df0-beb3-dccb38e7bc3d', 'turn': 82, 'me': {'name': 'mark_snake_test BLUE', 'health': 20, 'body': [(3, 9), (4, 9), (4, 8), (3, 8)]}, 'others': [{'name': 'Frank The Tank', 'health': 64, 'body': [(4, 4), (5, 4), (5, 3), (5, 2), (6, 2), (6, 1), (7, 1), (8, 1), (9, 1)]}, {'name': 'Kakemonsteret-v2', 'health': 99, 'body': [(10, 2), (10, 3), (9, 3), (9, 4), (9, 5), (8, 5), (7, 5), (7, 6), (6, 6), (6, 5)]}, {'name': 'Wim HU [dev]', 'health': 96, 'body': [(4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (9, 9), (8, 9), (8, 8), (7, 8)]}], 'food': [(0, 1)], 'module': 'simp', 'decision_path': ['1vn', 'kill'], 'next_coord': (3, 10), 'next_move': 'up', 'time': '0.000s'}
    log = {'id': '19abee7a-906d-4775-98cf-3736dbc5c613', 'turn': 107, 'me': {'name': 'mark_snake_test BLUE', 'health': 17, 'body': [(6, 1), (5, 1), (5, 2), (5, 3), (5, 4)]}, 'others': [{'name': 'Frank The Tank', 'health': 95, 'body': [(7, 2), (7, 3), (8, 3), (9, 3), (10, 3), (10, 2), (9, 2)]}, {'name': 'Kakemonsteret-v2', 'health': 97, 'body': [(3, 2), (3, 3), (3, 4), (3, 5), (2, 5), (2, 4), (2, 3), (1, 3), (1, 2), (1, 1), (1, 0), (0, 0), (0, 1), (0, 2)]}, {'name': 'Wim HU [dev]', 'health': 50, 'body': [(4, 7), (4, 6), (5, 6), (6, 6), (6, 7), (7, 7), (8, 7), (9, 7)]}], 'food': [(7, 1)], 'module': 'simp', 'decision_path': ['1vn', 'killer collision points [(7, 1), (6, 2)]'], 'next_coord': (6, 0), 'next_move': 'down', 'time': '0.002s'}
    log = {'id': '5199997b-ea22-40a6-b745-d3234e040fc2', 'turn': 62, 'me': {'name': 'mark_snake_test BLUE', 'health': 97, 'body': [(2, 8), (2, 9), (3, 9), (4, 9), (5, 9)]}, 'others': [{'name': 'Frank The Tank', 'health': 93, 'body': [(1, 7), (1, 6), (2, 6), (2, 7), (3, 7), (4, 7), (5, 7), (5, 8), (6, 8), (6, 7)]}, {'name': 'Kakemonsteret-v2', 'health': 94, 'body': [(7, 5), (6, 5), (5, 5), (5, 4), (5, 3), (5, 2), (5, 1), (6, 1)]}, {'name': 'Wim HU [dev]', 'health': 89, 'body': [(3, 3), (3, 2), (2, 2), (1, 2), (0, 2), (0, 3), (0, 4)]}], 'food': [(8, 5), (8, 3)], 'module': 'simp', 'decision_path': ['1vn', 'confined move [(3, 8)]'], 'next_coord': (1, 8), 'next_move': 'left', 'time': '0.001s'}
    log = {'id': '210c451a-bd0d-4219-bb7f-386e38317317', 'turn': 29, 'me': {'name': 'mark_snake_test GREEN', 'health': 73, 'body': [(8, 9), (7, 9), (6, 9), (5, 9)]}, 'others': [{'name': 'mark_snake_test BLUE', 'health': 86, 'body': [(9, 8), (9, 7), (9, 6), (9, 5), (9, 4)]}, {'name': 'mark_snake_test BLUE', 'health': 87, 'body': [(1, 4), (1, 5), (1, 6), (2, 6), (3, 6), (4, 6)]}, {'name': 'mark_snake_test RED', 'health': 95, 'body': [(2, 1), (3, 1), (4, 1), (5, 1), (5, 0), (6, 0)]}], 'food': [(1, 3), (1, 1)], 'module': 'simp', 'decision_path': ['1vn'], 'next_coord': (9, 9), 'next_move': 'right', 'time': '0.004s'}
    log = {'id': 'd504c5d2-1456-4771-9129-9b270390ad1b', 'turn': 39, 'me': {'name': 'mark_snake_test GREEN', 'health': 98, 'body': [(4, 9), (3, 9), (3, 8), (2, 8), (1, 8), (0, 8), (0, 9)]}, 'others': [{'name': 'mark_snake_test BLUE', 'health': 91, 'body': [(9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7)]}, {'name': 'mark_snake_test BLUE', 'health': 72, 'body': [(6, 9), (6, 8), (6, 7), (6, 6), (6, 5), (6, 4)]}, {'name': 'mark_snake_test RED', 'health': 89, 'body': [(5, 8), (5, 7), (4, 7), (4, 6), (4, 5), (4, 4)]}], 'food': [(5, 3), (1, 1)], 'module': 'simp', 'decision_path': ['1vn'], 'next_coord': (4, 10), 'next_move': 'up', 'time': '0.006s'}
    log = {'id': '113443e3-32e5-4166-ab4b-d1dabcd6389f', 'turn': 69, 'me': {'name': 'mark_snake_test RED', 'health': 86, 'body': [(9, 8), (9, 7), (9, 6), (9, 5), (9, 4), (9, 3), (8, 3)]}, 'others': [{'name': 'mark_snake_test BLUE', 'health': 100, 'body': [(2, 5), (1, 5), (0, 5), (0, 4), (1, 4), (1, 3), (1, 2), (1, 1), (2, 1), (3, 1), (3, 1)]}, {'name': 'mark_snake_test BLUE', 'health': 92, 'body': [(4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (5, 8)]}, {'name': 'mark_snake_test GREEN', 'health': 88, 'body': [(8, 9), (7, 9), (6, 9), (5, 9), (4, 9), (3, 9), (2, 9), (1, 9)]}], 'food': [(10, 0)], 'module': 'simp', 'decision_path': ['1vn'], 'next_coord': (9, 9), 'next_move': 'up', 'time': '0.005s'}
    log = {'id': '9f7bf5f4-4673-4d11-ae1a-ea3761d51ba0', 'turn': 48, 'me': {'name': 'mark_snake_test RED', 'health': 54, 'body': [(9, 7), (9, 8), (8, 8), (8, 7)]}, 'others': [{'name': 'mark_snake_test BLUE', 'health': 92, 'body': [(8, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1), (7, 1)]}, {'name': 'mark_snake_test GREEN', 'health': 98, 'body': [(5, 9), (5, 10), (6, 10), (6, 9), (7, 9), (7, 8), (6, 8), (6, 7)]}, {'name': 'mark_snake_test YELLOW', 'health': 96, 'body': [(6, 6), (6, 5), (6, 4), (6, 3), (5, 3), (4, 3), (3, 3), (3, 2)]}], 'food': [(10, 6), (3, 5)], 'module': 'simp', 'decision_path': ['1vn', 'multi killer 3'], 'next_coord': (9, 6), 'next_move': 'down', 'time': '0.009s'}
    log = {'id': '7b522bfa-1f7f-49b6-8789-e39f91092252', 'turn': 99, 'me': {'name': 'mark_snake_test BLUE', 'health': 89, 'body': [(1, 8), (2, 8), (2, 7), (3, 7), (4, 7), (4, 8), (4, 9)]}, 'others': [{'name': 'mark_snake_test GREEN', 'health': 84, 'body': [(2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (10, 0)]}, {'name': 'mark_snake_test RED', 'health': 68, 'body': [(3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (8, 5)]}, {'name': 'mark_snake_test YELLOW', 'health': 72, 'body': [(10, 9), (10, 8), (10, 7), (10, 6), (9, 6), (8, 6), (7, 6), (6, 6), (5, 6)]}], 'food': [(0, 8)], 'module': 'simp', 'decision_path': ['1vn'], 'next_coord': (1, 7), 'next_move': 'down', 'time': '0.004s'}

    game_state = init_from_log(log)
    main(game_state)

