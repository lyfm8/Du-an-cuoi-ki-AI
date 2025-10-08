from collections import deque
import heapq
import random
import copy
import itertools




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
        self.ui.log(f"➡️ Đang xử lý màu {color.upper()} từ {start} đến {end}")

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
    # Khác biệt: Có sử dụng backtracking để thử bắt đầu từ 1 root (màu) mới để mở rộng hơn
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
                return False, None
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

            # duyệt 4 hướng
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                    if (nr, nc) not in parents:
                        cell = grid[nr][nc]

                        # chỉ được đi nếu:
                        # - ô trống, hoặc
                        # - ô cùng màu, hoặc
                        # - ô end (và ô end đang trống hoặc có đúng màu)
                        if (
                            cell == "" 
                            or cell == color 
                            or ((nr, nc) == end and (grid[nr][nc] in ["", color]))
                        ):
                            parents[(nr, nc)] = (r, c)
                            q.append((nr, nc))
        return None
    

    
    
    #----------GREEDY----------
    def heuristic_greedy(self, grid, color, alpha):
        (sx, sy), (ex, ey) = self.ui.pairs[color]
        # yeu to 1_manhattan: |x1-x2| + |y1-y2|
        h1 = abs(sx - ex) + abs(sy - ey)

        # yeu to 2: tinh cac diem mau khac lien ke mau dang xet
        h2 = 0
        for (r, c) in [(sx, sy), (ex, ey)]:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                    cell = grid[nr][nc]
                    if cell != "" and cell != color:
                        h2 += 1

        return h1 + alpha * h2

    
    def greedy_solver(self, grid, colors, alpha):
        # Kiểm tra stop request
        if self.ui.stop_requested:
            return False, None

        if not colors:
            return True, grid
        
        hq = []

        for color in colors:
            cost = self.heuristic_greedy(grid, color, alpha)
            heapq.heappush(hq, (cost, color))

        new_grid = [row[:] for row in grid]
        solved_colors = []

        while hq:
            cost, color = heapq.heappop(hq)
            start, end = self.ui.pairs[color]
            self.ui.log(f"➡️ Tìm đường cho màu {color} (h={cost})")

            path = self.bfs_find_path(new_grid, start, end, color)
            if not path:
                self.ui.log(f"⚠️Không tìm được đường cho màu {color}")
                continue

            # tô màu và cập nhật grid
            for (r, c) in path:
                new_grid[r][c] = color
            self.ui.paint_path(path, color)
            solved_colors.append(color)

        return True, new_grid
    
    #----------Hill-Climbing------------
    '''Ý tưởng: chạy thuật toán bfs nhưng không backtracking theo thứ tự trong colors list để 
    sinh ra trường hợp xấu sau đó dùng hill_climbing để tìm lời giải cuối cùng'''
    def heuristic_hc(self, grid):
        #y tuong: so cap mau chua duoc noi
        cnt = 0
        for color, (start, end) in self.ui.pairs.items():
            if self.path_exists(grid, start, end, color) == False:
                cnt += 1
        return cnt
    
    def path_exists(self, grid, start, end, color):
        q = deque([start])
        visited = {start}

        while q:
            r, c = q.popleft()
            if (r, c) == end:
                return True

            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                    if (nr, nc) not in visited:
                        cell = grid[nr][nc]
                        #  chỉ đi qua ô cùng màu hoặc ô end
                        if cell == color or (nr, nc) == end:
                            visited.add((nr, nc))
                            q.append((nr, nc))
        return False
    
    #dùng thẳng bfs_find_path sẽ ghi nhiều log thừa,  2 hàm tương tự nhau
    '''def path_exists(self, grid, start, end, color): #cong dung: kiem tra xem cap mau da duoc noi chua 
        path = self.bfs_find_path(grid, start, end, color) 
        return bool(path)'''


    
    def generate_neighbor(self, grid, colors):
        new_grid = copy.deepcopy(grid)

        connected = []
        unconnected = []

        for color, (start, end) in self.ui.pairs.items():
            if self.path_exists(grid, start, end, color):
                connected.append(color)
            else:
                unconnected.append(color)

        self.ui.log(f"🧩 Connected: {connected}, Unconnected: {unconnected}")

        if not unconnected:
            self.ui.log("🎯 Tất cả màu đã nối xong, không tạo neighbor mới.")
            return new_grid

        if not connected:
            color_remove = None
            self.ui.log("⚠️ Chưa có màu nào nối xong để xoá.")
        else:
            color_remove = random.choice(connected)

        color_try = random.choice(unconnected)
        self.ui.log(f"🔄 Đang thử xoá màu: {color_remove}, thử nối lại màu: {color_try}")

        # xoá màu đã nối (giữ lại 2 đầu)
        if color_remove:
            start_rm, end_rm = self.ui.pairs[color_remove]
            for r in range(self.ui.grid_size):
                for c in range(self.ui.grid_size):
                    if new_grid[r][c] == color_remove and (r, c) not in [start_rm, end_rm]:
                        new_grid[r][c] = ""

        # thử nối lại tất cả màu chưa nối
        self.ui.log("🔁 Đang thử nối lại toàn bộ màu chưa nối...")
        for color in unconnected:
            start, end = self.ui.pairs[color]
            path = self.bfs_find_path(new_grid, start, end, color)
            if path:
                self.ui.log(f"✅ Nối lại thành công {color} trong UNCONNECTED")
                for (r, c) in path:
                    new_grid[r][c] = color
            else:
                self.ui.log(f"❌ Không nối được {color}")

        # thử nối lại màu đã xóa (nếu có)
        if color_remove:
            start_r, end_r = self.ui.pairs[color_remove]
            path_r = self.bfs_find_path(new_grid, start_r, end_r, color_remove)
            if path_r:
                self.ui.log(f"🔁 Nối lại {color_remove} thành công trong CONNECTED")
                for (r, c) in path_r:
                    new_grid[r][c] = color_remove

        return new_grid

    

    def hc_solver(self, grid, colors, max_steps):
        # Kiểm tra stop request
        if self.ui.stop_requested:
            return False, None
        
        current = copy.deepcopy(grid)
        for color in colors:
            start, end = self.ui.pairs[color]
            path = self.bfs_find_path(current, start, end, color)
            if path:
                self.ui.paint_path(path, color)
                for (r, c) in path:
                    current[r][c] = color
        best_score = self.heuristic_hc(current)
        steps = 0

        self.ui.log(f"🚀 Bắt đầu Hill-Climbing với heuristic ban đầu = {best_score}")

        

        while steps < max_steps and best_score > 0:
            neighbor = self.generate_neighbor(current, colors)
            score = self.heuristic_hc(neighbor)

            self.ui.log(f"🔁 Step {steps}: neighbor_heuristic = {score}")

            if score < best_score:
                self.ui.log(f"✅ Tìm thấy trạng thái tốt hơn ({best_score} → {score})")
                current = neighbor
                best_score = score
                self.ui.reset_game()
                grid = copy.deepcopy(current)
                for color in colors:
                    start, end = self.ui.pairs[color]
                    path = self.bfs_find_path(grid, start, end, color)
                    if path:
                        self.ui.paint_path(path, color)


            steps += 1

        if best_score == 0:
            self.ui.log("🎉 Tất cả màu đã được nối thành công!")
            return True, current
        else:
            self.ui.log(f"⛔ Dừng sau {steps} bước, chưa giải được (heuristic={best_score})")
        
        return False, current
    
    #-----------Backtracking + Forward Checking---------------
    '''ý tưởng: bắt đầu theo thứ tự trong colors list nếu FC tìm ra 1 màu không thể nối thì 
    break nhánh đấy và quay lui root mới'''

    def b_fc_solver(self, grid, colors):
        if self.ui.stop_requested:
            return False, None

        self.ui.log("🚀 Bắt đầu BFS + Forward Checking (đa root)...")


        def forward_check(grid_local, remaining_colors):
            for color in remaining_colors:
                s, e = self.ui.pairs[color]
                if not self.path_exists(grid_local, s, e, color):
                    return False
            return True

        def backtrack(idx, grid_local, solved_paths, order):
            if idx == len(order):
                # chỉ vẽ khi tìm được lời giải hoàn chỉnh
                for c, p in solved_paths.items():
                    self.ui.paint_path(p, c)
                self.ui.master.update()
                return True, grid_local

            color = order[idx]
            s, e = self.ui.pairs[color]
            self.ui.log(f"➡️ Đang nối màu {color}")

            path = self.bfs_find_path(grid_local, s, e, color)
            if not path:
                self.ui.log(f"❌ Không tìm được đường cho {color}")
                return False, None

            new_grid = [row[:] for row in grid_local]
            for (r, c) in path:
                new_grid[r][c] = color
            solved_paths[color] = path

            remaining = order[idx+1:]
            if not forward_check(new_grid, remaining):
                # thử hoán đổi thứ tự các màu còn lại
                for i in range(len(remaining)):
                    new_order = order[:idx+1] + [remaining[i]] + [c for j, c in enumerate(remaining) if j != i]
                    ok, sol = backtrack(idx+1, new_grid, solved_paths, new_order)
                    if ok:
                        return True, sol
                return False, None

            ok, sol = backtrack(idx+1, new_grid, solved_paths, order)
            if ok:
                return True, sol

            del solved_paths[color]
            return False, None

        # --- thử lần lượt mỗi màu làm root ---
        for root in colors:
            order = [root] + [c for c in colors if c != root]
            self.ui.log(f"\n🎯 Thử màu {root} làm root đầu tiên...")
            solved_paths = {}
            ok, sol = backtrack(0, [row[:] for row in grid], solved_paths, order)
            if ok:
                self.ui.log(f"🏆 Tìm được lời giải khi {root} làm root!")
                return True, sol
            else:
                self.ui.log(f"❌ Root {root} thất bại, thử root khác...")

        self.ui.log("⛔ Không có lời giải với bất kỳ root nào.")
        return False, None




        


