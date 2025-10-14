import math
import random
from collections import deque
import copy





class algorithm:
    def __init__(self, ui):
        self.ui=ui


    # ---------- DFS ---------

    def blocked(self, grid, colorsToCheck):
        #Kiem tra state(grid) hien tai co mau nao bi chan khono (flood fill)
        for color in colorsToCheck:
            start, end = self.ui.pairs[color]

            q = deque([start])
            visited = {start}
            found = False
            while q:
                r, c = q.popleft()
                if (r,c) == end:
                    found = True
                    break
                for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size and (nr, nc) not in visited:
                        if grid[nr][nc] == '' or (nr, nc) == end:
                            visited.add((nr, nc))
                            q.append((nr, nc))
            if not found:
                return True
        return False

    def findAllPaths(self, grid, start, end, path, visited):
        #Tim tat ca duong di co the cua mot mau
        if self.ui.stop_requested:
            return

        r, c = path[-1]
        if (r, c) == end:
            yield path[:]
            return

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                if (nr, nc) not in visited and (grid[nr][nc] == '' or (nr, nc) == end):
                    path.append((nr, nc))
                    visited.add((nr, nc))
                    yield from self.findAllPaths(grid, start, end, path, visited)
                    path.pop()
                    visited.remove((nr, nc))

    def DFSSolver(self, intialGrid, colors):
        stack = [(intialGrid, colors)]
        while stack:
            if self.ui.stop_requested:
                return False, None
            currentGrid, colorsToSolve = stack.pop()
            self.ui.visualizeSearchState(currentGrid)

            if not colorsToSolve:
                return True, currentGrid

            colorsToProcess = colorsToSolve[0]
            remainingColors = colorsToSolve[1:]
            start, end = self.ui.pairs[colorsToProcess]

            self.ui.log(f"Dang xu ly {colorsToProcess}...")
            pathGenerator = self.findAllPaths(currentGrid, start, end, [start], {start})

            paths = sorted(list(pathGenerator), key=len, reverse=True)

            if not paths:
                self.ui.log(f"   x Khong tim thay duonng cho {colorsToProcess}!")

            for path in paths:
                if self.ui.stop_requested:
                    return False, None
                newGrid = [row[:] for row in currentGrid]
                for r, c in path:
                    newGrid[r][c] = colorsToProcess

                pathStr = "->".join(map(str, path)) #chuyen path thanh chuoi duong di
                #self.ui.log(f" -> Thu duong di cho {colorsToProcess}: {pathStr}")

                if not self.blocked(newGrid, remainingColors):
                    self.ui.log(f" Hop le. Dua trang thai vao stack. Duong di: {pathStr}")
                    stack.append((newGrid, remainingColors))
                #else:
                    #self.ui.log(" Chan duong mau khac nen khong dua vao stack")
        return False, None

    def IDSSolver(self, intialGrid, colors):
        numCells = self.ui.grid_size*self.ui.grid_size
        for depth_limit in range(1, numCells+1):
            if self.ui.stop_requested:
                return False, None

            self.ui.log(f"Dang xu ly o do sau {depth_limit}...")

            stack = [(intialGrid, colors, 0)]
            visitedState = {tuple(map(tuple, intialGrid))}
            while stack:
                if self.ui.stop_requested:
                    return False, None
                currentGrid, colorsToSolve, currentDepth = stack.pop()
                self.ui.visualizeSearchState(currentGrid)

                if not colorsToSolve:
                    return True, currentGrid

                if currentDepth >= depth_limit:
                    continue

                colorsToProcess = colorsToSolve[0]
                remainingColors = colorsToSolve[1:]
                start, end = self.ui.pairs[colorsToProcess]

                self.ui.log(f"Dang xu ly {colorsToProcess} o do sau {depth_limit}...")
                pathGenerator = self.findAllPaths(currentGrid, start, end, [start], {start})

                paths = sorted(list(pathGenerator), key=len, reverse=True)

                if not paths:
                    self.ui.log(f" x Khong tim thay duonng cho {colorsToProcess}!")

                for path in paths:
                    if self.ui.stop_requested:
                        return False, None
                    newGrid = [row[:] for row in currentGrid]
                    for r, c in path:
                        newGrid[r][c] = colorsToProcess

                    pathStr = "->".join(map(str, path))
                    #self.ui.log(f" -> Thu duong di cho {colorsToProcess}: {pathStr}")
                    if not self.blocked(newGrid, remainingColors):
                        stateTuple = tuple(map(tuple, newGrid))
                        if stateTuple not in visitedState:
                            self.ui.log(f" Hop le. Dua trang thai vao stack. Duong di:{pathStr}")
                            stack.append((newGrid, remainingColors, currentDepth+1))
                            visitedState.add(stateTuple)
                        else:
                            self.ui.log(f" Trang thai nay da duyet, khong duyet lai. Duong di:{pathStr}")
                    #else:
                        #self.ui.log(" Trang thai nay co mau bi chan duong")
        return False, None

    def SASolver(self, intialGrid, colors, TStart=100, TEnd=1, alpha=0.95, maxIter=500):
        currentGrid = copy.deepcopy(intialGrid)
        bestGrid = copy.deepcopy(intialGrid)
        currentCost = self.evaluateCost(currentGrid, colors)
        bestCost = currentCost
        T = TStart
        iterations = 0

        self.ui.log(f"🔥 Bắt đầu Simulated Annealing...")
        self.ui.log(f"  🔹 Nhiệt độ khởi tạo: {TStart}, hệ số giảm: {alpha}")
        self.ui.log(f"  🔹 Cost ban đầu: {currentCost}")

        while T > TEnd and iterations < maxIter:
            iterations += 1
            newGrid = self.generateNeighbor(currentGrid, colors)
            newCost = self.evaluateCost(newGrid, colors)

            delta = newCost - currentCost
            accept = False

            if delta < 0:
                accept = True
                reason = "Tot hon truoc"
            else:
                prob = math.exp(-delta/T)
                if random.random() < prob:
                    accept = True
                    reason = f"Te hon nhung van chap nhan voi xac suat {prob:.3f}"
                else:
                    reason = f"Te hon va bi tu choi (Δ={delta})"

            if accept:
                currentGrid = copy.deepcopy(newGrid)
                currentCost = newCost

                self.ui.log(f" [{iterations}] Chap nhan trang thai moi ({reason}), cost={newCost}, T={T:.2f}")
                self.ui.visualizeSearchState(currentGrid)
            else:
                self.ui.log(f" [{iterations}] ({reason})")

            if newCost < bestCost:
                bestGrid = copy.deepcopy(newGrid)
                bestCost = newCost
                self.ui.log(f" Tim thay trang thai tot hon (best cost={bestCost})")
            if bestCost == 0:
                self.ui.log(f" Da tim thay loi giai sau {iterations} lan lap")
                return True, bestGrid

            T*=alpha

        if bestCost == 0:
            return True, bestGrid
        else:
            self.ui.log(f" Dung lai sau {iterations} lan lap. Best cost={bestCost}")
            return False, bestGrid

    def evaluateCost(self, grid, colors):
        totalCost = 0
        penaltyBlock = 0
        penaltyEmpty = 0

        for color in colors:
            start, end = self.ui.pairs[color]
            dist = abs(start[0] - end[0]) + abs(start[1] - end[1]) #mahattan

            #Dem so o ma mau nay dang chiem
            occupied = sum(1 for r in range(self.ui.grid_size)
                           for c in range(self.ui.grid_size)
                           if grid[r][c] == color)

            q = deque([start])
            visited = {start}
            foundEnd = False
            while q:
                r, c = q.popleft()
                if (r, c) == end:
                    foundEnd = True
                    break
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.ui.grid_size and 0 <= nc < self.ui.grid_size:
                        if grid[nr][nc] == color and (nr, nc) not in visited:
                            q.append((nr, nc))
                            visited.add((nr, nc))
            if not foundEnd:
                totalCost += 10

            totalCost += abs(occupied-dist)

        if self.blocked(grid, colors):
            penaltyBlock += 5

        #Dem so o trong
        emptyCells = sum(1 for r in range(self.ui.grid_size)
                         for c in range(self.ui.grid_size)
                         if grid[r][c] == '')
        penaltyEmpty += emptyCells /4

        return totalCost + penaltyBlock + penaltyEmpty
    def generateNeighbor(self, grid, colors):
        newGrid = copy.deepcopy(grid)
        color = random.choice(colors)
        start, end = self.ui.pairs[color]

        #Xoa duong hien tai cua mau duoc chon
        for r in range(self.ui.grid_size):
            for c in range(self.ui.grid_size):
                if newGrid[r][c] == color and (r, c) not in [start, end]:
                    newGrid[r][c] = ''
        #Sinh duong moi sau khi xoa
        path = [start]
        visited = {start}
        for _ in range(random.randint(3, self.ui.grid_size*2 )):
            r,c = path[-1]
            moves = [(r + dr, c + dc) for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                     if 0 <= r + dr < self.ui.grid_size and 0 <= c + dc < self.ui.grid_size]
            random.shuffle(moves)
            for nr, nc in moves:
                if (nr, nc) not in visited and (newGrid[nr][nc] in ['', color] or (nr, nc)==end):
                    path.append((nr, nc))
                    visited.add((nr, nc))
                    newGrid[nr][nc] = color
                    if (nr, nc) == end:
                        return newGrid
                    break
        return newGrid



