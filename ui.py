import tkinter as tk

MAU_DAM  = "#FF8C00"
MAU_NHAT = "#F3E5C6"
MAU_NEN  = "#FFFFFF"

COT  = list(range(8))
HANG = list(range(8))

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
