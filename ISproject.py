import tkinter as tk
from tkinter import messagebox, ttk
from queue import PriorityQueue
from collections import deque
from tkinter import PhotoImage


GRID_SIZE = 20
CANVAS_SIZE = 400

class Ruby:
    def __init__(self, root):
        self.root = root
        self.root.title("Pathfinding")
        self.cell_size=CANVAS_SIZE // GRID_SIZE

        self.robot_pos = None
        self.goal_pos = None
        self.obstacles = set()
        self.action_history = []
        self.algorithm = "BFS"  # Default algorithm
        self.robot_image = PhotoImage(file="robot7.png")
        self.create_widgets()
        self.create_grid()

    def create_widgets(self):

        self.canvas = tk.Canvas(self.root, width=GRID_SIZE * self.cell_size, height=GRID_SIZE * self.cell_size)
        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<Button-1>", self.place_element)

        panel = tk.Frame(self.root)
        panel.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

        self.create_hover_button(panel, "Place Robot", self.set_robot_mode, "lightblue", "dodgerblue")
        self.create_hover_button(panel, "Place Obstacle", self.set_obstacle_mode, "lightgray", "darkgray")
        self.create_hover_button(panel, "Place Goal", self.set_goal_mode, "lightgreen", "forestgreen")


        tk.Label(panel, text="Algorithm:").pack(pady=5)
        self.algorithm_menu = ttk.Combobox(panel, values=["BFS", "DFS", "UCS", "Greedy", "A*"])
        self.algorithm_menu.set("BFS")
        self.algorithm_menu.pack(fill="x", pady=5)
        self.algorithm_menu.bind("<<ComboboxSelected>>", self.algorithm_changed)

        self.create_hover_button(panel, "Find Path", self.find_path, "yellow", "gold")
        self.create_hover_button(panel, "Reset", self.reset, "orange", "darkorange")
        self.create_hover_button(panel, "Undo", self.undo, "pink", "hotpink")

    def create_hover_button(self, parent, text, command, bg, hover_bg):
        
        button = tk.Button(parent, text=text, command=command, bg=bg)
        button.pack(fill="x", pady=5)
        button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
        button.bind("<Leave>", lambda e: button.config(bg=bg))

    def create_grid(self):

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x0, y0 = i * self.cell_size, j * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="gray")

    def set_robot_mode(self):

        self.mode = "robot"

    def set_obstacle_mode(self):
        """Activate obstacle placement mode."""
        self.mode = "obstacle"

    def set_goal_mode(self):

        self.mode = "goal"

    def place_element(self, event):

        x, y = event.x // self.cell_size, event.y // self.cell_size

        if self.mode == "robot":
            if self.robot_pos:
                self.canvas.delete("robot")
            self.robot_pos = (x, y)
            self.canvas.create_image(
                x * self.cell_size + self.cell_size // 2,  # Center the image in the cell
                y * self.cell_size + self.cell_size // 2,
                image=self.robot_image,
                tags="robot"
            )
            self.action_history.append(("robot", self.robot_pos))

        elif self.mode == "obstacle":
            if (x, y) not in self.obstacles:
                self.obstacles.add((x, y))
                self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                             fill="black", tags=f"obstacle_{x}_{y}")
                self.action_history.append(("obstacle", (x, y)))

        elif self.mode == "goal":
            if self.goal_pos:
                self.canvas.delete("goal")
            self.goal_pos = (x, y)
            self.canvas.create_oval(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                    fill="green", tags="goal")
            self.action_history.append(("goal", self.goal_pos))

    def algorithm_changed(self, event):
        self.canvas.delete("path")
        self.find_path()

    def find_path(self):
        if not self.robot_pos or not self.goal_pos:
            messagebox.showwarning("Warning", "Place both the robot and goal on the grid.")
            return

        algorithm = self.algorithm_menu.get()
        path = None

        if algorithm == "BFS":
            path = self.bfs(self.robot_pos, self.goal_pos)
        elif algorithm == "DFS":
            path = self.dfs(self.robot_pos, self.goal_pos)
        elif algorithm == "UCS":
            path = self.ucs(self.robot_pos, self.goal_pos)
        elif algorithm == "Greedy":
            path = self.greedy(self.robot_pos, self.goal_pos)
        elif algorithm == "A*":
            path = self.a_star(self.robot_pos, self.goal_pos)

        if path:
            for (x, y) in path:
                self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size, fill="yellow", tags="path")
        else:
            messagebox.showinfo("Info", "No path found!")

    def bfs(self, start, goal):
        queue = deque([[start]])
        visited = set()

        while queue:
            path = queue.popleft()
            current = path[-1]

            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited and neighbor not in self.obstacles:
                    queue.append(path + [neighbor])

        return None

    def dfs(self, start, goal):
        stack = [[start]]
        visited = set()

        while stack:
            path = stack.pop()
            current = path[-1]

            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited and neighbor not in self.obstacles:
                    stack.append(path + [neighbor])

        return None

    def ucs(self, start, goal):
        pq = PriorityQueue()
        pq.put((0, [start]))
        visited = set()

        while not pq.empty():
            cost, path = pq.get()
            current = path[-1]

            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited and neighbor not in self.obstacles:
                    pq.put((cost + 1, path + [neighbor]))

        return None

    def greedy(self, start, goal):
        pq = PriorityQueue()
        pq.put((self.heuristic(start, goal), [start]))
        visited = set()

        while not pq.empty():
            _, path = pq.get()
            current = path[-1]

            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited and neighbor not in self.obstacles:
                    pq.put((self.heuristic(neighbor, goal), path + [neighbor]))

        return None

    def a_star(self, start, goal):
        pq = PriorityQueue()
        pq.put((0, 0, [start]))  # (f_cost, g_cost, path)
        visited = set()

        while not pq.empty():
            _, g_cost, path = pq.get()
            current = path[-1]

            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited and neighbor not in self.obstacles:
                    new_g_cost = g_cost + 1
                    f_cost = new_g_cost + self.heuristic(neighbor, goal)
                    pq.put((f_cost, new_g_cost, path + [neighbor]))

        return None

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos):
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x, y = pos[0] + dx, pos[1] + dy
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                neighbors.append((x, y))
        return neighbors

    def reset(self):

        self.canvas.delete("all")
        self.create_grid()
        self.robot_pos = None
        self.goal_pos = None
        self.obstacles = set()
        self.action_history.clear()

    def undo(self):
        if not self.action_history:
            return

        last_action, pos = self.action_history.pop()
        if last_action == "robot":
            self.canvas.delete("robot")
            self.robot_pos = None
        elif last_action == "goal":
            self.canvas.delete("goal")
            self.goal_pos = None
        elif last_action == "obstacle":
            x, y = pos
            self.canvas.delete(f"obstacle_{x}_{y}")
            self.obstacles.remove(pos)

if __name__ == "__main__":
    root = tk.Tk()
    Ruby(root)
    root.mainloop()
