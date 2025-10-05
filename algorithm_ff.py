from collections import deque




'''
Uninformed: 1.BFS, 2.DFS, 3.UCS, 1.IDS

Informed: 2.Greedy, 3.A*

Local & Optimization: 1.Hill-Climbing, 2.Simulated Annealing, 3.Beam Search, GA

CSP: 1.Backtracking+Forward Checking, AC-3

Adversarial: 1.Minimax, 2.Alpha-Beta, 3.Expectiminimax (dối kháng)

Planning: 2.And-Or search, 3.Belief search




'''

class algorithm:
    def __init__(self, ui):
        self.ui=ui


    # ---------- DFS ----------
    def dfs_solver(self, grid, colors, idx):
        # Kiểm tra stop request
        if self.ui.stop_requested:
            return False, None

        if idx == len(colors):
            return True, grid
        color = colors[idx]
        start, end = self.ui.pairs[color]
        #self.ui.log(f"➡️ Đang xử lý màu {color.upper()} từ {start} đến {end}")

        def backtrack(path, visited):
            # Kiểm tra stop request
            if self.ui.stop_requested:
                return False, None


            r, c = path[-1]
            if (r, c) == end:
                new_grid = [row[:] for row in grid]
                for (pr, pc) in path:
                    new_grid[pr][pc] = color
                self.ui.log(f"✅ Tìm thấy đường cho màu {color}")
                ok, res = self.dfs_solver(new_grid, colors, idx+1)
                if ok:
                    # Vẽ đường hoàn chỉnh cho màu này
                    self.ui.paint_path(path, colors[idx])
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
        # Kiểm tra stop request
        if self.ui.stop_requested:
            return False, None

        if not colors:
            return True, grid

        for i, color in enumerate(colors):
            start, end = self.ui.pairs[color]
            self.ui.log(f"➡️ Tìm đường cho màu {color} bằng BFS...")
            path = self.bfs_find_path(grid, start, end, color)
            if not path:
                self.ui.log(f"⚠️ Không tìm được đường cho màu {color}")
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

    def bfs_find_path(self, grid, start, end, color):
        q = deque([start])
        parents = {start: None}
        while q:
            # Kiểm tra stop request
            if self.ui.stop_requested:
                return False, None

            r, c = q.popleft()
            # highlight node đang xét
            if (r, c) not in [start, end]:
                self.ui.paint_cell(r, c, "lightblue")
                self.ui.log(f"🔹 Mở rộng {color} tại ({r},{c})")


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