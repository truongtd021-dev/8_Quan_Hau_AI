import tkinter as tk
from tkinter import scrolledtext

# UI & Core
from ui import ChessBoard, resize_boards
import core

# Thuật toán
from algorithms_state import BFS, DFS, DLS, IDS, sinh_UCS, sinh_Greedy, sinh_AStar, lua_chon_tot_nhat
from algorithms_csp_local import (
    hill_climbing, simulated_annealing, beam_search, genetic, ANDOR,
    backtrack_core
)

# ===== Handlers cấp cao =====
def on_reset():
    core.dung_va_mo_khoa()
    core.left_board.clear()
    core.right_board.clear()
    core.xoa_logs()
    core.log_trai("Đã Reset.")

def on_generate_goal():
    core.dung_va_mo_khoa()
    goal = core.sinh_nghiem_hop_le(8)
    core.right_board.set_state(goal)
    core.log_trai("Đã sinh trạng thái mục tiêu (bàn phải).")

def on_show_detail():
    if not core.thuTuDuyet:
        core.log_phai("Chưa có dữ liệu duyệt. Hãy chạy thuật toán trước.")
        return
    core.log_phai("—— Xem Đường Đi Chi Tiết ——")
    for i, s in enumerate(core.thuTuDuyet):
        core.log_phai(f"State {i}: {s}")

def chuan_bi_chay():
    core.dung_va_mo_khoa()
    core.left_board.clear()
    core.xoa_logs()
    core.dat_trang_thai_chay(True)

def chay_va_phat(nhan, ham_tinh):
    found, path = ham_tinh()
    core.log_trai(f"{nhan} — Số trạng thái đã duyệt: {len(core.thuTuDuyet)}")
    if found is not None and path:
        nhanh = 200 if nhan.startswith(("Backtracking", "Forward")) else 300
        core.phat_duong_di(path, delay_ms=nhanh)
    else:
        core.log_trai(f"{nhan}: Không tìm thấy.")
        core.dat_trang_thai_chay(False)

# ===== Run-* (gọi thuật toán) =====
def run_BFS():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    start = tuple()
    chay_va_phat("BFS", lambda: BFS(start, goal))

def run_DFS():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    start = tuple()
    chay_va_phat("DFS", lambda: DFS(start, goal))

def run_DLS():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    start = tuple()
    chay_va_phat("DLS", lambda: DLS(start, goal, 8))

def run_IDS():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    startp=(tuple(), 0); goalp=(goal, None)
    chay_va_phat("IDS", lambda: IDS(startp, goalp))

def run_UCS():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    chay_va_phat("UCS", lambda: lua_chon_tot_nhat(tuple(), goal, sinh_UCS, "UCS"))

def run_Greedy():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    chay_va_phat("Greedy", lambda: lua_chon_tot_nhat(tuple(), goal, sinh_Greedy, "Greedy"))

def run_AStar():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    chay_va_phat("A*", lambda: lua_chon_tot_nhat(tuple(), goal, sinh_AStar, "A*"))

def run_HC():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    cols=[c for _,c in sorted(goal)]
    vec, buoc, ok, trace = hill_climbing(tuple(cols))
    core.log_trai(f"Hill Climbing — {'tìm được' if ok else 'kẹt cực tiểu'} sau {buoc} lần cải thiện.")
    core.log_phai("—— Hill Climbing: diễn tiến ——")
    for i, v in enumerate(trace):
        core.log_phai(f"State {i}: {[(r, v[r]) for r in range(8)]}")
    core.left_board.set_state([(r, vec[r]) for r in range(8)])
    core.dat_trang_thai_chay(False)

def run_SA():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    cols=[c for _,c in sorted(goal)]
    vec, thu, ok, acc = simulated_annealing(tuple(cols))
    core.log_trai(f"Simulated Annealing — {'tìm được' if ok else 'không đạt'} sau {thu} lần thử.")
    core.log_phai("—— Simulated Annealing: các bước ACCEPT ——")
    for i, v in enumerate(acc):
        core.log_phai(f"State {i}: {[(r, v[r]) for r in range(8)]}")
    core.left_board.set_state([(r, vec[r]) for r in range(8)])
    core.dat_trang_thai_chay(False)

def run_Beam():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    cols=[c for _,c in sorted(goal)]
    vec, it, ok, bests = beam_search(tuple(cols))
    core.log_trai(f"Beam — {'tìm được' if ok else 'không đạt'} sau {it} vòng lặp.")
    core.log_phai("—— Beam Search: best mỗi vòng ——")
    for i, v in enumerate(bests):
        core.log_phai(f"State {i}: {[(r, v[r]) for r in range(8)]}")
    core.left_board.set_state([(r, vec[r]) for r in range(8)])
    core.dat_trang_thai_chay(False)

def run_GA():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    cols=[c for _,c in sorted(goal)]
    vec, gen, ok, bests = genetic(tuple(cols))
    core.log_trai(f"Genetic — {'tìm được' if ok else 'không đạt'} sau {gen} thế hệ.")
    core.log_phai("—— Genetic: best mỗi thế hệ ——")
    for i, v in enumerate(bests):
        core.log_phai(f"State {i}: {[(r, v[r]) for r in range(8)]}")
    core.left_board.set_state([(r, vec[r]) for r in range(8)])
    core.dat_trang_thai_chay(False)

def run_ANDOR():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    chay_va_phat("AND-OR", lambda: ANDOR(tuple(), goal))

def run_BT():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    target_cols = [c for (r,c) in sorted(goal)]
    chay_va_phat("Backtracking (MRV+Degree+LCV)",
                 lambda: backtrack_core(use_fc=False, use_ac3=False, target_cols=tuple(target_cols)))

def run_FC():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    target_cols = [c for (r,c) in sorted(goal)]
    chay_va_phat("Forward Checking (MRV+Degree+LCV+AC-3)",
                 lambda: backtrack_core(use_fc=True, use_ac3=True, target_cols=tuple(target_cols)))

def run_AC3():
    goal = core.lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    target_cols = [c for (r,c) in sorted(goal)]
    chay_va_phat("AC-3 + Backtracking",
                 lambda: backtrack_core(use_fc=False, use_ac3=True, target_cols=tuple(target_cols)))

# ===== Khởi tạo UI =====
def main():
    core.root = tk.Tk()
    core.root.title("Bàn cờ N-Queens (2 bảng) • Điều khiển • Nhật ký • Thuật toán — Nhãn 0–7")

    container = tk.Frame(core.root, bg=core.MAU_NEN)
    container.pack(expand=True, fill="both", padx=8, pady=8)

    core.left_board  = ChessBoard(container, colored=True, title="Bàn cờ 1", show_queens=True, solution=[])
    core.right_board = ChessBoard(container, colored=True, title="Bàn cờ 2 (Mục tiêu)", show_queens=True, solution=core.NGHIEM_MAU)

    core.left_board.pack(side="left", expand=True, fill="both", padx=(0,8))
    core.right_board.pack(side="left", expand=True, fill="both", padx=(8,0))

    boards = [core.left_board, core.right_board]
    container.bind("<Configure>", lambda e: resize_boards(e, boards))

    # Cụm điều khiển
    control_frame = tk.Frame(core.root, bg=core.MAU_NEN)
    control_frame.pack(fill="x", padx=8, pady=(0,8))
    btn_reset  = tk.Button(control_frame, text="Reset Bàn Cờ", width=22, command=on_reset)
    btn_gen    = tk.Button(control_frame, text="Sinh Trạng Thái Mục Tiêu", width=22, command=on_generate_goal)
    btn_detail = tk.Button(control_frame, text="Xem Đường Đi Chi Tiết", width=22, command=on_show_detail)
    btn_reset.pack(side="left", padx=6, pady=4)
    btn_gen.pack(side="left", padx=6, pady=4)
    btn_detail.pack(side="left", padx=6, pady=4)
    core.control_buttons[:] = [btn_reset, btn_gen, btn_detail]

    # Hai hộp nhật ký
    log_frame = tk.Frame(core.root, bg=core.MAU_NEN)
    log_frame.pack(fill="both", expand=True, padx=8, pady=(0,8))
    core.log_box1 = scrolledtext.ScrolledText(log_frame, width=50, height=10, wrap="word")
    core.log_box2 = scrolledtext.ScrolledText(log_frame, width=50, height=10, wrap="word")
    core.log_box1.pack(side="left", fill="both", expand=True, padx=(0,6))
    core.log_box2.pack(side="left", fill="both", expand=True, padx=(6,0))

    # Hai hàng nút thuật toán
    def them_nut(frame, nhan, cmd):
        b = tk.Button(frame, text=nhan, width=16, height=2, command=cmd,
                      bg="gray", fg="black", activebackground="white", activeforeground="black")
        b.pack(side="left", padx=5)
        core.algo_buttons.append(b)

    hang1 = tk.Frame(core.root, bg=core.MAU_NEN); hang1.pack(pady=(0,8))
    hang2 = tk.Frame(core.root, bg=core.MAU_NEN); hang2.pack(pady=(0,8))

    # Hàng 1 — Tìm kiếm trạng thái
    them_nut(hang1, "BFS", run_BFS)
    them_nut(hang1, "DFS", run_DFS)
    them_nut(hang1, "DLS", run_DLS)
    them_nut(hang1, "IDS", run_IDS)
    them_nut(hang1, "UCS", run_UCS)
    them_nut(hang1, "Greedy", run_Greedy)
    them_nut(hang1, "A*", run_AStar)
    them_nut(hang1, "Backtracking", run_BT)
    them_nut(hang1, "Forward Checking", run_FC)
    them_nut(hang1, "AC-3", run_AC3)

    # Hàng 2 — Heuristic / Tối ưu cục bộ
    them_nut(hang2, "Hill Climbing", run_HC)
    them_nut(hang2, "Simulated Annealing", run_SA)
    them_nut(hang2, "Beam", run_Beam)
    them_nut(hang2, "Genetic", run_GA)
    them_nut(hang2, "AND OR", run_ANDOR)

    core.root.geometry("1200x880")
    core.root.mainloop()

if __name__ == "__main__":
    main()
