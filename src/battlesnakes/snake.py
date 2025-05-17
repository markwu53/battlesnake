import typing
import math


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


# this is a work in progress
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

    def allowed_move():
        head = get_my_head()
        allowed = permissible_first_step(head)
        allowed = [p for p in allowed if len(permissible_second_step(p)) != 0]
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
        for snake in game_state["board"]["snakes"]:
            #including myself
            if p in get_body_coord(snake["body"]):
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

    def colliding_pattern_1(my_body: typing.List, snake_body: typing.List, colliding_point: typing.Tuple):
        if is_cell_occupied(colliding_point):
            return

        def dir_to_coord(d: str) -> typing.Tuple:
            x,y = get_my_head()
            if d == "left":
                return (x-1, y)
            if d == "right":
                return (x+1, y)
            if d == "up":
                return (x, y+1)
            if d == "down":
                return (x, y-1)

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
                    suggest = [[dir_to_coord(d) for d in g] for g in suggest]
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

    def avoid_danger():
        game_state["avoid_danger"] = []

        my_body = get_body_coord(game_state["you"]["body"])
        for snake in opponent_snakes():
            snake_body = get_body_coord(snake["body"])
            snake_head = snake_body[0]
            my_head = get_my_head()
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

    def find_food():

        game_state["find_food"] = []

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

    def best_choice():

        #routine move always exists and set as default
        game_state["next_head_coord"] = game_state["routine_move"]

        if len(game_state["allowed_move"]) == 0:
            return

        if game_state["next_head_coord"] not in game_state["allowed_move"]:
            game_state["next_head_coord"] = game_state["allowed_move"][0]

        if len(game_state["find_food"]) != 0:
            game_state["next_head_coord"] = game_state["find_food"][0]

        if not off_border(get_my_head()):
            off_border_coord = [p for p in game_state["allowed_move"] if off_border(p)]
            if len(off_border_coord) != 0:
                game_state["next_head_coord"] = off_border_coord[0]

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
                        a,b = suggest
                        if off_border(a):
                            game_state["next_head_coord"] = a
                        elif off_border(b):
                            game_state["next_head_coord"] = b
                        else:
                            game_state["next_head_coord"] = a

                else:
                    #two suggestions
                    #suggest = [[a],[b]]
                    assert(len(suggest) == 2)
                    a,b = suggest
                    a = a[0]
                    b = b[0]
                    if a in game_state["allowed_move"]:
                        game_state["next_head_coord"] = a
                    if b in game_state["allowed_move"]:
                        game_state["next_head_coord"] = b
            elif pattern == "pattern2":
                suggest = [s for s in suggest if s in game_state["allowed_move"]]
                if len(suggest) != 0:
                    game_state["next_head_coord"] = suggest[0]

            if len(game_state["avoid_danger"]) > 1:
                #multiple collisions
                _,__, suggest = game_state["avoid_danger"][0]
                sset = set([p for g in suggest for p in g])
                for _,__, suggest in game_state["avoid_danger"][1:]:
                    sset = sset.intersection(set([p for g in suggest for p in g]))
                suggest = [p for p in sset if p in game_state["allowed_move"]]
                if len(suggest) != 0:
                    game_state["next_head_coord"] = suggest[0]



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
    ])
    print(log_text)

    return {"move": next_move}


