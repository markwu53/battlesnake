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

def get_up_coord(head_coord: dict[str, int]) -> dict[str, int]:
    if "x" not in head_coord.keys() or "y" not in head_coord.keys():
        raise ValueError(f"head_coord must have both 'x' and 'y' keys: {head_coord}")

    return {"x": head_coord["x"], "y": head_coord["y"] + 1}

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

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


    def check_self(body: typing.List) -> typing.Set:
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

        return move_set

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

    move_set_result: typing.Set = check_border()
    safer_move_set_result: typing.Set = check_border()
    for body in [s["body"] for s in game_state["board"]["snakes"]]:
        move_set, safer_move_set = check_opponent(body)
        move_set_result = move_set_result.intersection(move_set)
        safer_move_set_result = safer_move_set_result.intersection(safer_move_set)
    move_set = check_self(game_state["you"]["body"])
    move_set_result = move_set_result.intersection(move_set)
    safer_move_set_result = safer_move_set_result.intersection(move_set)

    danger_set = move_set_result - safer_move_set_result
    if next_move in move_set_result:
        if next_move in danger_set:
            #prefer risk
            pass
        else:
            #no doubt
            pass
    else:
        if len(move_set_result) == 0:
            pass
        else:
            next_move = next(iter(move_set_result))
    print(f"next_move final: {next_move}")

    return {"move": next_move}
