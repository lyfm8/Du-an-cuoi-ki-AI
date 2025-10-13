from collections import deque
import heapq
import random
import copy





'''
Uninformed: 1.BFS, 2.DFS, 3.UCS, 1.IDS

Informed: 2.Greedy, 3.A*

Local & Optimization: 1.Hill-Climbing, 2.Simulated Annealing, 3.Beam Search, GA

CSP: 1.Backtracking+Forward Checking, 

Adversarial: 1.Minimax, 2.Alpha-Beta, 3.Expectiminimax (dối kháng)

Planning: 2.And-Or search, 3.Belief search

extra: dls, ac-3


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
    # Ý tưởng: lấy lần lượt từng màu trong colors list làm root
    def bfs_solver(self, grid, colors):
        if self.ui.stop_requested:
            return False, None
        
        if not colors:
            return True, grid
        
        for root in colors:
            self.ui.log(f"➡️Thử root: {root}")
            order = [root] + [c for c in colors if c != root]
            new_grid = [row[:] for row in grid]
            solved = True
            self.ui.reset_game()
            for color in order:
                start, end  = self.ui.pairs[color]
                self.ui.log(f"➡️ Tìm đường cho màu {color} bằng BFS...")
                path = self.bfs_find_path(new_grid, start, end, color)
                if not path:
                    self.ui.log(f"⚠️ Không tìm được đường cho màu {color}")
                    solved = False
                    continue
                
                for (r, c) in path:
                    new_grid[r][c] = color

                # tô luôn đường tìm được cho cặp này
                self.ui.paint_path(path, color)
                
            if solved:
                self.ui.log(f"🏆 Tìm được lời giải khi {root} làm root!")
                return True, new_grid
            
        self.ui.log("⛔ Không có lời giải với bất kỳ root nào.")
        return False, None

        

    def bfs_find_path(self, grid, start, end, color):
        q = deque([start])
        visited = {start: None}
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
                    cur = visited[cur]
                path.reverse()
                return path

            # duyệt 4 hướng
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                    if (nr, nc) not in visited:
                        if grid[nr][nc] == "" or (nr, nc) == end:
                            visited[(nr, nc)] = (r, c)
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
    



    
    def generate_neighbor(self, grid):
        new_grid = copy.deepcopy(grid)
        paths = {}

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

        self.ui.log(f"🔄 Đang thử xoá màu: {color_remove}")

        # xoá màu đã nối (giữ lại 2 đầu)
        if color_remove:
            self.ui.log(f"💥 Đang thử xoá màu: {color_remove}")
            start_rm, end_rm = self.ui.pairs[color_remove]
            old_path = self.bfs_find_path(grid, start_rm, end_rm, color_remove)
            if old_path:
                paths[color_remove] = old_path  # lưu path trước khi xoá
            
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
                paths[color] = path  # 🔹 lưu path nối mới
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
                paths[color_remove] = path_r  # 🔹 ghi đè path mới nếu nối lại được
                self.ui.log(f"🔁 Nối lại thành công {color_remove} trong CONNECTED")
                for (r, c) in path_r:
                    new_grid[r][c] = color_remove

        return new_grid, paths

    

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
        best_paths = {}
        steps = 0

        self.ui.log(f"🚀 Bắt đầu Hill-Climbing với heuristic ban đầu = {best_score}")

        

        while steps < max_steps and best_score > 0:
            neighbor, neighbor_paths = self.generate_neighbor(current)
            score = self.heuristic_hc(neighbor)

            self.ui.log(f"🔁 Step {steps}: neighbor_heuristic = {score}")

            if score < best_score:
                self.ui.log(f"✅ Tìm thấy trạng thái tốt hơn ({best_score} → {score})")
                current = neighbor
                best_score = score
                best_paths = neighbor_paths

                grid = copy.deepcopy(current)
                
                # vẽ trực tiếp path tốt nhất đã lưu trong best_paths
                for color, path in best_paths.items():
                    self.ui.paint_path(path, color)



            steps += 1

        

        if best_score == 0:
            self.ui.log("🎉 Tất cả màu đã được nối thành công!")
            return True, current
        else:
            self.ui.log(f"⛔ Dừng sau {steps} bước, chưa giải được (heuristic={best_score})")
        
        return False, current
    
    #-----------Backtracking---------------
    '''ý tưởng: duyệt tuần tự theo colors list, thử nối từng màu,
    nếu thất bại thì quay lui và thử root khác'''

    def backtracking_solver(self, grid, colors):
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

            new_grid = [row[:] for row in grid]
            for (r, c) in path:
                new_grid[r][c] = color

            # tô luôn đường tìm được cho cặp này
            self.ui.paint_path(path, color)

            remaining = colors[:i] + colors[i+1:]
            ok, solution = self.backtracking_solver(new_grid, remaining)
            if ok:
                return True, solution
            
            self.ui.log(f"↩️ Backtrack: hủy đường {color}")
        return False, None

    
    #-----------Backtracking + Forward Checking---------------
    '''ý tưởng: bắt đầu theo thứ tự trong colors list nếu FC tìm ra 1 màu không thể nối thì 
    break nhánh đấy và quay lui root mới'''
    def path_possible(self, grid, start, end, color):
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
                        #  chỉ đi qua ô cùng trong hoặc ô end
                        if cell == '' or cell == color or (nr, nc) == end:
                            visited.add((nr, nc))
                            q.append((nr, nc))
        return False
    
    def forward_check(self, grid, remaining_colors):
        for color in remaining_colors:
            s, e = self.ui.pairs[color]
            # nếu không còn đường nối khả thi cho màu này thì fail sớm
            if not self.path_possible(grid, s, e, color):
                self.ui.log(f"🚫 FC: màu {color} không còn đường nối khả thi.")
                return False
        return True
    

    def b_fc_solver(self, grid, colors):
            # kiểm tra stop request
        if self.ui.stop_requested:
            return False, None

        # nếu không còn màu nào => đã giải xong
        if not colors:
            return True, grid

        for i, color in enumerate(colors):
            start, end = self.ui.pairs[color]
            self.ui.log(f"➡️ Tìm đường cho màu {color} bằng BFS...")
            path = self.bfs_find_path(grid, start, end, color)
            if not path:
                self.ui.log(f"⚠️ Không tìm được đường cho màu {color}")
                continue

            new_grid = [row[:] for row in grid]
            for (r, c) in path:
                new_grid[r][c] = color

            # tô luôn đường tìm được cho cặp này
            self.ui.paint_path(path, color)

            # 🔹 forward checking: kiểm tra xem các cặp còn lại có còn khả năng nối không
            remaining = colors[:i] + colors[i+1:]
            # hàm forward checking: kiểm tra xem các cặp còn lại có còn khả năng nối không
            
            if not self.forward_check(new_grid, remaining):
                self.ui.log(f"❌ FC phát hiện bế tắc sau khi nối {color}, backtrack sớm.")
                for c in colors:
                    if c == color:
                        break
                    s2, e2 = self.ui.pairs[c]
                    p2 = self.bfs_find_path(grid, s2, e2, c)
                    if p2:
                        self.ui.paint_path(p2, c)
                continue  # thử nhánh khác

            # nếu FC hợp lệ thì tiếp tục đệ quy cho phần còn lại
            ok, solution = self.b_fc_solver(new_grid, remaining)
            if ok:
                return True, solution

            self.ui.log(f"↩️ Backtrack: hủy đường {color}")

        return False, None
        

    

    #------------And-Or Search--------------
    '''ý tưởng: bản chất game flow free là 1 mô hình and-or search mở rộng. khi chọn 1 màu làm or node thì bắt buộc
    các cặp màu còn lại tức and - node phải được nối thành công thì mới có lời giải'''

    def or_search(self, grid, colors, visited):
        if self.ui.stop_requested:
            return None

        if self.heuristic_hc(grid) == 0:
            return grid

        grid_key = tuple(tuple(row) for row in grid)
        if grid_key in visited:
            return None
        visited.add(grid_key)

        remaining = [c for c in colors if not self.path_exists(grid, *self.ui.pairs[c], c)]
        if not remaining:
            return grid

        for color in remaining:
            self.ui.log(f"🔹 OR-SEARCH: thử nối màu {color}")
            start, end = self.ui.pairs[color]

            possible_path = self.bfs_find_path(grid, start, end, color)
            if not possible_path:
                self.ui.log(f"⚠️ Không tìm được đường cho {color}, thử màu khác...")
                continue

            new_grid = [row[:] for row in grid]
            for (r, c) in possible_path:
                new_grid[r][c] = color
            self.ui.paint_path(possible_path, color)

            # quan trọng: truyền visited bản sao cho nhánh con (không muốn nhánh khác bị ảnh hưởng)
            visited_copy = set(visited)
            result = self.and_search(new_grid, colors, visited_copy)
            if result is not None:
                self.ui.log(f"✅ Thành công với OR-node {color}")
                return result

            self.ui.log(f"↩️ OR-SEARCH: thất bại ở {color}, backtrack...")

        self.ui.log("⛔ OR-SEARCH: không tìm được lời giải ở cấp này.")
        return None


    def and_search(self, grid, colors, visited):
        if self.ui.stop_requested:
            return None

        remaining = [c for c in colors if not self.path_exists(grid, *self.ui.pairs[c], c)]
        if not remaining:
            return grid

        self.ui.log(f"🔸 AND-SEARCH: còn {len(remaining)} màu chưa nối → phải nối hết")

        # thử nối từng màu còn lại theo thứ tự; nếu thành công, cập nhật grid và tiếp tục
        for c in remaining:
            self.ui.log(f"➡️ AND-SEARCH: cố gắng nối {c}")

            # gọi or_search trên trạng thái hiện tại; truyền visited 
            visited_copy = set(visited)
            subplan = self.or_search(grid, [c], visited_copy)
            if subplan is None:
                self.ui.log(f"❌ AND thất bại tại màu {c}")
                return None

            # nếu or_search thành công, **cập nhật grid** sang subplan và tiếp tục với màu tiếp theo
            grid = subplan
            self.ui.log(f"✅ AND-SEARCH: đã nối {c}, tiếp tục...")

        return grid



    def and_or_solver(self, grid, colors):
        if self.ui.stop_requested:
            return False, None

        self.ui.log("🚀 Bắt đầu AND-OR Search...")
        plan = self.or_search(grid, colors, set())
        if plan is not None:
            self.ui.log("🎯 Đã tìm thấy kế hoạch thành công!")
            return True, plan
        else:
            self.ui.log("⛔ Không tìm thấy lời giải.")
            return False, None




        


