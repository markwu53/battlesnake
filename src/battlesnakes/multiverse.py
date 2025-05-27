import random
import itertools
import copy

board_width = 11
board_height = 11

def order_to_position(ord):
    return ord % board_width, ord // board_width

def is_cell_occupied(board, pos):
    return any([pos in snake["body"] for snake in board["snakes"]])

def is_pos_on_board(pos):
    x,y = pos
    return (0 <= x < board_width
            and 0 <= y < board_height)

def order_to_dir(ord):
    if ord == 0: return "right"
    if ord == 1: return "up"
    if ord == 2: return "left"
    if ord == 3: return "down"
    raise(ValueError("order_to_dir"))

def dir_position(p, dir):
    x,y = p
    if dir == "right": return (x+1,y)
    if dir == "up": return (x,y+1)
    if dir == "left": return (x-1,y)
    if dir == "down": return (x,y-1)
    raise(ValueError("dir_position"))

def distance_pq(p, q):
    x1,y1 = p
    x2,y2 = q
    return abs(x1-x2)+abs(y1-y2)

def create_food(board):

    food = []
    while len(food) < 10:
        pos = order_to_position(random.randint(0, board_width*board_height-1))
        while is_cell_occupied(board, pos) or pos in food:
            pos = order_to_position(random.randint(0, board_width*board_height-1))
        food.append(pos)
    return food

def create_snake(board):

    snake = {}

    length = random.randint(3,10)
    health = random.randint(90,100)
    snake["health"] = health
    snake["body"] = []

    head = order_to_position(random.randint(0,board_width*board_height-1))
    while True:
        if is_cell_occupied(board, head):
            head = order_to_position(random.randint(0,board_width*board_height-1))
            continue
        if len(board["snakes"]) != 0:
            head0 = board["snakes"][0]["body"][0]
            if distance_pq(head0, head) % 2 != 0:
                head = order_to_position(random.randint(0,board_width*board_height-1))
                continue
        break
    snake["body"].append(head)

    tail = head
    attempts = 0
    while len(snake["body"]) < length:
        new_tail = dir_position(tail, order_to_dir(random.randint(0,3)))
        while (1==0 
               or (not is_pos_on_board(new_tail))
               or is_cell_occupied(board, new_tail) 
               or new_tail in snake["body"]):
            attempts += 1
            if attempts > 10000:
                raise(ValueError("create_snake: cannot create snake"))
            new_tail = dir_position(tail, order_to_dir(random.randint(0,3)))

        tail = new_tail
        snake["body"].append(tail)

    return snake


def init_board():
    board = {}
    board["snakes"] = []
    for i in range(4):
        snake = create_snake(board)
        snake["id"] = i
        board["snakes"].append(snake)
    board["food"] = create_food(board)
    return board

def adjacent_cells(p):
    x,y = p
    cells = [
        (x+1,y),
        (x,y+1),
        (x-1,y),
        (x,y-1),
    ]
    return [c for c in cells if is_pos_on_board(c)]

def allowed_moves(board, head):
    next_occupied_cells = []
    for snake in board["snakes"]:
        if snake["health"] == 100:
            next_occupied_cells += snake["body"]
        else:
            next_occupied_cells += snake["body"][:-1]
    return [c for c in adjacent_cells(head) if not c in next_occupied_cells]

def next_board(board, combined_move):
    nboard = copy.deepcopy(board)
    for (nhead, id), snake in zip(combined_move, nboard["snakes"]):
        snake["live"] = False
        if snake["health"] == 100:
            snake["body"] = [nhead] + snake["body"]
        else:
            snake["body"] = [nhead] + snake["body"][:-1]
        if nhead in nboard["food"]:
            snake["health"] = 100
            nboard["food"] = [f for f in nboard["food"] if f != nhead]
        else:
            snake["health"] = snake["health"]-1

    #resolve collision
    for pos, id in combined_move:
        colliding_snakes = [snake for snake in nboard["snakes"] if snake["body"][0] == pos]
        max_length = max([len(snake["body"]) for snake in colliding_snakes])
        max_length_snakes = [snake for snake in colliding_snakes if len(snake["body"]) == max_length]
        if len(max_length_snakes) == 1:
            snake = max_length_snakes[0]
            snake["live"] = True
    nboard["snakes"] = [snake for snake in nboard["snakes"] if snake["live"]]
    return nboard

def evolve_board(board):

    xboard = copy.deepcopy(board)
    for snake in xboard["snakes"]:
        snake_head = snake["body"][0]
        snake["allowed_moves"] = allowed_moves(xboard, snake_head)

    #remove snakes that run out of moves
    #throw_out = [snake["id"] for snake in xboard["snakes"] if len(snake["allowed_moves"]) == 0]
    #if len(throw_out) != 0: print(f"throw out {throw_out}")
    xboard["snakes"] = [snake for snake in xboard["snakes"] if len(snake["allowed_moves"]) != 0]
    snake_moves = [[(move, snake["name"]) for move in snake["allowed_moves"]] for snake in xboard["snakes"]]
    combined_moves = [config for config in itertools.product(*snake_moves)]
    #print(len(combined_moves))

    branching = [(combined_move, next_board(xboard, combined_move)) for combined_move in combined_moves]
    return branching

log = {
"food": [(0, 1)], 
"snakes": [{'name': 'Rusty the Hungry Sneke', 'id': 'gs_krj7SbPJ4gqRq4gjXPbCWRhK', 'health': 96, 'body': [(1, 5), (1, 6), (1, 7), (1, 8), (1, 9)]}, {'name': 'the evening and the morning', 'id': 'gs_wCqP4B7BW7tDxTKPtqjCFWFJ', 'health': 90, 'body': [(3, 5), (4, 5), (4, 6), (5, 6), (5, 7)]}, {'name': 'mark_snake', 'id': 'gs_bQMJ8gQMgDRqm7pxpGdSQhfB', 'health': 86, 'body': [(1, 3), (2, 3), (3, 3), (4, 3)]}, {'name': 'Barry', 'id': 'gs_bBjh4FYHdd9KfjJT7SwYYtX9', 'health': 90, 'body': [(3, 9), (3, 10), (4, 10), (5, 10), (5, 9)]}]
}
log = {
    "food": [(9, 1)], 
    "snakes": [{'name': 'Rusty the Hungry Sneke', 'id': 'gs_krj7SbPJ4gqRq4gjXPbCWRhK', 'health': 84, 'body': [
        (3, 1), (2, 1), (2, 2), (2, 3), (2, 4)]}, 
        {'name': 'the evening and the morning', 'id': 'gs_wCqP4B7BW7tDxTKPtqjCFWFJ', 'health': 100, 'body': [
            (10, 2), (9, 2), (8, 2), (7, 2), (6, 2)]}, 
            {'name': 'mark_snake', 'id': 'gs_bQMJ8gQMgDRqm7pxpGdSQhfB', 'health': 91, 'body': [(8, 0), (7, 0), (6, 0), (5, 0), (4, 0)]}, 
            {'name': 'Barry', 'id': 'gs_bBjh4FYHdd9KfjJT7SwYYtX9', 'health': 78, 'body': [(7, 3), (6, 3), (5, 3), (4, 3), (4, 4)]}]
}
log = {
    "food": [(1, 5)], 
    "snakes": [
        {'name': 'Jazz snake', 'id': 'gs_JyjyYrhBJwwhFdWdXTMGgJtC', 
         'health': 98, 'body': [(6, 10), (5, 10), (4, 10), (4, 9), (4, 8), (3, 8), (3, 9)]}, 
         {'name': 'exp-field-snake', 'id': 'gs_BWTr7tK3Bdgfp84RhSjJm6cB', 
          'health': 94, 'body': [(8, 8), (7, 8), (6, 8), (6, 7), (6, 6), (6, 5)]}, 
          {'name': 'mark_snake', 'id': 'gs_vdhhmYC6hTbMQbXrRqxxyJcV', 
           'health': 94, 'body': [(5, 7), (5, 6), (5, 5), (4, 5), (4, 4), (5, 4), (5, 3)]}, 
           {'name': 'pforsythe-battlesnake', 'id': 'gs_r7PRcRHGtyfm3Xkjk6HDRK9c', 
            'health': 100, 'body': [(0, 6), (1, 6), (2, 6), (3, 6), (3, 6)]}]
}

my_name = "mark_snake"

def run():

    #board0 = init_board()
    board0 = log
    n_evolve = 3
    path_result = [[result] for result in evolve_board(board0)]
    for it in range(n_evolve-1):
        path_result = [
            path+[result] 
                 for path in path_result for _,board in [path[-1]]
                    for result in evolve_board(board)
                 ]
    print(len(path_result))

    """
    path_result = [
        ((move1, board1), (move2, board2), (move3, board3))
        for move1, board1 in evolve_board(board0)
            for move2, board2 in evolve_board(board1)
                for move3, board3 in evolve_board(board2)
    ]
    """
    #for path in paths: print(path)

    path_summary = [
        sorted(list(set([
            tuple((
                tuple((move 
                    for move_set,_ in steps[:n]
                    for move,name in move_set
                    if name == my_name
                    )),
                my_name in [snake["name"] for snake in board["snakes"]]
                ))
            for steps in path_result
            for move, board in [steps[n-1]]
            if my_name in [name for m, name in move]
            ])))
        for n in range(1,n_evolve+1)
    ]
    for i in range(n_evolve):
        print(f"step{i+1} new calc")
        for x in path_summary[i]: print(x)


    def survived_level(move):
        step = len(move)
        look = path_summary[step-1]

        if not all([survived for mm, survived in look if mm == move]):
            #die or probability die in this step
            return step

        if step == len(path_summary):
            #the last level
            return 99

        look = path_summary[step] #0-based, this is next step
        next_step_moves = list(set([mm for mm,_ in look if mm[:-1] == move]))
        if len(next_step_moves) == 0:
            return step+1

        return max([survived_level(move) for move in next_step_moves])

    for move, survived in path_summary[0]:
        print(f"{move}, {survived_level(move)}")

run()
