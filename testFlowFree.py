import tkinter as tk
from collections import deque
import time

class FlowGameSolver:
    def __init__(self, master):
        self.master = master
        master.title("Flow Game Solver")
        master.minsize(800, 600)

        self.grid_size = 6
        self.colors = ["red", "green", "blue", "yellow", "black"]

        # ví dụ pairs
        self.pairs = {
            "red": [(0, 3), (0, 5)],
            "green": [(0, 4), (4, 4)],
            "blue": [(0, 0), (1, 1)],
            "yellow": [(1, 0), (0, 2)],
            "black": [(2, 1), (4, 1)]
        }

        self.initial_grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for color, pair in self.pairs.items():
            self.initial_grid[pair[0][0]][pair[0][1]] = color
            self.initial_grid[pair[1][0]][pair[1][1]] = color

        self.cell_size = 70
        self.create_widgets()
        self.update_grid_display(self.initial_grid)

    def create_widgets(self):
        # canvas để vẽ grid
        self.canvas = tk.Canvas(self.master,
                                width=self.grid_size*self.cell_size,
                                height=self.grid_size*self.cell_size,
                                bg="white")
        self.canvas.pack(pady=10)

        self.rects = {}
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                x1 = c*self.cell_size
                y1 = r*self.cell_size
                x2 = x1+self.cell_size
                y2 = y1+self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill="white", outline="gray")
                self.rects[(r, c)] = rect

        # control buttons
        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(pady=10)

        tk.Button(self.control_frame, text="Đặt lại", command=self.reset_game).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="DFS", command=lambda: self.solve_game(DFS=True)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="BFS", command=lambda: self.solve_game(BFS=True)).pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.master, text="Sẵn sàng...", fg="black")
        self.status_label.pack(pady=5)

    def update_grid_display(self, grid_state, animate=False):
        """Cập nhật màu grid. Nếu animate=True thì tô từng bước"""
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                color = grid_state[r][c]
                fill_color = color if color else "white"
                self.canvas.itemconfig(self.rects[(r, c)], fill=fill_color)
                if animate and color != "":
                    self.master.update()
                    time.sleep(0.1)
        self.master.update_idletasks()

    def solve_game(self, DFS=False, BFS=False):
        self.status_label.config(text="Đang giải...", fg="blue")
        self.master.update_idletasks()
        if DFS:
            solved, solution = self.dfs_solver(self.initial_grid, list(self.colors), 0)
        if BFS:
            solved, solution = self.bfs_solver(self.initial_grid, list(self.colors))
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
        self.status_label.config(text="Sẵn sàng...", fg="black")

def main():
    root = tk.Tk()
    app = FlowGameSolver(root)
    root.mainloop()

if __name__ == "__main__":
    main()
