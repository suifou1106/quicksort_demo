import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import time
import random
import sys
import os
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Danh sách TẤT CẢ các hàm sắp xếp từ C++
ALL_ALGORITHMS = [
    "qs_first", "qs_last", "qs_middle", "qs_random", "qs_random_lomuto",
    "qs_median_of_3", "qs_median_of_medians", "qs_dual_pivot", "qs_pdqsort"
]

class SortBenchmarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quicksort Complexity Benchmark - Pro Version")
        self.root.geometry("1000x900")
        
        self.algo_vars = {}
        self.stop_requested = False 
        self.lib = None
        
        self.last_sizes = []
        self.last_results = {}
        self.last_title = ""
        
        self.load_c_library()
        self.setup_ui()

    def load_c_library(self):
        lib_name = "sort_engine.dll" if sys.platform == "win32" else "./sort_engine.so"
        try:
            self.lib = ctypes.CDLL(os.path.abspath(lib_name))
            for func_name in ALL_ALGORITHMS:
                if hasattr(self.lib, func_name):
                    func = getattr(self.lib, func_name)
                    func.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
                    func.restype = None
        except Exception as e:
            messagebox.showerror("Lỗi Load Thư Viện", f"Không tìm thấy hoặc lỗi nạp thư viện: {lib_name}\nChi tiết: {e}")

    def setup_ui(self):
        # --- 1. PANEL ĐIỀU KHIỂN THÔNG SỐ ---
        control_frame = ttk.LabelFrame(self.root, text="1. Cài đặt thông số (Đo độ phức tạp)")
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(control_frame, text="N Tối đa:").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.StringVar(value="5000")
        ttk.Entry(control_frame, textvariable=self.size_var, width=8).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Bước nhảy:").pack(side=tk.LEFT, padx=5)
        self.step_var = tk.StringVar(value="1000")
        ttk.Entry(control_frame, textvariable=self.step_var, width=8).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Loại mảng:").pack(side=tk.LEFT, padx=5)
        self.scenario_var = tk.StringVar()
        self.scenario_cb = ttk.Combobox(control_frame, textvariable=self.scenario_var, state="readonly", width=15)
        self.scenario_cb['values'] = ("Ngẫu nhiên", "Đã sắp xếp", "Sắp xếp ngược", "Toàn trùng lặp")
        self.scenario_cb.current(0)
        self.scenario_cb.pack(side=tk.LEFT, padx=5)

        # --- 2. PANEL CHỌN THUẬT TOÁN ---
        algo_frame = ttk.LabelFrame(self.root, text="2. Chọn thuật toán cần đánh giá")
        algo_frame.pack(fill=tk.X, padx=10, pady=5)

        for i, algo in enumerate(ALL_ALGORITHMS):
            var = tk.BooleanVar(value=(algo != "qs_random_lomuto")) 
            self.algo_vars[algo] = var
            cb = ttk.Checkbutton(algo_frame, text=algo, variable=var)
            cb.grid(row=i // 4, column=i % 4, sticky=tk.W, padx=15, pady=2)
            
        ttk.Button(algo_frame, text="Chọn tất cả", command=lambda: self.set_all_checkboxes(True)).grid(row=3, column=0, pady=5, padx=15, sticky=tk.W)
        ttk.Button(algo_frame, text="Bỏ chọn tất cả", command=lambda: self.set_all_checkboxes(False)).grid(row=3, column=1, pady=5, padx=15, sticky=tk.W)

        # --- 3. PANEL TÙY CHỌN HIỂN THỊ ---
        display_frame = ttk.LabelFrame(self.root, text="3. Tùy chọn hiển thị biểu đồ")
        display_frame.pack(fill=tk.X, padx=10, pady=5)

        self.show_nlogn_var = tk.BooleanVar(value=True)
        cb_nlogn = ttk.Checkbutton(display_frame, text="Hiển thị lý thuyết O(n log n)", variable=self.show_nlogn_var, command=self.redraw_plot)
        cb_nlogn.pack(side=tk.LEFT, padx=15, pady=5)

        self.show_n2_var = tk.BooleanVar(value=True)
        cb_n2 = ttk.Checkbutton(display_frame, text="Hiển thị lý thuyết O(n²)", variable=self.show_n2_var, command=self.redraw_plot)
        cb_n2.pack(side=tk.LEFT, padx=15, pady=5)

        # --- 4. PANEL CHẠY VÀ VẼ BIỂU ĐỒ ---
        main_frame = ttk.LabelFrame(self.root, text="4. Chạy và vẽ biểu đồ")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=5)

        self.run_btn = ttk.Button(btn_frame, text="▶ BẮT ĐẦU CHẠY ĐÁNH GIÁ", command=self.run_benchmark)
        self.run_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = ttk.Button(btn_frame, text="⏹ DỪNG CHẠY", command=self.stop_benchmark, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.result_text = tk.Text(main_frame, height=4, state=tk.DISABLED)
        self.result_text.pack(fill=tk.X, padx=5, pady=5)

        # --- KHU VỰC VẼ BIỂU ĐỒ & THANH CÔNG CỤ TÍCH HỢP ---
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Khởi tạo Canvas (Nhưng CHƯA gọi lệnh pack vội)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        
        # 2. Khởi tạo Toolbar và để nó tự động bám vào đáy (Bottom) của graph_frame
        self.toolbar = NavigationToolbar2Tk(self.canvas, graph_frame)
        self.toolbar.update()
        
        # 3. BÂY GIỜ mới gọi lệnh pack cho Canvas nằm ở TRÊN (Top) thanh công cụ
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # --------------------------------------------------

    def set_all_checkboxes(self, state):
        for var in self.algo_vars.values():
            var.set(state)

    def generate_array(self, n, scenario):
        if scenario == "Ngẫu nhiên": return [random.randint(0, n) for _ in range(n)]
        elif scenario == "Đã sắp xếp": return list(range(n))
        elif scenario == "Sắp xếp ngược": return list(range(n, 0, -1))
        elif scenario == "Toàn trùng lặp": return [42] * n

    def update_text(self, text_widget, content):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        text_widget.yview(tk.END)
        self.root.update()

    def get_test_sizes(self):
        try:
            max_n = int(self.size_var.get())
            step = int(self.step_var.get())
            if max_n <= 0 or step <= 0: raise ValueError
            sizes = list(range(step, max_n + 1, step))
            if sizes[-1] != max_n: sizes.append(max_n)
            return sizes
        except ValueError:
            messagebox.showerror("Lỗi", "N và Bước nhảy phải là số nguyên dương hợp lệ.")
            return None

    def stop_benchmark(self):
        self.stop_requested = True
        self.stop_btn.config(state=tk.DISABLED)
        self.update_text(self.result_text, self.result_text.get("1.0", tk.END) + "=> Đang yêu cầu dừng...\n")

    def run_algorithm_direct(self, func_name, data):
        if not self.lib or not hasattr(self.lib, func_name): return -3
        func = getattr(self.lib, func_name)
        c_arr = (ctypes.c_int * len(data))(*data)
        
        start_time = time.perf_counter()
        func(c_arr, 0, len(data) - 1)
        end_time = time.perf_counter()
        return end_time - start_time

    def run_benchmark(self):
        if not self.lib:
            messagebox.showerror("Lỗi", "Thư viện C++ chưa được nạp!")
            return

        selected_algos = [algo for algo, var in self.algo_vars.items() if var.get()]
        if not selected_algos:
            messagebox.showwarning("Cảnh báo", "Vui lòng tick chọn ít nhất một thuật toán!")
            return

        sizes = self.get_test_sizes()
        if not sizes: return
        scenario = self.scenario_var.get()

        self.stop_requested = False
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        results_dict = {func: [] for func in selected_algos}
        self.update_text(self.result_text, f"Bắt đầu đo tốc độ {len(selected_algos)} thuật toán (Kịch bản: {scenario})...\n")

        for size in sizes:
            if self.stop_requested: break 
            self.update_text(self.result_text, self.result_text.get("1.0", tk.END) + f"Đang test N = {size}...\n")
            arr = self.generate_array(size, scenario)
            
            for func in selected_algos:
                if self.stop_requested: break 
                time_taken = self.run_algorithm_direct(func, arr.copy())
                results_dict[func].append(time_taken)
                self.root.update()

        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        if self.stop_requested:
            self.update_text(self.result_text, self.result_text.get("1.0", tk.END) + "=> ĐÃ DỪNG KIỂM THỬ!\n")
        else:
            self.update_text(self.result_text, self.result_text.get("1.0", tk.END) + "Hoàn thành toàn bộ!\n")
            
        self.last_sizes = sizes
        self.last_results = results_dict
        self.last_title = "Độ phức tạp các thuật toán (Giây)"
        
        self.redraw_plot()

    def redraw_plot(self):
        if not self.last_sizes:
            return 
            
        self.ax.clear()
        
        anchor_n = self.last_sizes[0]
        anchor_times = []
        max_actual_time = 0
        
        for times in self.last_results.values():
            valid_times = [t for t in times if t is not None]
            if valid_times:
                max_actual_time = max(max_actual_time, max(valid_times))
            if times and times[0] is not None:
                anchor_times.append(times[0])
                
        anchor_time = sum(anchor_times) / len(anchor_times) if anchor_times else 0.0001
        if max_actual_time == 0: max_actual_time = 0.001 

        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*']
        for i, (label, times) in enumerate(self.last_results.items()):
            current_sizes = self.last_sizes[:len(times)] 
            clean_label = label.replace('qs_', '')
            marker = markers[i % len(markers)]
            
            if current_sizes:
                self.ax.plot(current_sizes, times, marker=marker, linewidth=2, label=f"Thực tế: {clean_label}")

        if anchor_time > 0:
            smooth_n = [i for i in range(max(1, anchor_n), self.last_sizes[-1] + 1, max(1, self.last_sizes[-1] // 100))]
            
            if self.show_nlogn_var.get():
                c_nlogn = anchor_time / (anchor_n * math.log2(anchor_n) if anchor_n > 1 else 1)
                y_nlogn = [c_nlogn * (n * math.log2(n) if n > 1 else 1) for n in smooth_n]
                self.ax.plot(smooth_n, y_nlogn, color='green', linestyle='--', alpha=0.6, linewidth=2, label='Lý thuyết: O(n log n)')
                
            if self.show_n2_var.get():
                c_n2 = anchor_time / (anchor_n ** 2)
                y_n2 = [c_n2 * (n ** 2) for n in smooth_n]
                self.ax.plot(smooth_n, y_n2, color='red', linestyle='--', alpha=0.6, linewidth=2, label='Lý thuyết: O(n²)')

        self.ax.set_ylim(bottom=0, top=max_actual_time * 1.1)
        self.ax.set_xlabel("Số lượng phần tử (N)", fontweight='bold')
        self.ax.set_ylabel("Thời gian chạy (Giây)", fontweight='bold')
        self.ax.set_title(self.last_title, fontsize=12, fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        if self.last_results:
            self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = SortBenchmarkApp(root)
    root.mainloop()