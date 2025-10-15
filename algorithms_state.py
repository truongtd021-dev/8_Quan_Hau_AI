from collections import deque
import itertools
from core import sinh_trang_thai_con, log_trai, thuTuDuyet

# === BFS / DFS / DLS / IDS ===
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
    from core import log_trai  # tránh import vòng
    depth=0
    while True:
        s, p, seen = DFS_IDS(start_pair, goal_pair, depth)
        if s is not None:
            log_trai(f"Tìm thấy ở độ sâu {depth}")
            log_trai(f"Số trạng thái đã duyệt: {seen}")
            return s, p
        depth += 1

# === UCS / Greedy / A* dùng bộ sinh + bộ chọn ===
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

from core import o_hop_le
def sinh_UCS(trangThai):
    row_next = len(trangThai)
    if row_next >= 8: return []
    res=[]
    for col in range(8):
        if o_hop_le(trangThai, row_next, col):
            res.append((chi_phi_g(trangThai,row_next,col), next(thuTuThem), trangThai+((row_next,col),)))
    return res

def sinh_Greedy(trangThai):
    row_next = len(trangThai)
    if row_next >= 8: return []
    res=[]
    for col in range(8):
        if o_hop_le(trangThai, row_next, col):
            res.append((uoc_luong_h(trangThai,row_next,col), next(thuTuThem), trangThai+((row_next,col),)))
    return res

def sinh_AStar(trangThai):
    row_next = len(trangThai)
    if row_next >= 8: return []
    res=[]
    for col in range(8):
        if o_hop_le(trangThai, row_next, col):
            f = chi_phi_g(trangThai,row_next,col) + uoc_luong_h(trangThai,row_next,col)
            res.append((f, next(thuTuThem), trangThai+((row_next,col),)))
    return res

def lua_chon_tot_nhat(start_state, goal_state, succ_fn, nhan):
    from core import log_trai, thuTuDuyet
    pq=[(0,-1,start_state)]
    parent={start_state:None}
    thuTuDuyet.clear()
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
