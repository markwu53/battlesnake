import random
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


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")




def move_work_in_progress(game_state: typing.Dict) -> typing.Dict:
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
            #2 opponents
            return (4,4)
        #only 1 opponent
        return (4,5)

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
        
    def opponents():
        my_head = game_state["you"]["body"][0]
        snakes = [s for s in game_state["board"]["snakes"] 
                if ( s["body"][0]["x"], s["body"][0]["x"]) != (my_head["x"], my_head["y"]) ]
        return snakes

    def head_in_a_quadrant(head) -> bool:
        #head can be in a quadrant or in the middle line
        if head["x"] == game_state["board"]["width"] //2:
            return False
        if head["y"] == game_state["board"]["height"] //2:
            return False
        return True
    
    def head_quadrant(head) -> typing.Tuple:
        if head["x"] < (game_state["board"]["width"] //2):
            xx = 0
        else:
            xx = 1
        if head["y"] < (game_state["board"]["height"] //2):
            yy = 0
        else:
            yy = 1
        return (xx, yy)
    
    def opponent_head_count_in_quadrant(q):
        snakes = opponents()
        snake_heads = [s["body"][0] for s in snakes]
        snake_heads = [sh for sh in snake_heads if head_in_a_quadrant(sh)]
        snake_heads = [sh for sh in snake_heads if head_quadrant(sh) == q]
        return len(snake_heads)

    def quadrant_order():
        #counterclockwise
        return [
            (0,0),
            (1,0),
            (1,1),
            (0,1),
        ]

    def next_quadrant(q):
        qs = quadrant_order()
        next_quadrant_dict = {a:b for a,b in zip(qs, qs[1:]+[qs[0]])}
        return next_quadrant_dict[q]

    def resolve_head_in_middle(head):
        if head["x"] < game_state["board"]["width"] //2:
            return (0,0)
        if head["x"] > game_state["board"]["width"] //2:
            return (1,1)
        if head["y"] < game_state["board"]["height"] //2:
            return (1,0)
        if head["y"] > game_state["board"]["height"] //2:
            return (0,1)
        return (0,0)

    def quadrant_area(q):
        x,y = q
        if x == 0:
            x1 = 1
        else:
            x2 = game_state["board"]["width"] -2
            x1 = x2 - area_dim()[0]+1
        if y == 0:
            y1 = 1
        else:
            y2 = game_state["board"]["height"] -2
            y1 = y2 - area_dim()[1]+1

        x2 = x1 + area_dim()[0]-1
        y2 = y1 + area_dim()[1]-1
        return ((x1,y1), (x2,y2))

    def food_target(area) -> typing.Tuple:

        my_head = game_state["you"]["body"][0]
        ((x1,y1), (x2,y2)) = area
        foods = game_state["board"]["food"]
        foods = [f for f in foods if x1<=f["x"]<=x2 and y1<=f["y"]<=y2]
        food_density = len(foods)
        food_dist = [abs(f["x"]-my_head["x"])+abs(f["y"]-my_head["y"]) for f in foods]
        min_dist = 100 if len(food_dist) == 0 else min(food_dist)

        return (food_density, 100-min_dist)

    def calc_target_area():

        ################################################
        # if health is good, only move when it's too crowded
        ################################################

        if game_state["you"]["health"] >= 30:
            my_head = game_state["you"]["body"][0]
            if head_in_a_quadrant(my_head):
                quadrant = head_quadrant(my_head)
                count = opponent_head_count_in_quadrant(quadrant)
                if count >= 2:
                    #too crowded --> move to diagonal opposite corner
                    area = quadrant_area(next_quadrant(quadrant))
                else:
                    #stay
                    area = quadrant_area(quadrant)
            else:
                #resolve head in the middle line
                area = quadrant_area(resolve_head_in_middle(my_head))
            return area

        ################################################
        # if health is bad, find food
        ################################################

        #health < 30 ---> find food
        dimx, dimy = area_dim()
        all_areas = [((x,y), (x+dimx-1,y+dimy-1)) 
                     for x in range(game_state["board"]["width"])
                     for y in range(game_state["board"]["height"]) ]
        all_valid_areas = [a for a in all_areas if valid_area(a)]
        areas_sorted = sorted(all_valid_areas, key=food_target, reverse=True)
        area = areas_sorted[0]
        return area

    def get_area() -> typing.Tuple:
        """
        get a rectangular area depend on the snake initial position
        so that even when the snake moves, the area doesn't change
        """

        target = calc_target_area()
        game_state["debug_target"] = target

        if body_in_area(target, game_state["you"]["body"]):
            return target

        areas = all_containing_area()

        def sort_area_to_target(area: typing.Tuple):
            ((x1,y1), (x2,y2)) = area
            ((xx1,yy1), (xx2,yy2)) = target
            dist = abs(x1-xx1)+abs(y1-yy1)
            return dist

        areas = sorted(areas, key=sort_area_to_target)
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
        if abs(x1-x0)+abs(y1-y0) == 1:
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
    
    log_move = f"next_move final: {next_move}"
    log_turn = f"turn: {game_state['turn']}"
    log_head = f"my pos: {game_state['you']['body'][0]}"
    log_health = f"health: {game_state['you']['health']}"
    log_target =f"target: {game_state['debug_target']}"
    log_snakes = [s["name"] for s in opponents()]
    log_snakes = "|".join(log_snakes)
    log_opponents = f"oppo: {log_snakes}"
    log = ", ".join([
        log_move,
        log_turn,
        log_head,
        log_health,
        log_target,
        log_opponents,
    ])

    if game_state["you"]["health"] < 40:
        print(log)

    return {"move": next_move}


#this is a good move that give me 6719 #83 in leaderboard
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
