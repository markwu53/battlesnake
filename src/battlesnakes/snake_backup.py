import typing
import math
import time
import itertools


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



#this gives me #20 score 8603 on 6/3/2025
def move(game_state: typing.Dict) -> typing.Dict:
    """
    move in a square area
    following an area filling path
    the area has a dimension of n x m
    where n is an even number
    so that the path can close
    start with 4x3
    then 4x4, 4x5, 4x6
    then 6x5, 6x6, 6x7, 6x8
    then 8x7, ...
    """

    """
    Then avoid immediate danger
    check opponents and self
    """

#############################################
# utility functions
#############################################

    def get_adjacent_dir(p: typing.Tuple, q: typing.Tuple) -> str:
        assert(is_adjacent(p, q))
        x,y = p
        nx,ny = q
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        return get_adjacent_dir(head_coord, next_head_coord)

    def pos_on_board(pos: typing.Tuple) -> bool:
        x,y = pos
        if x < 0:
            return False
        if y < 0:
            return False
        if x >= game_state["board"]["width"]:
            return False
        if y >= game_state["board"]["height"]:
            return False
        return True

    def adj_cells(pos: typing.Tuple) -> typing.List:
        x,y = pos
        moves = [(1,0), (-1,0), (0,1), (0,-1)]
        npos = [(a+x,b+y) for a,b in moves]
        npos = [p for p in npos if pos_on_board(p)]
        return npos

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

    def on_border(coord: typing.Tuple) -> bool:
        x,y = coord
        if x == 0 or x == game_state["board"]["width"]-1:
            return True
        if y == 0 or y == game_state["board"]["height"]-1:
            return True
        return False

    def opponent_snakes() -> typing.List:
        my_head = game_state["you"]["body"][0]
        head = (my_head["x"], my_head["y"])
        snakes = [s for s in game_state["board"]["snakes"]]
        snakes = [s for s in snakes if (s["body"][0]["x"], s["body"][0]["y"]) != head]
        return snakes

    def distance_pq(p: typing.Tuple, q: typing.Tuple) -> int:
        x1,y1 = p
        x2,y2 = q
        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def is_adjacent(p1: typing.Tuple, p2: typing.Tuple) -> bool:
        return distance_pq(p1, p2) == 1

    def get_my_head() -> typing.Tuple:
        my_head = game_state["you"]["body"][0]
        head_coord = (my_head["x"], my_head["y"])
        return head_coord

    def get_coord(items: typing.List) -> typing.List:
        return [(c["x"], c["y"]) for c in items]

    def lean_board() -> typing.Dict:
        return {
            "id": game_state["game"]["id"],
            "turn": game_state["turn"],
            "food": get_coord(game_state["board"]["food"]),
            "snakes": [{
                "name": snake["name"],
                "health": snake["health"],
                "body": get_coord(snake["body"]),
            } for snake in game_state["board"]["snakes"]],
        }

    def occupied_cells(step):
        #not including head
        #assuming no die
        #assuming no eating food
        #if eating food it will be more
        snakes = game_state["board"]["snakes"]
        sbody = []
        for s in snakes:
            body = get_coord(s["body"])
            if s["health"] == 100:
                #eat food, tail will not move in the next step
                body += [body[-1]]
            sbody.append(body[:-step])
        cells = [c for s in sbody for c in s]
        return cells

#############################################
# end of utility functions
#############################################

    #ideas:
    #1. In avoid_danger:
    # if in 3 allowed moves, one has rank 1, the others are rank 99, 
    # take the one that is NOT opposite to the rank 1 move (with respect to head)
    #2. don't go in trap - this is not in avoid_danger - need a separate module
    # I use this idea to try_kill others, but don't let others kill me using the same idea
    #2.1 don't go in a position that has only one next move
    #3. when finding food, don't let equal length opponents affect food move.
    #4. better try_kill method


    def allowed_move():

        def permissible_nstep(head, n):
            paths = [[head]]
            for step in range(1, n+1):
                occupied = occupied_cells(step)
                paths = [ npath 
                        for path in paths 
                        for npath in [path+[p] for p in adj_cells(path[-1]) 
                                if p not in occupied and p not in path] ]
            result = list(set([path[1] for path in paths]))
            return result


        head = get_my_head()
        allowed = permissible_nstep(head, 5)
        allowed_1 = permissible_nstep(head, 1)
        game_state["allowed_move"] = allowed
        game_state["allowed_move_1"] = allowed_1

    #1. determine the area dimension corners
    # determine my position dirs
    def routine_move():

        def valid_area(area: typing.Tuple) -> bool:
            ((x1,y1), (x2,y2)) = area
            if not 0 <= x2 < game_state["board"]["width"]:
                return False
            if not 0 <= y2 < game_state["board"]["height"]:
                return False
            return True

        def body_in_box(area: typing.Tuple, body: typing.List) -> bool:
            ((x1,y1), (x2,y2)) = area
            for cell in body:
                x = cell["x"]
                y = cell["y"]
                if not x1 <= x <= x2:
                    return False
                if not y1 <= y <= y2:
                    return False
            return True
        
        def find_containing_boxes(body: typing.List) -> typing.List:
            boxes = []
            width, height = box_dim()
            for x1 in range(game_state["board"]["width"]):
                for y1 in range(game_state["board"]["height"]):
                    #bottom-left corner (x1,y1)
                    x2 = x1+width-1
                    y2 = y1+height-1
                    box = ((x1,y1), (x2,y2))
                    if not valid_area(box):
                        continue
                    if body_in_box(box, body):
                        boxes.append(box)
            return boxes

        def all_moving_boxes() -> typing.List:
            body = game_state["you"]["body"]

            #only check first 3
            body = body[:3]

            boxes = []
            width, height = box_dim()
            for x1 in range(game_state["board"]["width"]):
                for y1 in range(game_state["board"]["height"]):
                    #bottom-left corner (x1,y1)
                    x2 = x1+width-1
                    y2 = y1+height-1
                    box = ((x1,y1), (x2,y2))
                    if not valid_area(box):
                        continue
                    if body_in_box(box, body):
                        boxes.append(box)

            assert(len(boxes) != 0)
            return boxes

        def box_dim() -> typing.Tuple:
            nsnakes = len(game_state["board"]["snakes"])
            length = game_state["you"]["length"]
            if nsnakes >= 4:
                #return (4,3)
                return (4,4)
            if nsnakes == 3:
                #return (4,4)
                return (4,5)
            if nsnakes <= 2:
                #if length <= 15: return (4,5)
                #if length <= 20: return (4,7)
                return (4,9)
            raise(ValueError("area_dim"))

        def attractor_boxes() -> typing.List:
            adim = box_dim()
            if adim == (4,3):
                return [
                    ((1,2), (4,4)),
                    ((1,6), (4,8)),
                    ((6,2), (9,4)),
                    ((6,6), (9,8)),
                ]
            if adim == (4,4):
                return [
                    ((1,1), (4,4)),
                    ((1,6), (4,9)),
                    ((6,1), (9,4)),
                    ((6,6), (9,9)),
                ]
            if adim == (4,5):
                #return [ ((1,0), (4,4)), ((1,6), (4,10)), ((6,0), (9,4)), ((6,6), (9,10)), ]
                #change to two boxes, both off-border
                return [
                    ((1,1), (4,5)),
                    ((6,5), (9,9))
                ]
            if adim == (4,7):
                return [
                    ((1,2), (4,8)),
                    ((6,2), (9,8)),
                ]
            if adim == (4,9):
                return [
                    ((1,1), (4,9)),
                    ((6,1), (9,9)),
                ]

            raise(ValueError("BOX DIMENSION"))


        def target_bounding_box() -> typing.Tuple:
            #also only check first 4
            body = game_state["you"]["body"][:3]
            body_center_x = sum([cell["x"] for cell in body]) / len(body)
            body_center_y = sum([cell["y"] for cell in body]) / len(body)
            boxes = attractor_boxes()

            def sort_corner(corner: typing.Tuple):
                ((x1,y1), (x2,y2)) = corner
                xc = (x1+x2)/2
                yc = (y1+y2)/2
                return math.sqrt((xc-body_center_x)**2+(yc-body_center_y)**2)

            boxes = sorted(boxes, key=sort_corner)
            return boxes[0]

        def get_bounding_box() -> typing.Tuple:
            """
            get a rectangular area depend on the snake initial position
            so that even when the snake moves, the area doesn't change
            """

            #prefer the attactor boxes
            for box in attractor_boxes():

                #experiment first 3
                body = game_state["you"]["body"][:3]

                if body_in_box(box, body):
                    return box

            #if not in one of attractor boxes, find one close to it,
            #so that the area will move to the closest attractor box

            target = target_bounding_box()

            #find boxes that contain my snake body or the first n of it
            boxes = all_moving_boxes()

            def sort_box(box: typing.Tuple):
                ((x1,y1), (x2,y2)) = box
                xc = (x1+x2)/2
                yc = (y1+y2)/2
                ((target_x1, target_y1), (target_x2, target_y2)) = target
                target_xc = (target_x1+target_x2)/2
                target_yc = (target_y1+target_y2)/2
                return math.sqrt((xc-target_xc)**2+(yc-target_yc)**2)

            boxes = sorted(boxes, key=sort_box)
            box = boxes[0]
            return box


        def space_filling_path(width, height):
            assert(width % 2 == 0)
            base = [(x, 0) for x in range(width)]
            vert_lines = [[(x, y) for y in range(1, height)] for x in range(width)]
            vert_lines = [line if index % 2 != 0 else list(reversed(line)) for index, line in enumerate(vert_lines)]
            vert_lines = list(reversed(vert_lines))
            path = base + [p for line in vert_lines for p in line]
            return path

        area = get_bounding_box()
        game_state["boxing_area"] = area

        order_list = space_filling_path(*box_dim())

        bottom_left_corner = area[0]
        x0,y0 = bottom_left_corner
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        head_coord = (my_head["x"], my_head["y"])
        neck_coord = (my_neck["x"], my_neck["y"])
        relative_head_coord = (head_coord[0]-x0, head_coord[1]-y0)
        relative_neck_coord = (neck_coord[0]-x0, neck_coord[1]-y0)
        head_pos = 0
        for head_pos in range(len(order_list)):
            if relative_head_coord == order_list[head_pos]:
                break
        next_head_pos = head_pos+1
        next_head_pos %= len(order_list)
        if relative_neck_coord == order_list[next_head_pos]:
            next_head_pos = head_pos-1
            next_head_pos %= len(order_list)

        #get next_head absolute coordinate
        x2,y2 = order_list[next_head_pos]
        x2 += x0
        y2 += y0

        #save in global var
        game_state["routine_move"] = (x2,y2)

    def avoid_danger():
        game_state["avoid_danger"] = []


        #try avoid danger in every step
        """
        snakes = opponent_snakes()
        danger_snakes = [snake for snake in snakes 
                         if len(snake["body"]) >= game_state["you"]["length"]
                         and distance_pq(get_my_head(), get_coord(snake["body"])[0]) <= 4]
        if len(danger_snakes) == 0: return
        """

        board = lean_board()

        step_occupied_cells = [
            occupied_cells(step)
            for step in [1,2,3,4]
        ]

        max_step = 3
        if len(board["snakes"]) <=3:
            max_step = 4

        def grow_path(head, steps=max_step):
            paths = [[head]]
            for step in range(steps):
                paths = [path+[nhead] 
                        for path in paths
                        for head in [path[-1]]
                        for nhead in adj_cells(head)
                        if nhead not in step_occupied_cells[step]
                        and nhead not in path
                        ]
            return paths

        for snake in board["snakes"]:
            snake["paths"] = grow_path(snake["body"][0])

        my_name = game_state["you"]["name"]
        my_snake = [snake for snake in board["snakes"] if snake["name"] == my_name][0]

        def danger_rank(apath, safer):
            length = len(apath)
            if apath[-1] in [
                path[length-1] 
                for snake in board["snakes"]
                for path in snake["paths"]
                if snake["name"] != my_name
                and (len(snake["body"]) >= len(my_snake["body"])
                if safer
                else len(snake["body"]) > len(my_snake["body"])
                )
            ]:
                return length-1
            if length == max_step+1:
                #no danger
                return 99
            return max([danger_rank(apath+[nhead], safer)
                for nhead in set([
                    path[length]
                    for path in my_snake["paths"]
                    if tuple(path[:length]) == tuple(apath)
                ])])
        
        game_state["avoid_danger"].append([
            [(apath[1], danger_rank(list(apath), safer=True))
                    for apath in set([tuple(path[:2]) for path in my_snake["paths"]])],
            [(apath[1], danger_rank(list(apath), safer=False))
                    for apath in set([tuple(path[:2]) for path in my_snake["paths"]])],
        ])


    def find_food():

        def food_path(food: typing.Tuple) -> typing.List:
            x0,y0 = get_my_head()
            x1,y1 = food
            mx = min(x0,x1)
            Mx = max(x0,x1)
            my = min(y0,y1)
            My = max(y0,y1)
            region = [(x,y) for x in range(mx,Mx+1) for y in range(my, My+1)]
            if len(region) != distance_pq(get_my_head(), food)+1:
                #has a rectangular region
                border = [(x,y) for x,y in region if not (mx<x<Mx and my<y<My)]
                line1 = sorted([(x,y) for x,y in border if x==mx])
                line2 = sorted([(x,y) for x,y in border if y==my])
                line3 = sorted([(x,y) for x,y in border if x==Mx])
                line4 = sorted([(x,y) for x,y in border if y==My])

                if x1 > x0 and y1 > y0:
                    #upper right
                    path1 = line2 + line3[1:]
                    path2 = line1 + line4[1:]
                elif x1 < x0 and y1 > y0:
                    #upper left
                    path1 = line3 + list(reversed(line4[1:]))
                    path2 = list(reversed(line2)) + line1[1:]
                elif x1 < x0 and y1 < y0:
                    #lower left
                    path1 = list(reversed(line4)) + list(reversed(line1[1:]))
                    path2 = list(reversed(line3)) + list(reversed(line2[1:]))
                else:
                    #if x1 > x0 and y1 < y0:
                    #lower right
                    path1 = list(reversed(line1)) + line2[1:]
                    path2 = line4 + list(reversed(line3[1:]))
                paths = [path1, path2]
            else:
                #straight line to food
                path = sorted(region)
                if x1 < x0 or y1 < y0:
                    path = list(reversed(path))
                paths = [path]

            return paths
        
        def good_path(path: typing.List) -> bool:
            for snake in opponent_snakes():
                for cell in snake["body"]:
                    x = cell["x"]
                    y = cell["y"]
                    if (x,y) in path:
                        return False
            for cell in game_state["you"]["body"][1:]:
                x = cell["x"]
                y = cell["y"]
                if (x,y) in path:
                    return False
            return True

        def find_food_condition() -> bool:
            snakes = opponent_snakes()
            if len(snakes) >= 2 and game_state["you"]["length"] < 10:
                return True
            if len(snakes) >= 3 and game_state["you"]["health"] < 60:
                return True
            if len(snakes) >= 2 and game_state["you"]["health"] < 40:
                return True
            if len(snakes) >= 0 and game_state["you"]["health"] < 20:
                return True
            return False

        game_state["find_food"] = []

        #if opponent snake == 1 and health < 20 find food
        snakes = opponent_snakes()
        if find_food_condition():
            snakes = [get_coord(s["body"]) for s in snakes]
            snake_heads = [s[0] for s in snakes]
            food_target = [(food["x"], food["y"]) for food in game_state["board"]["food"]]
            food_target = [p 
                           for p in food_target 
                           if all([distance_pq(p, get_my_head()) < distance_pq(p, snake_head) 
                                   for snake_head in snake_heads ])]
            food_target = [(food, [path for path in food_path(food) if good_path(path)]) for food in food_target]
            food_target = [(food, paths) for food, paths in food_target if len(paths) != 0]
            food_target = sorted(food_target, key=lambda f: distance_pq(get_my_head(), f[0]))
            if len(food_target) != 0:
                food, paths = food_target[0]
                my_neck = game_state["you"]["body"][1]
                my_neck = (my_neck["x"], my_neck["y"])
                paths = sorted(paths, key=lambda path: 0 if get_adjacent_dir(path[0], path[1]) == get_adjacent_dir(my_neck, path[0]) else 1)
                path = paths[0]
                next_head_coord = path[1]
                #save in the global var
                game_state["find_food"].append(next_head_coord)

    def try_kill():
        game_state["try_kill"] = []

        #kill in any case
        #if len(game_state["board"]["snakes"]) != 2: return

        if game_state["you"]["length"] < 4:
            return

        board = lean_board()
        my_name = "mark_snake"
        my_snake = [snake for snake in board["snakes"] if snake["name"] == my_name][0]
        others = [snake for snake in board["snakes"] if snake["name"] != my_name]

        def entering_kill(snake):
            #the other snake head is on border
            #one of my body cell is adjacent to the other snake head at off-border position
            #they moving in the same dir
            my_body = my_snake["body"]
            head = snake["body"][0]
            neck = snake["body"][1]
            if not on_border(head):
                return False
            length = len(my_snake["body"])
            found = False
            for i, cell in enumerate(my_snake["body"]):
                if i in range(3, length-1) and not on_border(cell):
                    if is_adjacent(cell, head):
                        found = True
                        break
            if not found:
                return False
            if get_adjacent_dir(my_body[i], my_body[i-1]) != get_adjacent_dir(neck, head):
                return False

            return True

        def kill_action_performed():
            return any([on_border(cell) for cell in my_snake["body"]])

        def my_head_at_kill_position():
            if on_border(get_my_head()):
                return False
            if not any([on_border(p) for p in adj_cells(get_my_head())]):
                return False
            return True

        def kill_condition():
            if not any([entering_kill(snake) for snake in others]):
                return False
            if not my_head_at_kill_position():
                return False
            if kill_action_performed():
                return False
            return True        
        
        if not kill_condition():
            return

        suggest = [p for p in adj_cells(get_my_head()) if on_border(p)]
        game_state["try_kill"].append(suggest)

    def best_choice():

        #lower priority first, higher priority will override lower priority

        #routine move always exists and set as default
        game_state["next_head_coord"] = game_state["routine_move"]

        if len(game_state["allowed_move"]) == 0:
            #most strict allowed move empty
            #immediate allowed move may still have some
            if len(game_state["allowed_move_1"]) != 0:
                #use the first of the allowed move
                game_state["next_head_coord"] = game_state["allowed_move_1"][0]
            return

        #set to the first of the allowed moves, then let other considerations override it

        if game_state["next_head_coord"] not in game_state["allowed_move"]:
            game_state["next_head_coord"] = game_state["allowed_move"][0]

        if len(game_state["find_food"]) != 0:
            if game_state["find_food"][0] in game_state["allowed_move"]:
                game_state["next_head_coord"] = game_state["find_food"][0]

        #do not check off-border anymore
        #instead let attractor boxes move the snake off-border

        #new avoid danger

        if len(game_state["avoid_danger"]) != 0:
            #avoid danger is activated
            avoid_danger_1, avoid_danger_2 = game_state["avoid_danger"][0]
            #avoid_danger_1 consider dangers coming from all opponents snakes that have length greater or equal to 
            #avoid_danger_2 only consider length greater than mine

            #special case 1
            #if opponent is longer
            #and distance = 2
            #and in a diagonal position
            #and there are 2 rank 99 moves - which means the opponent head is in a chasing position
            #then perfer the move that keeps this chasing position
            #until to 1-off of the border
            #this is eventually separate the danger by separating the space

            def case_1_condition():
                #go straight when being chased
                if (
                    1 == 1
                    and len([move for move, rank in avoid_danger_2 if rank == 99]) == 2
                    and len([move for move, rank in avoid_danger_2 if rank == 1]) == 1
                ):
                    my_head = get_my_head()
                    a,b = [move for move, rank in avoid_danger_2 if rank == 99]
                    if (get_adjacent_dir(my_head, a) == get_adjacent_dir(my_head, b)
                        or get_adjacent_dir(a, my_head) == get_adjacent_dir(my_head, b)):
                        return False
                    return True

                return False

            def case_2_condition():
                #don't enter a trap
                my_head = get_my_head()
                if not on_border(my_head):
                    return False
                if len([move for move, rank in avoid_danger_2 if rank == 99]) == 2:
                    a,b = [move for move, rank in avoid_danger_2 if rank == 99]
                    for snake in opponent_snakes():
                        body = get_coord(snake["body"])
                        for i, cell in enumerate(body):
                            if i == 0 or i == len(body)-1:
                                continue
                            if is_adjacent(a, cell) and not on_border(cell):
                                if get_adjacent_dir(my_head, a) == get_adjacent_dir(cell, body[i-1]):
                                    #a is a trap, take b
                                    if b in game_state["allowed_move"]:
                                        game_state["next_head_coord"] = b
                                        return True
                            if is_adjacent(b, cell) and not on_border(cell):
                                if get_adjacent_dir(my_head, b) == get_adjacent_dir(cell, body[i-1]):
                                    #a is a trap, take b
                                    if a in game_state["allowed_move"]:
                                        game_state["next_head_coord"] = a
                                        return True
                return False
                    

            def case_3_condition():
                #don't crawl on border
                my_head = get_my_head()


            if case_1_condition():
                my_head = get_my_head()
                move_danger_rank_1 = [move for move, rank in avoid_danger_2 if rank == 1][0]
                move_keep = [move for move, rank in avoid_danger_2 if rank == 99
                    and get_adjacent_dir(my_head, move_danger_rank_1) != get_adjacent_dir(move, my_head)][0]
                move_opposite = [move for move, rank in avoid_danger_2 if rank == 99
                    and get_adjacent_dir(my_head, move_danger_rank_1) == get_adjacent_dir(move, my_head)][0]
                if on_border(move_keep) and not on_border(move_opposite):
                    suggest = move_opposite
                else:
                    suggest = move_keep
                if suggest in game_state["allowed_move"]:
                    game_state["next_head_coord"] = suggest

            elif case_2_condition(): pass

            #more special cases here:


            else:
                #avoid danger default process

                result = [move for move, rank in avoid_danger_1 if rank == 99]
                if len(result) == 0:
                    result = [move for move, rank in avoid_danger_2 if rank == 99]
                if len(result) == 0:
                    result = first_group(avoid_danger_2, reverse=True)

                #prefer off-border when killer near
                def killer_near():
                    my_head = get_my_head()
                    return len([snake_head
                        for snake in opponent_snakes()
                        for snake_head in [get_coord(snake["body"])[0]]
                        if snake["length"] >= game_state["you"]["length"]
                        and distance_pq(my_head, snake_head) <= 4
                        ]) != 0

                if killer_near():
                    result = [(move, 1 if on_border(move) else 0) for move in result]
                    result = first_group(result, reverse=False)
                result = [move for move in result if move in game_state["allowed_move"]]
                if len(result) != 0:
                    if game_state["next_head_coord"] not in result:
                        game_state["next_head_coord"] = result[0]


        #try kill
        if len(game_state["try_kill"]) != 0:
            #try kill is activated
            result = game_state["try_kill"][0]

            #no danger in 3 steps
            result = [move for move in result if move in game_state["allowed_move"]]
            if len(result) != 0:
                if game_state["next_head_coord"] not in result:
                    game_state["next_head_coord"] = result[0]



    #main

    start_time = time.time()
    #ideas
    #next routine path
    #calculated space filling path
    #longer lookahead

    #must satisfy
    allowed_move()

    #priority: avoid danger, find food, routine move
    routine_move()
    avoid_danger()
    find_food()
    try_kill()

    best_choice()

    end_time = time.time()

    next_move = get_next_move(get_my_head(), game_state["next_head_coord"])

    #logging
    log_move = next_move
    log_boxing_area = game_state["boxing_area"]
    log_routine_move = game_state["routine_move"]
    log_allowed_move = game_state["allowed_move"]
    log_avoid_danger = game_state["avoid_danger"]
    log_time_diff = end_time - start_time
    log_time_diff = f"time: {log_time_diff:.3f}s"
    log_find_food = game_state["find_food"]
    log_try_kill = game_state["try_kill"]

    log_board = lean_board()

    log_text = ", ".join([
        f"board: {log_board}",
        f"move: {log_move}",
        f"boxing_area: {log_boxing_area}",
        f"routine_move: {log_routine_move}",
        f"avoid_danger: {log_avoid_danger}",
        f"allowed_move: {log_allowed_move}",
        f"find_food: {log_find_food}",
        f"try_kill: {log_try_kill}",
        log_time_diff,
    ])

    print(log_text)

    return {"move": next_move}





#this gives me #34 score 8134 on 5/27/2025
def move10(game_state: typing.Dict) -> typing.Dict:
    """
    move in a square area
    following an area filling path
    the area has a dimension of n x m
    where n is an even number
    so that the path can close
    start with 4x3
    then 4x4, 4x5, 4x6
    then 6x5, 6x6, 6x7, 6x8
    then 8x7, ...
    """

    """
    Then avoid immediate danger
    check opponents and self
    """


    def valid_area(area: typing.Tuple) -> bool:
        ((x1,y1), (x2,y2)) = area
        if not 0 <= x2 < game_state["board"]["width"]:
            return False
        if not 0 <= y2 < game_state["board"]["height"]:
            return False
        return True

    def body_in_box(area: typing.Tuple, body: typing.List) -> bool:
        ((x1,y1), (x2,y2)) = area
        for cell in body:
            x = cell["x"]
            y = cell["y"]
            if not x1 <= x <= x2:
                return False
            if not y1 <= y <= y2:
                return False
        return True
    
    def find_containing_boxes(body: typing.List) -> typing.List:
        boxes = []
        width, height = box_dim()
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+width-1
                y2 = y1+height-1
                box = ((x1,y1), (x2,y2))
                if not valid_area(box):
                    continue
                if body_in_box(box, body):
                    boxes.append(box)
        return boxes

    def all_moving_boxes() -> typing.List:
        body = game_state["you"]["body"]

        #only check first 3
        body = body[:3]

        boxes = []
        width, height = box_dim()
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+width-1
                y2 = y1+height-1
                box = ((x1,y1), (x2,y2))
                if not valid_area(box):
                    continue
                if body_in_box(box, body):
                    boxes.append(box)

        assert(len(boxes) != 0)
        return boxes

    def space_filling_path(width, height):
        assert(width % 2 == 0)
        base = [(x, 0) for x in range(width)]
        vert_lines = [[(x, y) for y in range(1, height)] for x in range(width)]
        vert_lines = [line if index % 2 != 0 else list(reversed(line)) for index, line in enumerate(vert_lines)]
        vert_lines = list(reversed(vert_lines))
        path = base + [p for line in vert_lines for p in line]
        return path

    def box_dim() -> typing.Tuple:
        nsnakes = len(game_state["board"]["snakes"])
        length = game_state["you"]["length"]
        if nsnakes >= 4:
            #return (4,3)
            return (4,4)
        if nsnakes == 3:
            #return (4,4)
            return (4,5)
        if nsnakes <= 2:
            #if length <= 15: return (4,5)
            #if length <= 20: return (4,7)
            return (4,9)
        raise(ValueError("area_dim"))

    def attractor_boxes() -> typing.List:
        adim = box_dim()
        if adim == (4,3):
            return [
                ((1,2), (4,4)),
                ((1,6), (4,8)),
                ((6,2), (9,4)),
                ((6,6), (9,8)),
            ]
        if adim == (4,4):
            return [
                ((1,1), (4,4)),
                ((1,6), (4,9)),
                ((6,1), (9,4)),
                ((6,6), (9,9)),
            ]
        if adim == (4,5):
            #return [ ((1,0), (4,4)), ((1,6), (4,10)), ((6,0), (9,4)), ((6,6), (9,10)), ]
            #change to two boxes, both off-border
            return [
                ((1,1), (4,5)),
                ((6,5), (9,9))
            ]
        if adim == (4,7):
            return [
                ((1,2), (4,8)),
                ((6,2), (9,8)),
            ]
        if adim == (4,9):
            return [
                ((1,1), (4,9)),
                ((6,1), (9,9)),
            ]

        raise(ValueError("BOX DIMENSION"))

    def target_bounding_box() -> typing.Tuple:
        #also only check first 4
        body = game_state["you"]["body"][:3]
        body_center_x = sum([cell["x"] for cell in body]) / len(body)
        body_center_y = sum([cell["y"] for cell in body]) / len(body)
        boxes = attractor_boxes()

        def sort_corner(corner: typing.Tuple):
            ((x1,y1), (x2,y2)) = corner
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            return math.sqrt((xc-body_center_x)**2+(yc-body_center_y)**2)

        boxes = sorted(boxes, key=sort_corner)
        return boxes[0]

    def get_bounding_box() -> typing.Tuple:
        """
        get a rectangular area depend on the snake initial position
        so that even when the snake moves, the area doesn't change
        """

        #prefer the attactor boxes
        for box in attractor_boxes():

            #experiment first 3
            body = game_state["you"]["body"][:3]

            if body_in_box(box, body):
                return box

        #if not in one of attractor boxes, find one close to it,
        #so that the area will move to the closest attractor box

        target = target_bounding_box()

        #find boxes that contain my snake body or the first n of it
        boxes = all_moving_boxes()

        def sort_box(box: typing.Tuple):
            ((x1,y1), (x2,y2)) = box
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            ((target_x1, target_y1), (target_x2, target_y2)) = target
            target_xc = (target_x1+target_x2)/2
            target_yc = (target_y1+target_y2)/2
            return math.sqrt((xc-target_xc)**2+(yc-target_yc)**2)

        boxes = sorted(boxes, key=sort_box)
        box = boxes[0]
        return box

    def get_adjacent_dir(p: typing.Tuple, q: typing.Tuple) -> str:
        assert(is_adjacent(p, q))
        x,y = p
        nx,ny = q
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        return get_adjacent_dir(head_coord, next_head_coord)

    #1. determine the area dimension corners
    # determine my position dirs
    def routine_move():
        area = get_bounding_box()
        game_state["boxing_area"] = area

        order_list = space_filling_path(*box_dim())

        bottom_left_corner = area[0]
        x0,y0 = bottom_left_corner
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        head_coord = (my_head["x"], my_head["y"])
        neck_coord = (my_neck["x"], my_neck["y"])
        relative_head_coord = (head_coord[0]-x0, head_coord[1]-y0)
        relative_neck_coord = (neck_coord[0]-x0, neck_coord[1]-y0)
        head_pos = 0
        for head_pos in range(len(order_list)):
            if relative_head_coord == order_list[head_pos]:
                break
        next_head_pos = head_pos+1
        next_head_pos %= len(order_list)
        if relative_neck_coord == order_list[next_head_pos]:
            next_head_pos = head_pos-1
            next_head_pos %= len(order_list)

        #get next_head absolute coordinate
        x2,y2 = order_list[next_head_pos]
        x2 += x0
        y2 += y0

        #save in global var
        game_state["routine_move"] = (x2,y2)

    def pos_on_board(pos: typing.Tuple) -> bool:
        x,y = pos
        if x < 0:
            return False
        if y < 0:
            return False
        if x >= game_state["board"]["width"]:
            return False
        if y >= game_state["board"]["height"]:
            return False
        return True

    def adj_cells(pos: typing.Tuple) -> typing.List:
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
        snakes = game_state["board"]["snakes"]
        sbody = []
        for s in snakes:
            body = get_body_coord(s["body"])
            if s["health"] == 100:
                #eat food, tail will not move in the next step
                body += [body[-1]]
            sbody.append(body[:-step])
        cells = [c for s in sbody for c in s]
        return cells

    def permissible_nstep(head, n):
        paths = [[head]]
        for step in range(1, n+1):
            occupied = occupied_cells(step)
            paths = [ npath 
                     for path in paths 
                     for npath in [path+[p] for p in adj_cells(path[-1]) 
                              if p not in occupied and p not in path] ]
        result = list(set([path[1] for path in paths]))
        return result

    def allowed_move():
        head = get_my_head()
        allowed = permissible_nstep(head, 5)
        allowed_1 = permissible_nstep(head, 1)
        game_state["allowed_move"] = allowed
        game_state["allowed_move_1"] = allowed_1

    def get_body_coord(body) -> typing.List:
        return [(c["x"], c["y"]) for c in body]

    def head_colliding_points(head1: typing.Tuple, head2: typing.Tuple) -> typing.List:
        assert(distance_pq(head1, head2) == 2)

        adj1 = set(adj_cells(head1))
        adj2 = set(adj_cells(head2))
        common = adj1.intersection(adj2)
        return list(common)

    def is_cell_occupied(p: typing.Tuple) -> bool:
        #check not including tail
        for snake in game_state["board"]["snakes"]:
            #including myself
            if p in get_body_coord(snake["body"])[:-1]:
                return True
        return False

    def opposite_dir(d):
        if d == "left": return "right"
        if d == "right": return "left"
        if d == "up": return "down"
        if d == "down": return "up"
    
    def is_perpendicular(d1, d2):
        if d1 == d2:
            return False
        if opposite_dir(d1) == d2:
            return False
        return True

    def dir_to_coord(head: typing.Tuple, d: str) -> typing.Tuple:
        x,y = head
        if d == "left":
            return (x-1, y)
        if d == "right":
            return (x+1, y)
        if d == "up":
            return (x, y+1)
        if d == "down":
            return (x, y-1)
        raise(ValueError("dir_to_coord"))

    def too_far(p1: typing.Tuple, p2: typing.Tuple) -> bool:
        paths = [[p1]]
        for step in range(6):
            occupied = occupied_cells(1)
            paths = [ npath 
                     for path in paths 
                     for npath in [path+[p] for p in adj_cells(path[-1]) 
                              if p not in occupied and p not in path] ]
        return not any([p2 in path for path in paths])

    def colliding_pattern_1(my_body: typing.List, snake_body: typing.List, colliding_point: typing.Tuple):
        #restore this - do not process when colliding point is occupied - for now
        if is_cell_occupied(colliding_point): 
            return

        my_head = my_body[0]
        my_neck = my_body[1]
        snake_head = snake_body[0]
        snake_neck = snake_body[1]

        mdir0 = get_adjacent_dir(my_neck, my_head)
        sdir0 = get_adjacent_dir(snake_neck, snake_head)
        cdir0 = get_adjacent_dir(my_head, colliding_point)

        adirs = ["left", "right", "up", "down"]
        for cdir in adirs:
            mdirs = [d for d in adirs if d != opposite_dir(cdir)]
            sdirs = [d for d in adirs if d != cdir]
            for mdir in mdirs:
                assert(cdir != opposite_dir(mdir))
                for sdir in sdirs:
                    if not (mdir == mdir0 and sdir == sdir0 and cdir == cdir0):
                        continue

                    #we get two dirs
                    pdirs = [d for d in adirs if d not in [cdir, opposite_dir(mdir)]]
                    assert(len(pdirs) == 2)
                    if mdir == cdir and mdir == opposite_dir(sdir):
                        #straight head-to-head, no preference of two dirs
                        suggest = [pdirs]
                    else:
                        #either sdir or opposite exists
                        #prefer opposite the first, sdir the last, the other one in the middle
                        odir = opposite_dir(sdir)
                        assert(sdir in pdirs or odir in pdirs)
                        others = [d for d in pdirs if d not in [sdir, odir]]

                        if len(others) == 0:
                            suggest = [[odir], [sdir]]
                        else:
                            assert(len(others) == 1)
                            other = others[0]
                            if odir in pdirs:
                                suggest = [[odir], [other]]
                            else:
                                suggest = [[other], [sdir]]

                    #save in the global var
                    suggest = [[dir_to_coord(my_head, d) for d in g] for g in suggest]
                    game_state["avoid_danger"].append((snake_head, "pattern1", suggest))

    def colliding_pattern_2(my_body: typing.List, snake_body: typing.List, collinding_points: typing.List):
        if all([is_cell_occupied(p) for p in collinding_points]):
            return

        my_head = my_body[0]
        my_neck = my_body[1]
        adjs = adj_cells(my_head)
        choices = [p for p in adjs if p not in collinding_points+[my_neck]]
        #choices can have 1 or 2 points
        if len(choices) == 0:
            return
        if len(choices) == 1:
            suggest = choices
        else:
            assert(len(choices) == 2)
            #one perpendicular one parallel
            a, b = choices
            if is_perpendicular(get_adjacent_dir(my_head, a), get_adjacent_dir(my_neck, my_head)):
                suggest = [a, b]
            else:
                suggest = [b, a]
        game_state["avoid_danger"].append((snake_body[0], "pattern2", suggest))

    def head_to_head_danger(my_body: typing.List, snake_body: typing.List):
        if len(my_body) > len(snake_body):
            return

        my_head = get_my_head()
        snake_head = snake_body[0]
        colliding_points = head_colliding_points(my_head, snake_head)

        assert(len(colliding_points) in [1,2])

        x0,y0 = my_head
        x1,y1 = snake_head
        if x0 == x1 or y0 == y1:
            #single colliding point
            assert(len(colliding_points) == 1)
            colliding_pattern_1(my_body, snake_body, colliding_points[0])
        else:
            #2 colliding points
            assert(len(colliding_points) == 2)
            colliding_pattern_2(my_body, snake_body, colliding_points)

    def avoid_danger_2():
        game_state["avoid_danger"] = []
        game_state["colliding_pattern_1"] = []

        #check distance == 2
        my_body = get_body_coord(game_state["you"]["body"])
        my_head = my_body[0]
        snake_heads = [get_body_coord(snake["body"])[0] for snake in opponent_snakes()]
        snake_dist = [distance_pq(my_head, head) for head in snake_heads]

        #process distance == 2 danger
        if min(snake_dist, default=0) == 2:
            for snake in opponent_snakes():
                snake_body = get_body_coord(snake["body"])
                snake_head = snake_body[0]
                if distance_pq(my_head, snake_head) == 2:
                    head_to_head_danger(my_body, snake_body)
 
    def danger_rank(move: typing.Tuple, snake_moves: typing.List) -> int:
        #maximum number of distance == 2
        def config_rank(config: typing.List) -> int:
            dist = [distance_pq(move, snake_move) for snake_move in config]
            return len([d for d in dist if d == 2])
        rank = max([config_rank(config) for config in itertools.product(*snake_moves)], default=0)
        return rank

    def avoid_danger_4():
        game_state["avoid_danger_4"] = []

        #check distance == 4
        snakes = [snake for snake in opponent_snakes() if len(snake["body"]) >= game_state["you"]["length"]]
        if len(snakes) == 0:
            return

        my_body = get_body_coord(game_state["you"]["body"])
        my_head = my_body[0]
        snake_heads = [get_body_coord(snake["body"])[0] for snake in snakes]
        snake_dist = [distance_pq(my_head, head) for head in snake_heads]

        #process distance == 4 danger
        if len([d for d in snake_dist if d == 2]) > 0:
            return

        if len([d for d in snake_dist if d == 4]) <= 1:
            return

        #avoid the situation that in the next step it becomes multiple distance == 2
        snake_moves = [permissible_nstep(head, 1) for head in snake_heads if distance_pq(my_head, head) == 4]
        snake_moves = [moves for moves in snake_moves if len(moves) != 0]
        if len(snake_moves) <= 1:
            return

        my_moves = permissible_nstep(my_head, 1)
        my_moves = [(danger_rank(move, snake_moves), move) for move in my_moves]
        my_moves = [(rank, move) for rank, move in my_moves if rank < 2]
        my_moves = sorted(my_moves, key=lambda x: x[0])
        choices = [move for _, move in my_moves]
        #choices can be empty
        #appending an empty list means there is a distance == 4 danger 
        # but no choices to avoid multiple distance == 2 in the next step
        game_state["avoid_danger_4"].append(choices) 

    def danger_in_single_danger_4(p: typing.Tuple, snake_head: typing.Tuple) -> bool:
        step_2_moves = set(adj_cells(p))-set(occupied_cells(2))-set([get_my_head()])
        danger = any([p1 for p1 in permissible_nstep(snake_head, 1)
            if all([is_adjacent(p1, p2) for p2 in step_2_moves]) ])
        return danger

    def avoid_single_danger_4():
        game_state["avoid_single_danger_4"] = []

        #check distance == 4
        snakes = [snake for snake in opponent_snakes() if len(snake["body"]) >= game_state["you"]["length"]]
        if len(snakes) == 0:
            return

        my_body = get_body_coord(game_state["you"]["body"])
        my_head = my_body[0]
        snake_heads = [get_body_coord(snake["body"])[0] for snake in snakes]
        snake_dist = [distance_pq(my_head, head) for head in snake_heads]

        #process distance == 4 danger
        if len([d for d in snake_dist if d == 2]) > 0:
            return

        if len([d for d in snake_dist if d == 4]) != 1:
            return

        snake = [snake for snake in snakes if distance_pq(my_head, get_body_coord(snake["body"])[0]) == 4][0]
        snake_body = get_body_coord(snake["body"])
        if len(snake_body) <= len(my_body):
            return
        
        snake_head = snake_body[0]
        my_moves = permissible_nstep(my_head, 1)
        suggests = [p for p in my_moves if not danger_in_single_danger_4(p, snake_head)]
        if len(suggests) < len(my_moves):
            game_state["avoid_single_danger_4"].append(suggests)

    def avoid_danger():
        #I'll structure this in a better way
        #for now I'll just deal with separate cases

        #avoid_danger_2() deals with distance == 2
        #this is immediate danger
        avoid_danger_2()

        #avoid_danger_4() deals with when there are multiple distance == 4 snakes
        #but no distance == 2 snakes
        #the goal is to avoid multiple distance == 2 in the next step
        avoid_danger_4()

        #avoid_single_danger_4() deals with when there is only one distance == 4 snake
        #but no distance == 2 snakes
        #sometimes when near the border, certain moves can put myself in a distance == 2 danger and no escape direction
        #the goal is to avoid such moves
        avoid_single_danger_4()

    def opponent_snakes() -> typing.List:
        my_head = game_state["you"]["body"][0]
        head = (my_head["x"], my_head["y"])
        snakes = [s for s in game_state["board"]["snakes"]]
        snakes = [s for s in snakes if (s["body"][0]["x"], s["body"][0]["y"]) != head]
        return snakes

    def distance_pq(p: typing.Tuple, q: typing.Tuple) -> int:
        x1,y1 = p
        x2,y2 = q
        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def is_adjacent(p1: typing.Tuple, p2: typing.Tuple) -> bool:
        return distance_pq(p1, p2) == 1

    def get_my_head() -> typing.Tuple:
        my_head = game_state["you"]["body"][0]
        head_coord = (my_head["x"], my_head["y"])
        return head_coord

    def food_path(food: typing.Tuple) -> typing.List:
        x0,y0 = get_my_head()
        x1,y1 = food
        mx = min(x0,x1)
        Mx = max(x0,x1)
        my = min(y0,y1)
        My = max(y0,y1)
        region = [(x,y) for x in range(mx,Mx+1) for y in range(my, My+1)]
        if len(region) != distance_pq(get_my_head(), food)+1:
            #has a rectangular region
            border = [(x,y) for x,y in region if not (mx<x<Mx and my<y<My)]
            line1 = sorted([(x,y) for x,y in border if x==mx])
            line2 = sorted([(x,y) for x,y in border if y==my])
            line3 = sorted([(x,y) for x,y in border if x==Mx])
            line4 = sorted([(x,y) for x,y in border if y==My])

            if x1 > x0 and y1 > y0:
                #upper right
                path1 = line2 + line3[1:]
                path2 = line1 + line4[1:]
            elif x1 < x0 and y1 > y0:
                #upper left
                path1 = line3 + list(reversed(line4[1:]))
                path2 = list(reversed(line2)) + line1[1:]
            elif x1 < x0 and y1 < y0:
                #lower left
                path1 = list(reversed(line4)) + list(reversed(line1[1:]))
                path2 = list(reversed(line3)) + list(reversed(line2[1:]))
            else:
                #if x1 > x0 and y1 < y0:
                #lower right
                path1 = list(reversed(line1)) + line2[1:]
                path2 = line4 + list(reversed(line3[1:]))
            paths = [path1, path2]
        else:
            #straight line to food
            path = sorted(region)
            if x1 < x0 or y1 < y0:
                path = list(reversed(path))
            paths = [path]

        return paths
    
    def good_path(path: typing.List) -> bool:
        for snake in opponent_snakes():
            for cell in snake["body"]:
                x = cell["x"]
                y = cell["y"]
                if (x,y) in path:
                    return False
        for cell in game_state["you"]["body"][1:]:
            x = cell["x"]
            y = cell["y"]
            if (x,y) in path:
                return False
        return True

    def find_food_condition() -> bool:
        snakes = opponent_snakes()
        if len(snakes) >= 2 and game_state["you"]["length"] < 8:
            return True
        if len(snakes) >= 3 and game_state["you"]["health"] < 60:
            return True
        if len(snakes) >= 2 and game_state["you"]["health"] < 40:
            return True
        if len(snakes) >= 0 and game_state["you"]["health"] < 20:
            return True
        return False

    def find_food():

        game_state["find_food"] = []

        #if opponent snake == 1 and health < 20 find food
        snakes = opponent_snakes()
        if find_food_condition():
            snakes = [get_body_coord(s["body"]) for s in snakes]
            snake_heads = [s[0] for s in snakes]
            food_target = [(food["x"], food["y"]) for food in game_state["board"]["food"]]
            food_target = [p 
                           for p in food_target 
                           if all([distance_pq(p, get_my_head()) < distance_pq(p, snake_head) 
                                   for snake_head in snake_heads ])]
            food_target = [(food, [path for path in food_path(food) if good_path(path)]) for food in food_target]
            food_target = [(food, paths) for food, paths in food_target if len(paths) != 0]
            food_target = sorted(food_target, key=lambda f: distance_pq(get_my_head(), f[0]))
            if len(food_target) != 0:
                food, paths = food_target[0]
                my_neck = game_state["you"]["body"][1]
                my_neck = (my_neck["x"], my_neck["y"])
                paths = sorted(paths, key=lambda path: 0 if get_adjacent_dir(path[0], path[1]) == get_adjacent_dir(my_neck, path[0]) else 1)
                path = paths[0]
                next_head_coord = path[1]
                #save in the global var
                game_state["find_food"].append(next_head_coord)

    def too_crowded():
        #when I'm at a corner - not near the center
        #when I'm all contained in 5x5 corner
        #when two or more opponent snakes are entering

        pass

    def off_border(p: typing.Tuple) -> bool:
        x,y = p
        if x == 0 or y == 0:
            return False
        if x == game_state["board"]["width"]-1 or y == game_state["board"]["height"]-1:
            return False
        return True

    def unwrap_suggest(suggest: typing.List, pattern: str) -> typing.List:
        if pattern == "pattern1":
            return [s for g in suggest for s in g]
        if pattern == "pattern2":
            return suggest
        raise(ValueError("unwrap_suggest"))

    def best_choice():

        #lower priority first, higher priority will override lower priority

        #routine move always exists and set as default
        game_state["next_head_coord"] = game_state["routine_move"]

        if len(game_state["allowed_move"]) == 0:
            #most strict allowed move empty
            #immediate allowed move may still have some
            if len(game_state["allowed_move_1"]) != 0:
                #use the first of the allowed move
                game_state["next_head_coord"] = game_state["allowed_move_1"][0]
            return

        #set to the first of the allowed moves, then let other considerations override it

        if game_state["next_head_coord"] not in game_state["allowed_move"]:
            game_state["next_head_coord"] = game_state["allowed_move"][0]

        if len(game_state["find_food"]) != 0:
            if game_state["find_food"][0] in game_state["allowed_move"]:
                game_state["next_head_coord"] = game_state["find_food"][0]

        #do not check off-border anymore
        #instead let attractor boxes move the snake off-border

        if len(game_state["avoid_danger_4"]) != 0:
            #there are distance == 4 danger
            choices = game_state["avoid_danger_4"][0]
            choice = [p for p in choices if p in game_state["allowed_move"]]
            if len(choice) != 0:
                if game_state["next_head_coord"] not in choice:
                    #if the current choice is not in the distance == 4 danger
                    #then use the first of the distance == 4 danger
                    game_state["next_head_coord"] = choice[0]

        if len(game_state["avoid_single_danger_4"]) != 0:
            #there are single distance == 4 danger
            choices = game_state["avoid_single_danger_4"][0]
            choices = [p for p in choices if p in game_state["allowed_move"]]
            if len(choices) != 0:
                if game_state["next_head_coord"] not in choices:
                    game_state["next_head_coord"] = choices[0]

        def sort_collision_choice(p: typing.Tuple) -> typing.Tuple:
            #two considerations:
            #off-border
            #not changing previous choice
            check_off_border = 0 if off_border(p) else 1
            check_change = 0 if p == game_state["next_head_coord"] else 1
            return check_off_border, check_change

        if len(game_state["avoid_danger"]) != 0:

            #consider the first collision and use as the default
            snake_head, pattern, suggest = game_state["avoid_danger"][0]
            if pattern == "pattern1":
                if len(suggest) == 1:
                    #suggest = [[a,b]]
                    assert(len(suggest[0]) == 2)
                    suggest = suggest[0]
                    suggest = [p for p in suggest if p in game_state["allowed_move"]]
                    if len(suggest) == 1:
                        game_state["next_head_coord"] = suggest[0]
                    elif len(suggest) == 2:
                        suggest = sorted(suggest, key=sort_collision_choice)
                        game_state["next_head_coord"] = suggest[0]

                else:
                    #two suggestions
                    #suggest = [[a],[b]]
                    assert(len(suggest) == 2)
                    a,b = suggest
                    a = a[0]
                    b = b[0]
                    if a in game_state["allowed_move"]:
                        game_state["next_head_coord"] = a
                    elif b in game_state["allowed_move"]:
                        game_state["next_head_coord"] = b
            elif pattern == "pattern2":
                suggest = [s for s in suggest if s in game_state["allowed_move"]]
                if len(suggest) != 0:
                    game_state["next_head_coord"] = suggest[0]

            if len(game_state["avoid_danger"]) > 1:
                #multiple collisions
                #at most one common suggestion, take it
                suggestions = [set(unwrap_suggest(suggest, pattern)) for _, pattern, suggest in game_state["avoid_danger"]]
                common = list(set.intersection(*suggestions))
                common = [p for p in common if p in game_state["allowed_move"]]
                if len(common) != 0:
                    game_state["next_head_coord"] = common[0]



    #main

    #ideas
    #next routine path
    #calculated space filling path
    #longer lookahead

    #must satisfy
    allowed_move()

    #priority: avoid danger, find food, routine move
    routine_move()
    avoid_danger()
    find_food()

    best_choice()

    next_move = get_next_move(get_my_head(), game_state["next_head_coord"])

    #logging
    log_move = next_move
    log_head = get_my_head()
    log_health = game_state["you"]["health"]
    log_length = game_state["you"]["length"]
    log_turn = game_state["turn"]
    log_food_count = len(game_state["board"]["food"])
    snakes = opponent_snakes()
    snakes = sorted(snakes, key=lambda s: s["name"])
    log_snake_count = len(snakes)
    log_snake_names = [s["name"] for s in snakes]
    log_snake_heads = [s["body"][0] for s in snakes]
    log_snake_health = [s["health"] for s in snakes]
    log_snake_length = [s["length"] for s in snakes]
    log_boxing_area = game_state["boxing_area"]
    log_game_id = game_state["game"]["id"]
    log_routine_move = game_state["routine_move"]
    log_avoid_danger = game_state["avoid_danger"]
    log_avoid_danger_4 = game_state["avoid_danger_4"]
    log_avoid_single_danger_4 = game_state["avoid_single_danger_4"]
    log_allowed_move = game_state["allowed_move"]
    if len(game_state["colliding_pattern_1"]) != 0:
        log_pattern1 = [f"{s[0]}: {s[1]}" for s in game_state["colliding_pattern_1"]]
        log_pattern1 = f"{log_pattern1}"
        log_pattern1 = "pattern_1_activated: " + log_pattern1
    else:
        log_pattern1 = ""

    def get_coord(list_xy):
        return [(c["x"], c["y"]) for c in list_xy]

    log_food = get_coord(game_state["board"]["food"])
    log_food = f"food: {log_food}"
    log_snakes = [snake for snake in game_state["board"]["snakes"] ]
    log_snakes = [{
        "name": snake["name"],
        "id": snake["id"],
        "health": snake["health"],
        "body": get_coord(snake["body"]),
        }
        for snake in log_snakes]
    log_snakes = f"snakes: {log_snakes}"

    log_text = ", ".join([
        f"game_id: {log_game_id}",
        f"move: {log_move}",
        f"turn: {log_turn}",
        f"health: {log_health}",
        f"head: {log_head}",
        f"scount: {log_snake_count}",
        f"snake names: {log_snake_names}",
        f"boxing_area: {log_boxing_area}",
        f"routine_move: {log_routine_move}",
        f"avoid_danger: {log_avoid_danger}",
        f"avoid_danger_4: {log_avoid_danger_4}",
        f"avoid_single_danger_4: {log_avoid_single_danger_4}",
        f"allowed_move: {log_allowed_move}",
        log_food,
        log_snakes,
    ])

    print(log_text)

    return {"move": next_move}



# this gives me #47 score 7840 on 5/22/2025
def move9(game_state: typing.Dict) -> typing.Dict:
    """
    move in a square area
    following an area filling path
    the area has a dimension of n x m
    where n is an even number
    so that the path can close
    start with 4x3
    then 4x4, 4x5, 4x6
    then 6x5, 6x6, 6x7, 6x8
    then 8x7, ...
    """

    """
    Then avoid immediate danger
    check opponents and self
    """


    def valid_area(area: typing.Tuple) -> bool:
        ((x1,y1), (x2,y2)) = area
        if not 0 <= x2 < game_state["board"]["width"]:
            return False
        if not 0 <= y2 < game_state["board"]["height"]:
            return False
        return True

    def body_in_box(area: typing.Tuple, body: typing.List) -> bool:
        ((x1,y1), (x2,y2)) = area
        for cell in body:
            x = cell["x"]
            y = cell["y"]
            if not x1 <= x <= x2:
                return False
            if not y1 <= y <= y2:
                return False
        return True
    
    def find_containing_boxes(body: typing.List) -> typing.List:
        boxes = []
        width, height = box_dim()
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+width-1
                y2 = y1+height-1
                box = ((x1,y1), (x2,y2))
                if not valid_area(box):
                    continue
                if body_in_box(box, body):
                    boxes.append(box)
        return boxes

    def all_moving_boxes() -> typing.List:
        body = game_state["you"]["body"]

        #only check first 3
        body = body[:3]

        boxes = []
        width, height = box_dim()
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+width-1
                y2 = y1+height-1
                box = ((x1,y1), (x2,y2))
                if not valid_area(box):
                    continue
                if body_in_box(box, body):
                    boxes.append(box)

        assert(len(boxes) != 0)
        return boxes

    def space_filling_path(width, height):
        assert(width % 2 == 0)
        base = [(x, 0) for x in range(width)]
        vert_lines = [[(x, y) for y in range(1, height)] for x in range(width)]
        vert_lines = [line if index % 2 != 0 else list(reversed(line)) for index, line in enumerate(vert_lines)]
        vert_lines = list(reversed(vert_lines))
        path = base + [p for line in vert_lines for p in line]
        return path

    def box_dim() -> typing.Tuple:
        nsnakes = len(game_state["board"]["snakes"])
        length = game_state["you"]["length"]
        if nsnakes >= 4:
            #return (4,3)
            return (4,4)
        if nsnakes == 3:
            #return (4,4)
            return (4,5)
        if nsnakes <= 2:
            #if length <= 15: return (4,5)
            #if length <= 20: return (4,7)
            return (4,9)
        raise(ValueError("area_dim"))

    def attractor_boxes() -> typing.List:
        adim = box_dim()
        if adim == (4,3):
            return [
                ((1,2), (4,4)),
                ((1,6), (4,8)),
                ((6,2), (9,4)),
                ((6,6), (9,8)),
            ]
        if adim == (4,4):
            return [
                ((1,1), (4,4)),
                ((1,6), (4,9)),
                ((6,1), (9,4)),
                ((6,6), (9,9)),
            ]
        if adim == (4,5):
            return [
                ((1,0), (4,4)),
                ((1,6), (4,10)),
                ((6,0), (9,4)),
                ((6,6), (9,10)),
            ]
        if adim == (4,7):
            return [
                ((1,2), (4,8)),
                ((6,2), (9,8)),
            ]
        if adim == (4,9):
            return [
                ((1,1), (4,9)),
                ((6,1), (9,9)),
            ]

        raise(ValueError("BOX DIMENSION"))

    def target_bounding_box() -> typing.Tuple:
        #also only check first 4
        body = game_state["you"]["body"][:3]
        body_center_x = sum([cell["x"] for cell in body]) / len(body)
        body_center_y = sum([cell["y"] for cell in body]) / len(body)
        boxes = attractor_boxes()

        def sort_corner(corner: typing.Tuple):
            ((x1,y1), (x2,y2)) = corner
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            return math.sqrt((xc-body_center_x)**2+(yc-body_center_y)**2)

        boxes = sorted(boxes, key=sort_corner)
        return boxes[0]

    def get_bounding_box() -> typing.Tuple:
        """
        get a rectangular area depend on the snake initial position
        so that even when the snake moves, the area doesn't change
        """

        #prefer the attactor boxes
        for box in attractor_boxes():

            #experiment first 3
            body = game_state["you"]["body"][:3]

            if body_in_box(box, body):
                return box

        #if not in one of attractor boxes, find one close to it,
        #so that the area will move to the closest attractor box

        target = target_bounding_box()

        #find boxes that contain my snake body or the first n of it
        boxes = all_moving_boxes()

        def sort_box(box: typing.Tuple):
            ((x1,y1), (x2,y2)) = box
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            ((target_x1, target_y1), (target_x2, target_y2)) = target
            target_xc = (target_x1+target_x2)/2
            target_yc = (target_y1+target_y2)/2
            return math.sqrt((xc-target_xc)**2+(yc-target_yc)**2)

        boxes = sorted(boxes, key=sort_box)
        box = boxes[0]
        return box

    def get_adjacent_dir(p: typing.Tuple, q: typing.Tuple) -> str:
        assert(is_adjacent(p, q))
        x,y = p
        nx,ny = q
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        return get_adjacent_dir(head_coord, next_head_coord)

    #1. determine the area dimension corners
    # determine my position dirs
    def routine_move():
        area = get_bounding_box()
        game_state["boxing_area"] = area

        order_list = space_filling_path(*box_dim())

        bottom_left_corner = area[0]
        x0,y0 = bottom_left_corner
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        head_coord = (my_head["x"], my_head["y"])
        neck_coord = (my_neck["x"], my_neck["y"])
        relative_head_coord = (head_coord[0]-x0, head_coord[1]-y0)
        relative_neck_coord = (neck_coord[0]-x0, neck_coord[1]-y0)
        head_pos = 0
        for head_pos in range(len(order_list)):
            if relative_head_coord == order_list[head_pos]:
                break
        next_head_pos = head_pos+1
        next_head_pos %= len(order_list)
        if relative_neck_coord == order_list[next_head_pos]:
            next_head_pos = head_pos-1
            next_head_pos %= len(order_list)

        #get next_head absolute coordinate
        x2,y2 = order_list[next_head_pos]
        x2 += x0
        y2 += y0

        #save in global var
        game_state["routine_move"] = (x2,y2)

    def pos_on_board(pos: typing.Tuple) -> bool:
        x,y = pos
        if x < 0:
            return False
        if y < 0:
            return False
        if x >= game_state["board"]["width"]:
            return False
        if y >= game_state["board"]["height"]:
            return False
        return True

    def adj_cells(pos: typing.Tuple) -> typing.List:
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
        snakes = game_state["board"]["snakes"]
        sbody = []
        for s in snakes:
            body = get_body_coord(s["body"])
            if s["health"] == 100:
                #eat food, tail will not move in the next step
                body += [body[-1]]
            sbody.append(body[:-step])
        cells = [c for s in sbody for c in s]
        return cells

    def permissible_nstep(head, n):
        paths = [[head]]
        for step in range(1, n+1):
            occupied = occupied_cells(step)
            paths = [ npath 
                     for path in paths 
                     for npath in [path+[p] for p in adj_cells(path[-1]) 
                              if p not in occupied and p not in path] ]
        result = list(set([path[1] for path in paths]))
        return result

    def allowed_move():
        head = get_my_head()
        allowed = permissible_nstep(head, 5)
        allowed_1 = permissible_nstep(head, 1)
        game_state["allowed_move"] = allowed
        game_state["allowed_move_1"] = allowed_1

    def get_body_coord(body) -> typing.List:
        return [(c["x"], c["y"]) for c in body]

    def head_colliding_points(head1: typing.Tuple, head2: typing.Tuple) -> typing.List:
        assert(distance_pq(head1, head2) == 2)

        adj1 = set(adj_cells(head1))
        adj2 = set(adj_cells(head2))
        common = adj1.intersection(adj2)
        return list(common)

    def is_cell_occupied(p: typing.Tuple) -> bool:
        #check not including tail
        for snake in game_state["board"]["snakes"]:
            #including myself
            if p in get_body_coord(snake["body"])[:-1]:
                return True
        return False

    def opposite_dir(d):
        if d == "left": return "right"
        if d == "right": return "left"
        if d == "up": return "down"
        if d == "down": return "up"
    
    def is_perpendicular(d1, d2):
        if d1 == d2:
            return False
        if opposite_dir(d1) == d2:
            return False
        return True

    def dir_to_coord(head: typing.Tuple, d: str) -> typing.Tuple:
        x,y = head
        if d == "left":
            return (x-1, y)
        if d == "right":
            return (x+1, y)
        if d == "up":
            return (x, y+1)
        if d == "down":
            return (x, y-1)
        raise(ValueError("dir_to_coord"))

    def colliding_pattern_1(my_body: typing.List, snake_body: typing.List, colliding_point: typing.Tuple):
        if is_cell_occupied(colliding_point):
            return

        my_head = my_body[0]
        my_neck = my_body[1]
        snake_head = snake_body[0]
        snake_neck = snake_body[1]

        mdir0 = get_adjacent_dir(my_neck, my_head)
        sdir0 = get_adjacent_dir(snake_neck, snake_head)
        cdir0 = get_adjacent_dir(my_head, colliding_point)

        adirs = ["left", "right", "up", "down"]
        for cdir in adirs:
            mdirs = [d for d in adirs if d != opposite_dir(cdir)]
            sdirs = [d for d in adirs if d != cdir]
            for mdir in mdirs:
                assert(cdir != opposite_dir(mdir))
                for sdir in sdirs:
                    if not (mdir == mdir0 and sdir == sdir0 and cdir == cdir0):
                        continue

                    #we get two dirs
                    pdirs = [d for d in adirs if d not in [cdir, opposite_dir(mdir)]]
                    assert(len(pdirs) == 2)
                    if mdir == cdir and mdir == opposite_dir(sdir):
                        #straight head-to-head, no preference of two dirs
                        suggest = [pdirs]
                    else:
                        #either sdir or opposite exists
                        #prefer opposite the first, sdir the last, the other one in the middle
                        odir = opposite_dir(sdir)
                        assert(sdir in pdirs or odir in pdirs)
                        others = [d for d in pdirs if d not in [sdir, odir]]

                        if len(others) == 0:
                            suggest = [[odir], [sdir]]
                        else:
                            assert(len(others) == 1)
                            other = others[0]
                            if odir in pdirs:
                                suggest = [[odir], [other]]
                            else:
                                suggest = [[other], [sdir]]

                    #save in the global var
                    suggest = [[dir_to_coord(my_head, d) for d in g] for g in suggest]
                    game_state["avoid_danger"].append((snake_head, "pattern1", suggest))

    def colliding_pattern_2(my_body: typing.List, snake_body: typing.List, collinding_points: typing.List):
        if all([is_cell_occupied(p) for p in collinding_points]):
            return

        my_head = my_body[0]
        my_neck = my_body[1]
        adjs = adj_cells(my_head)
        choices = [p for p in adjs if p not in collinding_points+[my_neck]]
        #choices can have 1 or 2 points
        if len(choices) == 0:
            return
        if len(choices) == 1:
            suggest = choices
        else:
            assert(len(choices) == 2)
            #one perpendicular one parallel
            a, b = choices
            if is_perpendicular(get_adjacent_dir(my_head, a), get_adjacent_dir(my_neck, my_head)):
                suggest = [a, b]
            else:
                suggest = [b, a]
        game_state["avoid_danger"].append((snake_body[0], "pattern2", suggest))

    def head_to_head_danger(my_body: typing.List, snake_body: typing.List):
        if len(my_body) > len(snake_body):
            return

        my_head = get_my_head()
        snake_head = snake_body[0]
        colliding_points = head_colliding_points(my_head, snake_head)

        assert(len(colliding_points) in [1,2])

        x0,y0 = my_head
        x1,y1 = snake_head
        if x0 == x1 or y0 == y1:
            #single colliding point
            assert(len(colliding_points) == 1)
            colliding_pattern_1(my_body, snake_body, colliding_points[0])
        else:
            #2 colliding points
            assert(len(colliding_points) == 2)
            colliding_pattern_2(my_body, snake_body, colliding_points)

    def avoid_danger_2():
        game_state["avoid_danger"] = []

        #check distance == 2
        my_body = get_body_coord(game_state["you"]["body"])
        my_head = my_body[0]
        snake_heads = [get_body_coord(snake["body"])[0] for snake in opponent_snakes()]
        snake_dist = [distance_pq(my_head, head) for head in snake_heads]

        #process distance == 2 danger
        if min(snake_dist, default=0) == 2:
            for snake in opponent_snakes():
                snake_body = get_body_coord(snake["body"])
                snake_head = snake_body[0]
                if distance_pq(my_head, snake_head) == 2:
                    head_to_head_danger(my_body, snake_body)
 
    def danger_rank(move: typing.Tuple, snake_moves: typing.List) -> int:
        #maximum number of distance == 2
        def config_rank(config: typing.List) -> int:
            dist = [distance_pq(move, snake_move) for snake_move in config]
            return len([d for d in dist if d == 2])
        rank = max([config_rank(config) for config in itertools.product(*snake_moves)], default=0)
        return rank

    def avoid_danger_4():
        game_state["avoid_danger_4"] = []

        #check distance == 4
        snakes = [snake for snake in opponent_snakes() if len(snake["body"]) >= game_state["you"]["length"]]
        if len(snakes) == 0:
            return

        my_body = get_body_coord(game_state["you"]["body"])
        my_head = my_body[0]
        snake_heads = [get_body_coord(snake["body"])[0] for snake in snakes]
        snake_dist = [distance_pq(my_head, head) for head in snake_heads]

        #process distance == 4 danger
        if len([d for d in snake_dist if d == 2]) > 0:
            return

        if len([d for d in snake_dist if d == 4]) <= 1:
            return

        #avoid the situation that in the next step it becomes multiple distance == 2
        snake_moves = [permissible_nstep(head, 1) for head in snake_heads if distance_pq(my_head, head) == 4]
        snake_moves = [moves for moves in snake_moves if len(moves) != 0]
        if len(snake_moves) <= 1:
            return

        my_moves = permissible_nstep(my_head, 1)
        my_moves = [(danger_rank(move, snake_moves), move) for move in my_moves]
        my_moves = [(rank, move) for rank, move in my_moves if rank < 2]
        my_moves = sorted(my_moves, key=lambda x: x[0])
        choices = [move for _, move in my_moves]
        #choices can be empty
        #appending an empty list means there is a distance == 4 danger 
        # but no choices to avoid multiple distance == 2 in the next step
        game_state["avoid_danger_4"].append(choices) 

    def avoid_danger():
        avoid_danger_2()
        avoid_danger_4()

    def opponent_snakes() -> typing.List:
        my_head = game_state["you"]["body"][0]
        head = (my_head["x"], my_head["y"])
        snakes = [s for s in game_state["board"]["snakes"]]
        snakes = [s for s in snakes if (s["body"][0]["x"], s["body"][0]["y"]) != head]
        return snakes

    def distance_pq(p: typing.Tuple, q: typing.Tuple) -> int:
        x1,y1 = p
        x2,y2 = q
        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def is_adjacent(p1: typing.Tuple, p2: typing.Tuple) -> bool:
        return distance_pq(p1, p2) == 1

    def get_my_head() -> typing.Tuple:
        my_head = game_state["you"]["body"][0]
        head_coord = (my_head["x"], my_head["y"])
        return head_coord

    def food_path(food: typing.Tuple) -> typing.List:
        x0,y0 = get_my_head()
        x1,y1 = food
        mx = min(x0,x1)
        Mx = max(x0,x1)
        my = min(y0,y1)
        My = max(y0,y1)
        region = [(x,y) for x in range(mx,Mx+1) for y in range(my, My+1)]
        if len(region) != distance_pq(get_my_head(), food)+1:
            #has a rectangular region
            border = [(x,y) for x,y in region if not (mx<x<Mx and my<y<My)]
            line1 = sorted([(x,y) for x,y in border if x==mx])
            line2 = sorted([(x,y) for x,y in border if y==my])
            line3 = sorted([(x,y) for x,y in border if x==Mx])
            line4 = sorted([(x,y) for x,y in border if y==My])

            if x1 > x0 and y1 > y0:
                #upper right
                path1 = line2 + line3[1:]
                path2 = line1 + line4[1:]
            elif x1 < x0 and y1 > y0:
                #upper left
                path1 = line3 + list(reversed(line4[1:]))
                path2 = list(reversed(line2)) + line1[1:]
            elif x1 < x0 and y1 < y0:
                #lower left
                path1 = list(reversed(line4)) + list(reversed(line1[1:]))
                path2 = list(reversed(line3)) + list(reversed(line2[1:]))
            else:
                #if x1 > x0 and y1 < y0:
                #lower right
                path1 = list(reversed(line1)) + line2[1:]
                path2 = line4 + list(reversed(line3[1:]))
            paths = [path1, path2]
        else:
            #straight line to food
            path = sorted(region)
            if x1 < x0 or y1 < y0:
                path = list(reversed(path))
            paths = [path]

        return paths
    
    def good_path(path: typing.List) -> bool:
        for snake in opponent_snakes():
            for cell in snake["body"]:
                x = cell["x"]
                y = cell["y"]
                if (x,y) in path:
                    return False
        for cell in game_state["you"]["body"][1:]:
            x = cell["x"]
            y = cell["y"]
            if (x,y) in path:
                return False
        return True

    def find_food_condition() -> bool:
        snakes = opponent_snakes()
        if len(snakes) >= 2 and game_state["you"]["length"] < 8:
            return True
        if len(snakes) >= 3 and game_state["you"]["health"] < 60:
            return True
        if len(snakes) >= 2 and game_state["you"]["health"] < 40:
            return True
        if len(snakes) >= 0 and game_state["you"]["health"] < 20:
            return True
        return False

    def find_food():

        game_state["find_food"] = []

        #if opponent snake == 1 and health < 20 find food
        snakes = opponent_snakes()
        if find_food_condition():
            snakes = [get_body_coord(s["body"]) for s in snakes]
            snake_heads = [s[0] for s in snakes]
            food_target = [(food["x"], food["y"]) for food in game_state["board"]["food"]]
            food_target = [p 
                           for p in food_target 
                           if all([distance_pq(p, get_my_head()) < distance_pq(p, snake_head) 
                                   for snake_head in snake_heads ])]
            food_target = [(food, [path for path in food_path(food) if good_path(path)]) for food in food_target]
            food_target = [(food, paths) for food, paths in food_target if len(paths) != 0]
            food_target = sorted(food_target, key=lambda f: distance_pq(get_my_head(), f[0]))
            if len(food_target) != 0:
                food, paths = food_target[0]
                my_neck = game_state["you"]["body"][1]
                my_neck = (my_neck["x"], my_neck["y"])
                paths = sorted(paths, key=lambda path: 0 if get_adjacent_dir(path[0], path[1]) == get_adjacent_dir(my_neck, path[0]) else 1)
                path = paths[0]
                next_head_coord = path[1]
                #save in the global var
                game_state["find_food"].append(next_head_coord)

    def too_crowded():
        #when I'm at a corner - not near the center
        #when I'm all contained in 5x5 corner
        #when two or more opponent snakes are entering

        pass

    def off_border(p: typing.Tuple) -> bool:
        x,y = p
        if x == 0 or y == 0:
            return False
        if x == game_state["board"]["width"]-1 or y == game_state["board"]["height"]-1:
            return False
        return True

    def unwrap_suggest(suggest: typing.List, pattern: str) -> typing.List:
        if pattern == "pattern1":
            return [s for g in suggest for s in g]
        if pattern == "pattern2":
            return suggest
        raise(ValueError("unwrap_suggest"))

    def best_choice():

        #lower priority first, higher priority will override lower priority

        #routine move always exists and set as default
        game_state["next_head_coord"] = game_state["routine_move"]

        if len(game_state["allowed_move"]) == 0:
            #most strict allowed move empty
            #immediate allowed move may still have some
            if len(game_state["allowed_move_1"]) != 0:
                #use the first of the allowed move
                game_state["next_head_coord"] = game_state["allowed_move_1"][0]
            return

        #set to the first of the allowed moves, then let other considerations override it

        if game_state["next_head_coord"] not in game_state["allowed_move"]:
            game_state["next_head_coord"] = game_state["allowed_move"][0]

        if len(game_state["find_food"]) != 0:
            if game_state["find_food"][0] in game_state["allowed_move"]:
                game_state["next_head_coord"] = game_state["find_food"][0]

        #do not check off-border anymore
        #instead let attractor boxes move the snake off-border

        if len(game_state["avoid_danger_4"]) != 0:
            #there are distance == 4 danger
            choices = game_state["avoid_danger_4"][0]
            choice = [p for p in choices if p in game_state["allowed_move"]]
            if len(choice) != 0:
                if game_state["next_head_coord"] not in choice:
                    #if the current choice is not in the distance == 4 danger
                    #then use the first of the distance == 4 danger
                    game_state["next_head_coord"] = choice[0]

        def sort_collision_choice(p: typing.Tuple) -> typing.Tuple:
            #two considerations:
            #off-border
            #not changing previous choice
            check_off_border = 0 if off_border(p) else 1
            check_change = 0 if p == game_state["next_head_coord"] else 1
            return check_off_border, check_change

        if len(game_state["avoid_danger"]) != 0:

            #consider the first collision and use as the default
            snake_head, pattern, suggest = game_state["avoid_danger"][0]
            if pattern == "pattern1":
                if len(suggest) == 1:
                    #suggest = [[a,b]]
                    assert(len(suggest[0]) == 2)
                    suggest = suggest[0]
                    suggest = [p for p in suggest if p in game_state["allowed_move"]]
                    if len(suggest) == 1:
                        game_state["next_head_coord"] = suggest[0]
                    elif len(suggest) == 2:
                        suggest = sorted(suggest, key=sort_collision_choice)
                        game_state["next_head_coord"] = suggest[0]

                else:
                    #two suggestions
                    #suggest = [[a],[b]]
                    assert(len(suggest) == 2)
                    a,b = suggest
                    a = a[0]
                    b = b[0]
                    if a in game_state["allowed_move"]:
                        game_state["next_head_coord"] = a
                    elif b in game_state["allowed_move"]:
                        game_state["next_head_coord"] = b
            elif pattern == "pattern2":
                suggest = [s for s in suggest if s in game_state["allowed_move"]]
                if len(suggest) != 0:
                    game_state["next_head_coord"] = suggest[0]

            if len(game_state["avoid_danger"]) > 1:
                #multiple collisions
                #at most one common suggestion, take it
                suggestions = [set(unwrap_suggest(suggest, pattern)) for _, pattern, suggest in game_state["avoid_danger"]]
                common = list(set.intersection(*suggestions))
                common = [p for p in common if p in game_state["allowed_move"]]
                if len(common) != 0:
                    game_state["next_head_coord"] = common[0]



    #main

    #ideas
    #next routine path
    #calculated space filling path
    #longer lookahead

    #must satisfy
    allowed_move()

    #priority: avoid danger, find food, routine move
    routine_move()
    avoid_danger()
    find_food()

    best_choice()

    next_move = get_next_move(get_my_head(), game_state["next_head_coord"])

    #logging
    log_move = next_move
    log_head = get_my_head()
    log_health = game_state["you"]["health"]
    log_length = game_state["you"]["length"]
    log_turn = game_state["turn"]
    log_food_count = len(game_state["board"]["food"])
    snakes = opponent_snakes()
    snakes = sorted(snakes, key=lambda s: s["name"])
    log_snake_count = len(snakes)
    log_snake_names = [s["name"] for s in snakes]
    log_snake_heads = [s["body"][0] for s in snakes]
    log_snake_health = [s["health"] for s in snakes]
    log_snake_length = [s["length"] for s in snakes]
    log_boxing_area = game_state["boxing_area"]
    log_game_id = game_state["game"]["id"]
    log_routine_move = game_state["routine_move"]
    log_avoid_danger = game_state["avoid_danger"]
    log_avoid_danger_4 = game_state["avoid_danger_4"]
    log_allowed_move = game_state["allowed_move"]

    log_text = ", ".join([
        f"game_id: {log_game_id}",
        f"move: {log_move}",
        f"turn: {log_turn}",
        f"health: {log_health}",
        f"head: {log_head}",
        f"scount: {log_snake_count}",
        f"boxing_area: {log_boxing_area}",
        f"routine_move: {log_routine_move}",
        f"avoid_danger: {log_avoid_danger}",
        f"avoid_danger_4: {log_avoid_danger_4}",
        f"allowed_move: {log_allowed_move}",
    ])
    print(log_text)

    return {"move": next_move}



# this is a good place to backup
# it encorages growth in the beginning
# it check distance 4 danger
def move8(game_state: typing.Dict) -> typing.Dict:
    """
    move in a square area
    following an area filling path
    the area has a dimension of n x m
    where n is an even number
    so that the path can close
    start with 4x3
    then 4x4, 4x5, 4x6
    then 6x5, 6x6, 6x7, 6x8
    then 8x7, ...
    """

    """
    Then avoid immediate danger
    check opponents and self
    """


    def valid_area(area: typing.Tuple) -> bool:
        ((x1,y1), (x2,y2)) = area
        if not 0 <= x2 < game_state["board"]["width"]:
            return False
        if not 0 <= y2 < game_state["board"]["height"]:
            return False
        return True

    def body_in_box(area: typing.Tuple, body: typing.List) -> bool:
        ((x1,y1), (x2,y2)) = area
        for cell in body:
            x = cell["x"]
            y = cell["y"]
            if not x1 <= x <= x2:
                return False
            if not y1 <= y <= y2:
                return False
        return True
    
    def find_containing_boxes(body: typing.List) -> typing.List:
        boxes = []
        width, height = area_dim()
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+width-1
                y2 = y1+height-1
                box = ((x1,y1), (x2,y2))
                if not valid_area(box):
                    continue
                if body_in_box(box, body):
                    boxes.append(box)
        return boxes

    def all_moving_boxes() -> typing.List:
        body = game_state["you"]["body"]

        #only check first 3
        body = body[:3]

        boxes = []
        width, height = area_dim()
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+width-1
                y2 = y1+height-1
                box = ((x1,y1), (x2,y2))
                if not valid_area(box):
                    continue
                if body_in_box(box, body):
                    boxes.append(box)

        assert(len(boxes) != 0)
        return boxes

    def space_filling_path(width, height):
        assert(width % 2 == 0)
        base = [(x, 0) for x in range(width)]
        vert_lines = [[(x, y) for y in range(1, height)] for x in range(width)]
        vert_lines = [line if index % 2 != 0 else list(reversed(line)) for index, line in enumerate(vert_lines)]
        vert_lines = list(reversed(vert_lines))
        path = base + [p for line in vert_lines for p in line]
        return path

    def area_dim() -> typing.Tuple:
        nsnakes = len(game_state["board"]["snakes"])
        length = game_state["you"]["length"]
        if nsnakes >= 4:
            return (4,3)
        if nsnakes == 3:
            return (4,4)
        if nsnakes <= 2:
            if length <= 15:
                return (4,5)
            if length <= 20:
                return (4,7)
            return (4,9)
        raise(ValueError("area_dim"))

    def attractor_boxes() -> typing.List:
        adim = area_dim()
        if adim == (4,3):
            return [
                ((1,2), (4,4)),
                ((1,6), (4,8)),
                ((6,2), (9,4)),
                ((6,6), (9,8)),
            ]
        if adim == (4,4):
            return [
                ((1,1), (4,4)),
                ((1,6), (4,9)),
                ((6,1), (9,4)),
                ((6,6), (9,9)),
            ]
        if adim == (4,5):
            return [
                ((1,0), (4,4)),
                ((1,6), (4,10)),
                ((6,0), (9,4)),
                ((6,6), (9,10)),
            ]
        if adim == (4,7):
            return [
                ((1,2), (4,8)),
                ((6,2), (9,8)),
            ]
        if adim == (4,9):
            return [
                ((1,1), (4,9)),
                ((6,1), (9,1)),
            ]

        raise(ValueError("BOX DIMENSION"))

    def target_bounding_box() -> typing.Tuple:
        #also only check first 4
        body = game_state["you"]["body"][:3]
        body_center_x = sum([cell["x"] for cell in body]) / len(body)
        body_center_y = sum([cell["y"] for cell in body]) / len(body)
        boxes = attractor_boxes()

        def sort_corner(corner: typing.Tuple):
            ((x1,y1), (x2,y2)) = corner
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            return math.sqrt((xc-body_center_x)**2+(yc-body_center_y)**2)

        boxes = sorted(boxes, key=sort_corner)
        return boxes[0]

    def get_bounding_box() -> typing.Tuple:
        """
        get a rectangular area depend on the snake initial position
        so that even when the snake moves, the area doesn't change
        """

        #prefer the attactor boxes
        for box in attractor_boxes():

            #experiment first 3
            body = game_state["you"]["body"][:3]

            if body_in_box(box, body):
                return box

        #if not in one of attractor boxes, find one close to it,
        #so that the area will move to the closest attractor box

        target = target_bounding_box()

        #find boxes that contain my snake body or the first n of it
        boxes = all_moving_boxes()

        def sort_box(box: typing.Tuple):
            ((x1,y1), (x2,y2)) = box
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            ((target_x1, target_y1), (target_x2, target_y2)) = target
            target_xc = (target_x1+target_x2)/2
            target_yc = (target_y1+target_y2)/2
            return math.sqrt((xc-target_xc)**2+(yc-target_yc)**2)

        boxes = sorted(boxes, key=sort_box)
        box = boxes[0]
        return box

    def get_adjacent_dir(p: typing.Tuple, q: typing.Tuple) -> str:
        assert(is_adjacent(p, q))
        x,y = p
        nx,ny = q
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        return get_adjacent_dir(head_coord, next_head_coord)

    #1. determine the area dimension corners
    # determine my position dirs
    def routine_move():
        area = get_bounding_box()
        game_state["boxing_area"] = area

        order_list = space_filling_path(*area_dim())

        bottom_left_corner = area[0]
        x0,y0 = bottom_left_corner
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        head_coord = (my_head["x"], my_head["y"])
        neck_coord = (my_neck["x"], my_neck["y"])
        relative_head_coord = (head_coord[0]-x0, head_coord[1]-y0)
        relative_neck_coord = (neck_coord[0]-x0, neck_coord[1]-y0)
        head_pos = 0
        for head_pos in range(len(order_list)):
            if relative_head_coord == order_list[head_pos]:
                break
        next_head_pos = head_pos+1
        next_head_pos %= len(order_list)
        if relative_neck_coord == order_list[next_head_pos]:
            next_head_pos = head_pos-1
            next_head_pos %= len(order_list)

        #get next_head absolute coordinate
        x2,y2 = order_list[next_head_pos]
        x2 += x0
        y2 += y0

        #save in global var
        game_state["routine_move"] = (x2,y2)

    def pos_on_board(pos: typing.Tuple) -> bool:
        x,y = pos
        if x < 0:
            return False
        if y < 0:
            return False
        if x >= game_state["board"]["width"]:
            return False
        if y >= game_state["board"]["height"]:
            return False
        return True

    def adj_cells(pos: typing.Tuple) -> typing.List:
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
        snakes = game_state["board"]["snakes"]
        sbody = []
        for s in snakes:
            body = get_body_coord(s["body"])
            if s["health"] == 100:
                #eat food, tail will not move in the next step
                body += [body[-1]]
            sbody.append(body[:-step])
        cells = [c for s in sbody for c in s]
        return cells

    def permissible_nstep(head, n):
        paths = [[head]]
        for step in range(1, n+1):
            occupied = occupied_cells(step)
            paths = [ npath 
                     for path in paths 
                     for npath in [path+[p] for p in adj_cells(path[-1]) 
                              if p not in occupied and p not in path] ]
        result = list(set([path[1] for path in paths]))
        return result

    def allowed_move():
        #head = get_my_head()
        #allowed = permissible_first_step(head)
        #allowed = [p for p in allowed if len(permissible_second_step(p)) != 0]
        allowed = permissible_nstep(get_my_head(), 5)
        game_state["allowed_move"] = allowed

    def get_body_coord(body) -> typing.List:
        return [(c["x"], c["y"]) for c in body]

    def head_colliding_points(head1: typing.Tuple, head2: typing.Tuple) -> typing.List:
        assert(distance_pq(head1, head2) == 2)

        adj1 = set(adj_cells(head1))
        adj2 = set(adj_cells(head2))
        common = adj1.intersection(adj2)
        return list(common)

    def is_cell_occupied(p: typing.Tuple) -> bool:
        #check not including tail
        for snake in game_state["board"]["snakes"]:
            #including myself
            if p in get_body_coord(snake["body"])[:-1]:
                return True
        return False

    def opposite_dir(d):
        if d == "left": return "right"
        if d == "right": return "left"
        if d == "up": return "down"
        if d == "down": return "up"
    
    def is_perpendicular(d1, d2):
        if d1 == d2:
            return False
        if opposite_dir(d1) == d2:
            return False
        return True

    def dir_to_coord(head: typing.Tuple, d: str) -> typing.Tuple:
        x,y = head
        if d == "left":
            return (x-1, y)
        if d == "right":
            return (x+1, y)
        if d == "up":
            return (x, y+1)
        if d == "down":
            return (x, y-1)
        raise(ValueError("dir_to_coord"))

    def colliding_pattern_1(my_body: typing.List, snake_body: typing.List, colliding_point: typing.Tuple):
        if is_cell_occupied(colliding_point):
            return

        my_head = my_body[0]
        my_neck = my_body[1]
        snake_head = snake_body[0]
        snake_neck = snake_body[1]

        mdir0 = get_adjacent_dir(my_neck, my_head)
        sdir0 = get_adjacent_dir(snake_neck, snake_head)
        cdir0 = get_adjacent_dir(my_head, colliding_point)

        adirs = ["left", "right", "up", "down"]
        for cdir in adirs:
            mdirs = [d for d in adirs if d != opposite_dir(cdir)]
            sdirs = [d for d in adirs if d != cdir]
            for mdir in mdirs:
                assert(cdir != opposite_dir(mdir))
                for sdir in sdirs:
                    if not (mdir == mdir0 and sdir == sdir0 and cdir == cdir0):
                        continue

                    #we get two dirs
                    pdirs = [d for d in adirs if d not in [cdir, opposite_dir(mdir)]]
                    assert(len(pdirs) == 2)
                    if mdir == cdir and mdir == opposite_dir(sdir):
                        #straight head-to-head, no preference of two dirs
                        suggest = [pdirs]
                    else:
                        #either sdir or opposite exists
                        #prefer opposite the first, sdir the last, the other one in the middle
                        odir = opposite_dir(sdir)
                        assert(sdir in pdirs or odir in pdirs)
                        others = [d for d in pdirs if d not in [sdir, odir]]

                        if len(others) == 0:
                            suggest = [[odir], [sdir]]
                        else:
                            assert(len(others) == 1)
                            other = others[0]
                            if odir in pdirs:
                                suggest = [[odir], [other]]
                            else:
                                suggest = [[other], [sdir]]

                    #save in the global var
                    suggest = [[dir_to_coord(my_head, d) for d in g] for g in suggest]
                    game_state["avoid_danger"].append((snake_head, "pattern1", suggest))

    def colliding_pattern_2(my_body: typing.List, snake_body: typing.List, collinding_points: typing.List):
        if all([is_cell_occupied(p) for p in collinding_points]):
            return

        my_head = my_body[0]
        my_neck = my_body[1]
        adjs = adj_cells(my_head)
        choices = [p for p in adjs if p not in collinding_points+[my_neck]]
        #choices can have 1 or 2 points
        if len(choices) == 0:
            return
        if len(choices) == 1:
            suggest = choices
        else:
            assert(len(choices) == 2)
            #one perpendicular one parallel
            a, b = choices
            if is_perpendicular(get_adjacent_dir(my_head, a), get_adjacent_dir(my_neck, my_head)):
                suggest = [a, b]
            else:
                suggest = [b, a]
        game_state["avoid_danger"].append((snake_body[0], "pattern2", suggest))

    def head_to_head_danger(my_body: typing.List, snake_body: typing.List):
        if len(my_body) > len(snake_body):
            return

        my_head = get_my_head()
        snake_head = snake_body[0]
        colliding_points = head_colliding_points(my_head, snake_head)

        assert(len(colliding_points) in [1,2])

        x0,y0 = my_head
        x1,y1 = snake_head
        if x0 == x1 or y0 == y1:
            #single colliding point
            assert(len(colliding_points) == 1)
            colliding_pattern_1(my_body, snake_body, colliding_points[0])
        else:
            #2 colliding points
            assert(len(colliding_points) == 2)
            colliding_pattern_2(my_body, snake_body, colliding_points)

    def no_multiple_distance_2(my_head: typing.Tuple, snake_moves: typing.List) -> bool:
        return min([min([distance_pq(my_head, head) for head in config]) 
             for config in itertools.product(*snake_moves)]) > 2

    def avoid_danger():
        game_state["avoid_danger"] = []
        game_state["avoid_danger_4"] = []

        my_body = get_body_coord(game_state["you"]["body"])
        my_head = my_body[0]
        snake_heads = [get_body_coord(snake["body"])[0] for snake in opponent_snakes()]
        snake_dist = [distance_pq(my_head, head) for head in snake_heads]

        #process distance == 4 danger
        if min(snake_dist, default=0) == 4 and len([d for d in snake_dist if d == 4]) > 1:
            #avoid the situation that in the next step it becomes multiple distance == 2
            snake_moves = [permissible_nstep(head, 1) for head in snake_heads]
            my_moves = permissible_nstep(my_head, 1)
            choices = [move for move in my_moves if no_multiple_distance_2(move, snake_moves)]
            game_state["avoid_danger_4"].append(choices) 

        #process distance == 2 danger
        if min(snake_dist, default=0) == 2:
            for snake in opponent_snakes():
                snake_body = get_body_coord(snake["body"])
                snake_head = snake_body[0]
                if distance_pq(my_head, snake_head) == 2:
                    head_to_head_danger(my_body, snake_body)

    def opponent_snakes() -> typing.List:
        my_head = game_state["you"]["body"][0]
        head = (my_head["x"], my_head["y"])
        snakes = [s for s in game_state["board"]["snakes"]]
        snakes = [s for s in snakes if (s["body"][0]["x"], s["body"][0]["y"]) != head]
        return snakes

    def distance_pq(p: typing.Tuple, q: typing.Tuple) -> int:
        x1,y1 = p
        x2,y2 = q
        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def is_adjacent(p1: typing.Tuple, p2: typing.Tuple) -> bool:
        return distance_pq(p1, p2) == 1

    def get_my_head() -> typing.Tuple:
        my_head = game_state["you"]["body"][0]
        head_coord = (my_head["x"], my_head["y"])
        return head_coord

    def food_path(food: typing.Tuple) -> typing.List:
        x0,y0 = get_my_head()
        x1,y1 = food
        mx = min(x0,x1)
        Mx = max(x0,x1)
        my = min(y0,y1)
        My = max(y0,y1)
        region = [(x,y) for x in range(mx,Mx+1) for y in range(my, My+1)]
        if len(region) != distance_pq(get_my_head(), food)+1:
            #has a rectangular region
            border = [(x,y) for x,y in region if not (mx<x<Mx and my<y<My)]
            line1 = sorted([(x,y) for x,y in border if x==mx])
            line2 = sorted([(x,y) for x,y in border if y==my])
            line3 = sorted([(x,y) for x,y in border if x==Mx])
            line4 = sorted([(x,y) for x,y in border if y==My])

            if x1 > x0 and y1 > y0:
                #upper right
                path1 = line2 + line3[1:]
                path2 = line1 + line4[1:]
            elif x1 < x0 and y1 > y0:
                #upper left
                path1 = line3 + list(reversed(line4[1:]))
                path2 = list(reversed(line2)) + line1[1:]
            elif x1 < x0 and y1 < y0:
                #lower left
                path1 = list(reversed(line4)) + list(reversed(line1[1:]))
                path2 = list(reversed(line3)) + list(reversed(line2[1:]))
            else:
                #if x1 > x0 and y1 < y0:
                #lower right
                path1 = list(reversed(line1)) + line2[1:]
                path2 = line4 + list(reversed(line3[1:]))
            paths = [path1, path2]
        else:
            #straight line to food
            path = sorted(region)
            if x1 < x0 or y1 < y0:
                path = list(reversed(path))
            paths = [path]

        return paths
    
    def good_path(path: typing.List) -> bool:
        for snake in opponent_snakes():
            for cell in snake["body"]:
                x = cell["x"]
                y = cell["y"]
                if (x,y) in path:
                    return False
        for cell in game_state["you"]["body"][1:]:
            x = cell["x"]
            y = cell["y"]
            if (x,y) in path:
                return False
        return True

    def find_food():

        game_state["find_food"] = []

        #if opponent snake == 1 and health < 20 find food
        snakes = opponent_snakes()
        if (1 == 0
            or (len(snakes) >= 3 and game_state["you"]["health"] < 50)
            or (len(snakes) >= 2 and game_state["you"]["health"] < 40) 
            or (len(snakes) >= 0 and game_state["you"]["health"] < 20) 
            ):
            snakes = [get_body_coord(s["body"]) for s in snakes]
            snake_heads = [s[0] for s in snakes]
            food_target = [(food["x"], food["y"]) for food in game_state["board"]["food"]]
            food_target = [p for p in food_target if all([distance_pq(p, get_my_head()) < distance_pq(p, snake_head) for snake_head in snake_heads])]
            food_target = [(food, [path for path in food_path(food) if good_path(path)]) for food in food_target]
            food_target = [(food, paths) for food, paths in food_target if len(paths) != 0]
            food_target = sorted(food_target, key=lambda f: distance_pq(get_my_head(), f[0]))
            if len(food_target) != 0:
                food, paths = food_target[0]
                my_neck = game_state["you"]["body"][1]
                my_neck = (my_neck["x"], my_neck["y"])
                paths = sorted(paths, key=lambda path: 0 if get_adjacent_dir(path[0], path[1]) == get_adjacent_dir(my_neck, path[0]) else 1)
                path = paths[0]
                next_head_coord = path[1]
                #save in the global var
                game_state["find_food"].append(next_head_coord)

    def too_crowded():
        #when I'm at a corner - not near the center
        #when I'm all contained in 5x5 corner
        #when two or more opponent snakes are entering

        pass

    def off_border(p: typing.Tuple) -> bool:
        x,y = p
        if x == 0 or y == 0:
            return False
        if x == game_state["board"]["width"]-1 or y == game_state["board"]["height"]-1:
            return False
        return True

    def unwrap_suggest(suggest: typing.List, pattern: str) -> typing.List:
        if pattern == "pattern1":
            return [s for g in suggest for s in g]
        if pattern == "pattern2":
            return suggest
        raise(ValueError("unwrap_suggest"))

    def best_choice():

        #lower priority first, higher priority will override lower priority

        #routine move always exists and set as default
        game_state["next_head_coord"] = game_state["routine_move"]

        if len(game_state["allowed_move"]) == 0:
            #no allowed move, will die
            return

        #set to the first of the allowed moves, then let other considerations override it

        if game_state["next_head_coord"] not in game_state["allowed_move"]:
            game_state["next_head_coord"] = game_state["allowed_move"][0]

        if len(game_state["find_food"]) != 0:
            if game_state["find_food"][0] in game_state["allowed_move"]:
                game_state["next_head_coord"] = game_state["find_food"][0]

        #do not check off-border anymore
        #instead let attractor boxes move the snake off-border

        if len(game_state["avoid_danger_4"]) != 0:
            #there are distance == 4 danger
            choices = game_state["avoid_danger_4"][0]
            choice = [p for p in choices if p in game_state["allowed_move"]]
            if len(choice) != 0:
                if game_state["next_head_coord"] not in choice:
                    #if the current choice is not in the distance == 4 danger
                    #then use the first of the distance == 4 danger
                    game_state["next_head_coord"] = choice[0]

        def sort_collision_choice(p: typing.Tuple) -> typing.Tuple:
            #two considerations:
            #off-border
            #not changing previous choice
            check_off_border = 0 if off_border(p) else 1
            check_change = 0 if p == game_state["next_head_coord"] else 1
            return check_off_border, check_change

        if len(game_state["avoid_danger"]) != 0:

            #consider the first collision and use as the default
            snake_head, pattern, suggest = game_state["avoid_danger"][0]
            if pattern == "pattern1":
                if len(suggest) == 1:
                    #suggest = [[a,b]]
                    assert(len(suggest[0]) == 2)
                    suggest = suggest[0]
                    suggest = [p for p in suggest if p in game_state["allowed_move"]]
                    if len(suggest) == 1:
                        game_state["next_head_coord"] = suggest[0]
                    elif len(suggest) == 2:
                        suggest = sorted(suggest, key=sort_collision_choice)
                        game_state["next_head_coord"] = suggest[0]

                else:
                    #two suggestions
                    #suggest = [[a],[b]]
                    assert(len(suggest) == 2)
                    a,b = suggest
                    a = a[0]
                    b = b[0]
                    if a in game_state["allowed_move"]:
                        game_state["next_head_coord"] = a
                    elif b in game_state["allowed_move"]:
                        game_state["next_head_coord"] = b
            elif pattern == "pattern2":
                suggest = [s for s in suggest if s in game_state["allowed_move"]]
                if len(suggest) != 0:
                    game_state["next_head_coord"] = suggest[0]

            if len(game_state["avoid_danger"]) > 1:
                #multiple collisions
                #at most one common suggestion, take it
                suggestions = [set(unwrap_suggest(suggest, pattern)) for _, pattern, suggest in game_state["avoid_danger"]]
                common = list(set.intersection(*suggestions))
                common = [p for p in common if p in game_state["allowed_move"]]
                if len(common) != 0:
                    game_state["next_head_coord"] = common[0]



    #main

    #ideas
    #next routine path
    #calculated space filling path
    #longer lookahead

    #must satisfy
    allowed_move()

    #priority: avoid danger, find food, routine move
    routine_move()
    avoid_danger()
    find_food()

    best_choice()

    next_move = get_next_move(get_my_head(), game_state["next_head_coord"])

    #logging
    log_move = next_move
    log_head = get_my_head()
    log_health = game_state["you"]["health"]
    log_length = game_state["you"]["length"]
    log_turn = game_state["turn"]
    log_food_count = len(game_state["board"]["food"])
    snakes = opponent_snakes()
    snakes = sorted(snakes, key=lambda s: s["name"])
    log_snake_count = len(snakes)
    log_snake_names = [s["name"] for s in snakes]
    log_snake_heads = [s["body"][0] for s in snakes]
    log_snake_health = [s["health"] for s in snakes]
    log_snake_length = [s["length"] for s in snakes]
    log_boxing_area = game_state["boxing_area"]
    log_game_id = game_state["game"]["id"]
    log_routine_move = game_state["routine_move"]
    log_avoid_danger = game_state["avoid_danger"]
    log_allowed_move = game_state["allowed_move"]

    log_text = ", ".join([
        f"game_id: {log_game_id}",
        f"move: {log_move}",
        f"turn: {log_turn}",
        f"health: {log_health}",
        f"head: {log_head}",
        f"scount: {log_snake_count}",
        f"boxing_area: {log_boxing_area}",
        f"routine_move: {log_routine_move}",
        f"avoid_danger: {log_avoid_danger}",
        f"allowed_move: {log_allowed_move}",
    ])
    print(log_text)

    return {"move": next_move}



# this is a good move that gives me 6976 #76 on 5/16/25
def move7(game_state: typing.Dict) -> typing.Dict:
    """
    move in a square area
    following an area filling path
    the area has a dimension of n x m
    where n is an even number
    so that the path can close
    start with 4x3
    then 4x4, 4x5, 4x6
    then 6x5, 6x6, 6x7, 6x8
    then 8x7, ...
    """

    """
    Then avoid immediate danger
    check opponents and self
    """


    def valid_area(area: typing.Tuple) -> bool:
        ((x1,y1), (x2,y2)) = area
        if not 0 <= x2 < game_state["board"]["width"]:
            return False
        if not 0 <= y2 < game_state["board"]["height"]:
            return False
        return True

    def body_in_area(area: typing.Tuple, body: typing.List) -> bool:
        ((x1,y1), (x2,y2)) = area
        for cell in body:
            x = cell["x"]
            y = cell["y"]
            if not x1 <= x <= x2:
                return False
            if not y1 <= y <= y2:
                return False
        return True

    def area_dim() -> typing.Tuple:
        if len(game_state["board"]["snakes"]) >= 4:
            #3 or more opponents
            return (4,3)
        if len(game_state["board"]["snakes"]) == 3:
            #3 or more opponents
            return (4,4)
        #only 1 opponent
        return (4,5)

    def four_corner() -> typing.List:
        if len(game_state["board"]["snakes"]) >= 4:
            #3 or more apponents
            return [
                ((1,1), (4,3)),
                ((6,1), (9,3)),
                ((1,7), (4,9)),
                ((6,7), (9,9)),
            ]
        if len(game_state["board"]["snakes"]) == 3:
            #2 opponents
            return [
                ((1,1), (4,4)),
                ((6,1), (9,4)),
                ((1,6), (4,9)),
                ((6,6), (9,9)),
            ]
        if len(game_state["board"]["snakes"]) <= 2:
            #1 opponent
            return [
                ((0,0), (3,4)),
                ((7,0), (10,4)),
                ((0,6), (3,10)),
                ((7,6), (10,10)),
            ]
        #fallback
        #not used actually
        return four_corner_orig()

    def four_corner_orig() -> typing.List:
        x1,y1 = (0, 0)
        x2,y2 = x1+area_dim()[0]-1, y1+area_dim()[1]-1
        bottom_left_corner = ((x1,y1), (x2,y2))
        x1,y1 = (game_state["board"]["width"]-area_dim()[0], 0)
        x2,y2 = x1+area_dim()[0]-1, y1+area_dim()[1]-1
        bottom_right_corner = ((x1,y1), (x2,y2))
        x1,y1 = (0, game_state["board"]["height"]-area_dim()[1])
        x2,y2 = x1+area_dim()[0]-1, y1+area_dim()[1]-1
        top_left_corner = ((x1,y1), (x2,y2))
        x1,y1 = (game_state["board"]["width"]-area_dim()[0], game_state["board"]["height"]-area_dim()[1])
        x2,y2 = x1+area_dim()[0]-1, y1+area_dim()[1]-1
        top_right_corner = ((x1,y1), (x2,y2))
        return [
            bottom_left_corner,
            bottom_right_corner,
            top_left_corner,
            top_right_corner,
        ]

    def all_containing_area() -> typing.List:
        all_area = []
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+area_dim()[0]-1
                y2 = y1+area_dim()[1]-1
                area = ((x1,y1), (x2,y2))
                if not valid_area(area):
                    continue
                if body_in_area(area, game_state["you"]["body"]):
                    all_area.append(area)
        if len(all_area) != 0:
            return all_area
        
        #when the body is too long, this can be empty
        #in this case, check the first several cells
        #we go from 6 to 3 cells 
        #this is determined by the dimension of the area
        #3 is the smallest dimension size
        #this ensure the function must return something
        def check_first_n(n: int) -> typing.List:
            areas = []
            for x1 in range(game_state["board"]["width"]):
                for y1 in range(game_state["board"]["height"]):
                    #bottom-left corner (x1,y1)
                    x2 = x1+area_dim()[0]-1
                    y2 = y1+area_dim()[1]-1
                    area = ((x1,y1), (x2,y2))
                    if not valid_area(area):
                        continue
                    if body_in_area(area, game_state["you"]["body"][:n]):
                        areas.append(area)
            return areas
        for n in [6,5,4,3]:
            areas = check_first_n(n)
            if len(areas) != 0:
                all_area += areas
                break
                
        return all_area
        

    def target_corner() -> typing.Tuple:
        body_center_x = sum([cell["x"] for cell in game_state["you"]["body"]]) / game_state["you"]["length"]
        body_center_y = sum([cell["y"] for cell in game_state["you"]["body"]]) / game_state["you"]["length"]
        corners = four_corner()

        def sort_corner(corner: typing.Tuple):
            ((x1,y1), (x2,y2)) = corner
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            return math.sqrt((xc-body_center_x)**2+(yc-body_center_y)**2)

        corners = sorted(corners, key=sort_corner)
        return corners[0]

    def get_area() -> typing.Tuple:
        """
        get a rectangular area depend on the snake initial position
        so that even when the snake moves, the area doesn't change
        """

        #prefer four corner
        for area in four_corner():
            if body_in_area(area, game_state["you"]["body"]):
                return area

        #if not in one of four corners, find one close to it,
        #so that the area will move to the closest corner

        #if not found then find the first area that contains the snake
        #this can move so that next time will find a fixed area
        target = target_corner()

        #when it's too long, this can be empty
        areas = all_containing_area()

        def sort_area(area: typing.Tuple):
            ((x1,y1), (x2,y2)) = area
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            ((target_x1, target_y1), (target_x2, target_y2)) = target
            target_xc = (target_x1+target_x2)/2
            target_yc = (target_y1+target_y2)/2
            return math.sqrt((xc-target_xc)**2+(yc-target_yc)**2)

        areas = sorted(areas, key=sort_area)
        area = areas[0]
        return area

    def order_4x3() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (0,2),
            (0,1),
        ]

    def order_4x4() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (3,3),
            (2,3),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (1,3),
            (0,3),
            (0,2),
            (0,1),
        ]

    def order_4x5() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (3,3),
            (3,4),
            (2,4),
            (2,3),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (1,3),
            (1,4),
            (0,4),
            (0,3),
            (0,2),
            (0,1),
        ]

    def order_4x6() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (4,0),
            (5,0),
            (5,1),
            (5,2),
            (5,3),
            (4,3),
            (4,2),
            (4,1),
            (3,1),
            (3,2),
            (3,3),
            (2,3),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (1,3),
            (0,3),
            (0,2),
            (0,1),
        ]

    def get_adjacent_dir(p: typing.Tuple, q: typing.Tuple) -> str:
        assert(is_adjacent(p, q))
        x,y = p
        nx,ny = q
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        return get_adjacent_dir(head_coord, next_head_coord)

    #1. determine the area dimension corners
    # determine my position dirs
    def routine_move():
        area = get_area()
        game_state["boxing_area"] = area

        order_list = order_4x4()
        if area_dim() == (4,3):
            order_list = order_4x3()
        elif area_dim() == (4,4):
            order_list = order_4x4()
        elif area_dim() == (4,5):
            order_list = order_4x5()

        bottom_left_corner = area[0]
        x0,y0 = bottom_left_corner
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        head_coord = (my_head["x"], my_head["y"])
        neck_coord = (my_neck["x"], my_neck["y"])
        relative_head_coord = (head_coord[0]-x0, head_coord[1]-y0)
        relative_neck_coord = (neck_coord[0]-x0, neck_coord[1]-y0)
        for head_pos in range(len(order_list)):
            if relative_head_coord == order_list[head_pos]:
                break
        next_head_pos = head_pos+1
        next_head_pos %= len(order_list)
        if relative_neck_coord == order_list[next_head_pos]:
            next_head_pos = head_pos-1
            next_head_pos %= len(order_list)

        #get next_head absolute coordinate
        x2,y2 = order_list[next_head_pos]
        x2 += x0
        y2 += y0

        #save in global var
        game_state["next_head_coord"] = (x2,y2)

    def pos_on_board(pos: typing.Tuple) -> bool:
        x,y = pos
        if x < 0:
            return False
        if y < 0:
            return False
        if x >= game_state["board"]["width"]:
            return False
        if y >= game_state["board"]["height"]:
            return False
        return True

    def adj_cells(pos: typing.Tuple) -> typing.List:
        x,y = pos
        moves = [(1,0), (-1,0), (0,1), (0,-1)]
        npos = [(a+x,b+y) for a,b in moves]
        npos = [p for p in npos if pos_on_board(p)]
        return npos

    def permissible_first_step(head: typing.Tuple) -> typing.List:
        #head is the head coordinate
        npos = adj_cells(head)
        allowed = []

        def run_into(p, s):
            body = [(c["x"],c["y"]) for c in s["body"]]
            if s["health"] == 100:
                #just eat food, tail will not move
                check_body = body
            else:
                #tail will move, no need to check
                check_body = body[:-1]
            return p in check_body

        for p in npos:
            if not any([run_into(p, s) for s in game_state["board"]["snakes"]]):
                allowed.append(p)
        return allowed

    def permissible_second_step(head: typing.Tuple) -> typing.List:
        #head is the head coordinate
        npos = adj_cells(head)
        allowed = []

        def run_into(p, s):
            body = [(c["x"],c["y"]) for c in s["body"]]
            if s["health"] == 100:
                check_body = body[:-1]
            else:
                check_body = body[:-2]
            return p in check_body

        for p in npos:
            if not any([run_into(p, s) for s in game_state["board"]["snakes"]]):
                allowed.append(p)
        return allowed

    def allowed_next_move():
        head = get_my_head()
        allowed = permissible_first_step(head)
        allowed = [p for p in allowed if len(permissible_second_step(p)) != 0]
        return allowed

    def opponent_snakes() -> typing.List:
        my_head = game_state["you"]["body"][0]
        head = (my_head["x"], my_head["y"])
        snakes = [s for s in game_state["board"]["snakes"]]
        snakes = [s for s in snakes if (s["body"][0]["x"], s["body"][0]["y"]) != head]
        return snakes

    def distance_pq(p: typing.Tuple, q: typing.Tuple) -> int:
        x1,y1 = p
        x2,y2 = q
        distance = abs(x1-x2) + abs(y1-y2)
        return distance

    def is_adjacent(p1: typing.Tuple, p2: typing.Tuple) -> bool:
        return distance_pq(p1, p2) == 1

    def is_2step_head_to_head_danger(pos):
        for s in opponent_snakes():
            shead = s["body"][0]
            shead = shead["x"], shead["y"]
            if distance_pq(pos, shead) == 3:
                if game_state["you"]["length"] <= s["length"]:
                    return True
        return False

    def is_head_to_head_danger(pos):
        for s in opponent_snakes():
            shead = s["body"][0]
            shead = shead["x"], shead["y"]
            if is_adjacent(pos, shead):
                if game_state["you"]["length"] <= s["length"]:
                    return True
        return False

    def get_my_head() -> typing.Tuple:
        my_head = game_state["you"]["body"][0]
        head_coord = (my_head["x"], my_head["y"])
        return head_coord

    def old_choice(next_head_coord, allowed, dangered, safed):

        if next_head_coord in allowed:
            if next_head_coord in dangered:
                if len(safed) != 0:
                    next_head_coord = safed[0]
                else:
                    #keep next_move
                    pass
            else:
                #no doubt, move in routine
                pass
        else:
            if len(allowed) == 0:
                #no allowed move
                pass
            else:
                next_head_coord = allowed[0]

        return next_head_coord

    def open_area_index(next_head: typing.Tuple) -> typing.Tuple:
        #check opponent snake heads in 5x5 area
        x0,y0 = get_my_head()
        x1,y1 = next_head
        if y1-y0 == 1:
            corner1 = (x0-2, y0+1)
        elif y1-y0 == -1:
            corner1 = (x0-2, y0-5)
        elif x1-x0 == 1:
            corner1 = (x0+1, y0-2)
        else:
            corner1 = (x0-5, y0-2)
        corner2 = (n+4 for n in corner1)
        snakes = opponent_snakes()
        snake_heads = [s["body"][0] for s in snakes]
        snake_heads = [(s["x"], s["y"]) for s in snake_heads]
        a1,b1 = corner1
        a2,b2 = corner2
        head_count = len([x for x,y in snake_heads if a1<=x<=a2 and b1<=y<=b2])
        open_cell_count = len([(x,y) for x in range(a1,a2+1) for y in range(b1,b2+1) 
                           if pos_on_board((x,y))
                           and not (x,y) in [(p["x"], p["y"]) for s in snakes for p in s["body"]]
                           ])

        return head_count, 1000-open_cell_count #reverse order

    def food_path(food: typing.Tuple) -> typing.List:
        x0,y0 = get_my_head()
        x1,y1 = food
        mx = min(x0,x1)
        Mx = max(x0,x1)
        my = min(y0,y1)
        My = max(y0,y1)
        region = [(x,y) for x in range(mx,Mx+1) for y in range(my, My+1)]
        if len(region) != distance_pq(get_my_head(), food)+1:
            #has a rectangular region
            border = [(x,y) for x,y in region if not (mx<x<Mx and my<y<My)]
            line1 = sorted([(x,y) for x,y in border if x==mx])
            line2 = sorted([(x,y) for x,y in border if y==my])
            line3 = sorted([(x,y) for x,y in border if x==Mx])
            line4 = sorted([(x,y) for x,y in border if y==My])

            if x1 > x0 and y1 > y0:
                #upper right
                path1 = line2 + line3[1:]
                path2 = line1 + line4[1:]
            if x1 < x0 and y1 > y0:
                #upper left
                path1 = line3 + list(reversed(line4[1:]))
                path2 = list(reversed(line2)) + line1[1:]
            if x1 < x0 and y1 < y0:
                #lower left
                path1 = list(reversed(line4)) + list(reversed(line1[1:]))
                path2 = list(reversed(line3)) + list(reversed(line2[1:]))
            if x1 > x0 and y1 < y0:
                #lower right
                path1 = list(reversed(line1)) + line2[1:]
                path2 = line4 + list(reversed(line3[1:]))
            paths = [path1, path2]
        else:
            #straight line to food
            path = sorted(region)
            if x1 < x0 or y1 < y0:
                path = list(reversed(path))
            paths = [path]

        return paths
    
    def good_path(path: typing.List) -> bool:
        for snake in opponent_snakes():
            for cell in snake["body"]:
                x = cell["x"]
                y = cell["y"]
                if (x,y) in path:
                    return False
        for cell in game_state["you"]["body"][1:]:
            x = cell["x"]
            y = cell["y"]
            if (x,y) in path:
                return False
        return True

    def head_count_and_routine(next_head_coord):
        def fn(next_head):
            head_count, _ = open_area_index(next_head)
            return head_count, 0 if next_head == next_head_coord else 1
        return fn

    def avoid_danger():

        next_head_coord = game_state["next_head_coord"]

        allowed = allowed_next_move()
        dangered = [p for p in allowed if is_head_to_head_danger(p)]
        dangered_2step = [p for p in allowed if is_2step_head_to_head_danger(p)]
        safed = [p for p in allowed if not p in dangered]
        safed_2step = [p for p in safed if not p in dangered_2step]

        #sort choices by open area index
        allowed = sorted(allowed, key=open_area_index)
        safed = sorted(safed, key=open_area_index)
        safed_2step = sorted(safed_2step, key=open_area_index)

        #next_head_coord = old_choice(next_head_coord, allowed, dangered, safed)

        #modify next_head_coord
        if not next_head_coord in allowed:
            if len(allowed) != 0:
                next_head_coord = allowed[0]
                if len(safed) != 0:
                    next_head_coord = safed[0]
                    if len(safed_2step) != 0:
                        next_head_coord = safed_2step[0]
        else:
            if not next_head_coord in safed:
                if len(safed) != 0:
                    next_head_coord = safed[0]
                    if len(safed_2step) != 0:
                        next_head_coord = safed_2step[0]
            else:
                if not next_head_coord in safed_2step:
                    if len(safed_2step) != 0:
                        next_head_coord = safed_2step[0]
                    else:
                        #choose between routine and better safed
                        #choose opponent head count over routine
                        safed2 = sorted(safed, key=head_count_and_routine(next_head_coord))
                        next_head_coord = safed2[0]

        #save in the global var
        game_state["next_head_coord"] = next_head_coord

    def find_food():

        next_head_coord = game_state["next_head_coord"]

        #if opponent snake == 1 and health < 20 find food
        snakes = opponent_snakes()
        if len(snakes) == 1 and game_state["you"]["health"] < 20:
            snake = snakes[0]
            snake_head = snake["body"][0]
            snake_head = (snake_head["x"], snake_head["y"])
            food_target = [(food["x"], food["y"]) for food in game_state["board"]["food"]]
            food_target = [p for p in food_target if distance_pq(p, get_my_head()) < distance_pq(p, snake_head)]
            food_target = [(food, [path for path in food_path(food) if good_path(path)]) for food in food_target]
            food_target = [(food, paths) for food, paths in food_target if len(paths) != 0]
            food_target = sorted(food_target, key=lambda f: distance_pq(get_my_head(), f[0]))
            if len(food_target) != 0:
                food, paths = food_target[0]
                my_neck = game_state["you"]["body"][1]
                my_neck = (my_neck["x"], my_neck["y"])
                paths = sorted(paths, key=lambda path: 0 if get_adjacent_dir(path[0], path[1]) == get_adjacent_dir(my_neck, path[0]) else 1)
                path = paths[0]
                next_head_coord = path[1]

        #save in the global var
        game_state["next_head_coord"] = next_head_coord

    def too_crowded():
        #when I'm at a corner - not near the center
        #when I'm all contained in 5x5 corner
        #when two or more opponent snakes are entering

        pass

    #main

    #must do routine_move first - it populate game_state["next_head_coord"]
    routine_move()

    #modification from routine move
    avoid_danger()
    find_food()

    next_move = get_next_move(get_my_head(), game_state["next_head_coord"])

    #logging
    log_move = next_move
    log_head = get_my_head()
    log_health = game_state["you"]["health"]
    log_length = game_state["you"]["length"]
    log_turn = game_state["turn"]
    log_food_count = len(game_state["board"]["food"])
    snakes = opponent_snakes()
    snakes = sorted(snakes, key=lambda s: s["name"])
    log_snake_count = len(snakes)
    log_snake_names = [s["name"] for s in snakes]
    log_snake_heads = [s["body"][0] for s in snakes]
    log_snake_health = [s["health"] for s in snakes]
    log_snake_length = [s["length"] for s in snakes]
    log_boxing_area = game_state["boxing_area"]

    log_text = ", ".join([
        f"move: {log_move}",
        f"turn: {log_turn}",
        f"health: {log_health}",
        f"head: {log_head}",
        f"scount: {log_snake_count}",
        f"boxing_area: {log_boxing_area}",
    ])
    print(log_text)

    return {"move": next_move}

#this is a good move that give me 6719 #83 in leaderboard
def move6(game_state: typing.Dict) -> typing.Dict:
    """
    move in a square area
    following an area filling path
    the area has a dimension of n x m
    where n is an even number
    so that the path can close
    start with 4x3
    then 4x4, 4x5, 4x6
    then 6x5, 6x6, 6x7, 6x8
    then 8x7, ...
    """

    """
    Then avoid immediate danger
    check opponents and self
    """


    def valid_area(area: typing.Tuple) -> bool:
        ((x1,y1), (x2,y2)) = area
        if not 0 <= x2 < game_state["board"]["width"]:
            return False
        if not 0 <= y2 < game_state["board"]["height"]:
            return False
        return True

    def body_in_area(area: typing.Tuple, body: typing.List) -> bool:
        ((x1,y1), (x2,y2)) = area
        for cell in body:
            x = cell["x"]
            y = cell["y"]
            if not x1 <= x <= x2:
                return False
            if not y1 <= y <= y2:
                return False
        return True

    def area_dim() -> typing.Tuple:
        if len(game_state["board"]["snakes"]) >= 4:
            #3 or more opponents
            return (4,3)
        if len(game_state["board"]["snakes"]) == 3:
            #3 or more opponents
            return (4,4)
        #only 1 opponent
        return (4,5)

    def four_corner() -> typing.List:
        x1,y1 = (0, 0)
        x2,y2 = x1+area_dim()[0]-1, y1+area_dim()[1]-1
        bottom_left_corner = ((x1,y1), (x2,y2))
        x1,y1 = (game_state["board"]["width"]-area_dim()[0], 0)
        x2,y2 = x1+area_dim()[0]-1, y1+area_dim()[1]-1
        bottom_right_corner = ((x1,y1), (x2,y2))
        x1,y1 = (0, game_state["board"]["height"]-area_dim()[1])
        x2,y2 = x1+area_dim()[0]-1, y1+area_dim()[1]-1
        top_left_corner = ((x1,y1), (x2,y2))
        x1,y1 = (game_state["board"]["width"]-area_dim()[0], game_state["board"]["height"]-area_dim()[1])
        x2,y2 = x1+area_dim()[0]-1, y1+area_dim()[1]-1
        top_right_corner = ((x1,y1), (x2,y2))
        return [
            bottom_left_corner,
            bottom_right_corner,
            top_left_corner,
            top_right_corner,
        ]

    def all_containing_area() -> typing.List:
        all_area = []
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+area_dim()[0]-1
                y2 = y1+area_dim()[1]-1
                area = ((x1,y1), (x2,y2))
                if not valid_area(area):
                    continue
                if body_in_area(area, game_state["you"]["body"]):
                    all_area.append(area)
        if len(all_area) != 0:
            return all_area
        
        #when the body is too long, this can be empty
        #in this case, check the first several cells
        #we go from 6 to 3 cells 
        #this is determined by the dimension of the area
        #3 is the smallest dimension size
        #this ensure the function must return something
        def check_first_n(n: int) -> typing.List:
            areas = []
            for x1 in range(game_state["board"]["width"]):
                for y1 in range(game_state["board"]["height"]):
                    #bottom-left corner (x1,y1)
                    x2 = x1+area_dim()[0]-1
                    y2 = y1+area_dim()[1]-1
                    area = ((x1,y1), (x2,y2))
                    if not valid_area(area):
                        continue
                    if body_in_area(area, game_state["you"]["body"][:n]):
                        areas.append(area)
            return areas
        for n in [6,5,4,3]:
            areas = check_first_n(n)
            if len(areas) != 0:
                all_area += areas
                break
                
        return all_area
        

    def target_corner() -> typing.Tuple:
        body_center_x = sum([cell["x"] for cell in game_state["you"]["body"]]) / game_state["you"]["length"]
        body_center_y = sum([cell["y"] for cell in game_state["you"]["body"]]) / game_state["you"]["length"]
        corners = four_corner()

        def sort_corner(corner: typing.Tuple):
            ((x1,y1), (x2,y2)) = corner
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            return math.sqrt((xc-body_center_x)**2+(yc-body_center_y)**2)

        corners = sorted(corners, key=sort_corner)
        return corners[0]

    def get_area() -> typing.Tuple:
        """
        get a rectangular area depend on the snake initial position
        so that even when the snake moves, the area doesn't change
        """

        #prefer four corner
        for area in four_corner():
            if body_in_area(area, game_state["you"]["body"]):
                return area

        #if not in one of four corners, find one close to it,
        #so that the area will move to the closest corner

        #if not found then find the first area that contains the snake
        #this can move so that next time will find a fixed area
        target = target_corner()

        #when it's too long, this can be empty
        areas = all_containing_area()

        def sort_area(area: typing.Tuple):
            ((x1,y1), (x2,y2)) = area
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            ((target_x1, target_y1), (target_x2, target_y2)) = target
            target_xc = (target_x1+target_x2)/2
            target_yc = (target_y1+target_y2)/2
            return math.sqrt((xc-target_xc)**2+(yc-target_yc)**2)

        areas = sorted(areas, key=sort_area)
        return areas[0]

    def order_4x3() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (0,2),
            (0,1),
        ]

    def order_4x4() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (3,3),
            (2,3),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (1,3),
            (0,3),
            (0,2),
            (0,1),
        ]

    def order_4x5() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (3,3),
            (3,4),
            (2,4),
            (2,3),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (1,3),
            (1,4),
            (0,4),
            (0,3),
            (0,2),
            (0,1),
        ]

    def order_4x6() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (4,0),
            (5,0),
            (5,1),
            (5,2),
            (5,3),
            (4,3),
            (4,2),
            (4,1),
            (3,1),
            (3,2),
            (3,3),
            (2,3),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (1,3),
            (0,3),
            (0,2),
            (0,1),
        ]

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        x,y = head_coord
        nx,ny = next_head_coord
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    #1. determine the area dimension corners
    # determine my position dirs
    def get_next_head_coord():
        area = get_area()

        order_list = order_4x4()
        if area_dim() == (4,3):
            order_list = order_4x3()
        elif area_dim() == (4,4):
            order_list = order_4x4()
        elif area_dim() == (4,5):
            order_list = order_4x5()

        bottom_left_corner = area[0]
        x0,y0 = bottom_left_corner
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        head_coord = (my_head["x"], my_head["y"])
        neck_coord = (my_neck["x"], my_neck["y"])
        relative_head_coord = (head_coord[0]-x0, head_coord[1]-y0)
        relative_neck_coord = (neck_coord[0]-x0, neck_coord[1]-y0)
        for head_pos in range(len(order_list)):
            if relative_head_coord == order_list[head_pos]:
                break
        next_head_pos = head_pos+1
        next_head_pos %= len(order_list)
        if relative_neck_coord == order_list[next_head_pos]:
            next_head_pos = head_pos-1
        next_head_pos %= len(order_list)

        #get next_head absolute coordinate
        x2,y2 = order_list[next_head_pos]
        x2 += x0
        y2 += y0

        return (x2,y2)

    def check_border() -> typing.Set:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_head_coord = (my_head["x"], my_head["y"])
        x0,y0 = my_head_coord

        move_set = set()

        #left
        x1,y1 = x0-1,y0
        if x1 >= 0:
            move_set.add("left")

        #right
        x1,y1 = x0+1,y0
        if x1 < game_state["board"]["width"]:
            move_set.add("right")

        #up
        x1,y1 = x0,y0+1
        if y1 < game_state["board"]["height"]:
            move_set.add("up")

        #down
        x1,y1 = x0,y0-1
        if y1 >= 0:
            move_set.add("down")
        
        return move_set


    def check_self(body: typing.List) -> typing.Tuple:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_head_coord = (my_head["x"], my_head["y"])
        x0,y0 = my_head_coord

        move_set = set()

        body_list = [(b["x"],b["y"]) for b in body]
        #tail should move - not considering eating food
        body_list = body_list[:-1]

        #left
        x1,y1 = x0-1,y0
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("left")
        
        #right
        x1,y1 = x0+1,y0
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("right")
        
        #up
        x1,y1 = x0,y0+1
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("up")
        
        #down
        x1,y1 = x0,y0-1
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("down")
        
        safer_move_set = set(move_set)

        return move_set, safer_move_set

    def possible_head_to_head_die(my_next_head_coord: typing.Tuple, body: typing.List) -> bool:
        if len(body) < len(game_state["you"]["body"]):
            return False
        x0,y0 = my_next_head_coord
        x1,y1 = body[0]["x"], body[0]["y"]
        if y0 == y1 and abs(x1-x0) == 1:
            return True
        if x0 == x1 and abs(y1-y0) == 1:
            return True
        return False

    def check_opponent(body: typing.List) -> typing.Tuple:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_head_coord = (my_head["x"], my_head["y"])
        x0,y0 = my_head_coord

        move_set = set()
        safer_move_set = set()

        body_list = [(b["x"],b["y"]) for b in body]
        #tail should move - not considering eating food
        body_list = body_list[:-1]

        #left
        x1,y1 = x0-1,y0
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("left")
            if not possible_head_to_head_die(my_next_head_coord, body):
                safer_move_set.add("left")
        
        #right
        x1,y1 = x0+1,y0
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("right")
            if not possible_head_to_head_die(my_next_head_coord, body):
                safer_move_set.add("right")
        
        #up
        x1,y1 = x0,y0+1
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("up")
            if not possible_head_to_head_die(my_next_head_coord, body):
                safer_move_set.add("up")
        
        #down
        x1,y1 = x0,y0-1
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("down")
            if not possible_head_to_head_die(my_next_head_coord, body):
                safer_move_set.add("down")

        return move_set, safer_move_set

    def next_move_set() -> typing.Tuple:
        move_set_result = check_border()
        safer_move_set_result = check_border()
        for snake in game_state["board"]["snakes"]:
            #game_state snakes include myself, need to exclude it
            snake_head = snake["body"][0]
            if (snake_head["x"], snake_head["y"]) == head_coord:
                continue
            move_set, safer_move_set = check_opponent(snake["body"])
            move_set_result = move_set_result.intersection(move_set)
            safer_move_set_result = safer_move_set_result.intersection(safer_move_set)
        move_set, safer_move_set = check_self(game_state["you"]["body"])
        move_set_result = move_set_result.intersection(move_set)
        safer_move_set_result = safer_move_set_result.intersection(safer_move_set)
        return move_set_result, safer_move_set_result

    #main
    my_head = game_state["you"]["body"][0]
    head_coord = (my_head["x"], my_head["y"])
    next_head_coord = get_next_head_coord()
    next_move = get_next_move(head_coord, next_head_coord)

    move_set_result, safer_move_set_result = next_move_set()

    danger_set = move_set_result - safer_move_set_result
    if next_move in move_set_result:
        if next_move in danger_set:
            #next_move can cause a head-to-head die, but not deterministic
            if len(safer_move_set_result) != 0:
                next_move = next(iter(safer_move_set_result))
            else:
                #keep next_move
                pass
        else:
            #no doubt, move in routine
            pass
    else:
        if len(move_set_result) == 0:
            #no move set, will die
            pass
        else:
            #planned move not possible, choose the first dir allowed
            next_move = next(iter(move_set_result))
    print(f"next_move final: {next_move}")

    return {"move": next_move}


def move5(game_state: typing.Dict) -> typing.Dict:
    """
    move in a square area
    following an area filling path
    the area has a dimension of n x m
    where n is an even number
    so that the path can close
    start with 4x3
    then 4x4, 4x5, 4x6
    then 6x5, 6x6, 6x7, 6x8
    then 8x7, ...
    """

    """
    Then avoid immediate danger
    check opponents and self
    """


    def valid_area(area: typing.Tuple) -> bool:
        ((x1,y1), (x2,y2)) = area
        if not 0 <= x2 < game_state["board"]["width"]:
            return False
        if not 0 <= y2 < game_state["board"]["height"]:
            return False
        return True

    def body_in_area(area: typing.Tuple, body: typing.List) -> bool:
        ((x1,y1), (x2,y2)) = area
        for cell in body:
            x = cell["x"]
            y = cell["y"]
            if not x1 <= x <= x2:
                return False
            if not y1 <= y <= y2:
                return False
        return True

    area_width = 4
    area_height = 4

    def four_corner() -> typing.List:
        x1,y1 = (0, 0)
        x2,y2 = x1+area_width-1, y1+area_height-1
        bottom_left_corner = ((x1,y1), (x2,y2))
        x1,y1 = (game_state["board"]["width"]-area_width, 0)
        x2,y2 = x1+area_width-1, y1+area_height-1
        bottom_right_corner = ((x1,y1), (x2,y2))
        x1,y1 = (0, game_state["board"]["height"]-area_height)
        x2,y2 = x1+area_width-1, y1+area_height-1
        top_left_corner = ((x1,y1), (x2,y2))
        x1,y1 = (game_state["board"]["width"]-area_width, game_state["board"]["height"]-area_height)
        x2,y2 = x1+area_width-1, y1+area_height-1
        top_right_corner = ((x1,y1), (x2,y2))
        return [
            bottom_left_corner,
            bottom_right_corner,
            top_left_corner,
            top_right_corner,
        ]

    def all_containing_area() -> typing.List:
        all_area = []
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+area_width-1
                y2 = y1+area_height-1
                area = ((x1,y1), (x2,y2))
                if not valid_area(area):
                    continue
                if body_in_area(area, game_state["you"]["body"]):
                    all_area.append(area)
        if len(all_area) != 0:
            return all_area
        
        #when the body is too long, this can be empty
        #in this case, check the first 4 cells
        #this ensure the function must return something
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+area_width-1
                y2 = y1+area_height-1
                area = ((x1,y1), (x2,y2))
                if not valid_area(area):
                    continue
                if body_in_area(area, game_state["you"]["body"][:area_width]):
                    all_area.append(area)
            
        return all_area
        

    def target_corner() -> typing.Tuple:
        body_center_x = sum([cell["x"] for cell in game_state["you"]["body"]]) / game_state["you"]["length"]
        body_center_y = sum([cell["y"] for cell in game_state["you"]["body"]]) / game_state["you"]["length"]
        corners = four_corner()

        def sort_corner(corner: typing.Tuple):
            ((x1,y1), (x2,y2)) = corner
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            return math.sqrt((xc-body_center_x)**2+(yc-body_center_y)**2)

        corners = sorted(corners, key=sort_corner)
        return corners[0]

    def get_area() -> typing.Tuple:
        """
        get a rectangular area depend on the snake initial position
        so that even when the snake moves, the area doesn't change
        """
        x_blocks = game_state["board"]["width"]//area_width
        if game_state["board"]["width"] % area_width != 0:
            x_blocks += 1
        y_blocks = game_state["board"]["height"]//area_height
        if game_state["board"]["height"] % area_height != 0:
            y_blocks += 1

        #prefer four corner
        for area in four_corner():
            if body_in_area(area, game_state["you"]["body"]):
                return area

        #if not in one of four corners, find one close to it,
        #so that the area will move to the closest corner

        #if not found then find the first area that contains the snake
        #this can move so that next time will find a fixed area
        target = target_corner()

        #when it's too long, this can be empty
        areas = all_containing_area()

        def sort_area(area: typing.Tuple):
            ((x1,y1), (x2,y2)) = area
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            ((target_x1, target_y1), (target_x2, target_y2)) = target
            target_xc = (target_x1+target_x2)/2
            target_yc = (target_y1+target_y2)/2
            return math.sqrt((xc-target_xc)**2+(yc-target_yc)**2)

        areas = sorted(areas, key=sort_area)
        return areas[0]

    def order_4x3() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (0,2),
            (0,1),
        ]

    def order_4x4() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (3,3),
            (2,3),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (1,3),
            (0,3),
            (0,2),
            (0,1),
        ]

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        x,y = head_coord
        nx,ny = next_head_coord
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    #1. determine the area dimension corners
    # determine my position dirs
    def get_next_head_coord():
        area = get_area()
        order_list = order_4x4()

        bottom_left_corner = area[0]
        x0,y0 = bottom_left_corner
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        head_coord = (my_head["x"], my_head["y"])
        neck_coord = (my_neck["x"], my_neck["y"])
        relative_head_coord = (head_coord[0]-x0, head_coord[1]-y0)
        relative_neck_coord = (neck_coord[0]-x0, neck_coord[1]-y0)
        for head_pos in range(len(order_list)):
            if relative_head_coord == order_list[head_pos]:
                break
        next_head_pos = head_pos+1
        next_head_pos %= len(order_list)
        if relative_neck_coord == order_list[next_head_pos]:
            next_head_pos = head_pos-1
        next_head_pos %= len(order_list)

        #get next_head absolute coordinate
        x2,y2 = order_list[next_head_pos]
        x2 += x0
        y2 += y0

        return (x2,y2)

    def check_border() -> typing.Set:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_head_coord = (my_head["x"], my_head["y"])
        x0,y0 = my_head_coord

        move_set = set()

        #left
        x1,y1 = x0-1,y0
        if x1 >= 0:
            move_set.add("left")

        #right
        x1,y1 = x0+1,y0
        if x1 < game_state["board"]["width"]:
            move_set.add("right")

        #up
        x1,y1 = x0,y0+1
        if y1 < game_state["board"]["height"]:
            move_set.add("up")

        #down
        x1,y1 = x0,y0-1
        if y1 >= 0:
            move_set.add("down")
        
        return move_set


    def check_self(body: typing.List) -> typing.Tuple:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_head_coord = (my_head["x"], my_head["y"])
        x0,y0 = my_head_coord

        move_set = set()

        body_list = [(b["x"],b["y"]) for b in body]
        #tail should move - not considering eating food
        body_list = body_list[:-1]

        #left
        x1,y1 = x0-1,y0
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("left")
        
        #right
        x1,y1 = x0+1,y0
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("right")
        
        #up
        x1,y1 = x0,y0+1
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("up")
        
        #down
        x1,y1 = x0,y0-1
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("down")
        
        safer_move_set = set(move_set)

        return move_set, safer_move_set

    def possible_head_to_head_die(my_next_head_coord: typing.Tuple, body: typing.List) -> bool:
        if len(body) < len(game_state["you"]["body"]):
            return False
        x0,y0 = my_next_head_coord
        x1,y1 = body[0]["x"], body[0]["y"]
        if y0 == y1 and abs(x1-x0) == 1:
            return True
        if x0 == x1 and abs(y1-y0) == 1:
            return True
        return False

    def check_opponent(body: typing.List) -> typing.Tuple:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_head_coord = (my_head["x"], my_head["y"])
        x0,y0 = my_head_coord

        move_set = set()
        safer_move_set = set()

        body_list = [(b["x"],b["y"]) for b in body]
        #tail should move - not considering eating food
        body_list = body_list[:-1]

        #left
        x1,y1 = x0-1,y0
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("left")
            if not possible_head_to_head_die(my_next_head_coord, body):
                safer_move_set.add("left")
        
        #right
        x1,y1 = x0+1,y0
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("right")
            if not possible_head_to_head_die(my_next_head_coord, body):
                safer_move_set.add("right")
        
        #up
        x1,y1 = x0,y0+1
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("up")
            if not possible_head_to_head_die(my_next_head_coord, body):
                safer_move_set.add("up")
        
        #down
        x1,y1 = x0,y0-1
        my_next_head_coord = x1,y1
        if my_next_head_coord not in body_list:
            move_set.add("down")
            if not possible_head_to_head_die(my_next_head_coord, body):
                safer_move_set.add("down")

        return move_set, safer_move_set

    #main
    my_head = game_state["you"]["body"][0]
    head_coord = (my_head["x"], my_head["y"])
    next_head_coord = get_next_head_coord()
    next_move = get_next_move(head_coord, next_head_coord)
    print(f"next_move calc: {next_move}")

    move_set_result = check_border()
    safer_move_set_result = check_border()
    print(f"turn {game_state['turn']}, safer_move_set {safer_move_set_result}")
    for snake in game_state["board"]["snakes"]:
        #game_state snakes include myself, need to exclude it
        snake_head = snake["body"][0]
        if (snake_head["x"], snake_head["y"]) == head_coord:
            continue
        move_set, safer_move_set = check_opponent(snake["body"])
        move_set_result = move_set_result.intersection(move_set)
        safer_move_set_result = safer_move_set_result.intersection(safer_move_set)
        print(f"turn {game_state['turn']}, name {snake['name']}, safer_move_set {safer_move_set_result}")
    move_set, safer_move_set = check_self(game_state["you"]["body"])
    move_set_result = move_set_result.intersection(move_set)
    safer_move_set_result = safer_move_set_result.intersection(safer_move_set)

    danger_set = move_set_result - safer_move_set_result
    print(f"turn {game_state['turn']}, head {head_coord}, move_set {move_set_result}, safer_move_set {safer_move_set_result}, danger_set {danger_set}")
    if next_move in move_set_result:
        if next_move in danger_set:
            #next_move can cause a head-to-head die, but not deterministic
            if len(safer_move_set_result) != 0:
                next_move = next(iter(safer_move_set_result))
            else:
                #keep next_move
                pass
        else:
            #no doubt, move in routine
            pass
    else:
        if len(move_set_result) == 0:
            #no move set, will die
            pass
        else:
            #planned move not possible, choose the first dir allowed
            next_move = next(iter(move_set_result))
    print(f"next_move final: {next_move}")

    return {"move": next_move}


def move4(game_state: typing.Dict) -> typing.Dict:
    """
    move in a square area
    following an area filling path
    the area has a dimension of n x m
    where n is an even number
    so that the path can close
    start with 4x3
    then 4x4, 4x5, 4x6
    then 6x5, 6x6, 6x7, 6x8
    then 8x7, ...
    """


    def valid_area(area: typing.Tuple) -> bool:
        ((x1,y1), (x2,y2)) = area
        if not 0 <= x2 < game_state["board"]["width"]:
            return False
        if not 0 <= y2 < game_state["board"]["height"]:
            return False
        return True

    def body_in_area(area: typing.Tuple) -> bool:
        ((x1,y1), (x2,y2)) = area
        for cell in game_state["you"]["body"]:
            x = cell["x"]
            y = cell["y"]
            if not x1 <= x <= x2:
                return False
            if not y1 <= y <= y2:
                return False
        return True

    area_width = 4
    area_height = 4

    def four_corner() -> typing.List:
        x1,y1 = (0, 0)
        x2,y2 = x1+area_width-1, y1+area_height-1
        bottom_left_corner = ((x1,y1), (x2,y2))
        x1,y1 = (game_state["board"]["width"]-area_width, 0)
        x2,y2 = x1+area_width-1, y1+area_height-1
        bottom_right_corner = ((x1,y1), (x2,y2))
        x1,y1 = (0, game_state["board"]["height"]-area_height)
        x2,y2 = x1+area_width-1, y1+area_height-1
        top_left_corner = ((x1,y1), (x2,y2))
        x1,y1 = (game_state["board"]["width"]-area_width, game_state["board"]["height"]-area_height)
        x2,y2 = x1+area_width-1, y1+area_height-1
        top_right_corner = ((x1,y1), (x2,y2))
        return [
            bottom_left_corner,
            bottom_right_corner,
            top_left_corner,
            top_right_corner,
        ]

    def all_containing_area() -> typing.List:
        all_area = []
        for x1 in range(game_state["board"]["width"]):
            for y1 in range(game_state["board"]["height"]):
                #bottom-left corner (x1,y1)
                x2 = x1+area_width-1
                y2 = y1+area_height-1
                area = ((x1,y1), (x2,y2))
                if not valid_area(area):
                    continue
                if body_in_area(area):
                    print(f"my_print moving area: {area}, turn: {game_state['turn']}, length: {game_state['you']['length']}")
                    all_area.append(area)
        return all_area

    def target_corner() -> typing.Tuple:
        body_center_x = sum([cell["x"] for cell in game_state["you"]["body"]]) / game_state["you"]["length"]
        body_center_y = sum([cell["y"] for cell in game_state["you"]["body"]]) / game_state["you"]["length"]
        corners = four_corner()

        def sort_corner(corner: typing.Tuple):
            ((x1,y1), (x2,y2)) = corner
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            return math.sqrt((xc-body_center_x)**2+(yc-body_center_y)**2)

        corners = sorted(corners, key=sort_corner)
        return corners[0]

    def get_area() -> typing.Tuple:
        """
        get a rectangular area depend on the snake initial position
        so that even when the snake moves, the area doesn't change
        """
        x_blocks = game_state["board"]["width"]//area_width
        if game_state["board"]["width"] % area_width != 0:
            x_blocks += 1
        y_blocks = game_state["board"]["height"]//area_height
        if game_state["board"]["height"] % area_height != 0:
            y_blocks += 1

        #prefer four corner
        for area in four_corner():
            if body_in_area(area):
                print(f"my_print fixed area: {area}, turn: {game_state['turn']}, length: {game_state['you']['length']}")
                return area

        #if not in one of four corners, find one close to it,
        #so that the area will move to the closest corner

        #if not found then find the first area that contains the snake
        #this can move so that next time will find a fixed area
        target = target_corner()
        areas = all_containing_area()

        def sort_area(area: typing.Tuple):
            ((x1,y1), (x2,y2)) = area
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            ((target_x1, target_y1), (target_x2, target_y2)) = target
            target_xc = (target_x1+target_x2)/2
            target_yc = (target_y1+target_y2)/2
            return math.sqrt((xc-target_xc)**2+(yc-target_yc)**2)

        areas = sorted(areas, key=sort_area)
        return areas[0]

    def order_4x3() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (0,2),
            (0,1),
        ]

    def order_4x4() -> typing.List:
        return [
            (0,0),
            (1,0),
            (2,0),
            (3,0),
            (3,1),
            (3,2),
            (3,3),
            (2,3),
            (2,2),
            (2,1),
            (1,1),
            (1,2),
            (1,3),
            (0,3),
            (0,2),
            (0,1),
        ]

    def get_next_move(head_coord: typing.Tuple, next_head_coord: typing.Tuple) -> str:
        x,y = head_coord
        nx,ny = next_head_coord
        if nx > x:
            return "right"
        if nx < x:
            return "left"
        if ny > y:
            return "up"
        return "down"

    #1. determine the area dimension corners
    # determine my position dirs
    area = get_area()
    corner1 = area[0]
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
    head_coord = (my_head["x"], my_head["y"])
    neck_coord = (my_neck["x"], my_neck["y"])
    normalized_head_coord = (head_coord[0]-corner1[0], head_coord[1]-corner1[1])
    normalized_neck_coord = (neck_coord[0]-corner1[0], neck_coord[1]-corner1[1])
    order_list = order_4x4()
    for head_pos in range(len(order_list)):
        if normalized_head_coord == order_list[head_pos]:
            break
    next_head_pos = head_pos+1
    next_head_pos %= len(order_list)
    if normalized_neck_coord == order_list[next_head_pos]:
        next_head_pos = head_pos-1
    next_head_pos %= len(order_list)
    next_move = get_next_move(order_list[head_pos], order_list[next_head_pos])
    return {"move": next_move}

def move3(game_state: typing.Dict) -> typing.Dict:

    """
    move on a square orbit
    """

    def on_orbit(game_state: typing.Dict) -> bool:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        x_boarder = [game_state["margin"]-1, game_state["board"]["width"]-game_state["margin"]]
        y_boarder = [game_state["margin"]-1, game_state["board"]["height"]-game_state["margin"]]
        if my_head["x"] == my_neck["x"]:
            if my_head["x"] in x_boarder:
                return True
        if my_head["y"] == my_neck["y"]:
            if my_head["y"] in y_boarder:
                return True
        return False

    def orbit_corners(game_state: typing.Dict):
        x_boarder = [game_state["margin"]-1, game_state["board"]["width"]-game_state["margin"]]
        y_boarder = [game_state["margin"]-1, game_state["board"]["height"]-game_state["margin"]]
        corners = [(x,y) for x in x_boarder for y in y_boarder]
        return corners

    def at_corner(game_state: typing.Dict) -> bool:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        return (my_head["x"], my_head["y"]) in orbit_corners(game_state)

    def current_dir(game_state: typing.Dict) -> str:
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        if my_head["x"] - my_neck["x"] == 1:
            return "right"
        if my_head["x"] - my_neck["x"] == -1:
            return "left"
        if my_head["y"] - my_neck["y"] == 1:
            return "up"
        return "down"

    def corner_move(game_state: typing.Dict) -> str:
        #assume on orbit and head at corner
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        if my_head["x"]-my_neck["x"] == 1:
            if my_head["y"] == game_state["margin"]-1:
                return "up"
            return "down"
        if my_head["x"]-my_neck["x"] == -1:
            if my_head["y"] == game_state["margin"]-1:
                return "up"
            return "down"
        if my_head["y"]-my_neck["y"] == 1:
            if my_head["x"] == game_state["margin"]-1:
                return "right"
            return "left"
        #if my_head["y"]-my_neck["y"] == -1:
        if my_head["x"] == game_state["margin"]-1:
            return "right"
        return "left"

    def right_case(game_state: typing.Dict) -> str:
        # current_dir is right
        # not on orbit
        x_boarder = [game_state["margin"]-1, game_state["board"]["width"]-game_state["margin"]]
        y_boarder = [game_state["margin"]-1, game_state["board"]["height"]-game_state["margin"]]
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        if my_head["y"] <= y_boarder[0]:
            if my_head["x"] < x_boarder[0]:
                return "right"
            return "up"
        if my_head["y"] >= y_boarder[1]:
            if my_head["x"] < x_boarder[0]:
                return "right"
            return "down"
        # y in the middle part
        if my_head["x"] < x_boarder[0]:
            return "right"
        if my_head["x"] == x_boarder[0]:
            #return "down"
            return "up"
        if my_head["x"] < x_boarder[1]:
            return "right"
        return "up"

    def left_case(game_state: typing.Dict) -> str:
        # current_dir is left
        # not on orbit
        x_boarder = [game_state["margin"]-1, game_state["board"]["width"]-game_state["margin"]]
        y_boarder = [game_state["margin"]-1, game_state["board"]["height"]-game_state["margin"]]
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        if my_head["y"] <= y_boarder[0]:
            if my_head["x"] > x_boarder[1]:
                return "left"
            return "up"
        if my_head["y"] >= y_boarder[1]:
            if my_head["x"] > x_boarder[1]:
                return "left"
            return "down"
        # y in the middle part
        if my_head["x"] > x_boarder[1]:
            return "left"
        if my_head["x"] == x_boarder[1]:
            #return "down"
            return "up"
        if my_head["x"] > x_boarder[0]:
            return "left"
        return "up"

    def up_case(game_state: typing.Dict) -> str:
        # current_dir is up
        # not on orbit
        x_boarder = [game_state["margin"]-1, game_state["board"]["width"]-game_state["margin"]]
        y_boarder = [game_state["margin"]-1, game_state["board"]["height"]-game_state["margin"]]
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        if my_head["x"] <= x_boarder[0]:
            if my_head["y"] < y_boarder[0]:
                return "up"
            return "right"
        if my_head["x"] >= x_boarder[1]:
            if my_head["y"] > y_boarder[1]:
                return "up"
            return "left"
        # x in the middle part
        if my_head["y"] < y_boarder[0]:
            return "up"
        if my_head["y"] == y_boarder[0]:
            #return "down"
            return "left"
        if my_head["y"] > y_boarder[0]:
            return "up"
        return "left"

    def down_case(game_state: typing.Dict) -> str:
        # current_dir is down
        # not on orbit
        x_boarder = [game_state["margin"]-1, game_state["board"]["width"]-game_state["margin"]]
        y_boarder = [game_state["margin"]-1, game_state["board"]["height"]-game_state["margin"]]
        my_head = game_state["you"]["body"][0]  # Coordinates of your head
        my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
        if my_head["x"] <= x_boarder[0]:
            if my_head["y"] > y_boarder[1]:
                return "down"
            return "right"
        if my_head["x"] >= x_boarder[1]:
            if my_head["y"] > y_boarder[1]:
                return "down"
            return "left"
        # x in the middle part
        if my_head["y"] > y_boarder[1]:
            return "down"
        if my_head["y"] == y_boarder[1]:
            #return "down"
            return "left"
        if my_head["y"] > y_boarder[0]:
            return "down"
        return "left"

def get_up_coord(head_coord: dict[str, int]) -> dict[str, int]:
    if "x" not in head_coord.keys() or "y" not in head_coord.keys():
        raise ValueError(f"head_coord must have both 'x' and 'y' keys: {head_coord}")

    return {"x": head_coord["x"], "y": head_coord["y"] + 1}

    
    #orbit on a square route

    #my var
    game_state["margin"] = 3

    if on_orbit(game_state):
        if not at_corner(game_state):
            return { "move": current_dir(game_state) }
        # at corner
        return { "move": corner_move(game_state) }
    #not on orbit
    move = "left"
    if current_dir(game_state) == "right":
        move = right_case(game_state)
    elif current_dir(game_state) == "left":
        move = left_case(game_state)
    elif current_dir(game_state) == "up":
        move = up_case(game_state)
    elif current_dir(game_state) == "down":
        move = down_case(game_state)

    return { "move": move }
    
# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move2(game_state: typing.Dict) -> typing.Dict:

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    #redeploy
    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    if my_head["x"] == 0:
        is_move_safe["left"] = False
    elif my_head["x"] == board_width - 1:
        is_move_safe["right"] = False
    if my_head["y"] == 0:
        is_move_safe["down"] = False
    elif my_head["y"] == board_height - 1:
        is_move_safe["up"] = False

    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
    my_body = game_state['you']['body']
    for i in range(1, len(my_body)):
        if my_head["x"] == my_body[i]["x"] and my_head["y"] == my_body[i]["y"]:
            if my_head["x"] < my_body[i]["x"]:
                is_move_safe["left"] = False
            elif my_head["x"] > my_body[i]["x"]:
                is_move_safe["right"] = False
            elif my_head["y"] < my_body[i]["y"]:
                is_move_safe["down"] = False
            elif my_head["y"] > my_body[i]["y"]:
                is_move_safe["up"] = False

    # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    opponents = game_state['board']['snakes']

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # Choose a random move from the safe ones
    #next_move = random.choice(safe_moves)
    if len(my_body) <= 20:
        if my_head["x"] < my_neck["x"] and my_head["x"] >= board_width // 2:
            next_move = "left"
        elif my_head["x"] > my_neck["x"] and my_head["x"] <= board_width // 2:
            next_move = "right"
        elif my_head["y"] < my_neck["y"] and my_head["y"] >= board_height // 2:
            next_move = "down"
        elif my_head["y"] > my_neck["y"] and my_head["y"] <= board_height // 2:
            next_move = "up"
        else:
            next_move = safe_moves[0]
    else:
        next_move = safe_moves[0]

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    # food = game_state['board']['food']

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}
