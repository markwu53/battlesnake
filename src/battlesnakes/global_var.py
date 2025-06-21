class Game:
    state = None #game_state
    logger = {} #print everything in it
    board = {}
    me = {}
    others = []
    snakes = []
    my_head = None
    my_neck = None
    my_tail = None
    other_head = None
    other_neck = None
    other_tail = None
    my_length = None
    other_length = None
    node = None #current node
    env = {} #decision supporting
    dn = {} #decision_tree nodes

class Node:
    def __init__(self, question_description):
        self.question_description = question_description
        self.gather_info = lambda: None
        self.question = None
        self.yes = None
        self.no = None
        self.moves = None

game = Game()
