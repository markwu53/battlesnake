
algorithm = """
    begin = game_1_vs_1?
    game_1_vs_1+ = mine_bigger?
    game_1_vs_1- = game_1_vs_n
    game_1_vs_n = TODO
    mine_bigger+ = no_danger?
    mine_bigger- = TODO
    no_danger+ = food
    no_danger- = TODO
    food = food_near?
    food_near+ = get_food
    get_food = TODO
    food_near- = chase_tail
    chase_tail = see_my_tail?
    see_my_tail+ = chase_my_tail
    chase_my_tail = TODO
    see_my_tail- = see_enemy_tail?
    see_enemy_tail+ = chase_enemy_tail
    chase_enemy_tail = TODO
    see_enemy_tail- = no_tail
    no_tail = TODO
    """

def nothing():
    # Placeholder for a function that does nothing
    pass

class Node:
    def __init__(self, question_description):
        self.question_description = question_description
        self.gather_info = nothing
        self.question = None
        self.yes = None
        self.no = None
        self.moves = None

def run():
    nodes = {}
    rules = algorithm.split("\n")
    rules = [r.strip() for r in rules if len(r.strip()) > 0]
    rules = [r for r in rules if not r.startswith("#")]
    rules = [r.split("=") for r in rules]
    rules = [(a.strip(),b.strip()) for a, b in rules]
    #for rule in rules: print(rule)
    root = None
    for a, b in rules:
        if "?" in b:
            b = b.replace("?", "")
        nodes[b] = Node(b)
    for a, b in rules:
        if "?" in b:
            b = b.replace("?", "")
        if "+" in a:
            a = a.replace("+", "")
            nodes[a].yes = nodes[b]
        elif "-" in a:
            a = a.replace("-", "")
            nodes[a].no = nodes[b]
        elif a == "begin":
            root = nodes[b]
        else:
            nodes[a].yes = nodes[b]
            nodes[a].no = nodes[b]
    return root

if __name__ == "__main__":
    run()

