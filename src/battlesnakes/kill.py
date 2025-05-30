board = {'id': '72f21fbf-c634-4604-9f35-443f0eb96feb', 'turn': 351, 'food': [(7, 0), (10, 6)], 'snakes': [{'name': 'MattIPv6', 'health': 81, 'body': [(5, 0), (4, 0), (4, 1), (3, 1), (3, 2), (2, 2), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5), (2, 4), (2, 3), (3, 3), (3, 4), (3, 5), (3, 6), (2, 6), (1, 6), (0, 6), (0, 7), (0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8)]}, {'name': 'mark_snake', 'health': 69, 'body': [(9, 8), (9, 7), (9, 6), (9, 5), (9, 4), (9, 3), (9, 2), (9, 1), (8, 1), (7, 1), (6, 1), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5)]}]}

board_width = board_height = 11

my_name = "mark_snake"
my_snake = [snake for snake in board["snakes"] if snake["name"] == my_name][0]
the_other = [snake for snake in board["snakes"] if snake["name"] != my_name][0]

def on_border(p):
    x,y = p
    if x == 0 or x == board_width -1:
        return True
    if y == 0 or y == board_height -1:
        return True
    return False

def distance_pq(p, q):
    x1,y1 = p
    x2,y2 = q
    return abs(x1-x2) + abs(y1-y2)

def is_adjacent(p, q):
    return distance_pq(p, q) == 1

def dir_pq(p, q):
    assert(is_adjacent(p, q))
    x1,y1 = p
    x2,y2 = q
    if x1 - x2 == 1: return "left"
    if x1 - x2 == -1: return "right"
    if y1 - y2 == 1: return "down"
    if y1 - y2 == -1: return "up"
    raise(ValueError("dir_pq"))

def entering_kill():
    #the other snake head is on border
    #one of my body cell is adjacent to the other snake head at off-border position
    #they moving in the same dir
    my_body = my_snake["body"]
    head = the_other["body"][0]
    neck = the_other["body"][1]
    if not on_border(head):
        return False
    length = len(my_snake["body"])
    assert(length >= 4)
    found = False
    for i, cell in enumerate(my_snake["body"]):
        if i in range(3, length-1) and not on_border(cell):
            if is_adjacent(cell, head):
                found = True
                break
    if not found:
        return False
    if dir_pq(my_body[i], my_body[i-1]) != dir_pq(neck, head):
        return False

    return True

def kill_action_performed():
    return any([on_border(cell) for cell in my_snake["body"]])

def kill_condition():
    if len(board["snakes"]) != 2:
        return False
    if not entering_kill():
        return False
    if kill_action_performed():
        return False
    return True