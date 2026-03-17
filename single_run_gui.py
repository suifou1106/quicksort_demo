import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import ctypes
import sys
import os
import copy

# ==========================================
# 1. NẠP THƯ VIỆN C++
# ==========================================
lib_name = 'sort_engine.dll' if sys.platform == 'win32' else './sort_engine.so'
try:
    cpp_lib = ctypes.CDLL(os.path.abspath(lib_name))
except OSError:
    print("CẢNH BÁO: Không tìm thấy thư viện C++! Hãy chắc chắn bạn đã biên dịch sort_engine.cpp")
    sys.exit(1)

def call_cpp_sort(func_name, arr):
    n = len(arr)
    arr_c = (ctypes.c_int * n)(*arr)
    func = getattr(cpp_lib, func_name)
    func(arr_c, 0, n - 1)

# ==========================================
# 2. GIAO DIỆN CHẠY ĐƠN LẺ
# ==========================================
class SingleRunSortingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quicksort Single Run Test Bench")
        self.root.geometry("600x650")
        
        self.original_array = [] # Nơi lưu trữ mảng gốc sau khi sinh
        
        # --- KHU VỰC 1: SINH DỮ LIỆU ---
        frame_data = tk.LabelFrame(root, text="1. Sinh Dữ Liệu Đầu Vào", font=("Arial", 11, "bold"), padx=10, pady=10)
        frame_data.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(frame_data, text="Nhập số lượng phần tử (N):").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_n = tk.Entry(frame_data, font=("Arial", 11), width=15)
        self.entry_n.insert(0, "1000000") # Mặc định 1 triệu phần tử để thấy rõ sức mạnh C++
        self.entry_n.grid(row=0, column=1, sticky="w", pady=5)
        
        tk.Label(frame_data, text="Loại dữ liệu:").grid(row=1, column=0, sticky="w", pady=5)
        self.data_type = tk.StringVar(value="Ngẫu nhiên")
        types = ["Ngẫu nhiên", "Sắp xếp tăng", "Sắp xếp giảm", "Trùng lặp"]
        self.combo_type = ttk.Combobox(frame_data, textvariable=self.data_type, values=types, state="readonly", width=17)
        self.combo_type.grid(row=1, column=1, sticky="w", pady=5)
        
        self.btn_generate = tk.Button(frame_data, text="Sinh Mảng Ngay", command=self.generate_data, bg="#d9ead3", font=("Arial", 10, "bold"))
        self.btn_generate.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.lbl_data_status = tk.Label(frame_data, text="Chưa có dữ liệu.", fg="gray")
        self.lbl_data_status.grid(row=3, column=0, columnspan=2, sticky="w")

        # --- KHU VỰC 2: CHỌN VÀ CHẠY THUẬT TOÁN ---
        frame_algo = tk.LabelFrame(root, text="2. Chạy Thuật Toán C++", font=("Arial", 11, "bold"), padx=10, pady=10)
        frame_algo.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.algorithms = {
            "1. Pivot Đầu": "qs_first",
            "2. Pivot Cuối": "qs_last",
            "3. Pivot Giữa": "qs_middle",
            "4. Pivot Ngẫu nhiên": "qs_random",
            "5. Trung vị của 3": "qs_median_of_3",
            "6. Trung vị của Trung vị": "qs_median_of_medians",
            "7. Dual-Pivot": "qs_dual_pivot",
            "8. pdqsort (Orson Peters)": "qs_pdqsort"
        }

        self.algo_var = tk.StringVar(value="8. pdqsort (Orson Peters)")
        
        # Tạo Radio buttons cho 8 thuật toán
        for text in self.algorithms.keys():
            tk.Radiobutton(frame_algo, text=text, variable=self.algo_var, value=text, font=("Arial", 10)).pack(anchor="w", pady=2)

        self.btn_run = tk.Button(frame_algo, text="▶ Chạy Thuật Toán", command=self.run_algorithm, bg="#ffcccb", font=("Arial", 11, "bold"))
        self.btn_run.pack(pady=15)

        # --- KHU VỰC 3: KẾT QUẢ ---
        frame_result = tk.Frame(root)
        frame_result.pack(fill=tk.X, padx=15, pady=10)
        
        self.lbl_result = tk.Label(frame_result, text="Kết quả sẽ hiển thị ở đây", font=("Arial", 14, "bold"), fg="blue")
        self.lbl_result.pack()

    def generate_data(self):
        try:
            n = int(self.entry_n.get())
            if n <= 0: raise ValueError
            
            # Cảnh báo an toàn cho Stack Overflow của C++
            dtype = self.data_type.get()
            if n > 6000 and dtype != "Ngẫu nhiên":
                response = messagebox.askyesno("Cảnh báo Nguy hiểm", 
                    f"Bạn đang tạo {n} phần tử cho mảng '{dtype}'.\n"
                    "Nếu chạy các thuật toán Pivot Đầu/Cuối, C++ sẽ bị tràn bộ nhớ (Crash) do độ phức tạp O(N^2).\n"
                    "Bạn có chắc chắn muốn tiếp tục tạo mảng không?")
                if not response: return

        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập một số nguyên dương hợp lệ!")
            return

        self.lbl_data_status.config(text="Đang sinh dữ liệu...", fg="orange")
        self.root.update()

        # Logic sinh mảng
        if dtype == "Ngẫu nhiên":
            self.original_array = [random.randint(0, n) for _ in range(n)]
        elif dtype == "Sắp xếp tăng":
            self.original_array = list(range(n))
        elif dtype == "Sắp xếp giảm":
            self.original_array = list(range(n, 0, -1))
        elif dtype == "Trùng lặp":
            self.original_array = [42] * n 

        self.lbl_data_status.config(text=f"Đã lưu mảng {n} phần tử ({dtype}) vào bộ nhớ ảo.", fg="green")
        self.lbl_result.config(text="Sẵn sàng chạy thử", fg="blue")

    def run_algorithm(self):
        if not self.original_array:
            messagebox.showwarning("Cảnh báo", "Vui lòng bấm 'Sinh Mảng Ngay' trước khi chạy thuật toán!")
            return

        selected_algo = self.algo_var.get()
        func_name = self.algorithms[selected_algo]
        
        self.lbl_result.config(text=f"Đang chạy {selected_algo}...", fg="orange")
        self.root.update()

        # Copy mảng gốc để mảng không bị thay đổi cho các lần test sau
        arr_copy = copy.deepcopy(self.original_array)

        try:
            start_time = time.perf_counter()
            call_cpp_sort(func_name, arr_copy)
            end_time = time.perf_counter()
            
            elapsed_ms = (end_time - start_time) * 1000
            self.lbl_result.config(text=f"⏱ Thời gian: {elapsed_ms:.2f} ms", fg="green")
        except Exception as e:
            self.lbl_result.config(text=f"Lỗi hệ thống hoặc Tràn ngăn xếp!", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = SingleRunSortingApp(root)
    root.mainloop()