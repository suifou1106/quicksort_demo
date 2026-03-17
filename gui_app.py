import tkinter as tk
from tkinter import messagebox
import random
import time
import ctypes
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Nạp thư viện C++
lib_name = 'sort_engine.dll' if sys.platform == 'win32' else './sort_engine.so'
try:
    cpp_lib = ctypes.CDLL(os.path.abspath(lib_name))
except OSError:
    print("CẢNH BÁO: Không tìm thấy thư viện C++! Hãy chắc chắn bạn đã biên dịch sort_engine.cpp")
    sys.exit(1)

# Wrapper để gọi hàm C++
def call_cpp_sort(func_name, arr):
    n = len(arr)
    arr_c = (ctypes.c_int * n)(*arr)
    func = getattr(cpp_lib, func_name)
    func(arr_c, 0, n - 1)
    # Không cần trả về mảng vì ta chỉ cần đo thời gian

class CppSortingBenchmarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("C++ Quicksort Engine: O(N^2) Stress Test")
        self.root.geometry("1000x650")
        
        # --- Khung Điều khiển ---
        frame_control = tk.Frame(root, width=300)
        frame_control.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(frame_control, text="Kích thước mảng tối đa (N):", font=("Arial", 10, "bold")).pack(pady=5)
        self.entry_n = tk.Entry(frame_control, font=("Arial", 12))
        self.entry_n.insert(0, "4000") # Giữ N = 4000 để C++ không bị tràn Stack (Segfault) khi dính O(N^2)
        self.entry_n.pack(pady=5)
        
        tk.Label(frame_control, text="Mô hình Dữ liệu (Stress Test):", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        self.data_type = tk.StringVar(value="Ngẫu nhiên")
        tk.Radiobutton(frame_control, text="Ngẫu nhiên (Random)", variable=self.data_type, value="Ngẫu nhiên").pack(anchor="w")
        tk.Radiobutton(frame_control, text="Sắp xếp tăng (O(N^2) Threat)", variable=self.data_type, value="Sắp xếp tăng").pack(anchor="w")
        tk.Radiobutton(frame_control, text="Sắp xếp giảm (O(N^2) Threat)", variable=self.data_type, value="Sắp xếp giảm").pack(anchor="w")
        tk.Radiobutton(frame_control, text="Tất cả Trùng lặp (Worst Case)", variable=self.data_type, value="Trùng lặp").pack(anchor="w")

        self.btn_run = tk.Button(frame_control, text="Chạy C++ Engine", command=self.run_benchmark, bg="#ffcccb", font=("Arial", 10, "bold"))
        self.btn_run.pack(pady=20)
        self.lbl_status = tk.Label(frame_control, text="Sẵn sàng kiểm thử C++.", fg="blue")
        self.lbl_status.pack(pady=5)

        self.algorithms = {
            "Pivot Đầu": "qs_first",
            "Pivot Cuối": "qs_last",
            "Pivot Giữa": "qs_middle",
            "Pivot Ngẫu nhiên": "qs_random",
            "pdqsort (Orson Peters)": "qs_pdqsort"
        }

        # --- Khung Đồ thị ---
        frame_chart = tk.Frame(root)
        frame_chart.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.fig, self.ax = plt.subplots(figsize=(7, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_chart)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.setup_chart()

    def setup_chart(self):
        self.ax.clear()
        self.ax.set_title(f"Hiệu năng C++: Dữ liệu {self.data_type.get()}", fontsize=13)
        self.ax.set_xlabel("Số lượng phần tử (N)", fontsize=10)
        self.ax.set_ylabel("Thời gian chạy (mili-giây)", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.7)

    def run_benchmark(self):
        try:
            max_n = int(self.entry_n.get())
            # Giới hạn an toàn: C++ sẽ bị lỗi Segmentation Fault nếu đệ quy quá sâu
            if max_n > 8000 and self.data_type.get() != "Ngẫu nhiên":
                messagebox.showwarning("Nguy hiểm", "Trong C++, O(N^2) sẽ gây tràn bộ nhớ ngăn xếp (Stack Overflow) làm crash chương trình. Hãy giữ N <= 5000 cho các test mảng đã sắp xếp.")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Nhập số nguyên!")
            return

        self.lbl_status.config(text="C++ đang xử lý...", fg="red")
        self.root.update()

        step = max_n // 5
        sizes = [step * i for i in range(1, 6)]
        self.setup_chart()
        markers = ['o', 's', '^', 'D', '*']
        
        for (name, func_name), marker in zip(self.algorithms.items(), markers):
            times = []
            for n in sizes:
                dtype = self.data_type.get()
                if dtype == "Ngẫu nhiên":
                    test_arr = [random.randint(0, max_n) for _ in range(n)]
                elif dtype == "Sắp xếp tăng":
                    test_arr = list(range(n))
                elif dtype == "Sắp xếp giảm":
                    test_arr = list(range(n, 0, -1))
                elif dtype == "Trùng lặp":
                    test_arr = [42] * n 
                
                # Bắt đầu tính thời gian
                start_time = time.perf_counter()
                try:
                    call_cpp_sort(func_name, test_arr)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                except Exception as e:
                    elapsed_ms = float('inf') # Đánh dấu lỗi nếu có
                
                times.append(elapsed_ms)
            
            self.ax.plot(sizes, times, marker=marker, linewidth=2, label=name)

        self.ax.legend(loc='upper left')
        self.fig.tight_layout()
        self.canvas.draw()
        self.lbl_status.config(text="Hoàn thành!\nHãy xem đường cong parabol.", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = CppSortingBenchmarkApp(root)
    root.mainloop()