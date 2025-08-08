import tkinter as tk
import json
import ast
import os

CELL_SIZE = 45  # adjust cell size based on board size
BOARD_SIZE = 11
CANVAS_SIZE = CELL_SIZE * BOARD_SIZE + 40
MARGIN = 4

GRID_COLOR = "#333"
SNAKE_COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]

class BattleSnakeReplay:
    def __init__(self, root):
        root.geometry("1000x600")
        self.root = root
        self.turn_index = 0
        self.is_playing = False
        self.delay = 100  # milliseconds

        self.board_width = BOARD_SIZE
        self.board_height = BOARD_SIZE

        # Left frame (board + buttons), pinned to top-left
        left_frame = tk.Frame(root, )
        left_frame.pack(side="left", anchor="nw")  # <-- north-west keeps it top-left, no vertical centering!

        # Canvas (board)
        self.canvas = tk.Canvas(left_frame, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="black")
        self.canvas.pack(side="top", anchor="nw")  # pinned to top of left_frame

        # Buttons directly under the board
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(side="bottom", pady=10, )

        # Info frame (right side, fixed height)
        self.info_frame = tk.Frame(root, bg="black", width=500, height=CANVAS_SIZE)
        self.info_frame.pack()
        self.info_frame.pack_propagate(False)

        self.player_labels = []

        #self.turn_label = tk.Label(self.info_frame, text="", fg="white", bg="black", font=("Arial", 16))
        #self.turn_label.pack(anchor="w")
        self.turn_label = tk.Label(self.info_frame, text="", fg="white", bg="black", font=("Arial", 16), width=25, anchor="w")
        self.turn_label.pack(anchor="w")

        tk.Button(btn_frame, text="⏮ Start", command=self.go_start).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏪ Back", command=self.step_back).pack(side="left", padx=5)
        tk.Button(btn_frame, text="▶ Play", command=self.play).pack(side="left", padx=5)
        #tk.Button(btn_frame, text="⏸ Pause", command=self.pause).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏩ Next", command=self.step_forward).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏭ End", command=self.go_end).pack(side="left", padx=5)
        tk.Button(btn_frame, text="RELOAD", command=self.reload).pack(side="left", padx=5)

        # Key bindings
        root.bind("<Left>", lambda e: self.step_back())
        root.bind("<Right>", lambda e: self.step_forward())
        root.bind("<space>", lambda e: self.toggle_play_pause())
        root.bind("<Home>", lambda e: self.go_start())
        root.bind("<End>", lambda e: self.go_end())

        self.game_data = self.load_game_file()
        self.dead_turn_calc()
        # Initial draw
        self.update_display()

    def draw_coordinates(self):
        self.canvas.delete("coords")  # clear old coordinate labels

        # Draw column numbers (x-axis) at top and bottom
        for x in range(BOARD_SIZE):
            coord = str(x)
            px = x * CELL_SIZE + CELL_SIZE // 2
            #self.canvas.create_text(px, -10, text=coord, fill="white", tags="coords")  # top
            self.canvas.create_text(px, BOARD_SIZE * CELL_SIZE + 20, text=coord, fill="white", tags="coords")  # bottom

        # Draw row numbers (y-axis) at left and right
        for y in range(BOARD_SIZE):
            coord = str(10-y)
            py = y * CELL_SIZE + CELL_SIZE // 2
            #self.canvas.create_text(-10, py, text=coord, fill="white", tags="coords")  # left
            self.canvas.create_text(BOARD_SIZE * CELL_SIZE + 20, py, text=coord, fill="white", tags="coords")  # right

    def dead_turn_calc(self):
        names = [snake["name"] for snake in self.game_data[0]["snakes"]]
        self.dead_turn = {name: t2
         for name in names
            for alive in [[(step["turn"], snake["alive"]) for step in self.game_data for snake in step["snakes"] if snake["name"] == name]]
            for ((t1,a1), (t2,a2)) in zip(alive[:-1], alive[1:]) if a1 and not a2
        }

    def draw_grid(self):
        self.canvas.delete("all")
        for x in range(self.board_width):
            for y in range(self.board_height):
                self.canvas.create_rectangle(
                    x*CELL_SIZE, (self.board_height-y-1)*CELL_SIZE,
                    (x+1)*CELL_SIZE, (self.board_height-y)*CELL_SIZE,
                    outline=GRID_COLOR, fill="#222"
                )

    def draw_food(self, turn):
        for fx, fy in turn["food"]:
            self.draw_oval(fx, fy, "#FF5555")

    def draw_snake(self, snake, color):
        for i,cell in enumerate(snake["body"]):
            x, y = cell
            margins = []
            if i == 0:
                x1,y1 = snake["body"][i+1]
                if x1 < x: margins.append("left")
                elif x1 > x: margins.append("right")
                elif y1 < y: margins.append("down")
                elif y1 > y: margins.append("up")
                else:
                    self.draw_snake_cell(x, y, color)
                    continue
                self.draw_snake_head(x,y, color, margins[0])
            elif i == len(snake["body"]) - 1:
                x0,y0 = snake["body"][i-1]
                if x0 < x: margins.append("left")
                elif x0 > x: margins.append("right")
                elif y0 < y: margins.append("down")
                elif y0 > y: margins.append("up")
                else:
                    self.draw_snake_cell(x, y, color)
                    continue
                self.draw_snake_tail(x,y, color, margins[0])
            else:
                self.draw_snake_cell(x, y, color)
                x0,y0 = snake["body"][i-1]
                x1,y1 = snake["body"][i+1]

                if x0 < x: margins.append("left")
                elif x0 > x: margins.append("right")
                elif y0 < y: margins.append("down")
                elif y0 > y: margins.append("up")

                if x1 < x: margins.append("left")
                elif x1 > x: margins.append("right")
                elif y1 < y: margins.append("down")
                elif y1 > y: margins.append("up")
            self.draw_snake_cell_margins(x,y, color, margins)

    def snake_color(self, snake):
        if snake["name"] == "mark_snake_test RED": return "red"
        if snake["name"] == "mark_snake_test BLUE": return "blue"
        if snake["name"] == "mark_snake_test GREEN": return "green"
        if snake["name"] == "mark_snake_test YELLOW": return "yellow"
        return "orange"

    def draw_snakes(self, turn):
        for idx, snake in enumerate(turn["snakes"]):
            if snake["alive"]:
                color = self.snake_color(snake)
                self.draw_snake(snake, color)

    def draw_oval(self, x, y, color):
        x1, y1 = x*CELL_SIZE, (self.board_height-y-1)*CELL_SIZE
        x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
        self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill=color, outline=color)

    def draw_snake_tail(self, x,y, color, adir):
        top_left = x*CELL_SIZE+MARGIN, (self.board_height-y-1)*CELL_SIZE+MARGIN
        top_right = (x+1)*CELL_SIZE-MARGIN, (self.board_height-y-1)*CELL_SIZE+MARGIN
        bottom_left = x*CELL_SIZE+MARGIN, (self.board_height-y)*CELL_SIZE-MARGIN
        bottom_right = (x+1)*CELL_SIZE-MARGIN, (self.board_height-y)*CELL_SIZE-MARGIN
        if adir == "left":
            x1,y1 = top_right
            y1 += CELL_SIZE/2 - MARGIN
            x2,y2 = top_left
            x3,y3 = bottom_left
        elif adir == "right":
            x1,y1 = top_left
            y1 += CELL_SIZE/2 - MARGIN
            x2,y2 = top_right
            x3,y3 = bottom_right
        elif adir == "up":
            x1,y1 = bottom_left
            x1 += CELL_SIZE/2 - MARGIN
            x2,y2 = top_left
            x3,y3 = top_right
        elif adir == "down":
            x1,y1 = top_left
            x1 += CELL_SIZE/2 - MARGIN
            x2,y2 = bottom_left
            x3,y3 = bottom_right
        self.canvas.create_polygon(x1,y1, x2,y2, x3,y3, fill=color)

    def draw_snake_head(self, x,y, color, adir):
        top_left = x*CELL_SIZE+MARGIN, (self.board_height-y-1)*CELL_SIZE+MARGIN
        top_right = (x+1)*CELL_SIZE-MARGIN, (self.board_height-y-1)*CELL_SIZE+MARGIN
        bottom_left = x*CELL_SIZE+MARGIN, (self.board_height-y)*CELL_SIZE-MARGIN
        bottom_right = (x+1)*CELL_SIZE-MARGIN, (self.board_height-y)*CELL_SIZE-MARGIN
        x1,y1 = top_left
        x1,y1 = x1+CELL_SIZE/2-MARGIN, y1+CELL_SIZE/2-MARGIN
        if adir == "left":
            x2,y2 = top_right
            x3,y3 = top_left
            x4,y4 = bottom_left
            x5,y5 = bottom_right
        elif adir == "right":
            x2,y2 = top_left
            x3,y3 = top_right
            x4,y4 = bottom_right
            x5,y5 = bottom_left
        elif adir == "up":
            x2,y2 = bottom_left
            x3,y3 = top_left
            x4,y4 = top_right
            x5,y5 = bottom_right
        elif adir == "down":
            x2,y2 = top_left
            x3,y3 = bottom_left
            x4,y4 = bottom_right
            x5,y5 = top_right
        self.canvas.create_polygon(x1,y1, x2,y2, x3,y3, x4,y4, x5,y5, fill=color)

    def draw_snake_cell_margins(self, x,y, color, margins):
        for side in margins:
            if side == "left":
                x1,y1 = x*CELL_SIZE, (self.board_height-y-1)*CELL_SIZE+MARGIN
                x2, y2 = x1+MARGIN, y1+CELL_SIZE-2*MARGIN
            elif side == "right":
                x1,y1 = (x+1)*CELL_SIZE-MARGIN, (self.board_height-y-1)*CELL_SIZE+MARGIN
                x2, y2 = x1+MARGIN, y1+CELL_SIZE-2*MARGIN
            elif side == "up":
                x1,y1 = x*CELL_SIZE+MARGIN, (self.board_height-y-1)*CELL_SIZE
                x2, y2 = x1+CELL_SIZE-2*MARGIN, y1+MARGIN
            elif side == "down":
                x1,y1 = x*CELL_SIZE+MARGIN, (self.board_height-y)*CELL_SIZE-MARGIN
                x2, y2 = x1+CELL_SIZE-2*MARGIN, y1+MARGIN
            self.canvas.create_rectangle(x1,y1, x2,y2, fill=color, outline="")

    def draw_snake_cell(self, x, y, color):
        x1, y1 = x*CELL_SIZE+MARGIN, (self.board_height-y-1)*CELL_SIZE+MARGIN
        x2, y2 = x1+CELL_SIZE-2*MARGIN, y1+CELL_SIZE-2*MARGIN
        #self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def update_player_info(self, turn):
        # Update turn label in place
        self.turn_label.config(text=f"TURN {turn['turn']}")

        # Clear old player labels
        for lbl in self.player_labels:
            lbl.destroy()
        self.player_labels = []

        # Add player info labels
        for idx, snake in enumerate(turn["snakes"]):
            color = self.snake_color(snake)

            dead_turn = self.dead_turn.get(snake["name"], -1)
            dead_text = f"DEAD at {dead_turn}" if not snake["alive"] else ""
            text = f"{snake['name']}: {dead_text}"
            lbl = tk.Label(
                self.info_frame,
                text=text,
                fg=color,
                bg="black",
                font=("Arial", 14),
                width=60,
                anchor="w"
            )
            lbl.pack(anchor="w", pady=20)
            self.player_labels.append(lbl)

            text = f"Length={snake['length']}, Health={snake['health']} "
            lbl = tk.Label(
                self.info_frame,
                text=text,
                fg=color,
                bg="black",
                font=("Arial", 12),
                width=60,
                anchor="w"
            )

            lbl.pack(anchor="w", pady=5)
            self.player_labels.append(lbl)

    def update_display(self):
        turn = self.game_data[self.turn_index]
        self.draw_grid()
        self.draw_coordinates()
        self.draw_food(turn)
        self.draw_snakes(turn)
        self.update_player_info(turn)

    def step_forward(self):
        if self.turn_index < len(self.game_data)-1:
            self.turn_index += 1
            self.update_display()

    def step_back(self):
        if self.turn_index > 0:
            self.turn_index -= 1
            self.update_display()

    def go_start(self):
        self.turn_index = 0
        self.update_display()

    def go_end(self):
        self.turn_index = len(self.game_data)-1
        self.update_display()

    def play(self):
        self.is_playing = not self.is_playing
        self.auto_play()

    def pause(self):
        self.is_playing = False

    def toggle_play_pause(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def reload(self):
        self.game_data = self.load_game_file()
        self.dead_turn_calc()
        self.turn_index = 0
        self.is_playing = False
        self.update_display()

    def auto_play(self):
        if self.is_playing:
            self.step_forward()
            if self.turn_index < len(self.game_data)-1:
                self.root.after(self.delay, self.auto_play)

    def load_game_file(self):
        filename = "last_game.log"
        data = []
        with open(filename, "r") as f:
            for line in f:
                if line.strip():
                    data.append(ast.literal_eval(line.strip()))  # Safely parse Python dict-style strings
        return data

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Battlesnake Replay Viewer")
    app = BattleSnakeReplay(root)  # Adjust size if needed
    root.mainloop()
