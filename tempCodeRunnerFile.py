import tkinter as tk
from collections import deque
import time

class FlowGameSolver:
    def __init__(self, master):
        self.master = master
        master.title("Flow Game Solver")
        master.minsize(800, 600)

        self.grid_size = 6
        self.colors = ["red", "green", "blue", "yellow", "orange"]
        self.cell_size = 70
        self.speed = 0.2
        self.theme = "Light"

        # ví dụ pairs
        self.pairs = {
            "red": [(0, 3), (0, 5)],
            "green": [(0, 4), (4, 4)],
            "blue": [(0, 0), (1, 1)],
            "yellow": [(1, 0), (0, 2)],
            "orange": [(2, 1), (4, 1)]
        }

        self.initial_grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for color, pair in self.pairs.items():
            self.initial_grid[pair[0][0]][pair[0][1]] = color
            self.initial_grid[pair[1][0]][pair[1][1]] = color

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_canvas(self.main_frame)
        self.create_control_panel(self.main_frame)
        self.update_grid_display(self.initial_grid)


    def create_canvas(self, parent):
        self.canvas = tk.Canvas(parent,
                                width=self.grid_size*self.cell_size,
                                height=self.grid_size*self.cell_size,
                                bg="white")
        self.canvas.grid(row=0, column=0, padx=20, pady=20)

        self.rects = {}
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                x1, y1 = c*self.cell_size, r*self.cell_size
                x2, y2 = x1+self.cell_size, y1+self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill="white", outline="gray")
                self.rects[(r, c)] = rect
        self.mark_start_end()

    def create_control_panel(self, parent):
        panel = tk.Frame(parent, bd=2, relief="ridge", padx=10, pady=10)
        panel.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

        # --- Actions ---
        tk.Label(panel, text="Actions", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(panel, text="⏮ Reset", command=self.reset_game, width=12).pack(pady=3)
        tk.Button(panel, text="🌳 DFS", command=lambda: self.solve_game(DFS=True), width=12).pack(pady=3)
        tk.Button(panel, text="🌊 BFS", command=lambda: self.solve_game(BFS=True), width=12).pack(pady=3)

        # --- Settings ---
        tk.Label(panel, text="Settings", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(panel, text="Speed:").pack()
        self.speed_slider = tk.Scale(panel, from_=0.05, to=1.0,
                                     resolution=0.05, orient="horizontal",
                                     command=self.update_speed, length=150)
        self.speed_slider.set(self.speed)
        self.speed_slider.pack(pady=5)

        tk.Button(panel, text="🌗 Toggle Theme", command=self.toggle_theme, width=15).pack(pady=5)

        # --- Info ---
        tk.Label(panel, text="Info", font=("Arial", 12, "bold")).pack(pady=10)
        self.status_label = tk.Label(panel, text="Sẵn sàng...", fg="black")
        self.status_label.pack(pady=5)

        self.timer_label = tk.Label(panel, text="⏱ 0.0s", font=("Arial", 11))
        self.timer_label.pack(pady=5)

    def update_speed(self, val):
        self.speed = float(val)

    def toggle_theme(self):
        if self.theme == "Light":
            self.theme = "Dark"
            self.canvas.config(bg="black")
        else:
            self.theme = "Light"
            self.canvas.config(bg="white")

    def mark_start_end(self):
        for color, points in self.pairs.items():
            for (r, c) in points:
                # tô màu nền
                self.canvas.itemconfig(self.rects[(r, c)], fill=color)
                # thêm hình tròn để phân biệt
                x1, y1, x2, y2 = self.canvas.coords(self.rects[(r, c)])
                self.canvas.create_oval(
                    x1+15, y1+15, x2-15, y2-15,
                    fill=color, outline="black", width=2
                )


    def update_grid_display(self, grid_state, animate=False):
        """Cập nhật màu grid. Nếu animate=True thì tô từng bước"""
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                color = grid_state[r][c]
                fill_color = color if color else "white"
                self.canvas.itemconfig(self.rects[(r, c)], fill=fill_color)
                if animate and color != "":
                    self.master.update()
                    time.sleep(self.speed)
        self.master.update_idletasks()

    def solve_game(self, DFS=False, BFS=False):
        start_time = time.time()
        self.status_label.config(text="Đang giải...", fg="blue")
        self.master.update_idletasks()

        if DFS:
        
            solved, solution = self.dfs_solver(self.initial_grid, list(self.colors), 0)
        if BFS:
            solved, solution = self.bfs_solver(self.initial_grid, list(self.colors))

        elapsed = time.time() - start_time
        self.timer_label.config(text=f"⏱ {elapsed:.2f}s")

        if solved:
            self.update_grid_display(solution, animate=True)
            self.status_label.config(text="Đã giải xong!", fg="green")
        else:
            self.status_label.config(text="Không tìm thấy lời giải.", fg="red")

    # ---------- DFS ----------
    def dfs_solver(self, grid, colors, idx):
        if idx == len(colors):
            return True, grid
        color = colors[idx]
        start, end = self.pairs[color]

        def backtrack(path, visited):
            r, c = path[-1]
            if (r, c) == end:
                new_grid = [row[:] for row in grid]
                for (pr, pc) in path:
                    new_grid[pr][pc] = color
                ok, res = self.dfs_solver(new_grid, colors, idx+1)
                if ok:
                    return True, res
                return False, None

            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    if (nr, nc) not in visited and (grid[nr][nc] == '' or (nr, nc) == end):
                        visited.add((nr, nc))
                        path.append((nr, nc))
                        ok, res = backtrack(path, visited)
                        if ok: return True, res
                        path.pop()
                        visited.remove((nr, nc))
            return False, None

        return backtrack([start], {start})

    # ---------- BFS ----------
    def bfs_solver(self, grid, colors):
        if not colors:
            return True, grid

        for i, color in enumerate(colors):
            start, end = self.pairs[color]
            path = self.bfs_find_path(grid, start, end)
            if not path:
                continue
            if path:
                new_grid = [row[:] for row in grid]
                for (r, c) in path:
                    new_grid[r][c] = color

                # tô luôn đường tìm được cho cặp này
                self.paint_path(path, color)

                remaining = colors[:i] + colors[i+1:]
                ok, solution = self.bfs_solver(new_grid, remaining)
            if ok:
                return True, solution
        return False, None

    def bfs_find_path(self, grid, start, end):
        q = deque([start])
        parents = {start: None}
        while q:
            r, c = q.popleft()
            # highlight node đang xét
            if (r, c) not in [start, end]:
                self.paint_cell(r, c, "lightblue")

            if (r, c) == end:
                # reconstruct path
                path = []
                cur = end
                while cur is not None:
                    path.append(cur)
                    cur = parents[cur]
                path.reverse()
                return path

            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    if (nr, nc) not in parents and (grid[nr][nc] == '' or (nr, nc) == end):
                        parents[(nr, nc)] = (r, c)
                        q.append((nr, nc))
        return None

    def paint_cell(self, r, c, color):
        self.canvas.itemconfig(self.rects[(r, c)], fill=color)
        self.master.update()
        time.sleep(0.05)   # tốc độ hiển thị

    def paint_path(self, path, color):
        for (r, c) in path:
            self.canvas.itemconfig(self.rects[(r, c)], fill=color)
            self.master.update()
            time.sleep(0.5)  # tốc độ animation



    def reset_game(self):
        self.update_grid_display(self.initial_grid)
        self.mark_start_end()
        self.status_label.config(text="Sẵn sàng...", fg="black")
        self.timer_label.config(text="⏱ 0.0s")

def main():
    root = tk.Tk()
    app = FlowGameSolver(root)
    root.mainloop()

if __name__ == "__main__":
    main()
