import tkinter as tk
import time
from algorithm_ff import algorithm




class UI:
    def __init__(self, master):
        self.master = master
        self.algo = algorithm(self)
        master.title("Flow Game Solver")
        master.minsize(800, 600)

        self.grid_size = 6
        self.colors = ["red", "green", "blue", "yellow", "orange"]
        self.cell_size = 70
        self.speed = 0.2
        self.is_solving = False # kt có đang giải không
        self.stop_requested = False # flag dừng

        # ví dụ pairs
        self.pairs = {
            "red": [(0, 3), (0, 5)],
            "green": [(0, 4), (4, 4)],
            "blue": [(0, 0), (1, 1)],
            "yellow": [(1, 0), (0, 2)],
            "orange": [(2, 1), (4, 1)]
        }

        self.initial_grid = []

        for _ in range(self.grid_size):          # lặp qua số hàng
            row = []                             # tạo một hàng rỗng
            for _ in range(self.grid_size):      # lặp qua số cột
                row.append('')                   # thêm 1 ô rỗng vào hàng
            self.initial_grid.append(row)        # thêm hàng vào lưới
        for color, pair in self.pairs.items():
            self.initial_grid[pair[0][0]][pair[0][1]] = color
            self.initial_grid[pair[1][0]][pair[1][1]] = color

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_canvas(self.main_frame)
        self.create_control_panel(self.main_frame)


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

        # --- lựa chọn thuật toán---
        tk.Label(panel, text="Actions", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(panel, text="Reset", command=self.reset_game, width=12).pack(pady=3)
        tk.Button(panel, text="Stop", command=self.stop_solving, width=12).pack(pady=3)
        tk.Button(panel, text="DFS", command=lambda: self.solve_game(DFS=True), width=12).pack(pady=3)
        tk.Button(panel, text="BFS", command=lambda: self.solve_game(BFS=True), width=12).pack(pady=3)

        # --- lựa chọn cài đặt---
        tk.Label(panel, text="Settings", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(panel, text="Speed:").pack()
        self.speed_slider = tk.Scale(panel, from_=0.05, to=2.0,
                                     resolution=0.05, orient="horizontal",
                                     command=self.update_speed, length=150)
        self.speed_slider.set(self.speed)
        self.speed_slider.pack(pady=5)

        # --- hiển thị thông tin---
        tk.Label(panel, text="Info", font=("Arial", 12, "bold")).pack(pady=10)
        self.status_label = tk.Label(panel, text="Sẵn sàng...", fg="black")
        self.status_label.pack(pady=5)

        self.timer_label = tk.Label(panel, text="⏱ 0.0s", font=("Arial", 11))
        self.timer_label.pack(pady=5)

    def update_speed(self, val):
        self.speed = 0.2 / float(val)


    def mark_start_end(self):
        for color, points in self.pairs.items():
            for (r, c) in points:
                # tô màu nền
                self.canvas.itemconfig(self.rects[(r, c)], fill="white", outline="black")
                # thêm hình tròn để phân biệt
                x1, y1, x2, y2 = self.canvas.coords(self.rects[(r, c)])
                self.canvas.create_oval(
                    x1 + 15, y1 + 15, x2 - 15, y2 - 15,
                    fill=color, outline=color, width=2
                )

    def stop_solving(self):
        self.stop_requested = True
        self.status_label.config(text="Stop...", fg="orange")


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
        self.is_solving = True
        self.stop_requested = False
        start_time = time.time()
        self.status_label.config(text="Đang giải...", fg="blue")
        self.master.update_idletasks()

        if DFS:
            solved, solution = self.algo.dfs_solver(self.initial_grid, list(self.colors), 0)
        if BFS:
            solved, solution = self.algo.bfs_solver(self.initial_grid, list(self.colors))

        elapsed = time.time() - start_time
        self.timer_label.config(text=f"⏱ {elapsed:.2f}s")

        if self.stop_requested:
            self.status_label.config(text="Đã dừng!", fg="orange")
        elif solved:
            self.status_label.config(text="Đã giải xong!", fg="green")
        else:
            self.status_label.config(text="Không tìm thấy lời giải.", fg="red")

        self.is_solving = False
    

    #Hien thi duong di ma thuat toan duyet qua
    def paint_cell(self, r, c, color):
        self.canvas.itemconfig(self.rects[(r, c)], fill=color)
        self.master.update()
        time.sleep(self.speed)   

    #Hien thi duong di tung cap mau da xac dinh
    def paint_path(self, path, color):
        cell_size = self.cell_size  # kích thước 1 ô

        tag = f"path_{color}"
        # Xoá path cũ trước khi vẽ lại
        self.canvas.delete(tag)

        # Vẽ đường nối giữa các ô
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]

            x1, y1 = c1 * cell_size + cell_size // 2, r1 * cell_size + cell_size // 2
            x2, y2 = c2 * cell_size + cell_size // 2, r2 * cell_size + cell_size // 2

            self.canvas.create_line(x1, y1, x2, y2,
                                    fill=color, width=cell_size // 2,
                                    capstyle="round",tags=(tag,))

            self.master.update()
            time.sleep(self.speed)



    def reset_game(self):
        # Dừng quá trình giải nếu đang chạy
        if self.is_solving:
            self.stop_requested = True
            time.sleep(0.1)  
        
        # Xóa tất cả các đường vẽ
        for color in self.colors:
            self.canvas.delete(f"path_{color}")
        
        self.mark_start_end()
        self.status_label.config(text="Sẵn sàng...", fg="black")
        self.timer_label.config(text="⏱ 0.0s")
        self.stop_requested = False

