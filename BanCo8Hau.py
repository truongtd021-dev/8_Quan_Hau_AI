import tkinter as tk
from tkinter import scrolledtext
import random, math, itertools
from collections import deque

# =========================
# MÀU SẮC & NỀN GIAO DIỆN
# =========================
MAU_DAM  = "#FF8C00"
MAU_NHAT = "#F3E5C6"
MAU_NEN  = "#FFFFFF"

# NHÃN TRỤC 0–7 CHO CỘT & HÀNG
COT  = list(range(8))  
HANG = list(range(8))   

NGHIEM_MAU = [
    (0, 4), (1, 2), (2, 7), (3, 3),
    (4, 6), (5, 0), (6, 5), (7, 1)
]

# =========================
# LỚP BÀN CỜ (Canvas)
# =========================
class ChessBoard(tk.Frame):
    def __init__(self, master=None, colored=True, title="", show_queens=False, solution=None):
        super().__init__(master, bg=MAU_NEN)
        self.square = 72
        self.margin = 36
        self.colored = colored
        self.show_queens = show_queens
        self.solution = list(solution) if solution is not None else []

        if title:
            tk.Label(self, text=title, bg=MAU_NEN, font=("Arial", 12, "bold")).pack(pady=(6, 2))

        self.canvas = tk.Canvas(self, bg=MAU_NEN, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

    def set_state(self, state_pairs):
        self.solution = list(state_pairs) if state_pairs is not None else []
        self.draw_board(self.square, self.margin)

    def clear(self):
        self.set_state([])

    def draw_board(self, square, margin):
        self.square, self.margin = square, margin
        c, s, m = self.canvas, square, margin
        c.delete("all")
        canh = m*2 + s*8
        c.config(width=canh, height=canh)

        for r in range(8):
            for f in range(8):
                x0, y0 = m + f*s, m + r*s
                mau = MAU_DAM if (r+f) % 2 == 0 else MAU_NHAT
                c.create_rectangle(x0, y0, x0+s, y0+s, fill=mau, width=0)

        for f, nhan_cot in enumerate(COT):
            x = m + f*s + s/2
            c.create_text(x, m + 8*s + m/2, text=str(nhan_cot), font=("Arial", 14, "bold"))
            c.create_text(x, m/2,               text=str(nhan_cot), font=("Arial", 14, "bold"))
        for r, nhan_hang in enumerate(HANG):
            y = m + r*s + s/2
            c.create_text(m/2,             y, text=str(nhan_hang), font=("Arial", 14, "bold"))
            c.create_text(m + 8*s + m/2,   y, text=str(nhan_hang), font=("Arial", 14, "bold"))

        if self.show_queens and self.solution:
            for r, f in self.solution:
                cx, cy = m + f*s + s/2, m + r*s + s/2
                fill = "#FFFFFF" if ((r+f) % 2 == 0) else "#000000"
                size = int(s*0.65)
                c.create_text(cx, cy, text="♛", font=("Arial", size), fill=fill)

def resize_boards(event, boards):
    w, h = event.width, event.height
    moi_ben_w = w//2 - 20
    moi_ben_h = h - 40
    canh = min(moi_ben_w, moi_ben_h)
    margin = int(canh*0.09)
    square = (canh - 2*margin)//8
    for b in boards:
        b.draw_board(square, margin)

# =========================
# LOG / HOẠT ẢNH / KHÓA NÚT
# =========================
pending_after_ids = []
is_running = False
thuTuDuyet = []
algo_buttons = []
control_buttons = []

def log_trai(msg):
    log_box1.insert(tk.END, msg + "\n")
    log_box1.see(tk.END)

def log_phai(msg):
    log_box2.insert(tk.END, msg + "\n")
    log_box2.see(tk.END)

def xoa_logs():
    log_box1.delete("1.0", tk.END)
    log_box2.delete("1.0", tk.END)

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

def xem_duong_di_chi_tiet():
    if not thuTuDuyet:
        log_phai("Chưa có dữ liệu duyệt. Hãy chạy thuật toán trước.")
        return
    log_phai("—— Xem Đường Đi Chi Tiết ——")
    for i, s in enumerate(thuTuDuyet):
        log_phai(f"State {i}: {s}")

# =========================
# TIỆN ÍCH NGHIỆM & KIỂM TRA
# =========================
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
    state = right_board.solution if right_board.solution else []
    if len(state) != 8:
        log_trai("⚠️ Hãy bấm 'Sinh Trạng Thái Mục Tiêu' để tạo đủ 8 hậu ở bàn phải.")
        return None
    return tuple(state)

# =========================
# KHÔNG GIAN TRẠNG THÁI CƠ BẢN
# =========================
def o_hop_le(trangThai, row_next, col_next):
    for r, c in trangThai:
        if c == col_next:
            return False
        if abs(c - col_next) == abs(r - row_next):
            return False
    return True

def sinh_trang_thai_con(trangThai):
    row_next = len(trangThai)
    if row_next >= 8:
        return []
    res = []
    for col in range(8):
        if o_hop_le(trangThai, row_next, col):
            res.append(trangThai + ((row_next, col),))
    return res

# =========================
# THUẬT TOÁN HÀNG 1
# =========================
def BFS(start, goal):
    global thuTuDuyet
    q = deque([start]); visited={start}; parent={start:None}; thuTuDuyet=[]
    while q:
        s = q.popleft()
        thuTuDuyet.append(s)
        if s == goal:
            path=[]; cur=s
            while cur is not None:
                path.append(cur); cur=parent[cur]
            path.reverse()
            log_trai(f"Số trạng thái đã duyệt: {len(thuTuDuyet)}")
            return s, path
        for ns in sinh_trang_thai_con(s):
            if ns not in visited:
                visited.add(ns); parent[ns]=s; q.append(ns)
    return None, None

def DFS(start, goal):
    global thuTuDuyet
    stack=[start]; visited={start}; parent={start:None}; thuTuDuyet=[]
    while stack:
        s = stack.pop()
        thuTuDuyet.append(s)
        if s == goal:
            path=[]; cur=s
            while cur is not None:
                path.append(cur); cur=parent[cur]
            path.reverse()
            log_trai(f"Số trạng thái đã duyệt: {len(thuTuDuyet)}")
            return s, path
        for ns in sinh_trang_thai_con(s):
            if ns not in visited:
                visited.add(ns); parent[ns]=s; stack.append(ns)
    return None, None

def de_quy_DLS(s, goal, limit, visited, parent):
    global thuTuDuyet
    thuTuDuyet.append(s)
    if s == goal:
        return s, [s]
    if limit == 0:
        return "cutoff", []
    cutoff=False
    for ns in sinh_trang_thai_con(s):
        if ns not in visited:
            visited.add(ns); parent[ns]=s
            res, path = de_quy_DLS(ns, goal, limit-1, visited, parent)
            if res == "cutoff":
                cutoff=True
            elif res != "failure":
                path.append(s)
                return res, path
    return ("cutoff" if cutoff else "failure"), []

def DLS(start, goal, limit=8):
    global thuTuDuyet
    visited={start}; parent={start:None}; thuTuDuyet=[]
    res, path = de_quy_DLS(start, goal, limit, visited, parent)
    if res in (goal,):
        log_trai(f"Số trạng thái đã duyệt: {len(thuTuDuyet)}")
        return res, list(reversed(path))
    if res == "cutoff":
        log_trai("DLS — cutoff (đụng giới hạn trước khi thấy đích)")
    return None, None

def DFS_IDS(start_pair, goal_pair, limit):
    global thuTuDuyet
    stack=[start_pair]; visited={start_pair[0]}; parent={start_pair[0]:None}; thuTuDuyet=[]
    while stack:
        state, depth = stack.pop()
        thuTuDuyet.append(state)
        if state == goal_pair[0]:
            path=[]; cur=state
            while cur is not None:
                path.append(cur); cur=parent[cur]
            path.reverse()
            return state, path, len(thuTuDuyet)
        if depth < limit:
            for ns in sinh_trang_thai_con(state):
                if ns not in visited:
                    visited.add(ns); parent[ns]=state; stack.append((ns, depth+1))
    return None, None, None

def IDS(start_pair, goal_pair):
    depth=0
    while True:
        s, p, seen = DFS_IDS(start_pair, goal_pair, depth)
        if s is not None:
            log_trai(f"Tìm thấy ở độ sâu {depth}")
            log_trai(f"Số trạng thái đã duyệt: {seen}")
            return s, p
        depth += 1

thuTuThem = itertools.count()

def chi_phi_g(trangThai, row_next, col_next):
    g=0
    for r,c in trangThai:
        if c == col_next: g += 1
        if abs(c-col_next) == abs(r-row_next): g += 1
    return g

def uoc_luong_h(trangThai, row_next, col_next):
    s = trangThai + ((row_next, col_next),)
    h=0
    for i in range(row_next+1, 8):
        for j in range(8):
            for r0, c0 in s:
                if j==c0 or (i-j==r0-c0) or (i+j==r0+c0):
                    h += 1
                    break
    return h

def sinh_UCS(trangThai):
    row_next = len(trangThai)
    if row_next >= 8:
        return []
    res=[]
    for col in range(8):
        if o_hop_le(trangThai, row_next, col):
            res.append((chi_phi_g(trangThai,row_next,col), next(thuTuThem), trangThai+((row_next,col),)))
    return res

def sinh_Greedy(trangThai):
    row_next = len(trangThai)
    if row_next >= 8:
        return []
    res=[]
    for col in range(8):
        if o_hop_le(trangThai, row_next, col):
            res.append((uoc_luong_h(trangThai,row_next,col), next(thuTuThem), trangThai+((row_next,col),)))
    return res

def sinh_AStar(trangThai):
    row_next = len(trangThai)
    if row_next >= 8:
        return []
    res=[]
    for col in range(8):
        if o_hop_le(trangThai, row_next, col):
            f = chi_phi_g(trangThai,row_next,col) + uoc_luong_h(trangThai,row_next,col)
            res.append((f, next(thuTuThem), trangThai+((row_next,col),)))
    return res

def lua_chon_tot_nhat(start_state, goal_state, succ_fn, nhan):
    global thuTuDuyet
    pq=[(0,-1,start_state)]
    parent={start_state:None}
    thuTuDuyet=[]
    while pq:
        pq.sort()
        _,_,s = pq.pop(0)
        thuTuDuyet.append(s)
        if s == goal_state:
            path=[]; cur=s
            while cur is not None:
                path.append(cur); cur=parent[cur]
            path.reverse()
            log_trai(f"{nhan} — Số trạng thái đã duyệt: {len(thuTuDuyet)}")
            return s, path
        for c2,o2,st2 in succ_fn(s):
            if st2 not in parent:
                parent[st2]=s
                pq.append((c2,o2,st2))
    return None, None

# =========================
# HEURISTIC / TỐI ƯU CỤC BỘ (Hàng 2)
# =========================
def lang_gieng_vec(vec):
    n=len(vec); out=[]
    for r in range(n):
        for c in range(n):
            if c != vec[r]:
                nv = list(vec); nv[r]=c; out.append(tuple(nv))
    return out

def hieu_so_khac(vec, goal_vec):
    return sum(1 for i in range(8) if vec[i] != goal_vec[i])

# ——— Hill Climbing: trả thêm trace các lần CẢI THIỆN
def hill_climbing(goal_vec):
    vec = tuple(random.randint(0,7) for _ in range(8))
    buoc=0
    trace=[vec]  # có thể bỏ nếu chỉ muốn sau khi improve; để lại để thấy State 0

    while True:
        if vec == goal_vec:
            return vec, buoc, True, trace

        neigh = lang_gieng_vec(vec)
        tot_nhat = min(neigh, key=lambda v: hieu_so_khac(v, goal_vec))
        if hieu_so_khac(tot_nhat, goal_vec) < hieu_so_khac(vec, goal_vec):
            vec = tot_nhat
            buoc += 1
            trace.append(vec)  # chỉ ghi khi cải thiện
        else:
            return vec, buoc, False, trace

# ——— SA: trả về ONLY các bước ACCEPT (trace_accept)
def simulated_annealing(goal_vec, T=100, Tend=1e-3, alpha=0.85, K=10):
    vec = tuple(random.randint(0,7) for _ in range(8))
    thu = 0
    trace_accept=[vec]  # thêm trạng thái đầu (tuỳ chọn)

    while T > Tend:
        for _ in range(K):
            thu += 1
            if vec == goal_vec:
                return vec, thu, True, trace_accept
            r = random.randrange(8)
            c = random.randrange(8)
            while c == vec[r]:
                c = random.randrange(8)
            nxt = list(vec); nxt[r] = c; nxt = tuple(nxt)
            delta = hieu_so_khac(nxt, goal_vec) - hieu_so_khac(vec, goal_vec)
            if delta < 0 or random.random() < math.exp(-delta / T):
                vec = nxt
                trace_accept.append(vec)  # chỉ ghi khi ACCEPT
        T *= alpha
    return vec, thu, (vec == goal_vec), trace_accept

# ——— Beam: lưu best sau mỗi vòng
def beam_search(goal_vec, k=5, max_iter=1000):
    beams = [tuple(random.randint(0,7) for _ in range(8)) for _ in range(k)]
    it=0
    best_trace=[]
    while it < max_iter:
        if goal_vec in beams:
            best_trace.append(goal_vec)
            return goal_vec, it, True, best_trace
        tat_ca = []
        for v in beams:
            tat_ca += lang_gieng_vec(v)
        if not tat_ca:
            break
        tat_ca.sort(key=lambda v: hieu_so_khac(v, goal_vec))
        beams = tat_ca[:k]
        best_now = beams[0]
        best_trace.append(best_now)
        it += 1
    best = min(beams, key=lambda v: hieu_so_khac(v, goal_vec))
    best_trace.append(best)
    return best, it, (best == goal_vec), best_trace

# ——— Genetic: lưu best sau mỗi thế hệ
def genetic(goal_vec, pop_size=100, max_gen=1000, pmut=0.1):
    def ngau_nhien(): return tuple(random.randint(0,7) for _ in range(8))
    def lai(a,b):
        cat = random.randint(1,6)
        return tuple(list(a[:cat]) + list(b[cat:]))
    def dot_bien(v):
        if random.random() < pmut:
            r = random.randrange(8); c = random.randrange(8)
            v = list(v); v[r]=c; v = tuple(v)
        return v

    pop = [ngau_nhien() for _ in range(pop_size)]
    best_trace=[]

    for g in range(max_gen):
        if goal_vec in pop:
            best_trace.append(goal_vec)
            return goal_vec, g, True, best_trace

        pop.sort(key=lambda v: hieu_so_khac(v, goal_vec))
        best_trace.append(pop[0])

        giu = pop[:pop_size//2]
        moi = list(giu)
        while len(moi) < pop_size:
            p1, p2 = random.sample(giu[:min(50,len(giu))], 2)
            moi.append(dot_bien(lai(p1,p2)))
        pop = moi

    best = min(pop, key=lambda v: hieu_so_khac(v, goal_vec))
    best_trace.append(best)
    return best, max_gen, (best == goal_vec), best_trace

def ANDOR(start, goal):
    global thuTuDuyet
    stack=[start]; parent={start:None}; visited={start}; thuTuDuyet=[]
    while stack:
        s = stack.pop()
        thuTuDuyet.append(s)
        if s == goal:
            path=[]; cur=s
            while cur is not None:
                path.append(cur); cur=parent[cur]
            path.reverse()
            log_trai(f"Số trạng thái đã duyệt: {len(thuTuDuyet)}")
            return s, path
        for ns in sinh_trang_thai_con(s):
            if ns not in visited:
                visited.add(ns); parent[ns]=s; stack.append(ns)
    return None, None

# =========================
# BACKTRACKING & FORWARD CHECKING (MRV+Degree+LCV, TRACE đầy đủ)
# —— KHÔNG bó miền theo mục tiêu; chỉ chấp nhận nghiệm khi TRÙNG mục tiêu
# —— Vì vậy sẽ duyệt NHIỀU TRẠNG THÁI giống format các thuật toán khác
# =========================
def tan_cong(r1, c1, r2, c2):
    return c1 == c2 or abs(r1-r2) == abs(c1-c2)

def gan_ve_state(assignment):
    return tuple((r, assignment[r]) for r in sorted(assignment.keys()))

def mien_gia_tri_ban_dau():
    return {r: set(range(8)) for r in range(8)}

def AC3(domains):
    from collections import deque as dq
    q = dq([(xi,xj) for xi in range(8) for xj in range(8) if xi!=xj])
    def revise(xi,xj):
        revised=False
        xoa=set()
        for vi in list(domains[xi]):
            hop_le=False
            for vj in domains[xj]:
                if not tan_cong(xi,vi,xj,vj):
                    hop_le=True; break
            if not hop_le:
                xoa.add(vi)
        if xoa:
            domains[xi]-=xoa; revised=True
        return revised
    while q:
        xi,xj=q.popleft()
        if revise(xi,xj):
            if not domains[xi]:
                return False
            for xk in range(8):
                if xk!=xi and xk!=xj:
                    q.append((xk,xi))
    return True

def chon_bien_MRV_Degree(assignment, domains):
    chua_gan = [r for r in range(8) if r not in assignment]
    mien_min = min(len(domains[r]) for r in chua_gan)
    ung_cu = [r for r in chua_gan if len(domains[r]) == mien_min]
    if len(ung_cu) == 1:
        return ung_cu[0]
    def diem_bac(r): return sum(1 for rr in chua_gan if rr != r)
    return max(ung_cu, key=diem_bac)

def thu_tu_gia_tri_LCV(row, domains, assignment):
    def ton_that(col):
        dem=0
        for r2 in range(8):
            if r2 in assignment or r2==row: continue
            for v in domains[r2]:
                if tan_cong(row,col,r2,v):
                    dem += 1
        return dem
    return sorted(list(domains[row]), key=ton_that)

def forward_check(row, col, domains, assignment, trail):
    for r2 in range(8):
        if r2 == row or r2 in assignment:
            continue
        xoa=set()
        for v in list(domains[r2]):
            if tan_cong(row, col, r2, v):
                xoa.add(v)
        if xoa:
            domains[r2] -= xoa
            trail.append((r2, xoa))
            if not domains[r2]:
                return False
    return True

def undo_trail(domains, trail):
    for r, xoa in reversed(trail):
        domains[r] |= xoa

def backtrack_core(use_fc=False, use_ac3=False, target_cols=None):
    """
    Backtracking tổng quát.
    - KHÔNG bó miền theo mục tiêu (để duyệt nhiều trạng thái).
    - Nếu target_cols != None: chỉ chấp nhận nghiệm khi vector cột == target_cols.
    - Ghi thuTuDuyet đầy đủ (tiến & lùi). Trả về (goal_state, path_tien).
    """
    assignment = {}
    domains = mien_gia_tri_ban_dau()
    path = []  # dùng để animate: chỉ lưu trạng thái TIẾN (tăng kích thước)
    global thuTuDuyet
    thuTuDuyet = []

    if use_ac3:
        if not AC3(domains):
            return None, None

    def snapshot():
        st = gan_ve_state(assignment)
        thuTuDuyet.append(st)
        return st

    snapshot()  # rỗng

    def bt():
        nonlocal assignment, domains, path
        if len(assignment) == 8:
            if target_cols is None:
                return True
            vec = tuple(assignment[r] for r in range(8))
            if vec == tuple(target_cols):
                return True
            return False

        var = chon_bien_MRV_Degree(assignment, domains)
        for val in thu_tu_gia_tri_LCV(var, domains, assignment):
            ok = True
            for r, c in assignment.items():
                if tan_cong(r, c, var, val):
                    ok = False; break
            if not ok:
                continue

            # GÁN
            assignment[var] = val
            st = snapshot()
            if not path or len(st) > len(path[-1]):
                path.append(st)

            if use_fc:
                trail = []
                if forward_check(var, val, domains, assignment, trail):
                    if bt():
                        return True
                undo_trail(domains, trail)
            else:
                if bt():
                    return True

            # LÙI
            assignment.pop(var)
            snapshot()

        return False

    ok = bt()
    if not ok:
        return None, None

    full = gan_ve_state(assignment)
    if not path or path[-1] != full:
        path.append(full)
    return full, path

# =========================
# NÚT ĐIỀU KHIỂN
# =========================
def on_reset():
    dung_va_mo_khoa()
    left_board.clear()
    right_board.clear()
    xoa_logs()
    log_trai("Đã Reset.")

def on_generate_goal():
    dung_va_mo_khoa()
    goal = sinh_nghiem_hop_le(8)
    right_board.set_state(goal)
    log_trai("Đã sinh trạng thái mục tiêu (bàn phải).")

def on_show_detail():
    xem_duong_di_chi_tiet()

# =========================
# TRÌNH CHẠY CHUNG & GỌI THUẬT TOÁN
# =========================
def chuan_bi_chay():
    dung_va_mo_khoa()
    left_board.clear()
    xoa_logs()
    dat_trang_thai_chay(True)

def chay_va_phat(nhan, ham_tinh):
    found, path = ham_tinh()
    log_trai(f"{nhan} — Số trạng thái đã duyệt: {len(thuTuDuyet)}")
    if found is not None and path:
        nhanh = 200 if nhan.startswith(("Backtracking", "Forward")) else 300
        phat_duong_di(path, delay_ms=nhanh)
    else:
        log_trai(f"{nhan}: Không tìm thấy.")
        dat_trang_thai_chay(False)

# ——— Hàng 1
def run_BFS():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    start = tuple()
    chay_va_phat("BFS", lambda: BFS(start, goal))

def run_DFS():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    start = tuple()
    chay_va_phat("DFS", lambda: DFS(start, goal))

def run_DLS():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    start = tuple()
    chay_va_phat("DLS", lambda: DLS(start, goal, 8))

def run_IDS():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    startp=(tuple(), 0); goalp=(goal, None)
    chay_va_phat("IDS", lambda: IDS(startp, goalp))

def run_UCS():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    chay_va_phat("UCS", lambda: lua_chon_tot_nhat(tuple(), goal, sinh_UCS, "UCS"))

def run_Greedy():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    chay_va_phat("Greedy", lambda: lua_chon_tot_nhat(tuple(), goal, sinh_Greedy, "Greedy"))

def run_AStar():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    chay_va_phat("A*", lambda: lua_chon_tot_nhat(tuple(), goal, sinh_AStar, "A*"))

# ——— Hàng 2: Heuristic (log phải theo yêu cầu)
def run_HC():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()

    cols=[c for _,c in sorted(goal)]
    vec, buoc, ok, trace = hill_climbing(tuple(cols))

    # Trái: tóm tắt
    log_trai(f"Hill Climbing — {'tìm được' if ok else 'kẹt cực tiểu'} sau {buoc} lần cải thiện.")

    # Phải: State 0.. theo lần cải thiện
    log_phai("—— Hill Climbing: diễn tiến ——")
    for i, v in enumerate(trace):
        log_phai(f"State {i}: {[(r, v[r]) for r in range(8)]}")

    left_board.set_state([(r, vec[r]) for r in range(8)])
    dat_trang_thai_chay(False)

def run_SA():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()

    cols=[c for _,c in sorted(goal)]
    vec, thu, ok, acc = simulated_annealing(tuple(cols))

    log_trai(f"Simulated Annealing — {'tìm được' if ok else 'không đạt'} sau {thu} lần thử.")

    # Phải: chỉ các bước ACCEPT
    log_phai("—— Simulated Annealing: các bước ACCEPT ——")
    for i, v in enumerate(acc):
        log_phai(f"State {i}: {[(r, v[r]) for r in range(8)]}")

    left_board.set_state([(r, vec[r]) for r in range(8)])
    dat_trang_thai_chay(False)

def run_Beam():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()

    cols=[c for _,c in sorted(goal)]
    vec, it, ok, bests = beam_search(tuple(cols))

    log_trai(f"Beam — {'tìm được' if ok else 'không đạt'} sau {it} vòng lặp.")

    # Phải: best sau mỗi vòng
    log_phai("—— Beam Search: best mỗi vòng ——")
    for i, v in enumerate(bests):
        log_phai(f"State {i}: {[(r, v[r]) for r in range(8)]}")

    left_board.set_state([(r, vec[r]) for r in range(8)])
    dat_trang_thai_chay(False)

def run_GA():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()

    cols=[c for _,c in sorted(goal)]
    vec, gen, ok, bests = genetic(tuple(cols))

    log_trai(f"Genetic — {'tìm được' if ok else 'không đạt'} sau {gen} thế hệ.")

    # Phải: best mỗi thế hệ
    log_phai("—— Genetic: best mỗi thế hệ ——")
    for i, v in enumerate(bests):
        log_phai(f"State {i}: {[(r, v[r]) for r in range(8)]}")

    left_board.set_state([(r, vec[r]) for r in range(8)])
    dat_trang_thai_chay(False)

def run_ANDOR():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    chay_va_phat("AND-OR", lambda: ANDOR(tuple(), goal))

# —— Backtracking / Forward Checking / AC-3 + Backtracking
def run_BT():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    target_cols = [c for (r,c) in sorted(goal)]
    chay_va_phat("Backtracking (MRV+Degree+LCV)",
                 lambda: backtrack_core(use_fc=False, use_ac3=False, target_cols=tuple(target_cols)))

def run_FC():
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    target_cols = [c for (r,c) in sorted(goal)]
    chay_va_phat("Forward Checking (MRV+Degree+LCV+AC-3)",
                 lambda: backtrack_core(use_fc=True, use_ac3=True, target_cols=tuple(target_cols)))

def run_AC3():
    """
    AC-3 (tiền xử lý) + Backtracking để tìm nghiệm TRÙNG mục tiêu.
    """
    goal = lay_muc_tieu()
    if goal is None: return
    chuan_bi_chay()
    target_cols = [c for (r,c) in sorted(goal)]
    chay_va_phat("AC-3 + Backtracking",
                 lambda: backtrack_core(use_fc=False, use_ac3=True, target_cols=tuple(target_cols)))

# =========================
# KHỞI TẠO APP
# =========================
root = tk.Tk()
root.title("Bàn cờ N-Queens (2 bảng) • Điều khiển • Nhật ký • Thuật toán — Nhãn 0–7")

container = tk.Frame(root, bg=MAU_NEN)
container.pack(expand=True, fill="both", padx=8, pady=8)

left_board  = ChessBoard(container, colored=True, title="Bàn cờ 1", show_queens=True, solution=[])
right_board = ChessBoard(container, colored=True, title="Bàn cờ 2 (Mục tiêu)", show_queens=True, solution=NGHIEM_MAU)

left_board.pack(side="left", expand=True, fill="both", padx=(0,8))
right_board.pack(side="left", expand=True, fill="both", padx=(8,0))

boards = [left_board, right_board]
container.bind("<Configure>", lambda e: resize_boards(e, boards))

# Cụm điều khiển
control_frame = tk.Frame(root, bg=MAU_NEN)
control_frame.pack(fill="x", padx=8, pady=(0,8))
btn_reset  = tk.Button(control_frame, text="Reset Bàn Cờ", width=22, command=on_reset)
btn_gen    = tk.Button(control_frame, text="Sinh Trạng Thái Mục Tiêu", width=22, command=on_generate_goal)
btn_detail = tk.Button(control_frame, text="Xem Đường Đi Chi Tiết", width=22, command=on_show_detail)
btn_reset.pack(side="left", padx=6, pady=4)
btn_gen.pack(side="left", padx=6, pady=4)
btn_detail.pack(side="left", padx=6, pady=4)
control_buttons = [btn_reset, btn_gen, btn_detail]

# Hai hộp nhật ký
log_frame = tk.Frame(root, bg=MAU_NEN)
log_frame.pack(fill="both", expand=True, padx=8, pady=(0,8))
log_box1 = scrolledtext.ScrolledText(log_frame, width=50, height=10, wrap="word")
log_box2 = scrolledtext.ScrolledText(log_frame, width=50, height=10, wrap="word")
log_box1.pack(side="left", fill="both", expand=True, padx=(0,6))
log_box2.pack(side="left", fill="both", expand=True, padx=(6,0))

# Hai hàng nút thuật toán
def them_nut_thuat_toan(frame, nhan, cmd):
    b = tk.Button(frame, text=nhan, width=16, height=2, command=cmd,
                  bg="gray", fg="black", activebackground="white", activeforeground="black")
    b.pack(side="left", padx=5)
    algo_buttons.append(b)

hang1 = tk.Frame(root, bg=MAU_NEN); hang1.pack(pady=(0,8))
hang2 = tk.Frame(root, bg=MAU_NEN); hang2.pack(pady=(0,8))

# Hàng 1 — Tìm kiếm trạng thái
them_nut_thuat_toan(hang1, "BFS", run_BFS)
them_nut_thuat_toan(hang1, "DFS", run_DFS)
them_nut_thuat_toan(hang1, "DLS", run_DLS)
them_nut_thuat_toan(hang1, "IDS", run_IDS)
them_nut_thuat_toan(hang1, "UCS", run_UCS)
them_nut_thuat_toan(hang1, "Greedy", run_Greedy)
them_nut_thuat_toan(hang1, "A*", run_AStar)
them_nut_thuat_toan(hang1, "Backtracking", run_BT)
them_nut_thuat_toan(hang1, "Forward Checking", run_FC)
them_nut_thuat_toan(hang1, "AC-3", run_AC3)

# Hàng 2 — Heuristic / Tối ưu cục bộ (có log phải)
them_nut_thuat_toan(hang2, "Hill Climbing", run_HC)
them_nut_thuat_toan(hang2, "Simulated Annealing", run_SA)
them_nut_thuat_toan(hang2, "Beam", run_Beam)
them_nut_thuat_toan(hang2, "Genetic", run_GA)
them_nut_thuat_toan(hang2, "AND OR", run_ANDOR)

root.geometry("1200x880")
root.mainloop()
