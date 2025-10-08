import tkinter as tk
import time
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
        ctk.CTkButton(panel2, text="🌊 BFS", command=lambda: self.solve_game(BFS=True), width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 IDS", width=180).pack(pady=7, padx=10)

        ctk.CTkLabel(panel2, text="Informed", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        ctk.CTkButton(panel2, text="💡 UCS", width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 Greedy", command=lambda: self.solve_game(GREEDY=True), width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 A*", width=180).pack(pady=7, padx=10)

        ctk.CTkLabel(panel2, text="Local & Optimization", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        ctk.CTkButton(panel2, text="💡 Hill-Climbing", command=lambda: self.solve_game(HC=True), width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 Simulated Annealing", width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 Beam Search", width=180).pack(pady=7, padx=10)

        ctk.CTkLabel(panel2, text="CSP", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        ctk.CTkButton(panel2, text="💡 Backtracking + FC", command=lambda: self.solve_game(backtracking_fc=True), width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 ", width=180).pack(pady=7, padx=10)
        ctk.CTkButton(panel2, text="💡 AC-3", width=180).pack(pady=7, padx=10)

        ctk.CTkLabel(panel, text="\nSpeed", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 3))
        self.speed_slider = ctk.CTkSlider(panel, from_=0.05, to=2.0, number_of_steps=20,
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

    def solve_game(self, DFS=False, BFS=False, GREEDY = False, HC = False, 
                   backtracking_fc=False):
        self.is_solving = True
        self.stop_requested = False
        start_time = time.time()
        self.status_label.configure(text="Đang giải...", text_color="lightyellow" if ctk.get_appearance_mode() == "Dark" else "yellow")
        self.log("🚀 Bắt đầu tìm lời giải...\n")
        self.master.update_idletasks()

        if DFS:
            solved, solution = self.algo.dfs_solver(self.initial_grid, list(self.colors), 0)
        if BFS:
            solved, solution = self.algo.bfs_solver(self.initial_grid, list(self.colors))
        if GREEDY:
            solved, solution = self.algo.greedy_solver(self.initial_grid, list(self.colors), alpha=1)
        if HC:
            solved, solution = self.algo.hc_solver(self.initial_grid, list(self.colors), max_steps=10)
        if backtracking_fc:
            solved, solution = self.algo.b_fc_solver(self.initial_grid, list(self.colors))


        elapsed = time.time() - start_time
        self.timer_label.configure(text=f"⏱ {elapsed:.2f}s")

        if self.stop_requested:
            self.status_label.configure(text="Đã dừng!", text_color="orange")
        elif solved:
            self.status_label.configure(text="Đã giải xong!", text_color="lightblue" if ctk.get_appearance_mode() == "Dark" else "blue")
        else:
            self.status_label.configure(text="Không tìm thấy lời giải.", text_color="red")

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
        # Dừng quá trình giải nếu đang chạy
        if self.is_solving:
            self.stop_requested = True
            time.sleep(0.1)

        # Xóa tất cả các đường vẽ
        for color in self.colors:
            self.canvas.delete(f"path_{color}")

        # xoá các marker cũ
        self.canvas.delete()

        # dat tat ca o ve ban dau
        for _ in self.rects.values():
            self.canvas.itemconfig(_, fill='white')

        #ve lai cac cap mau
        self.mark_start_end()

        self.status_label.configure(text="Sẵn sàng...", text_color="lightblue" if ctk.get_appearance_mode() == "Dark" else "blue")
        self.timer_label.configure(text="⏱ 0.0s")
        self.stop_requested = False


