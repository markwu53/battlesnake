import typing
import math
import time

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

def get_up_coord(head_coord: dict[str, int]) -> dict[str, int]:
    if "x" not in head_coord.keys() or "y" not in head_coord.keys():
        raise ValueError(f"head_coord must have both 'x' and 'y' keys: {head_coord}")

    return {"x": head_coord["x"], "y": head_coord["y"] + 1}

def get_direction_coord(direction: str, head_coord: dict[str, int]) -> dict[str, int]:
    if "x" not in head_coord.keys() or "y" not in head_coord.keys():
        raise ValueError(f"head_coord must have both 'x' and 'y' keys: {head_coord}")

    match direction:
        case "up":
            return {"x": head_coord["x"], "y": head_coord["y"] + 1}
        case "down":
            return {"x": head_coord["x"], "y": head_coord["y"] - 1}
        case "left":
            return {"x": head_coord["x"] - 1, "y": head_coord["y"]}
        case "right":
            return {"x": head_coord["x"] + 1, "y": head_coord["y"]}

    raise ValueError(f"invalid direction: {direction}")

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

        def entering_trap(snake):
            #any part of the other snake is on border
            #one of my body cell is adjacent to the other snake that part at off-border position
            #they moving in the same dir
            for i, ic in enumerate(snake["body"]):
                for j, jc in enumerate(my_snake["body"]):
                    if 1 <= j < len(my_snake["body"])-1 and i < len(snake["body"])-1:
                        if on_border(ic) and is_adjacent(ic, jc) and not on_border(jc):
                            if get_adjacent_dir(jc, my_snake["body"][j-1]) == get_adjacent_dir(snake["body"][i+1], ic):
                                return True
            return False

        def kill_action_performed():
            return any([on_border(cell) for cell in my_snake["body"]])

        if not any([entering_trap(snake) for snake in others]):
            return

        if kill_action_performed():
            return

        for snake in others:
            if entering_trap(snake):
                break
        
        #assume only one
        #go to the closest kill position
        #1. It's on border
        #2. It's closer to me than the snake I'm trying to kill
        #3. It has shortest path to the snake head so that fastest kill
        width = game_state["board"]["width"]
        height = game_state["board"]["height"]
        my_head = my_snake["body"][0]
        snake_head = snake["body"][0]
        kill_position = [(x,y) for x in range(width) for y in range(height)]
        kill_position = [p for p in kill_position if on_border(p)]
        kill_position = [p for p in kill_position if distance_pq(p, my_head) < distance_pq(p, snake_head)]

        #nearest to the other so fastest kill
        #min_distance = min([distance_pq(p, snake_head) for p in kill_position])
        #kill_position = [p for p in kill_position if distance_pq(p, snake_head) == min_distance]

        #nearest to me so fastest action
        min_distance = min([distance_pq(p, my_head) for p in kill_position])
        kill_position = [p for p in kill_position if distance_pq(p, my_head) == min_distance]

        #may have more than 1, anyone is good
        target_kill_position = kill_position[0]
        game_state["target_kill_position"] = kill_position
        #route to get there
        if is_adjacent(my_head, target_kill_position):
            game_state["try_kill"].append([target_kill_position])
            return
        #must go to target_kill_position in a perpendicular way
        next_to_target = [p for p in adj_cells(target_kill_position) if not on_border(p)][0]
        if is_adjacent(my_head, next_to_target):
            game_state["try_kill"].append([next_to_target])
            return
        suggest = [p for p in adj_cells(my_head) if distance_pq(p, next_to_target) == distance_pq(my_head, next_to_target)-1]

        #suggest = [p for p in adj_cells(get_my_head()) if on_border(p)]
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
    log_target_kill_pos = game_state["target_kill_position"] if len(game_state["try_kill"]) != 0 else []

    log_board = lean_board()

    log_text = ", ".join([
        f"board: {log_board}",
        f"move: {log_move}",
        f"boxing_area: {log_boxing_area}",
        f"routine_move: {log_routine_move}",
        f"avoid_danger: {log_avoid_danger}",
        f"allowed_move: {log_allowed_move}",
        f"find_food: {log_find_food}",
        f"try_kill: {log_try_kill}, target: {log_target_kill_pos}",
        log_time_diff,
    ])

    print(log_text)

    return {"move": next_move}

