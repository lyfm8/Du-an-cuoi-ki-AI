import os
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
        window_width = 1100*2
        window_height = 1000

        # Lấy kích thước màn hình
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        master.title("Flow Game Solver")
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        #master.state('zoomed')

        self.grid_size = 6
        #self.grid_size = 10
        '''self.colors = ["red", "green", "blue", "yellow", "orange", "cyan", "violet", "crimson"]'''
        self.colors = ["red", "green", "blue", "yellow", "orange"]
        self.cell_size = 70
        self.speed = 0.2
        self.is_solving = False # kt có đang giải không
        self.stop_requested = False # flag dừng

        # ví dụ pairs
        '''self.pairs = {
            "red": [(3, 8), (5, 0)],
            "green": [(0, 9), (8, 5)],
            "blue": [(5, 1), (6, 6)],
            "yellow": [(5, 3), (3, 5)],
            "orange": [(2, 2), (4, 5)],
            "cyan": [(2, 6), (5, 4)],
            "violet": [(0, 7), (7, 7)],
            "crimson": [(1, 7), (7, 2)]
        }'''
        self.pairs = {
            "red": [(0, 3), (0, 5)],
            "green": [(0, 4), (4, 4)],
            "blue": [(0, 0), (1, 1)],
            "yellow": [(1, 0), (0, 2)],
            "orange": [(2, 1), (4, 1)]
        }



        self.initial_grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        '''for color, pair in self.pairs.items():
            self.initial_grid[pair[0][0]][pair[0][1]] = color
            self.initial_grid[pair[1][0]][pair[1][1]] = color'''
        self._init_grid_from_pairs()


        # ----- Layout chính -----
        self.main_frame = ctk.CTkFrame(master, corner_radius=20)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)



        # canvas + control
        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.canvas_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # prepare placeholders for control widgets references
        self.control_buttons = []
        self.speed_slider = None
        self.level_combobox = None
        self.load_level_button = None
        self.stop_button = None

        self.create_canvas(self.canvas_frame)
        self.create_control_panel(self.main_frame)
        self.create_log_panel(self.main_frame)

        self.update_grid_display(self.initial_grid)

        # ensure levels folder exists and populate combobox
        self.levels_folder = os.path.join(os.getcwd(), "levels")
        os.makedirs(self.levels_folder, exist_ok=True)
        self.load_levels_list()


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
        panel3 = ctk.CTkFrame(parent, width=250, corner_radius=15)
        panel.grid(row=0, column=1, sticky="ns", padx=15, pady=10)
        panel2.grid(row=0, column=2, padx=15, pady=10, sticky="ns")
        panel3.grid(row=0, column=3, padx=15, pady=10, sticky="ns")

        panel.grid_propagate(False)

        ctk.CTkLabel(panel, text="⚙️ Flow Solver", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))

        reset_btn = ctk.CTkButton(panel, text="⏮ Reset", command=self.reset_game1, width=180)
        reset_btn.pack(pady=7, padx=10)
        self.control_buttons.append(reset_btn)
        ctk.CTkButton(panel, text="⏸ Stop", command=self.stop_solving, width=180).pack(pady=7, padx=10)

        ctk.CTkLabel(panel2, text="Uninformed", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))

        dfs_btn = ctk.CTkButton(panel2, text="🌳 DFS", command=lambda: self.solve_game(DFS=True), width=180)
        dfs_btn.pack(pady=7, padx=10)
        self.control_buttons.append(dfs_btn)
        bfs_bt=ctk.CTkButton(panel2, text="🌊 BFS", width=180, command=lambda: self.solve_game(BFS=True))
        bfs_bt.pack(pady=7, padx=10)
        self.control_buttons.append(bfs_bt)
        ids_btn=ctk.CTkButton(panel2, text="💡 IDS", command=lambda: self.solve_game(IDS=True),width=180)
        ids_btn.pack(pady=7, padx=10)
        self.control_buttons.append(ids_btn)

        ctk.CTkLabel(panel2, text="Informed", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        ucs_btn=ctk.CTkButton(panel2, text="💡 UCS", command=lambda: self.solve_game(UCS=True), width=180)
        ucs_btn.pack(pady=7, padx=10)
        self.control_buttons.append(ucs_btn)
        greedy_btn=ctk.CTkButton(panel2, text="💡 Greedy", width=180, command=lambda: self.solve_game(GREEDY=True))
        greedy_btn.pack(pady=7, padx=10)
        self.control_buttons.append(greedy_btn)
        astart_btn=ctk.CTkButton(panel2, text="💡 A*", width=180, command=lambda: self.solve_game(Astar=True))
        astart_btn.pack(pady=7, padx=10)
        self.control_buttons.append(astart_btn)

        ctk.CTkLabel(panel2, text="Local & Optimization", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        hill_btn=ctk.CTkButton(panel2, text="💡 Hill-Climbing", width=180, command=lambda: self.solve_game(HC=True))
        hill_btn.pack(pady=7, padx=10)
        self.control_buttons.append(hill_btn)
        SA_btn=ctk.CTkButton(panel2, text="🔥 Simulated Annealing", command=lambda: self.solve_game(SA=True), width=180)
        SA_btn.pack(pady=7, padx=10)
        self.control_buttons.append(SA_btn)
        Beam_btn=ctk.CTkButton(panel2, text="💡 Beam Search",command=lambda: self.solve_game(Beam=True), width=180)
        Beam_btn.pack(pady=7, padx=10)
        self.control_buttons.append(Beam_btn)

        ctk.CTkLabel(panel2, text="CSP", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        BT_btn=ctk.CTkButton(panel2, text="💡 Backtracking", width=180, command=lambda: self.solve_game(backtracking=True))
        BT_btn.pack(pady=7, padx=10)
        self.control_buttons.append(BT_btn)
        FC_btn=ctk.CTkButton(panel2, text="💡 Forward Checking", width=180, command=lambda: self.solve_game(backtracking_fc=True))
        FC_btn.pack(pady=7, padx=10)
        self.control_buttons.append(FC_btn)
        AC3_btn=ctk.CTkButton(panel2, text="💡 AC-3", command=lambda: self.solve_game(AC3=True), width=180)
        AC3_btn.pack(pady=7, padx=10)
        self.control_buttons.append(AC3_btn)

        ctk.CTkLabel(panel3, text="Planning", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=7, padx=10)
        AO_btn=ctk.CTkButton(panel3, text="💡 And-Or Search", width=180, command=lambda: self.solve_game(and_or=True))
        AO_btn.pack(pady=7, padx=10)
        self.control_buttons.append(AO_btn)
        BL_btn=ctk.CTkButton(panel3, text="💡 Belief Search", command=lambda: self.solve_game(Belief_Search=True),width=180)
        BL_btn.pack(pady=7, padx=10)
        self.control_buttons.append(BL_btn)

        ctk.CTkLabel(panel, text="\nSpeed", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 3))
        self.speed_slider = ctk.CTkSlider(panel, from_=0.1, to=1.0, number_of_steps=20,
                                          command=self.update_speed, width=180)
        self.speed_slider.set(self.speed)
        self.speed_slider.pack(pady=5)
        self.control_buttons.append(self.speed_slider)

        ctk.CTkButton(panel, text="🌗 Toggle Theme", command=self.toggle_theme, width=180).pack(pady=5, padx=10)

        # Level selection combobox + Load button
        ctk.CTkLabel(panel, text="\nLevel:", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(8, 2))
        self.level_combobox = ctk.CTkComboBox(panel, values=["(no levels)"], width=180)
        self.level_combobox.set("Select level")
        self.level_combobox.pack(pady=5)
        self.control_buttons.append(self.level_combobox)

        self.load_level_button = ctk.CTkButton(panel, text="📂 Load Level", command=self.load_selected_level, width=180)
        self.load_level_button.pack(pady=5)
        self.control_buttons.append(self.load_level_button)

        ctk.CTkLabel(panel, text="\nTrạng thái:", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(8, 2))
        self.status_label = ctk.CTkLabel(panel, text="Sẵn sàng...", text_color="lightblue" if ctk.get_appearance_mode() == "Dark" else "blue")
        self.status_label.pack(pady=3)
        self.timer_label = ctk.CTkLabel(panel, text="⏱ 0.0s", font=ctk.CTkFont(size=13))
        self.timer_label.pack(pady=3)


    def create_log_panel(self, parent):
        """Khung log bên dưới"""
        log_frame = ctk.CTkFrame(parent, corner_radius=10)
        log_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=15, pady=(5, 10))
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
        # Xoá các ovals cũ (nếu có)
        for item in self.canvas.find_all():
            # giữ các rect, xóa oval bằng tag (nếu có)
            pass
        # Vẽ các điểm start/end
        # Để tránh vẽ chồng chéo, xóa các ovals bằng tag 'startend'
        self.canvas.delete('startend')
        for color, points in self.pairs.items():
            for (r, c) in points:
                x1, y1, x2, y2 = self.canvas.coords(self.rects[(r, c)])
                self.canvas.create_oval(
                    x1 + 15, y1 + 15, x2 - 15, y2 - 15,
                    fill=color, outline=color, width=2, tags=('startend',)
                )
                self.canvas.itemconfig(self.rects[(r, c)], fill="white")


    def stop_solving(self):
        self.stop_requested = True
        self.status_label.configure(text="Stop...", text_color="orange")
        self.log("🛑 Yêu cầu dừng đã gửi.")


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

    def solve_game(self, DFS=False, BFS=False, IDS=False,
                   UCS=False, Astar = False, GREEDY = False,
                   Beam = False, SA=False, HC = False,
                   backtracking_fc=False, backtracking=False, AC3 = False,
                   Belief_Search = False,  and_or=False):

        # disable controls (except stop)
        self.disable_controls(True)

        self.is_solving = True
        self.stop_requested = False
        start_time = time.time()
        self.status_label.configure(text="Đang giải...", text_color="lightyellow" if ctk.get_appearance_mode() == "Dark" else "yellow")
        self.log("🚀 Bắt đầu tìm lời giải...\n")
        self.master.update_idletasks()

        solved = False
        solution = None

        try:
            if DFS:
                self.log("🌳 Bắt đầu tìm kiếm bằng DFS (Stack)...")
                solved, solution = self.algo.DFSSolver(self.initial_grid, list(self.colors))
            elif BFS:
                solved, solution = self.algo.bfs_solver(self.initial_grid, list(self.colors))
            elif IDS:
                self.log("💡 Bắt đầu tìm kiếm bằng IDS...")
                solved, solution = self.algo.IDSSolver(self.initial_grid, list(self.colors))
            elif UCS:
                self.log("💡 Bắt đầu tìm kiếm bằng UCS...")
                solved, solution = self.algo.ucs_solver(self.initial_grid, list(self.colors))
            elif GREEDY:
                self.log("💡 Bắt đầu tìm kiếm bằng GreedySearch...")
                solved, solution = self.algo.greedy_solver(self.initial_grid, list(self.colors), alpha=1)
            elif Astar:
                self.log("💡 Bắt đầu tìm kiếm bằng Astar...")
                solved, solution = self.algo.aStar_solver(self.initial_grid, list(self.colors))
            elif HC:
                self.log("💡 Bắt đầu tìm kiếm bằng HillClimbing...")
                solved, solution = self.algo.hc_solver(self.initial_grid, list(self.colors), max_steps=50)
            elif Beam:
                self.log("💡 Bắt đầu tìm kiếm BeamSearch...")
                solved, solution = self.algo.beamSearch(self.initial_grid, list(self.colors), k=2)
            elif SA:
                self.log("🔥 Bắt đầu giải bằng Simulated Annealing...")
                solved, solution = self.algo.SASolver(self.initial_grid, list(self.colors))
            elif Belief_Search:
                self.log("🔥 Bắt đầu giải bằng Belief_Search...")
                solved, solution = self.algo.beliefSearch_bfs_solver(self.initial_grid, list(self.colors))
            elif backtracking_fc:
                self.log("🔥 Bắt đầu giải bằng Backtracking_ForwardChecking...")
                solved, solution = self.algo.b_fc_solver(self.initial_grid, list(self.colors))
            elif backtracking:
                self.log("🔥 Bắt đầu giải bằng Backtracking...")
                solved, solution = self.algo.backtracking_solver(self.initial_grid, list(self.colors))
            elif AC3:
                self.log("🔥 Bắt đầu giải bằng AC3...")
                solved, solution = self.algo.csp_ac3_solver(self.initial_grid, list(self.colors))
            elif and_or:
                self.log("🔥 Bắt đầu giải bằng AndOr_Search...")
                solved, solution = self.algo.and_or_solver(self.initial_grid, list(self.colors))
        except Exception as e:
            self.log(f"⚠️ Lỗi xảy ra khi chạy thuật toán: {e}")
        finally:
            elapsed = time.time() - start_time
            self.timer_label.configure(text=f"⏱ {elapsed:.2f}s")

            if self.stop_requested:
                self.status_label.configure(text="Đã dừng!", text_color="orange")
                self.log("🛑 Thuật toán đã dừng theo yêu cầu.")
            elif solved:
                self.status_label.configure(text="Đã giải xong!", text_color="lightgreen")
                self.log(f"🎉 Tìm thấy lời giải trong {elapsed:.2f} giây!")
                self.log("🎨 Đang vẽ lại kết quả cuối cùng...")
                # redraw with visualization
                if solution is not None:
                    self.redraw_solution(solution)
            else:
                self.status_label.configure(text="Không tìm thấy lời giải.", text_color="red")
                self.log("💔 Không tìm thấy lời giải cho bài toán.")

            # kết thúc chạy -> mở khóa controls
            self.is_solving = False
            self.stop_requested = False
            self.disable_controls(False)


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

    def reset_game1(self):
        if self.is_solving:
            self.stop_requested = True
            self.master.after(100, self._perform_reset)
        else:
            self._perform_reset()

    def redraw_solution(self, solution_grid):
        temp_speed = self.speed
        # vẽ nhanh
        self.speed = 0.01

        # remove visualization lines
        for color in self.colors:
            self.canvas.delete(f"path_{color}")
        self.canvas.delete("path_line_viz")

        # clear cells background
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.canvas.itemconfig(self.rects[(r, c)], fill="white")

        for color in self.colors:
            if self.stop_requested:
                break
            start_node, end_node = self.pairs[color]

            q = deque([[start_node]])
            path_found = []
            visited_path = {start_node}

            while q:
                if self.stop_requested:
                    break
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

# ---------- Level loading ----------
    def load_levels_list(self):
        # đọc file txt trong thư mục levels
        files = [f for f in os.listdir(self.levels_folder) if f.lower().endswith('.txt')]
        files.sort()
        if not files:
            self.level_combobox.configure(values=["(no levels)"])
            self.level_combobox.set("No levels")
        else:
            self.level_combobox.configure(values=files)
            self.level_combobox.set(files[0])

    def load_selected_level(self):
        if self.is_solving:
            self.log("⚠️ Không thể load level khi đang chạy.")
            return
        sel = self.level_combobox.get()
        if not sel or sel in ("Select level", "No levels", "(no levels)"):
            self.log("⚠️ Hãy chọn file level hợp lệ.")
            return
        path = os.path.join(self.levels_folder, sel)
        if not os.path.isfile(path):
            self.log("⚠️ File level không tồn tại.")
            self.load_levels_list()
            return
        try:
            self._parse_and_apply_level_file(path)
            self.log(f"📂 Đã load level: {sel}")
        except Exception as e:
            self.log(f"⚠️ Lỗi khi load level: {e}")

    def _parse_and_apply_level_file(self, filepath):
        """
        Định dạng file .txt mong đợi:
        grid_size=6
        red: (0,0)-(5,5)
        green: (1,1)-(4,4)
        ...
        """
        pairs = {}
        grid_size = None
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('grid_size'):
                    # grid_size=6
                    parts = line.split('=')
                    if len(parts) >= 2:
                        grid_size = int(parts[1].strip())
                else:
                    # color: (r1,c1)-(r2,c2)
                    if ':' not in line:
                        continue
                    color, rest = line.split(':', 1)
                    color = color.strip()
                    rest = rest.strip()
                    if '-' not in rest:
                        continue
                    a, b = rest.split('-', 1)
                    def parse_coord(s):
                        s = s.strip()
                        s = s.strip('()')
                        rr, cc = s.split(',')
                        return (int(rr.strip()), int(cc.strip()))
                    start = parse_coord(a)
                    end = parse_coord(b)
                    pairs[color] = [start, end]

        if grid_size is None:
            raise ValueError("File level thiếu dòng grid_size=...")

        # apply
        self.grid_size = grid_size
        self.pairs = pairs
        # recalc colors and initial grid
        self.colors = list(self.pairs.keys())
        # rebuild canvas to match new grid_size and cell_size
        self.cell_size = max(20, min(70, int(700 / self.grid_size)))
        # recreate canvas rects
        self.canvas.delete("all")
        self.rects = {}
        self.canvas.config(width=self.grid_size * self.cell_size, height=self.grid_size * self.cell_size)
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill="white", outline="#CCC", width=1.5)
                self.rects[(r, c)] = rect

        # rebuild initial grid
        self.initial_grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for color, pair in self.pairs.items():
            (r1, c1), (r2, c2) = pair
            self.initial_grid[r1][c1] = color
            self.initial_grid[r2][c2] = color

        self.mark_start_end()
        self.update_grid_display(self.initial_grid)

    def _init_grid_from_pairs(self):
        self.initial_grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for color, pair in self.pairs.items():
            (r1, c1), (r2, c2) = pair
            if 0 <= r1 < self.grid_size and 0 <= c1 < self.grid_size:
                self.initial_grid[r1][c1] = color
            if 0 <= r2 < self.grid_size and 0 <= c2 < self.grid_size:
                self.initial_grid[r2][c2] = color

    # ---------- Controls enabling/disabling ----------
    def disable_controls(self, disable: bool):
        """
        Khi disable=True -> khóa tất cả controls TRỪ nút Stop.
        Khi disable=False -> mở lại mọi control.
        """
        for widget in self.control_buttons:
            try:
                if isinstance(widget, ctk.CTkSlider):
                    widget.configure(state="disabled" if disable else "normal")
                else:
                    widget.configure(state="disabled" if disable else "normal")
            except Exception:
                pass
        # ensure stop button is always enabled so user can stop
        try:
            self.stop_button.configure(state="normal")
        except Exception:
            pass







