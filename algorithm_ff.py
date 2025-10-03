from collections import deque





'''
Uninformed: BFS, DFS, UCS, IDS

Informed: Greedy, A*

Local & Optimization: Hill-Climbing, Simulated Annealing, Beam Search, GA

CSP: Backtracking, Forward Checking, AC-3

Adversarial:Minimax, Alpha-Beta, Expectiminimax (dối kháng)

And-Or search: Planning


'''

class algorithm:
    def __init__(self, ui):
        self.ui=ui
        

    # ---------- DFS ----------
    def dfs_solver(self, grid, colors, idx):
        if idx == len(colors):
            return True, grid
        color = colors[idx]
        start, end = self.ui.pairs[color]

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
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
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
            start, end = self.ui.pairs[color]
            path = self.bfs_find_path(grid, start, end)
            if not path:
                continue
            if path:
                new_grid = [row[:] for row in grid]
                for (r, c) in path:
                    new_grid[r][c] = color

                # tô luôn đường tìm được cho cặp này
                self.ui.paint_path(path, color)

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
                self.ui.paint_cell(r, c, "lightblue")

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
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                    if (nr, nc) not in parents and (grid[nr][nc] == '' or (nr, nc) == end):
                        parents[(nr, nc)] = (r, c)
                        q.append((nr, nc))
        return None