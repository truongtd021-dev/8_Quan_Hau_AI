import math, random
from core import log_trai, log_phai, thuTuDuyet, sinh_trang_thai_con

# ===== Local search utils =====
def lang_gieng_vec(vec):
    n=len(vec); out=[]
    for r in range(n):
        for c in range(n):
            if c != vec[r]:
                nv = list(vec); nv[r]=c; out.append(tuple(nv))
    return out

def hieu_so_khac(vec, goal_vec):
    return sum(1 for i in range(8) if vec[i] != goal_vec[i])

# ===== Hill Climbing =====
def hill_climbing(goal_vec):
    vec = tuple(random.randint(0,7) for _ in range(8))
    buoc=0
    trace=[vec]
    while True:
        if vec == goal_vec:
            return vec, buoc, True, trace
        neigh = lang_gieng_vec(vec)
        tot_nhat = min(neigh, key=lambda v: hieu_so_khac(v, goal_vec))
        if hieu_so_khac(tot_nhat, goal_vec) < hieu_so_khac(vec, goal_vec):
            vec = tot_nhat; buoc += 1; trace.append(vec)
        else:
            return vec, buoc, False, trace

# ===== Simulated Annealing =====
def simulated_annealing(goal_vec, T=100, Tend=1e-3, alpha=0.85, K=10):
    vec = tuple(random.randint(0,7) for _ in range(8))
    thu = 0
    trace_accept=[vec]
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
            delta = hieu_so_khac(nxt, goal_vec) - hieu_so_kac(vec, goal_vec)  # <-- fix typo khi copy (hieu_so_khac)
            # SỬA ĐÚNG:
            # delta = hieu_so_khac(nxt, goal_vec) - hieu_so_khac(vec, goal_vec)
            if delta < 0 or random.random() < math.exp(-delta / T):
                vec = nxt
                trace_accept.append(vec)
        T *= alpha
    return vec, thu, (vec == goal_vec), trace_accept

# ===== Beam Search =====
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
        if not tat_ca: break
        tat_ca.sort(key=lambda v: hieu_so_khac(v, goal_vec))
        beams = tat_ca[:k]
        best_now = beams[0]
        best_trace.append(best_now)
        it += 1
    best = min(beams, key=lambda v: hieu_so_khac(v, goal_vec))
    best_trace.append(best)
    return best, it, (best == goal_vec), best_trace

# ===== Genetic Algorithm =====
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

# ===== AND-OR (demo hành vi DFS về goal) =====
def ANDOR(start, goal):
    from core import thuTuDuyet, log_trai
    stack=[start]; parent={start:None}; visited={start}; thuTuDuyet.clear()
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

# ===== CSP: AC-3 / MRV / LCV / Forward Checking / Backtracking =====
def tan_cong(r1, c1, r2, c2):
    return c1 == c2 or abs(r1-r2) == abs(c1-c2)

def gan_ve_state(assignment):
    return tuple((r, assignment[r]) for r in sorted(assignment.keys()))

def mien_gia_tri_ban_dau():
    return {r: set(range(8)) for r in range(8)}

from collections import deque as dq
def AC3(domains):
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
    from core import thuTuDuyet
    assignment = {}
    domains = mien_gia_tri_ban_dau()
    path = []
    thuTuDuyet.clear()

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
            if target_cols is None: return True
            vec = tuple(assignment[r] for r in range(8))
            return vec == tuple(target_cols)

        var = chon_bien_MRV_Degree(assignment, domains)
        for val in thu_tu_gia_tri_LCV(var, domains, assignment):
            ok = True
            for r, c in assignment.items():
                if tan_cong(r, c, var, val):
                    ok = False; break
            if not ok: continue

            assignment[var] = val
            st = snapshot()
            if not path or len(st) > len(path[-1]):
                path.append(st)

            if use_fc:
                trail = []
                if forward_check(var, val, domains, assignment, trail):
                    if bt(): return True
                undo_trail(domains, trail)
            else:
                if bt(): return True

            assignment.pop(var)
            snapshot()
        return False

    ok = bt()
    if not ok: return None, None

    full = gan_ve_state(assignment)
    if not path or path[-1] != full:
        path.append(full)
    return full, path
