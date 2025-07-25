import typing
import snake_1vn
import functional
import functional2
import simp_entry

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

def dummy(game_state):
    snake_ids = [s["id"] for s in game_state["board"]["snakes"]]
    my_id = game_state["you"]["id"]
    if my_id == snake_ids[0]:
        snake_name = "mark_snake_A"
        color = "#FF0000"
    else:
        snake_name = "mark_snake_B"
        color = "#00BB00"

    return {
        "name": snake_name,
        "color": color,
    }    

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    id = game_state["game"]["id"]
    names = [snake["name"] for snake in game_state["board"]["snakes"]]
    print(f"GAME START {id} {names}")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


def move(game_state: typing.Dict) -> typing.Dict:

    if simp_entry.main(game_state): return {"move": game_state["next_move"]}
    if functional2.special_experimenting_code(game_state): return {"move": game_state["next_move"]}
    if functional.special_experimenting_code(game_state): return {"move": game_state["next_move"]}
    return snake_1vn.snake_1vn(game_state)
