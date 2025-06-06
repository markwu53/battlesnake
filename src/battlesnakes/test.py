game_state = {
    "entered_trap": "good"
}
a = game_state.get("entered_trap", "")
print(f"a: {a}")