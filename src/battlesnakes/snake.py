import typing
import snake_1vn
import functional
import functional2

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

    if functional.special_experimenting_code(game_state): return {"move": game_state["next_move"]}
    if functional2.special_experimenting_code(game_state): return {"move": game_state["next_move"]}
    return snake_1vn.snake_1vn(game_state)
