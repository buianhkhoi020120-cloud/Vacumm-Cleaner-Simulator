# ===================
# Link Github: https://github.com/buianhkhoi020120-cloud/Vacumm-Cleaner-Simulator
# ===================

import tkinter as tk
from tkinter import ttk

# IMPORT ALGORITHMS
from algorithms.BFS_Vaccum_1 import BFS_Vaccum_1
from algorithms.BFS_Vaccum_2 import BFS_Vaccum_2
from algorithms.DFS_Vaccum_1 import DFS_Vaccum_1
from algorithms.DFS_Vaccum_2 import DFS_Vaccum_2
from algorithms.Vacuum_cleaner_MBA import ModelBased_Wrapper
from algorithms.UCS_Vaccum import UCS_Vaccum
from algorithms.Greedy_Vaccum import Greedy_Vaccum
class VacuumApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Vacuum Cleaner AI")
        self.root.geometry("1100x650")
        self.root.configure(bg="#1e1e2e")

        # VARIABLES
        self.vaccum_logic = None
        self.path = []
        self.step_idx = 0
        self.is_running = False
        self.radio_buttons = {}  # Lưu danh sách widget Radio để đổi màu khi chọn

        # SETUP
        self.setup_style()
        self.setup_ui()

        # LOAD DEFAULT ALGORITHM
        self.load_algorithm()

        # DRAW DEFAULT MAP
        if self.vaccum_logic is not None:
            self.draw_grid(self.vaccum_logic.start)
        else:
            print("Cảnh báo: Không load được thuật toán mặc định.")

    # STYLE
    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        # Cấu hình nút RUN
        self.style.configure(
            "Run.TButton",
            font=("Segoe UI", 11, "bold"),
            background="#a6e3a1",
            foreground="#1e1e2e",
            padding=10,
            bordercolor="#1e1e2e"
        )
        self.style.map("Run.TButton", background=[('active', '#85c183'), ('pressed', '#6fa36d')])
        # Cấu hình nút RESET
        self.style.configure(
            "Reset.TButton",
            font=("Segoe UI", 11, "bold"),
            background="#f38ba8",
            foreground="#1e1e2e",
            padding=10,
            bordercolor="#1e1e2e"
        )
        self.style.map("Reset.TButton", background=[('active', '#e86b8b'), ('pressed', '#c84b6b')])
        # Cấu hình Thanh tiến trình (Progressbar) màu xanh khi chạy
        self.style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor="#181825",
            background="#a6e3a1",
            bordercolor="#11111b",
            lightcolor="#a6e3a1",
            darkcolor="#a6e3a1"
        )

    # UI
    def setup_ui(self):
        # TITLE
        title = tk.Label(
            self.root,
            text="🤖 Vacuum Cleaner AI",
            bg="#1e1e2e",
            fg="white",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=10)

        # MAIN FRAME
        main_frame = tk.Frame(
            self.root,
            bg="#1e1e2e"
        )
        main_frame.pack(
            fill="both",
            expand=True
        )

        # LEFT PANEL
        self.left_frame = tk.Frame(
            main_frame,
            bg="#313244",
            width=220
        )
        self.left_frame.pack(
            side="left",
            fill="y",
            padx=10,
            pady=10
        )
        tk.Label(
            self.left_frame,
            text="Thuật toán",
            bg="#313244",
            fg="white",
            font=("Segoe UI", 15, "bold")
        ).pack(pady=15)

        # ALGORITHM VARIABLE & TRACE
        self.algorithm_var = tk.StringVar()
        self.algorithm_var.set("Model_Based")
        # Theo dõi thay đổi của từ khóa để đổi màu chữ RadioButton tương ứng
        self.algorithm_var.trace_add("write", self.update_radio_colors)
        algorithms = [
            "DFS_1",
            "DFS_2",
            "BFS_1",
            "BFS_2",
            "UCS",
            "Greedy",
            "Model_Based"
        ]

        # RADIO BUTTONS
        for algo in algorithms:
            rb = tk.Radiobutton(
                self.left_frame,
                text=algo,
                variable=self.algorithm_var,
                value=algo,
                font=("Segoe UI", 12),
                bg="#313244",
                fg="white",
                activebackground="#313244",
                activeforeground="white",
                selectcolor="#1e1e2e"
            )
            rb.pack(
                anchor="w",
                padx=20,
                pady=5
            )
            self.radio_buttons[algo] = rb
        # Cập nhật màu chữ hiển thị ban đầu cho thuật toán mặc định
        self.update_radio_colors()

        # RUN BUTTON
        self.run_btn = ttk.Button(
            self.left_frame,
            text="▶ RUN",
            command=self.run_algorithm,
            style="Run.TButton"
        )
        self.run_btn.pack(
            pady=20,
            padx=15,
            fill="x"
        )

        # RESET BUTTON
        self.reset_btn = ttk.Button(
            self.left_frame,
            text="⟳ RESET",
            command=self.reset_app,
            style="Reset.TButton"
        )
        self.reset_btn.pack(
            pady=10,
            padx=15,
            fill="x"
        )

        # CENTER PANEL
        self.center_frame = tk.Frame(
            main_frame,
            bg="#1e1e2e"
        )
        self.center_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        # GRID CANVAS
        self.canvas = tk.Canvas(
            self.center_frame,
            width=500,
            height=500,
            bg="#181825",
            highlightthickness=0
        )
        self.canvas.pack(pady=20)

        # STATUS LABEL
        self.status_label = tk.Label(
            self.center_frame,
            text="Trạng thái: Sẵn sàng",
            bg="#1e1e2e",
            fg="#a6e3a1",
            font=("Segoe UI", 12, "bold")
        )

        self.status_label.pack()

        # PROGRESS BAR
        self.progress = ttk.Progressbar(
            self.center_frame,
            length=400,
            mode="determinate",
            style="Green.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=15)

        # SOLUTION FRAME
        solution_frame = tk.Frame(
            self.center_frame,
            bg="#1e1e2e"
        )
        solution_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )
        tk.Label(
            solution_frame,
            text="Solution Path",
            bg="#1e1e2e",
            fg="white",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        # CONTAINER
        solution_container = tk.Frame(
            solution_frame,
            bg="#313244",
            height=60
        )
        solution_container.pack(
            fill="x",
            pady=5
        )

        # SCROLLBAR
        self.solution_scroll = tk.Scrollbar(
            solution_container,
            orient="horizontal"
        )

        self.solution_scroll.pack(
            side="bottom",
            fill="x"
        )

        # SOLUTION CANVAS
        self.solution_canvas = tk.Canvas(
            solution_container,
            bg="#181825",
            height=50,
            width=500,
            highlightthickness=0,
            xscrollcommand=self.solution_scroll.set
        )
        self.solution_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )
        self.solution_scroll.config(
            command=self.solution_canvas.xview
        )

        # TEXT
        self.solution_text = self.solution_canvas.create_text(
            10,
            22,
            anchor="w",
            text="Chưa có",
            fill="#89b4fa",
            font=("Consolas", 11, "bold")
        )

        # RIGHT PANEL
        self.right_frame = tk.Frame(
            main_frame,
            bg="#313244",
            width=250
        )
        self.right_frame.pack(
            side="right",
            fill="y",
            padx=10,
            pady=10
        )
        tk.Label(
            self.right_frame,
            text="Log",
            bg="#313244",
            fg="white",
            font=("Segoe UI", 15, "bold")
        ).pack(pady=10)

        # LOG TEXT
        self.log_text = tk.Text(
            self.right_frame,
            bg="#181825",
            fg="white",
            font=("Consolas", 10)
        )
        self.log_text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # TỰ ĐỘNG ĐỔI MÀU TEXT THUẬT TOÁN ĐƯỢC CHỌN=
    def update_radio_colors(self, *args):
        selected = self.algorithm_var.get()
        for algo, rb in self.radio_buttons.items():
            if algo == selected:
                rb.config(fg="#a6e3a1", font=("Segoe UI", 12, "bold"))
            else:
                rb.config(fg="white", font=("Segoe UI", 12, "normal"))

    # LOAD ALGORITHM
    def load_algorithm(self):
        selected = self.algorithm_var.get()
        algorithms = {
            "DFS_1": DFS_Vaccum_1,
            "DFS_2": DFS_Vaccum_2,
            "BFS_1": BFS_Vaccum_1,
            "BFS_2": BFS_Vaccum_2,
            "UCS": UCS_Vaccum,
            "Greedy": Greedy_Vaccum,
            "Model_Based": ModelBased_Wrapper
        }
        self.vaccum_logic = None 
        if selected not in algorithms:
            # Thông báo cho người dùng biết thuật toán này chưa được cài đặt
            self.log(f"❌ Lỗi: Thuật toán {selected} chưa được tích hợp!")
            self.status_label.config(text=f"Chưa có code cho {selected}")
            return
        self.vaccum_logic = algorithms[selected]()

    # DRAW GRID
    def draw_grid(self, matrix):
        self.canvas.delete("all")
        rows = len(matrix)
        cols = len(matrix[0])
        cell_size = 500 // cols
        for i in range(rows):
            for j in range(cols):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                value = matrix[i][j]
                color = "#cdd6f4"
                if value == 1:
                    color = "#f9e2af"
                elif value == 2:
                    color = "#f38ba8"
                elif value == 3:
                    color = "#45475a"
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="#11111b",
                    width=3
                )
                if value == 1:
                    self.canvas.create_text(
                        x1 + cell_size // 2,
                        y1 + cell_size // 2,
                        text="🟤",
                        font=("Arial", 28)
                    )
                elif value == 2:
                    self.canvas.create_text(
                        x1 + cell_size // 2,
                        y1 + cell_size // 2,
                        text="🤖",
                        font=("Arial", 28)
                    )
                elif value == 3:
                    self.canvas.create_text(
                        x1 + cell_size // 2,
                        y1 + cell_size // 2,
                        text="🧱",
                        font=("Arial", 28)
                    )

    # LOG
    def log(self, message):

        self.log_text.insert(
            tk.END,
            message + "\n"
        )
        self.log_text.see(tk.END)

    # RUN
    def run_algorithm(self):
        if self.is_running:
            return
        self.load_algorithm()
        if self.vaccum_logic is None:
            return
        self.log(f"Running {self.algorithm_var.get()}...")
        self.status_label.config(
            text=f"Đang chạy {self.algorithm_var.get()}"
        )
        node = self.vaccum_logic.solve()
        if node is None:
            self.log("Không tìm thấy lời giải")
            self.status_label.config(
                text="Không tìm thấy lời giải"
            )
            return
        self.path = self.vaccum_logic.get_path(node)
        self.draw_grid(self.path[0][0])
        self.solution_canvas.itemconfig(
            self.solution_text,
            text="Đang chạy... Vui lòng đợi kết quả"
        )
        self.solution_canvas.config(scrollregion=(0, 0, 0, 0))
        self.progress["maximum"] = len(self.path)
        self.progress["value"] = 0
        self.step_idx = 0
        self.is_running = True
        self.animate_step()

    # ANIMATION
    def animate_step(self):
        if self.step_idx < len(self.path):
            matrix, action = self.path[self.step_idx]
            self.draw_grid(matrix)
            self.log(f"Step {self.step_idx}: {action}")
            self.progress["value"] = self.step_idx + 1
            self.step_idx += 1
            self.root.after(
                500,
                self.animate_step
            )
        else:
            actions = [step[1] for step in self.path if step[1] != "START"]
            total_steps = len(actions)
            self.status_label.config(
                text=f"✔ Hoàn thành ({total_steps} bước)"
            )
            self.log("DONE")
            solution = "  ➜  ".join(actions)
            self.solution_canvas.itemconfig(
                self.solution_text,
                text=solution
            )
            self.solution_canvas.update_idletasks()
            bbox = self.solution_canvas.bbox(self.solution_text)
            if bbox:
                self.solution_canvas.config(
                    scrollregion=bbox
                )
            self.is_running = False

    # RESET
    def reset_app(self):
        self.is_running = False
        self.path = []
        self.step_idx = 0
        self.log_text.delete("1.0", tk.END)
        self.solution_canvas.itemconfig(
            self.solution_text,
            text="Chưa có"
        )
        self.solution_canvas.config(
            scrollregion=(0, 0, 0, 0)
        )
        self.progress["value"] = 0
        self.status_label.config(
            text="Trạng thái: Sẵn sàng"
        )
        self.load_algorithm()
        if self.vaccum_logic:
            self.draw_grid(self.vaccum_logic.start)

# MAIN
if __name__ == "__main__":

    root = tk.Tk()
    app = VacuumApp(root)
    root.mainloop()