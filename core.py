import tkinter as tk
import random

# ===== MÀU & MẪU NGHIỆM =====
MAU_DAM  = "#FF8C00"
MAU_NHAT = "#F3E5C6"
MAU_NEN  = "#FFFFFF"

NGHIEM_MAU = [
    (0, 4), (1, 2), (2, 7), (3, 3),
    (4, 6), (5, 0), (6, 5), (7, 1)
]

# ===== “Ngữ cảnh” UI (sẽ được gán trong app.py) =====
root = None
left_board = None
right_board = None
log_box1 = None
log_box2 = None

# Trạng thái điều khiển/hoạt ảnh
pending_after_ids = []
is_running = False
thuTuDuyet = []          # dùng bởi mọi thuật toán
algo_buttons = []
control_buttons = []

# ===== Logging tiện dụng =====
def log_trai(msg: str):
    if log_box1 is not None:
        log_box1.insert(tk.END, msg + "\n")
        log_box1.see(tk.END)

def log_phai(msg: str):
    if log_box2 is not None:
        log_box2.insert(tk.END, msg + "\n")
        log_box2.see(tk.END)

def xoa_logs():
    if log_box1: log_box1.delete("1.0", tk.END)
    if log_box2: log_box2.delete("1.0", tk.END)

# ===== Hoạt ảnh / khoá nút =====
def hen_sau(ms, fn):
    aid = root.after(ms, fn)
    pending_after_ids.append(aid)

def huy_toan_bo_after():
    global pending_after_ids
    for aid in pending_after_ids:
        try:
            root.after_cancel(aid)
        except:
            pass
    pending_after_ids = []

def dat_trang_thai_chay(flag: bool):
    global is_running
    is_running = flag
    state = (tk.DISABLED if flag else tk.NORMAL)
    for b in algo_buttons:
        b.config(state=state)
    for b in control_buttons:
        if b.cget("text") == "Reset Bàn Cờ":
            b.config(state=tk.NORMAL)
        else:
            b.config(state=state)

def dung_va_mo_khoa():
    huy_toan_bo_after()
    dat_trang_thai_chay(False)

def phat_duong_di(path, delay_ms=300):
    if not path:
        log_trai("Không có đường đi để phát.")
        dat_trang_thai_chay(False)
        return
    for i, st in enumerate(path):
        log_trai(f"Bước {i}: {st}")
        hen_sau(delay_ms * i, lambda s=st: left_board.set_state(s))
    hen_sau(delay_ms * len(path) + 10, lambda: dat_trang_thai_chay(False))

# ===== Tiện ích sinh nghiệm / kiểm tra / không gian trạng thái =====
def sinh_nghiem_hop_le(n=8):
    while True:
        cols = list(range(n))
        random.shuffle(cols)
        ok = True
        for i in range(n):
            for j in range(i+1, n):
                if abs(i-j) == abs(cols[i]-cols[j]):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return [(i, cols[i]) for i in range(n)]

def lay_muc_tieu():
    state = right_board.solution if right_board and right_board.solution else []
    if len(state) != 8:
        log_trai("⚠️ Hãy bấm 'Sinh Trạng Thái Mục Tiêu' để tạo đủ 8 hậu ở bàn phải.")
        return None
    return tuple(state)

def o_hop_le(trangThai, row_next, col_next):
    for r, c in trangThai:
        if c == col_next: return False
        if abs(c - col_next) == abs(r - row_next): return False
    return True

def sinh_trang_thai_con(trangThai):
    row_next = len(trangThai)
    if row_next >= 8: return []
    res = []
    for col in range(8):
        if o_hop_le(trangThai, row_next, col):
            res.append(trangThai + ((row_next, col),))
    return res
