import tkinter as tk
import time
from collections import deque

from algorithm_ff import algorithm
import customtkinter as ctk



class UI:
    def __init__(self, master):
        self.master = master
        self.algo = algorithm(self)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Kích thước cửa sổ mong muốn
        window_width = 1100
        window_height = 1000

        # Lấy kích thước màn hình
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        master.title("Flow Game Solver")
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        master.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.grid_size = 10
        self.colors = ["red", "green", "blue", "yellow", "orange", "cyan", "violet", "crimson"]
        self.cell_size = 70
        self.speed = 0.2
        self.is_solving = False # kt có đang giải không
        self.stop_requested = False # flag dừng

        # ví dụ pairs
        self.pairs = {
            "red": [(3, 8), (5, 0)],
            "green": [(0, 9), (8, 5)],
            "blue": [(5, 1), (6, 6)],
            "yellow": [(5, 3), (3, 5)],
            "orange": [(2, 2), (4, 5)],
            "cyan": [(2, 6), (5, 4)],
            "violet": [(0, 7), (7, 7)],
            "crimson": [(1, 7), (7, 2)]
        }



        self.initial_grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for color, pair in self.pairs.items():
            self.initial_grid[pair[0][0]][pair[0][1]] = color
            self.initial_grid[pair[1][0]][pair[1][1]] = color


        # ----- Layout chính -----
        self.main_frame = ctk.CTkFrame(master, corner_radius=20)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)



        # canvas + control
        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.canvas_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self.create_canvas(self.canvas_frame)
        self.create_control_panel(self.main_frame)
        self.create_log_panel(self.main_frame)

        self.update_grid_display(self.initial_grid)




    # ---------- UI ----------
    def create_canvas(self, parent):
        self.canvas = tk.Canvas(parent,
                                width=self.grid_size * self.cell_size,
                                height=self.grid_size * self.cell_size,
                                bg="white", highlightthickness=2, highlightbackground="#999")
        self.canvas.pack(expand=True)
        self.rects = {}
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill="white", outline="#CCC", width=1.5)
                self.rects[(r, c)] = rect
        self.mark_start_end()




    def create_control_panel(self, parent):
        panel = ctk.CTkFrame(parent, width=250, corner_radius=15)
        panel2 = ctk.CTkFrame(parent, width=250, corner_radius=15)
        panel2.grid(row=0, column=2, padx=15, pady=10, sticky="ns")
        panel.grid(row=0, column=1, sticky="ns", padx=15, pady=10)
        panel.grid_propagate(False)

        ctk.CTkLabel(panel, text="⚙️ Flow Solver", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))

        ctk.CTkButton(panel, text="⏮ Reset", command=self.reset_game, width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel, text="⏸ Stop", command=self.stop_solving, width=180).pack(pady=7, padx=10)

        ctk.CTkLabel(panel2, text="Uninformed", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))

        ctk.CTkButton(panel2, text="🌳 DFS", command=lambda: self.solve_game(DFS=True), width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="🌊 BFS", width=180, state="disabled").pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 IDS", command=lambda: self.solve_game(IDS=True),width=180).pack(pady=7, padx=10)

        ctk.CTkLabel(panel2, text="Informed", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        ctk.CTkButton(panel2, text="💡 UCS", width=180, state="disabled").pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 Greedy", width=180, state="disabled").pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 A*", width=180, state="disabled").pack(pady=7, padx=10)

        ctk.CTkLabel(panel2, text="Local & Optimization", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        ctk.CTkButton(panel2, text="💡 Hill-Climbing", width=180, state="disabled").pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="🔥 Simulated Annealing", command=lambda: self.solve_game(SA=True), width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 Beam Search", width=180, state="disabled").pack(pady=7, padx=10)

        ctk.CTkLabel(panel2, text="CSP", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        ctk.CTkButton(panel2, text="💡 Backtracking", width=180, state="disabled").pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 Forward Checking", width=180, state="disabled").pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 AC-3", width=180, state="disabled").pack(pady=7, padx=10)

        ctk.CTkLabel(panel, text="\nSpeed", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 3))
        self.speed_slider = ctk.CTkSlider(panel, from_=0.1, to=1.0, number_of_steps=20,
                                          command=self.update_speed, width=180)
        self.speed_slider.set(self.speed)
        self.speed_slider.pack(pady=5)

        ctk.CTkButton(panel, text="🌗 Toggle Theme", command=self.toggle_theme, width=180).pack(pady=5, padx=10)

        ctk.CTkLabel(panel, text="\nTrạng thái:", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(8, 2))
        self.status_label = ctk.CTkLabel(panel, text="Sẵn sàng...", text_color="lightblue" if ctk.get_appearance_mode() == "Dark" else "blue")
        self.status_label.pack(pady=3)
        self.timer_label = ctk.CTkLabel(panel, text="⏱ 0.0s", font=ctk.CTkFont(size=13))
        self.timer_label.pack(pady=3)


    def create_log_panel(self, parent):
        """Khung log bên dưới"""
        log_frame = ctk.CTkFrame(parent, corner_radius=10)
        log_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=(5, 10))
        parent.rowconfigure(1, weight=1)

        ctk.CTkLabel(log_frame, text="📜 Log hoạt động", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 3))

        self.log_box = ctk.CTkTextbox(log_frame, height=180, width=1000, corner_radius=8)
        self.log_box.pack(padx=10, pady=5, fill="both", expand=True)
        self.log_box.insert("end", "Hệ thống sẵn sàng...\n")

        clear_btn = ctk.CTkButton(log_frame, text="🧹 Clear Log", command=lambda: self.log_box.delete("1.0", "end"))
        clear_btn.pack(pady=5)

    # ---------- Helper ----------

    def log(self, msg: str):
        self.log_box.insert("end", f"{msg}\n")
        self.log_box.see("end")  # tự động cuộn xuống cuối
        self.master.update_idletasks()

    def toggle_theme(self):
        mode = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"
        ctk.set_appearance_mode(mode)
        self.log(f"🌗 Chuyển sang giao diện {mode}")
        self.status_label.configure(text_color="lightblue" if ctk.get_appearance_mode() == "Dark" else "blue")


    def update_speed(self, val):
        self.speed = 0.2 / float(val)


    def mark_start_end(self):
        for color, points in self.pairs.items():
            for (r, c) in points:
                # thêm hình tròn để phân biệt
                x1, y1, x2, y2 = self.canvas.coords(self.rects[(r, c)])
                self.canvas.create_oval(
                    x1 + 15, y1 + 15, x2 - 15, y2 - 15,
                    fill=color, outline=color, width=2,
                )
                # tô màu nền
                self.canvas.itemconfig(self.rects[(r, c)], fill="white")


    def stop_solving(self):
        self.stop_requested = True
        self.status_label.configure(text="Stop...", text_color="orange")


    def update_grid_display(self, grid_state, animate=False):
        """Cập nhật màu grid. Nếu animate=True thì tô từng bước"""
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                color = grid_state[r][c]
                fill_color = "white"
                #self.canvas.itemconfig(self.rects[(r, c)], fill=fill_color)
                if animate and color != "":
                    self.master.update()
                    time.sleep(self.speed)
        self.master.update_idletasks()

    def solve_game(self, DFS=False, BFS=False, IDS=False, SA=False):
        self.is_solving = True
        self.stop_requested = False
        start_time = time.time()
        self.status_label.configure(text="Đang giải...", text_color="lightyellow" if ctk.get_appearance_mode() == "Dark" else "yellow")
        self.log("🚀 Bắt đầu tìm lời giải...\n")
        self.master.update_idletasks()

        if DFS:
            self.log("🌳 Bắt đầu tìm kiếm bằng DFS (Stack)...")
            solved, solution = self.algo.DFSSolver(self.initial_grid, list(self.colors))
        elif BFS:
            solved, solution = self.algo.bfs_solver(self.initial_grid, list(self.colors))
        elif IDS:
            self.log("💡 Bắt đầu tìm kiếm bằng IDS...")
            solved, solution = self.algo.IDSSolver(self.initial_grid, list(self.colors))
        elif SA:
            self.log("🔥 Bắt đầu giải bằng Simulated Annealing...")
            solved, solution = self.algo.SASolver(self.initial_grid, list(self.colors))

        elapsed = time.time() - start_time
        self.timer_label.configure(text=f"⏱ {elapsed:.2f}s")

        if self.stop_requested:
            self.status_label.configure(text="Đã dừng!", text_color="orange")
            self.log("🛑 Thuật toán đã dừng theo yêu cầu.")

        elif solved:
            self.status_label.configure(text="Đã giải xong!", text_color="lightgreen")
            self.log(f"🎉 Tìm thấy lời giải trong {elapsed:.2f} giây!")
            self.log("🎨 Đang vẽ lại kết quả cuối cùng...")
            self.redraw_solution(solution)
        else:
            self.status_label.configure(text="Không tìm thấy lời giải.", text_color="red")
            self.log("💔 Không tìm thấy lời giải cho bài toán.")

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
                                    fill=color, width=cell_size // 1.6,
                                    capstyle="round",tags=(tag,))

            self.master.update()
            time.sleep(self.speed)

    def reset_game(self):
        if self.is_solving:
            self.stop_requested = True
            self.master.after(100, self._perform_reset)
        else:
            self._perform_reset()


    def redraw_solution(self, solution_grid):
        temp_speed = self.speed
        self.speed = 0.01

        self.canvas.delete("path_line_viz")
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.canvas.itemconfig(self.rects[(r, c)], fill="white")

        for color in self.colors:
            if self.stop_requested: break
            start_node, end_node = self.pairs[color]

            q = deque([[start_node]])
            path_found = []
            visited_path = {start_node}

            while q:
                path = q.popleft()
                r, c = path[-1]

                if (r, c) == end_node:
                    path_found = path
                    break

                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                        if solution_grid[nr][nc] == color and (nr, nc) not in visited_path:
                            new_path = list(path)
                            new_path.append((nr, nc))
                            q.append(new_path)
                            visited_path.add((nr, nc))
            if path_found:
                self.paint_path(path_found, color)

        self.mark_start_end()
        self.speed = temp_speed

    def _perform_reset(self):
        """Hàm reset thực sự sau khi đã dừng thuật toán"""
        self.stop_requested = False
        self.is_solving = False

        # Xóa tất cả các đường vẽ
        for color in self.colors:
            self.canvas.delete(f"path_{color}")
        self.canvas.delete("path_line_viz")

        # Tô lại màu nền trắng và vẽ lại các điểm start/end
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.canvas.itemconfig(self.rects[(r, c)], fill="white")

        # <<< SỬA: Bỏ tô màu ô, chỉ vẽ lại điểm tròn >>>
        self.mark_start_end()

        self.status_label.configure(text="Sẵn sàng...",
                                    text_color="lightblue" if ctk.get_appearance_mode() == "Dark" else "blue")
        self.timer_label.configure(text="⏱ 0.0s")
        self.log("\n🔄 Đã reset trò chơi.")

    def visualizeSearchState(self, grid_state):
        self.canvas.delete("path_line_viz")
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.canvas.itemconfig(self.rects[(r, c)], fill="white")

        for color in self.colors:
            start_node, _ = self.pairs[color]
            path = [start_node]
            visited = {start_node}
            curr_r, curr_c = start_node
            while True:
                found_next = False
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = curr_r + dr, curr_c + dc
                    if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size and (nr, nc) not in visited:
                        if grid_state[nr][nc] == color:
                            path.append((nr, nc))
                            visited.add((nr, nc))
                            curr_r, curr_c = nr, nc
                            found_next = True
                            break
                if not found_next:
                    break
            if len(path) > 1:
                cell_size = self.cell_size
                for i in range(len(path) - 1):
                    r1, c1 = path[i]
                    r2, c2 = path[i + 1]
                    x1 = c1 * cell_size + cell_size // 2
                    y1 = r1 * cell_size + cell_size // 2
                    x2 = c2 * cell_size + cell_size // 2
                    y2 = r2 * cell_size + cell_size // 2
                    self.canvas.create_line(x1, y1, x2, y2,
                                            fill=color, width=cell_size // 1.6,
                                            capstyle="round", tags=("path_line_viz",))
        self.mark_start_end()
        self.master.update()
        time.sleep(self.speed)



