from collections import deque
from collections import defaultdict
import heapq
import random
import copy
import itertools
import time




'''
Uninformed: 1.BFS, 2.DFS, 3.UCS, 1.IDS

Informed: 2.Greedy, 3.A*

Local & Optimization: 1.Hill-Climbing, 2.Simulated Annealing, 3.Beam Search, GA

CSP: 1.Backtracking+Forward Checking, AC-3

Adversarial: 1.Minimax, 2.Alpha-Beta, 3.Expectiminimax (dối kháng)

Planning: 2.And-Or search, 3.Belief search

extra: dls, ida*, 


'''

class algorithm:
    def __init__(self, ui):
        self.ui=ui

# Uninformed ----------------------------------------
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
                self.ui.master.update()
                
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
    
# Informed ----------------------------------------   
    #----------UCS----------
    def cost(self, value):
        # chi phí từ trạng thái ban đầu đến trạng thái hiện tại
        # Chi phí mỗi ô = 1
        ''' Có thể mở rộng theo cách
                Tránh các đường rẽ - phạt khi rẽ
                Tránh các cùng dễ trùng với các đường khác
                Cân bằng độ dài các đường
            '''
        return value + 1

    def ucs_solver(self, grid, colors):
        # Tương tự bfs solver nhưng thay đổi cách sắp xếp các màu
        if self.ui.stop_requested:
            return False, None
        
        if not colors:
            return True, grid
        
        # Sắp xếp màu theo heuristic
        def manhattan(color):
            start, end = self.ui.pairs[color]
            return abs(start[0] - end[0]) + abs(start[1] - end[1])
    
        # Thử nhiều chiến lược sắp xếp
        strategies = [
            sorted(colors, key=manhattan, reverse=True),   # Xa nhất trước
            sorted(colors, key=manhattan),                 # Gần nhất trước
            colors,                                                 # Thứ tự gốc
            list(reversed(colors))                                  # Đảo ngược
        ]

        for order in strategies:
            self.ui.log(f"Thử thứ tự: {order}")
            new_grid = [row[:] for row in grid]
            solved = True
            self.ui.reset_game()

            for color in order:
                start, end  = self.ui.pairs[color]
                self.ui.log(f"Tìm đường cho màu {color} bằng UCS...")
                path = self.ucs_find_path(new_grid, start, end, color)

                if not path:
                    self.ui.log(f"Không tìm được đường cho màu {color}")
                    solved = False
                    continue
                
                for (r, c) in path:
                    new_grid[r][c] = color

                # tô luôn đường tìm được cho cặp này
                self.ui.paint_path(path, color)
                self.ui.master.update()
                
            if solved:
                self.ui.log(f"Tìm được lời giải với thứ tự: {order}")
                return True, new_grid
            
        self.ui.log("Không có lời giải với bất kỳ root nào.")
        return False, None
    
    def ucs_find_path(self, grid, start, end, color):
        # Priority queue: (cost, node)
        pq = [(0, start)]
        visited = {start: (None, 0)}  # {node: (parent, cost)}
    
        while pq:
            # Kiểm tra stop request
            if self.ui.stop_requested:
                return None
        
            cost, (r, c) = heapq.heappop(pq)
        
            # Bỏ qua nếu đã có đường rẻ hơn đến node này
            if cost > visited[(r, c)][1]:
                continue
        
            # highlight node đang xét
            if (r, c) not in [start, end]:
                self.ui.paint_cell(r, c, "lightblue")
                self.ui.log(f"🔹 Mở rộng {color} tại ({r},{c}) với cost={cost}")
        
            if (r, c) == end:
                # reconstruct path
                path = []
                cur = end
                while cur is not None:
                    path.append(cur)
                    cur = visited[cur][0]
                path.reverse()
                return path
        
            # duyệt 4 hướng
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                    if grid[nr][nc] == "" or (nr, nc) == end:
                        new_cost = self.cost(cost)  # tính cost
                    
                        # Chỉ thêm vào queue nếu chưa thăm hoặc tìm được đường rẻ hơn
                        if (nr, nc) not in visited or new_cost < visited[(nr, nc)][1]:
                            visited[(nr, nc)] = ((r, c), new_cost)
                            heapq.heappush(pq, (new_cost, (nr, nc)))
    
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
    
    #----------A*----------
    def aStar_solver(self, grid, colors):
        # Tương tự ucs solver
        if self.ui.stop_requested:
            return False, None
        
        if not colors:
            return True, grid
        
        # Sắp xếp màu theo heuristic
        def manhattan(color):
            start, end = self.ui.pairs[color]
            return abs(start[0] - end[0]) + abs(start[1] - end[1])
    
        # Thử nhiều chiến lược sắp xếp
        strategies = [
            sorted(colors, key=manhattan, reverse=True),   # Xa nhất trước
            sorted(colors, key=manhattan),                 # Gần nhất trước
            colors,                                                 # Thứ tự gốc
            list(reversed(colors))                                  # Đảo ngược
        ]

        for order in strategies:
            self.ui.log(f"Thử thứ tự: {order}")
            new_grid = [row[:] for row in grid]
            solved = True
            self.ui.reset_game()

            for color in order:
                start, end  = self.ui.pairs[color]
                self.ui.log(f"Tìm đường cho màu {color} bằng A*...")
                path = self.aStar_find_path(new_grid, start, end, color)

                if not path:
                    self.ui.log(f"Không tìm được đường cho màu {color}")
                    solved = False
                    break
                
                for (r, c) in path:
                    new_grid[r][c] = color

                # tô luôn đường tìm được cho cặp này
                self.ui.paint_path(path, color)
                self.ui.master.update()
                
            if solved:
                self.ui.log(f"Tìm được lời giải với thứ tự: {order}")
                return True, new_grid
            
        self.ui.log("Không có lời giải với bất kỳ màu nào.")
        return False, None
    
    def aStar_find_path(self, grid, start, end, color):
        def heuristic(pos):
            (r, c) = pos
            (ex, ey) = end
            # yeu to 1_manhattan: |x1-x2| + |y1-y2|
            h1 = abs(r - ex) + abs(c - ey)

            # yeu to 2: tinh cac diem mau khac lien ke mau dang xet
            h2 = 0
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                    cell = grid[nr][nc]
                    if cell != "" and cell != color:
                        h2 += 1
            return h1 + h2
    
        # Priority queue: (f_cost, g_cost, h_cost, node)
        # f_cost = g_cost + h_cost
        g_cost = 0
        h_cost = heuristic(start)
        f_cost = g_cost + h_cost
        pq = [(f_cost, g_cost, h_cost, start)]
    
        # visited: {node: (parent, f_cost, g_cost, h_cost)}
        visited = {start: (None, f_cost, g_cost, h_cost)}
    
        while pq:
            # Kiểm tra stop request
            if self.ui.stop_requested:
                return None
        
            f_cost, g_cost, h_cost, (r, c) = heapq.heappop(pq)
        
            # Bỏ qua nếu đã có đường rẻ hơn đến node này
            if f_cost > visited[(r, c)][1]:
                continue
        
            # highlight node đang xét
            if (r, c) not in [start, end]:
                self.ui.paint_cell(r, c, "lightblue")
                self.ui.log(f"Mở rộng {color} tại ({r},{c}) | g={g_cost}, h={h_cost}, f={f_cost}")
        
            # Kiểm tra đích
            if (r, c) == end:
                # reconstruct path
                path = []
                cur = end
                while cur is not None:
                    path.append(cur)
                    cur = visited[cur][0]
                path.reverse()
                self.ui.log(f"Tìm thấy đường cho {color} với tổng cost = {g_cost}")
                return path
        
            # duyệt 4 hướng
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                    if grid[nr][nc] == "" or (nr, nc) == end:
                        new_g_cost = self.cost(g_cost)
                        new_h_cost = heuristic((nr, nc))
                        new_f_cost = new_g_cost + new_h_cost
                    
                        # Chỉ thêm vào queue nếu chưa thăm hoặc tìm được đường rẻ hơn
                        if (nr, nc) not in visited or new_f_cost < visited[(nr, nc)][1]:
                            visited[(nr, nc)] = ((r, c), new_f_cost, new_g_cost, new_h_cost)
                            heapq.heappush(pq, (new_f_cost, new_g_cost, new_h_cost, (nr, nc)))
    
        return None
    
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
                        if cell == "" or cell == color or (nr, nc) == end:
                            visited.add((nr, nc))
                            q.append((nr, nc))
        return False
    
    #dùng thẳng bfs_find_path sẽ ghi nhiều log thừa,  2 hàm tương tự nhau
    '''def path_exists(self, grid, start, end, color): #cong dung: kiem tra xem cap mau da duoc noi chua 
        path = self.bfs_find_path(grid, start, end, color) 
        return bool(path)'''

    #----------Beam Search------------
    def beamSearch(self, grid, colors, k):
        if self.ui.stop_requested:
            return False, None
        
        if not colors:
            return True, grid
        
        # Sắp xếp màu theo heuristic
        def manhattan(color):
            start, end = self.ui.pairs[color]
            return abs(start[0] - end[0]) + abs(start[1] - end[1])
    
        # Thử nhiều chiến lược sắp xếp
        strategies = [
            sorted(colors, key=manhattan, reverse=True),   # Xa nhất trước
            sorted(colors, key=manhattan),                 # Gần nhất trước
            colors,                                                 # Thứ tự gốc
            list(reversed(colors))                                  # Đảo ngược
        ]

        for order in strategies:
            self.ui.log(f"Thử thứ tự: {order}")
            new_grid = [row[:] for row in grid]
            solved = True
            self.ui.reset_game()

            for color in order:
                start, end  = self.ui.pairs[color]
                self.ui.log(f"Tìm đường cho màu {color} bằng A*...")
                path = self.beamSearch_find_path(new_grid, start, end, color, k)

                if not path:
                    self.ui.log(f"Không tìm được đường cho màu {color}")
                    solved = False
                    break
                
                for (r, c) in path:
                    new_grid[r][c] = color

                # tô luôn đường tìm được cho cặp này
                self.ui.paint_path(path, color)
                self.ui.master.update()
                
            if solved:
                self.ui.log(f"Tìm được lời giải với thứ tự: {order}")
                return True, new_grid
            
        self.ui.log("Không có lời giải với bất kỳ màu nào.")
        return False, None
    
    def beamSearch_find_path(self, grid, start, end, color, k):
        # 
        current_q = deque([start])
        visited = {start: None}  # {node: parent}
        layer = 0
        while current_q:
            next_q = []
            # Kiểm tra stop request
            if self.ui.stop_requested:
                return None

            layer += 1
            self.ui.log(f"-----Layer {layer}-----")
            for (r, c) in current_q:

                # highlight node đang xét
                if (r, c) not in [start, end]:
                    self.ui.paint_cell(r, c, "lightblue")
                    self.ui.log(f"Mở rộng {color} tại ({r},{c})")
        
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
                                next_q.append((nr, nc))

            # Chọn k node tốt nhất 
            if next_q:
                def manhattan(pos):
                    (r, c) = pos
                    (ex, ey) = end
                    return abs(r - ex) + abs(c - ey)
                top_k = heapq.nsmallest(k, next_q, key=lambda x: manhattan(x))
                current_q = deque(top_k)
                self.ui.log(f"Giữ {k}/{len(next_q)} node tốt nhất")
            else:
                # Không tìm thấy node tiếp theo
                self.ui.log(f"Không tìm được đường đi cho màu {color}")
                return None

        return None

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
    
    
    def forward_check(self, grid, remaining_colors):
        for color in remaining_colors:
            s, e = self.ui.pairs[color]
            # nếu không còn đường nối khả thi cho màu này thì fail sớm
            if not self.path_exists(grid, s, e, color):
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
        
    def csp_ac3_solver(self, grid, colors):
        # kiểm tra stop request
        if self.ui.stop_requested:
            return False, None

        # nếu không còn màu nào => đã giải xong
        if not colors:
            return True, grid

        # Khai báo biến
        variables = []
        for i in range(self.ui.grid_size):
            for j in range(self.ui.grid_size):
                if grid[i][j] == "":
                    variables += [(i, j)]

        # Miền giá trị của mỗi biến
        domains = {x: colors for x in variables}

        # Thu hẹp domains lại dựa trên khoảng cách
        for var, cl in domains.items():
            r, c = var
            possibleColors = {}
            for color in cl:
                start, end = self.ui.pairs[color]
                d_to_start = abs(r - start[0]) + abs(c - start[1])              # k/c tới start
                d_to_end = abs(r - end[0]) + abs(c - end[1])                    # k/c tới end
                d_start_end = abs(start[0] - end[0]) + abs(start[1] - end[1])   # k/c start tới end
                # độ ưu tiên: ô càng gần đường nối 2 màu có độ ưu tiên càng cao
                score = (d_start_end + 8) - (d_to_start + d_to_end)
                possibleColors[color] = score

            domains[var] = sorted(cl, key=lambda x: possibleColors[x], reverse=True)

        def is_neighbor(var1, var2):
            # Kiểm tra 2 ô có kề nhau không
            r1, c1 = var1
            r2, c2 = var2
            return abs(r1 - r2) + abs(c1 - c2) == 1

        def constraint(var_i, val_i, var_j, val_j):
            """
            Constraint giữa 2 biến kề nhau

            Quy tắc:
            - Nếu 2 ô cùng màu → OK (tạo thành path)
            - Nếu 2 ô khác màu → OK (các path song song)
            - Luôn return True (constraint đơn giản nhất)

            Constraint phức tạp hơn sẽ kiểm tra path continuity
            """
            # Constraint cơ bản: Luôn thỏa mãn
            # (AC-3 sẽ không loại bỏ gì với constraint này)
            return True

        # Tạo các cung (arc)
        arcs = []
        for var_i in variables:
            for var_j in variables:
                if var_i != var_j and is_neighbor(var_i, var_j):
                    arcs.append((var_i, var_j))

        def revise(xi, xj):
            # Loại bỏ giá trị từ domain[xi] nếu không consistent với domain[xj]
            removed = False
            valid_vals = []
            for vi in domains[xi]:
                if any(constraint(xi, vi, xj, vj) for vj in domains[xj]):
                    valid_vals.append(vi)
            if len(valid_vals) < len(domains[xi]):
                domains[xi] = valid_vals
                removed = True
            return removed

        def ac3():
            # Thuật toán AC-3 cơ bản
            # Khởi tạo queue với tất cả arcs
            queue = list(arcs)

            while queue:
                if self.ui.stop_requested:
                    return False

                # Lấy arc từ queue
                xi, xj = queue.pop(0)

                # Revise domain của xi dựa trên xj
                if revise(xi, xj):
                    # Nếu domain[xi] rỗng → Không có solution
                    if len(domains[xi]) == 0:
                        self.ui.log(f"AC-3: Domain của {xi} rỗng!")
                        return False

                    # Thêm lại các arcs (xk, xi) vào queue
                    # (với xk là neighbors của xi, xk != xj)
                    for xk in variables:
                        if xk != xi and xk != xj and is_neighbor(xk, xi):
                            queue.append((xk, xi))

            return True

        self.ui.log("Chạy AC-3...")

        if not ac3():
            self.ui.log("AC-3 thất bại: Không có solution!")
            return False, None

        self.ui.log("AC-3 hoàn thành!")

        # Log kết quả domains
        for var in variables:
            self.ui.log(f"  Domain[{var}] = {domains[var]}")

        
        # ======== Backtracking đơn giản ============
        
        assignment = {}
        color_paths = {color: [self.ui.pairs[color][0]] for color in colors}
        grid_copy = [row[:] for row in grid]

        # --- Forward checking (kiểm tra còn đường nối khả thi) ---
        def path_exists(grid, start, end, color):
            q = deque([start])
            visited = {start}
            while q:
                r, c = q.popleft()
                if (r, c) == end:
                    return True
                for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                        if (nr, nc) not in visited:
                            cell = grid[nr][nc]
                            if cell == "" or cell == color or (nr, nc) == end:
                                visited.add((nr, nc))
                                q.append((nr, nc))
            return False

        # --- Chọn thứ tự màu theo khoảng cách (xa trước) ---
        def manhattan(color):
            s, e = self.ui.pairs[color]
            return abs(s[0] - e[0]) + abs(s[1] - e[1])

        color_order = sorted(colors, key=manhattan, reverse=True)

        # --- Hàm backtrack chính ---
        def backtrack(color_idx):
            if self.ui.stop_requested:
                return False

            # Nếu đã đi hết các màu 
            if color_idx == len(color_order):
                return True

            color = color_order[color_idx]
            start, end = self.ui.pairs[color]
            path = color_paths[color]

            # Nếu đã tới đích → sang màu tiếp theo
            if path[-1] == end:
                # Vẽ đường đi 
                self.ui.paint_path(path, color)
                self.ui.master.update()
                time.sleep(self.ui.speed)
                return backtrack(color_idx + 1)

            r, c = path[-1]
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size):
                    continue

                cell = grid_copy[nr][nc]
                if cell == "" or (nr, nc) == end:
                    # Gán màu tạm thời
                    grid_copy[nr][nc] = color
                    path.append((nr, nc))

                    # Forward checking: kiểm tra các màu khác còn khả thi không
                    valid = True
                    for other in colors:
                        if other != color:
                            s, e = self.ui.pairs[other]
                            if not path_exists(grid_copy, s, e, other):
                                valid = False
                                break

                    if valid and backtrack(color_idx):
                        return True

                    # Quay lui
                    grid_copy[nr][nc] = ""
                    path.pop()

            return False

        # --- Bắt đầu tìm kiếm ---
        self.ui.log("Bắt đầu Backtracking tìm đường sau AC-3...")

        if backtrack(0):
            new_grid = [row[:] for row in grid_copy]
            for (r, c), val in assignment.items():
                new_grid[r][c] = val
            self.ui.log("CSP AC-3 + Backtracking tìm được lời giải!")
            return True, new_grid
        else:
            self.ui.log("Backtracking thất bại sau AC-3!")
            return False, None
    
    def beliefSearch_bfs_solver(self, grid, colors):
        if self.ui.stop_requested:
            return False, None
        
        if not colors:
            return True, grid
        
        # Sắp xếp màu theo heuristic
        def manhattan(color):
            start, end = self.ui.pairs[color]
            return abs(start[0] - end[0]) + abs(start[1] - end[1])
    
        # Thử nhiều chiến lược sắp xếp
        strategies = [
            sorted(colors, key=manhattan, reverse=True),   # Xa nhất trước
            sorted(colors, key=manhattan),                 # Gần nhất trước
            colors,                                                 # Thứ tự gốc
            list(reversed(colors))                                  # Đảo ngược
        ]

        for order in strategies:
            self.ui.log(f"Thử thứ tự: {order}")
            new_grid = [row[:] for row in grid]
            solved = True
            self.ui.reset_game()

            for color in order:
                start, end  = self.ui.pairs[color]
                self.ui.log(f"➡️ Tìm đường cho màu {color} bằng BFS...")
                path = self.belief_bfs_find_path(new_grid, start, end, color)

                if not path:
                    self.ui.log(f"⚠️ Không tìm được đường cho màu {color}")
                    solved = False
                    continue
                
                for (r, c) in path:
                    new_grid[r][c] = color

                # tô luôn đường tìm được cho cặp này
                self.ui.paint_path(path, color)
                self.ui.master.update()
                
            if solved:
                self.ui.log(f"Tìm được lời giải với thứ tự: {order}")
                return True, new_grid
            
        self.ui.log("⛔ Không có lời giải với bất kỳ root nào.")
        return False, None
    
    def belief_bfs_find_path(self, grid, start, end, color):
        # Khởi tạo belief start gồm start và các ô lân cận
        # duyệt 4 hướng
        belief_start = {(start)}
        r, c = start
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < self.ui.grid_size and 
                0 <= nc < self.ui.grid_size and
                (grid[nr][nc] == "" or (nr, nc) == end)):
                belief_start.add((nr, nc))
                    
        belief_start = frozenset(belief_start)

        q = deque([(belief_start, [])])     # (belief, actions)
        visited = {belief_start}

        # Lưu parent để reconstruct path
        parent = {belief_start: (None, None)}  # belief -> (parent_belief, action)
    
        # 4 hành động: lên, xuống, trái, phải
        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        action_names = ['UP', 'DOWN', 'LEFT', 'RIGHT']

        while q:
            # Kiểm tra stop request
            if self.ui.stop_requested:
                return False, None

            curBelief, action_seq = q.popleft()

            # Kiểm tra goal: TẤT CẢ states trong belief đều là end
            if all(state == end for state in curBelief):
                # Reconstruct path từ action sequence
                path = self.reconstruct_path_from_actions(start, action_seq, grid, end)
                if path:
                    self.ui.log(f"✓ Tìm được path sau {len(action_seq)} actions: {path}")
                    return path

            # Sinh belief : thử từng action
            for action, action_name in zip(actions, action_names):
                dr, dc = action
                next_belief = set()
            
                # Áp dụng action cho TẤT CẢ states trong belief
                for state in curBelief:
                    r, c = state
                    nr, nc = r + dr, c + dc
                    
                    # Kiểm tra valid
                    if (0 <= nr < self.ui.grid_size and 
                        0 <= nc < self.ui.grid_size and
                        (grid[nr][nc] == "" or (nr, nc) == end)):
                        next_belief.add((nr, nc))
                    else:
                        # Nếu không đi được, giữ nguyên vị trí
                        next_belief.add(state)
                next_belief = frozenset(next_belief)
            
                # Thêm vào queue nếu chưa thăm
                if next_belief not in visited:
                    visited.add(next_belief)
                    q.append((next_belief, action_seq + [action]))
                    parent[next_belief] = (curBelief, action)
    
        return None
    
    def reconstruct_path_from_actions(self, start, actions, grid, end):
        """
        Từ start và chuỗi actions, tạo lại path thực tế.
        Chọn một state bất kỳ từ belief cuối và trace ngược.
        """
        path = [start]
        r, c = start
        
        for dr, dc in actions:
            nr, nc = r + dr, c + dc
            
            # Kiểm tra có thể đi được không
            if (0 <= nr < self.ui.grid_size and 
                0 <= nc < self.ui.grid_size and
                (grid[nr][nc] == "" or (nr, nc) == end)):
                r, c = nr, nc
                path.append((r, c))
            # Nếu không đi được, giữ nguyên (state không đổi)
        
        # Kiểm tra có đến đích không
        if path[-1] == end:
            return path
        
        return None
    
