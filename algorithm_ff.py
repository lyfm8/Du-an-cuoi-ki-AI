from collections import deque
import heapq
import random
import copy
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
        Reconstruct path từ action sequence.
        - Loại bỏ các ô trùng lặp (chu trình)
        - Nếu có nhiều path, chọn shortest path bằng BFS
        """
        # Bước 1: Follow actions để tạo path thô (có thể có chu trình)
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
            # Nếu không đi được, giữ nguyên (không thêm vào path)
        
        # Bước 2: Kiểm tra có đến đích không
        if path[-1] != end:
            # Nếu không đến được end, dùng BFS tìm path
            return self.bfs_shortest_path(grid, start, end)
        
        # Bước 3: Loại bỏ chu trình bằng cách chỉ giữ lần xuất hiện cuối
        seen = {}
        for i, pos in enumerate(path):
            seen[pos] = i  # Lưu index xuất hiện cuối cùng
        
        # Tạo path mới không có chu trình
        cleaned_path = []
        visited_in_clean = set()
        
        for pos in path:
            if pos not in visited_in_clean:
                cleaned_path.append(pos)
                visited_in_clean.add(pos)
        
        # Bước 4: Kiểm tra cleaned_path có hợp lệ không (các ô liên tiếp)
        valid = True
        for i in range(len(cleaned_path) - 1):
            r1, c1 = cleaned_path[i]
            r2, c2 = cleaned_path[i + 1]
            # Kiểm tra 2 ô có kề nhau không
            if abs(r1 - r2) + abs(c1 - c2) != 1:
                valid = False
                break
        
        if valid:
            return cleaned_path
        else:
            # Nếu path bị đứt sau khi loại chu trình, dùng BFS
            return self.bfs_shortest_path(grid, start, end)

    
    def bfs_shortest_path(self, grid, start, end):
        #Tìm shortest path bằng BFS thông thường
        
        q = deque([(start, [start])])
        visited = {start}
        
        while q:
            (r, c), path = q.popleft()
            
            if (r, c) == end:
                return path
            
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                
                if (0 <= nr < self.ui.grid_size and 
                    0 <= nc < self.ui.grid_size and
                    (nr, nc) not in visited and
                    (grid[nr][nc] == "" or (nr, nc) == end)):
                    
                    visited.add((nr, nc))
                    q.append(((nr, nc), path + [(nr, nc)]))
        
        return None
