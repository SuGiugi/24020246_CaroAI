import tkinter as tk
from tkinter import messagebox
import threading
import time

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────
BG_DARK       = "#0D1117"
BG_PANEL      = "#161B22"
BG_BOARD      = "#0D1117"
CELL_NORMAL   = "#1C2333"
CELL_HOVER    = "#243044"
GRID_LINE     = "#2D3748"
X_COLOR       = "#38BDF8"
X_GLOW        = "#0EA5E9"
O_COLOR       = "#F87171"
O_GLOW        = "#EF4444"
WIN_HIGHLIGHT = "#FFD700"
TEXT_PRIMARY  = "#E2E8F0"
TEXT_MUTED    = "#64748B"
TEXT_X        = X_COLOR
TEXT_O        = O_COLOR
ACCENT        = "#7C3AED"
BTN_BG        = "#1E293B"
BTN_HOVER     = "#334155"
BTN_BORDER    = "#334155"

CELL_SIZE  = 54
PADDING    = 20
FONT_TITLE = ("Courier New", 20, "bold")
FONT_CELL  = ("Courier New", 22, "bold")
FONT_INFO  = ("Courier New", 11)
FONT_BTN   = ("Courier New", 10, "bold")
FONT_LABEL = ("Courier New", 10)
FONT_SCORE = ("Courier New", 24, "bold")


class CaroGUI:
    def __init__(self, game_factory, ai_agent, board_size=9):
        """
        game_factory: callable() → Game_Caro instance
        ai_agent    : agent instance (has .get_best_move(game))
        board_size  : kích thước bàn cờ
        """
        self.game_factory = game_factory
        self.ai           = ai_agent
        self.size         = board_size
        self.game         = game_factory()
        self.human_player = 'X'
        self.ai_player    = 'O'
        self.ai_thinking  = False
        self.game_over    = False
        # scores['human'] và scores['ai'] thay vì gắn cứng vào ký hiệu X/O
        self.scores       = {'human': 0, 'ai': 0, 'Draw': 0}
        self.last_move    = None
        self.last_human   = []
        self.last_ai      = []
        self.win_cells    = []
        self._hover_cell  = None
        self.move_history = []   # list of (r, c, player) cho review
        self._review_mode = False
        self._review_step = 0
        self._overlay_win = None

        self.root = tk.Tk()
        self.root.title("CARO — Dark Edition")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self._build_ui()
        self._draw_board()
        self.root.mainloop()

    # ──────────────────────────────────────────────────────── BUILD UI ──────
    def _build_ui(self):
        # ── Header
        header = tk.Frame(self.root, bg=BG_DARK)
        header.pack(fill='x', padx=24, pady=(18, 0))

        tk.Label(header, text="⬡  CARO", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side='left')
        tk.Label(header, text="DARK EDITION", font=("Courier New", 8, "bold"),
                 bg=BG_DARK, fg=TEXT_MUTED).pack(side='left', padx=(8, 0), pady=(8, 0))

        # ── Main layout
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(padx=20, pady=12)

        # Left panel
        self.left = tk.Frame(body, bg=BG_PANEL, width=160,
                             highlightbackground=GRID_LINE, highlightthickness=1)
        self.left.pack(side='left', fill='y', padx=(0, 14))
        self.left.pack_propagate(False)
        self._build_left_panel()

        # Canvas
        canvas_size = self.size * CELL_SIZE + PADDING * 2
        self.canvas = tk.Canvas(body, width=canvas_size, height=canvas_size,
                                bg=BG_BOARD, highlightthickness=0)
        self.canvas.pack(side='left')
        self.canvas.bind("<Motion>",   self._on_hover)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Leave>",    self._on_leave)

        # Right panel
        self.right = tk.Frame(body, bg=BG_PANEL, width=160,
                              highlightbackground=GRID_LINE, highlightthickness=1)
        self.right.pack(side='left', fill='y', padx=(14, 0))
        self.right.pack_propagate(False)
        self._build_right_panel()

        # ── Status bar
        self.status_var = tk.StringVar(value="Your turn  ›  X")
        status_bar = tk.Frame(self.root, bg=BG_PANEL,
                              highlightbackground=GRID_LINE, highlightthickness=1)
        status_bar.pack(fill='x', padx=20, pady=(0, 16))
        tk.Label(status_bar, textvariable=self.status_var,
                 font=FONT_INFO, bg=BG_PANEL, fg=TEXT_PRIMARY,
                 anchor='w', padx=14, pady=8).pack(side='left')
        self.thinking_var = tk.StringVar(value="")
        tk.Label(status_bar, textvariable=self.thinking_var,
                 font=FONT_INFO, bg=BG_PANEL, fg=TEXT_MUTED,
                 anchor='e', padx=14).pack(side='right')

    def _build_left_panel(self):
        pad = dict(bg=BG_PANEL)
        tk.Label(self.left, text="SCORE", font=("Courier New", 8, "bold"),
                 fg=TEXT_MUTED, **pad).pack(pady=(18, 4))

        # Human score (luôn hiển thị màu theo ký hiệu người chơi chọn)
        xf = tk.Frame(self.left, **pad)
        xf.pack(fill='x', padx=14, pady=4)
        self.label_human_sym = tk.Label(xf, text="X", font=("Courier New", 13, "bold"),
                                        fg=X_COLOR, **pad)
        self.label_human_sym.pack(side='left')
        tk.Label(xf, text="YOU", font=("Courier New", 7),
                 fg=TEXT_MUTED, **pad).pack(side='left', padx=4, pady=2)
        self.score_human = tk.Label(xf, text="0", font=FONT_SCORE,
                                    fg=X_COLOR, **pad)
        self.score_human.pack(side='right')

        tk.Frame(self.left, bg=GRID_LINE, height=1).pack(fill='x', padx=14, pady=2)

        # AI score
        of = tk.Frame(self.left, **pad)
        of.pack(fill='x', padx=14, pady=4)
        self.label_ai_sym = tk.Label(of, text="O", font=("Courier New", 13, "bold"),
                                     fg=O_COLOR, **pad)
        self.label_ai_sym.pack(side='left')
        tk.Label(of, text="AI", font=("Courier New", 7),
                 fg=TEXT_MUTED, **pad).pack(side='left', padx=4, pady=2)
        self.score_ai = tk.Label(of, text="0", font=FONT_SCORE,
                                 fg=O_COLOR, **pad)
        self.score_ai.pack(side='right')

        tk.Frame(self.left, bg=GRID_LINE, height=1).pack(fill='x', padx=14, pady=2)

        # Draw score
        df = tk.Frame(self.left, **pad)
        df.pack(fill='x', padx=14, pady=4)
        tk.Label(df, text="—", font=("Courier New", 11),
                 fg=TEXT_MUTED, **pad).pack(side='left')
        tk.Label(df, text="DRAW", font=("Courier New", 7),
                 fg=TEXT_MUTED, **pad).pack(side='left', padx=4)
        self.score_d = tk.Label(df, text="0", font=("Courier New", 18, "bold"),
                                fg=TEXT_MUTED, **pad)
        self.score_d.pack(side='right')

        # ── Side picker
        tk.Frame(self.left, bg=GRID_LINE, height=1).pack(fill='x', padx=14, pady=(16, 4))
        tk.Label(self.left, text="PLAY AS", font=("Courier New", 8, "bold"),
                 fg=TEXT_MUTED, **pad).pack(pady=(4, 6))
        sf = tk.Frame(self.left, **pad)
        sf.pack()
        self._side_btns = {}
        for sym, col in [('X', X_COLOR)]:
            b = tk.Button(sf, text=sym, font=("Courier New", 11, "bold"),
                          bg=CELL_NORMAL, fg=col, width=3, relief='flat',
                          activebackground=CELL_HOVER, activeforeground=col,
                          cursor='hand2',
                          command=lambda s=sym: self._pick_side(s))
            b.pack(side='left', padx=4)
            self._side_btns[sym] = b
        self._highlight_side_btn('X')

    def _build_right_panel(self):
        pad = dict(bg=BG_PANEL)
        tk.Label(self.right, text="INFO", font=FONT_LABEL,
                 fg=TEXT_MUTED, **pad).pack(pady=(18, 8))

        tk.Label(self.right, text="NODES", font=FONT_LABEL,
                 fg=TEXT_MUTED, **pad).pack(anchor='w', padx=14)
        self.nodes_var = tk.StringVar(value="—")
        tk.Label(self.right, textvariable=self.nodes_var,
                 font=("Courier New", 12, "bold"), fg=TEXT_PRIMARY, **pad).pack(anchor='w', padx=14)

        tk.Frame(self.right, bg=GRID_LINE, height=1).pack(fill='x', padx=14, pady=8)

        tk.Label(self.right, text="TIME (s)", font=FONT_LABEL,
                 fg=TEXT_MUTED, **pad).pack(anchor='w', padx=14)
        self.time_var = tk.StringVar(value="—")
        tk.Label(self.right, textvariable=self.time_var,
                 font=("Courier New", 12, "bold"), fg=TEXT_PRIMARY, **pad).pack(anchor='w', padx=14)

        tk.Frame(self.right, bg=GRID_LINE, height=1).pack(fill='x', padx=14, pady=8)

        tk.Label(self.right, text="DEPTH", font=FONT_LABEL,
                 fg=TEXT_MUTED, **pad).pack(anchor='w', padx=14)
        tk.Label(self.right, text=str(self.ai.depth),
                 font=("Courier New", 12, "bold"), fg=ACCENT, **pad).pack(anchor='w', padx=14)

        tk.Frame(self.right, bg=GRID_LINE, height=1).pack(fill='x', padx=14, pady=8)

        # ─── THÀNH PHẦN CHÈN MỚI CHO LEVEL 2: CHỌN CHẾ ĐỘ AI ───
        tk.Label(self.right, text="AI MODE", font=FONT_LABEL, fg=TEXT_MUTED, **pad).pack(anchor='w', padx=14)
        self.ai_mode_var = tk.StringVar(value="alphabeta")  # Mặc định chọn Alpha-Beta

        for text_mode, val_mode in [("Minimax", "minimax"), ("Alpha-Beta", "alphabeta"), ("Đối Sánh", "compare")]:
            rb = tk.Radiobutton(self.right, text=text_mode, value=val_mode, variable=self.ai_mode_var,
                                font=("Courier New", 9), bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=BG_DARK,
                                activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY, anchor='w')
            rb.pack(fill='x', padx=14, pady=2)

        tk.Frame(self.right, bg=GRID_LINE, height=1).pack(fill='x', padx=14, pady=(8, 16))
        # ───────────────────────────────────────────────────────

        # Buttons gốc giữ nguyên
        for txt, cmd in [("NEW GAME", self._new_game), ("UNDO", self._undo)]:
            b = tk.Button(self.right, text=txt, font=FONT_BTN,
                          bg=BTN_BG, fg=TEXT_PRIMARY, relief='flat',
                          activebackground=BTN_HOVER, activeforeground=TEXT_PRIMARY,
                          cursor='hand2', width=13, pady=7,
                          highlightbackground=BTN_BORDER, highlightthickness=1,
                          command=cmd)
            b.pack(padx=14, pady=4)
    # ──────────────────────────────────────────────────────── DRAW ───────────
    def _draw_board(self):
        self.canvas.delete("all")
        sz = self.size
        cs = CELL_SIZE
        p  = PADDING

        # Background cells
        for r in range(sz):
            for c in range(sz):
                x0 = p + c * cs + 2
                y0 = p + r * cs + 2
                x1 = x0 + cs - 4
                y1 = y0 + cs - 4
                color = CELL_NORMAL
                if (r, c) == self._hover_cell and not self.game_over and not self.ai_thinking:
                    if self.game.board[r][c] == '.':
                        color = CELL_HOVER
                self.canvas.create_rectangle(x0, y0, x1, y1,
                                             fill=color, outline="", tags=f"cell_{r}_{c}")

        # Grid lines
        for i in range(sz + 1):
            x = p + i * cs
            self.canvas.create_line(x, p, x, p + sz * cs, fill=GRID_LINE, width=1)
            self.canvas.create_line(p, x, p + sz * cs, x, fill=GRID_LINE, width=1)

        # Pieces
        for r in range(sz):
            for c in range(sz):
                v = self.game.board[r][c]
                if v != '.':
                    self._draw_piece(r, c, v)

        # Last move highlight
        if self.last_move:
            lr, lc = self.last_move
            piece_color = X_COLOR if self.game.board[lr][lc] == 'X' else O_COLOR
            outline_color = WIN_HIGHLIGHT if self.win_cells else piece_color
            self.canvas.create_rectangle(
                p + lc * cs + 2, p + lr * cs + 2,
                p + lc * cs + cs - 2, p + lr * cs + cs - 2,
                outline=outline_color, width=2, fill=""
            )

        # Win highlight
        for (wr, wc) in self.win_cells:
            x0 = p + wc * cs + 3
            y0 = p + wr * cs + 3
            self.canvas.create_rectangle(x0, y0, x0 + cs - 6, y0 + cs - 6,
                                         fill=WIN_HIGHLIGHT + "33", outline=WIN_HIGHLIGHT, width=2)

        # Hover ghost piece — hiển thị cho cả X lẫn O
        if self._hover_cell and not self.game_over and not self.ai_thinking:
            hr, hc = self._hover_cell
            if self.game.board[hr][hc] == '.':
                self._draw_piece(hr, hc, self.human_player, ghost=True)

    def _draw_piece(self, r, c, player, ghost=False):
        p  = PADDING
        cs = CELL_SIZE
        cx = p + c * cs + cs // 2
        cy = p + r * cs + cs // 2

        # margin xác định kích thước — dùng chung cho X và O
        margin = 10

        if player == 'X':
            color = X_COLOR if not ghost else "#5BBFDB"
            self.canvas.create_line(cx - margin, cy - margin,
                                    cx + margin, cy + margin,
                                    fill=color, width=4, capstyle='round')
            self.canvas.create_line(cx + margin, cy - margin,
                                    cx - margin, cy + margin,
                                    fill=color, width=4, capstyle='round')
        else:
            # tkinter không hỗ trợ alpha hex — ghost dùng màu solid tối hơn
            color = "#A84444" if ghost else O_COLOR
            r_ = margin
            # Vẽ 2 oval lồng nhau (±1px) để nét dày tương đương X width=4
            self.canvas.create_oval(cx - r_ - 1, cy - r_ - 1,
                                    cx + r_ + 1, cy + r_ + 1,
                                    outline=color, width=2, fill="")
            self.canvas.create_oval(cx - r_ + 1, cy - r_ + 1,
                                    cx + r_ - 1, cy + r_ - 1,
                                    outline=color, width=2, fill="")

    # ──────────────────────────────────────────────────────── EVENTS ─────────
    def _cell_from_event(self, event):
        c = (event.x - PADDING) // CELL_SIZE
        r = (event.y - PADDING) // CELL_SIZE
        if 0 <= r < self.size and 0 <= c < self.size:
            return r, c
        return None

    def _on_hover(self, event):
        cell = self._cell_from_event(event)
        if cell != self._hover_cell:
            self._hover_cell = cell
            self._draw_board()

    def _on_leave(self, event):
        self._hover_cell = None
        self._draw_board()

    def _on_click(self, event):
        if self.game_over or self.ai_thinking:
            return
        if self.game.current_player != self.human_player:
            return
        cell = self._cell_from_event(event)
        if cell is None:
            return
        r, c = cell
        if self.game.board[r][c] != '.':
            return
        self._place_move(r, c)

    def _place_move(self, r, c):
        self.last_move = (r, c)
        self.last_human.append((r, c))
        player = self.game.current_player
        finished = self.game.make_move(r, c)
        self.move_history.append((r, c, player))
        self._draw_board()
        if finished:
            self._handle_game_over(r, c)
            return
        if not self.game_over:
            self._set_status(f"AI thinking…  {self.ai_player}", TEXT_MUTED)
            self.thinking_var.set("▌")
            self.root.after(80, self._ai_turn)

    def _ai_turn(self):
        self.ai_thinking = True
        self._animate_thinking()
        def run():
            current_mode = self.ai_mode_var.get()
            (x, y), nodes, elapsed = self.ai.get_best_move(self.game, mode=current_mode)
            self.root.after(0, lambda: self._finish_ai(x, y, nodes, elapsed))
        threading.Thread(target=run, daemon=True).start()

    def _finish_ai(self, x, y, nodes, elapsed):
        self.ai_thinking = False
        self.thinking_var.set("")
        self.nodes_var.set(f"{nodes:,}")
        self.time_var.set(f"{elapsed:.3f}")
        self.last_move = (x, y)
        self.last_ai.append((x, y))
        player = self.game.current_player
        finished = self.game.make_move(x, y)
        self.move_history.append((x, y, player))
        self._draw_board()
        if finished:
            self._handle_game_over(x, y)
        else:
            self._set_status(f"Your turn  ›  {self.human_player}", TEXT_PRIMARY)

    def _animate_thinking(self):
        if not self.ai_thinking:
            return
        frames = ["▌", "▐", "▌▐", "·"]
        cur = self.thinking_var.get()
        nxt = frames[(frames.index(cur) + 1) % len(frames)] if cur in frames else "▌"
        self.thinking_var.set(nxt)
        self.root.after(300, self._animate_thinking)

    def _handle_game_over(self, x, y):
        self.game_over = True
        if self.game.check_win(x, y, self.game.board):
            winner = self.game.board[x][y]
            if winner == self.human_player:
                self.scores['human'] += 1
                color = X_COLOR if self.human_player == 'X' else O_COLOR
                label = "YOU WIN!"
                sub   = "Congratulations 🎉"
                star  = True
            else:
                self.scores['ai'] += 1
                color = O_COLOR if self.human_player == 'X' else X_COLOR
                label = "AI WINS"
                sub   = "Better luck next time"
                star  = False
            self._update_scores()
            self._set_status(f"{'★   ' if star else ''}  {label}  {'   ★' if star else ''}", color)
            self._highlight_win(x, y, winner)
        else:
            self.scores['Draw'] += 1
            self._update_scores()
            color = TEXT_MUTED
            label = "DRAW"
            sub   = "Well played"
            self._set_status("DRAW  —  Well played", TEXT_MUTED)

        # Delay nhỏ để highlight win hiện trước rồi mới popup
        self.root.after(600, lambda: self._show_endgame_popup(label, sub, color))

    # ──────────────────────────────────────────────────── END-GAME POPUP ────
    def _show_endgame_popup(self, label, sub, accent_color):
        """Hiện popup dạng horizontal bar giữa màn hình."""
        if self._overlay_win and tk.Toplevel.winfo_exists(self._overlay_win):
            self._overlay_win.destroy()

        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)      # không có title bar
        popup.attributes('-topmost', True)
        popup.configure(bg=WIN_HIGHLIGHT)  # viền vàng 2px

        # ── Nội dung bên trong
        inner = tk.Frame(popup, bg=BG_PANEL)
        inner.pack(padx=2, pady=2)

        # Dòng kẻ ngang vàng trên cùng
        tk.Frame(inner, bg=WIN_HIGHLIGHT, height=3).pack(fill='x')

        content = tk.Frame(inner, bg=BG_PANEL)
        content.pack(fill='x', padx=30, pady=20)

        # Label kết quả
        tk.Label(content, text=label,
                 font=("Courier New", 22, "bold"),
                 fg=accent_color, bg=BG_PANEL).pack()

        tk.Label(content, text=sub,
                 font=("Courier New", 10),
                 fg=TEXT_MUTED, bg=BG_PANEL).pack(pady=(2, 14))

        # Dòng kẻ vàng giữa
        tk.Frame(content, bg=WIN_HIGHLIGHT, height=2).pack(fill='x', pady=(0, 18))

        # Nút
        btn_frame = tk.Frame(content, bg=BG_PANEL)
        btn_frame.pack()

        def _btn(parent, text, fg, cmd):
            b = tk.Button(parent, text=text,
                          font=("Courier New", 10, "bold"),
                          bg=BTN_BG, fg=fg, relief='flat',
                          activebackground=BTN_HOVER, activeforeground=fg,
                          cursor='hand2', padx=18, pady=8,
                          highlightbackground=BTN_BORDER, highlightthickness=1,
                          command=cmd)
            b.pack(side='left', padx=8)
            return b

        _btn(btn_frame, "▶  NEW GAME", X_COLOR,  lambda: self._popup_new_game(popup))
        _btn(btn_frame, "◀  REVIEW",  O_COLOR,   lambda: self._popup_review(popup))

        # Dòng kẻ ngang vàng dưới cùng
        tk.Frame(inner, bg=WIN_HIGHLIGHT, height=3).pack(fill='x')

        # ── Căn giữa popup theo cửa sổ chính
        self.root.update_idletasks()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        popup.update_idletasks()
        pw = popup.winfo_width()
        ph = popup.winfo_height()
        x  = rx + (rw - pw) // 2
        y  = ry + (rh - ph) // 2
        popup.geometry(f"+{x}+{y}")

        self._overlay_win = popup

    def _popup_new_game(self, popup):
        popup.destroy()
        self._overlay_win = None
        self._new_game()

    def _popup_review(self, popup):
        """Đóng popup, vào chế độ review."""
        popup.destroy()
        self._overlay_win = None
        if not self.move_history:
            return
        self._review_mode = True
        self._review_step = 0
        # Hiện toolbar review
        self._show_review_bar()
        self._review_draw()

    # ──────────────────────────────────────────────────── REVIEW MODE ────────
    def _show_review_bar(self):
        """Thanh điều khiển review xuất hiện ở dưới cùng."""
        self._review_bar = tk.Toplevel(self.root)
        self._review_bar.overrideredirect(True)
        self._review_bar.attributes('-topmost', True)
        self._review_bar.configure(bg=WIN_HIGHLIGHT)

        inner = tk.Frame(self._review_bar, bg=BG_PANEL)
        inner.pack(padx=2, pady=2)

        tk.Frame(inner, bg=WIN_HIGHLIGHT, height=2).pack(fill='x')

        bar = tk.Frame(inner, bg=BG_PANEL)
        bar.pack(padx=20, pady=10)

        def _btn(txt, fg, cmd):
            b = tk.Button(bar, text=txt, font=("Courier New", 10, "bold"),
                          bg=BTN_BG, fg=fg, relief='flat',
                          activebackground=BTN_HOVER, activeforeground=fg,
                          cursor='hand2', padx=14, pady=6,
                          highlightbackground=BTN_BORDER, highlightthickness=1,
                          command=cmd)
            b.pack(side='left', padx=5)
            return b

        _btn("◀◀ START", TEXT_MUTED,    lambda: self._review_goto(0))
        self._btn_prev = _btn("◀ PREV",  TEXT_PRIMARY, self._review_prev)
        self._review_counter = tk.Label(bar, text="0 / 0",
                                        font=("Courier New", 10, "bold"),
                                        fg=WIN_HIGHLIGHT, bg=BG_PANEL, width=8)
        self._review_counter.pack(side='left', padx=8)
        self._btn_next = _btn("NEXT ▶",  TEXT_PRIMARY, self._review_next)
        _btn("END ▶▶",  TEXT_MUTED,    lambda: self._review_goto(len(self.move_history)))

        tk.Frame(bar, bg=GRID_LINE, width=2).pack(side='left', fill='y', padx=10)

        _btn("✕  BACK", O_COLOR, self._review_back)

        tk.Frame(inner, bg=WIN_HIGHLIGHT, height=2).pack(fill='x')

        # Posiziona sotto il canvas
        self.root.update_idletasks()
        self._review_bar.update_idletasks()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        bw = self._review_bar.winfo_width()
        x  = rx + (rw - bw) // 2
        y  = ry + rh + 4          # ngay dưới cửa sổ chính
        self._review_bar.geometry(f"+{x}+{y}")

    def _review_draw(self):
        """Vẽ lại bàn cờ tại bước self._review_step."""
        step = self._review_step
        total = len(self.move_history)

        # Xây lại board từ đầu đến step
        board = [['.' for _ in range(self.size)] for _ in range(self.size)]
        last = None
        for i in range(step):
            r, c, p = self.move_history[i]
            board[r][c] = p
            last = (r, c)

        # Vẽ thủ công không dùng self.game.board
        self.canvas.delete("all")
        cs = CELL_SIZE
        p_ = PADDING
        sz = self.size

        for r in range(sz):
            for c in range(sz):
                x0 = p_ + c * cs + 2; y0 = p_ + r * cs + 2
                self.canvas.create_rectangle(x0, y0, x0+cs-4, y0+cs-4,
                                             fill=CELL_NORMAL, outline="")
        for i in range(sz + 1):
            x = p_ + i * cs
            self.canvas.create_line(x, p_, x, p_+sz*cs, fill=GRID_LINE, width=1)
            self.canvas.create_line(p_, x, p_+sz*cs, x, fill=GRID_LINE, width=1)

        for r in range(sz):
            for c in range(sz):
                if board[r][c] != '.':
                    self._draw_piece(r, c, board[r][c])

        # Highlight nước vừa đi
        if last:
            lr, lc = last
            col = X_COLOR if board[lr][lc] == 'X' else O_COLOR
            self.canvas.create_rectangle(
                p_+lc*cs+2, p_+lr*cs+2, p_+lc*cs+cs-2, p_+lr*cs+cs-2,
                outline=col, width=2, fill="")

        # Số thứ tự nước đi (nhỏ ở góc ô)
        for i in range(step):
            r, c, pl = self.move_history[i]
            cx = p_ + c*cs + cs - 8
            cy = p_ + r*cs + 6
            num_col = "#1C4A6E" if pl == 'X' else "#6E1C1C"
            self.canvas.create_text(cx, cy, text=str(i+1),
                                    font=("Courier New", 7), fill=num_col, anchor='ne')

        # Counter
        self._review_counter.config(text=f"{step} / {total}")

        # Cập nhật trạng thái nút
        self._btn_prev.config(state='normal' if step > 0 else 'disabled')
        self._btn_next.config(state='normal' if step < total else 'disabled')

        self._set_status(
            f"REVIEW  ·  Move {step} / {total}" if step > 0
            else "REVIEW  ·  Start position",
            WIN_HIGHLIGHT
        )

    def _review_goto(self, step):
        self._review_step = max(0, min(step, len(self.move_history)))
        self._review_draw()

    def _review_prev(self):
        if self._review_step > 0:
            self._review_step -= 1
            self._review_draw()

    def _review_next(self):
        if self._review_step < len(self.move_history):
            self._review_step += 1
            self._review_draw()

    def _review_back(self):
        """Thoát review, hiện lại popup kết quả."""
        if hasattr(self, '_review_bar') and self._review_bar.winfo_exists():
            self._review_bar.destroy()
        self._review_mode = False
        # Vẽ lại bàn cờ thật (trạng thái kết thúc)
        self._draw_board()
        # Hiện lại popup kết quả
        # Lấy lại thông tin từ scores để tái tạo popup
        hum = self.scores['human']
        ai  = self.scores['ai']
        # so với trước khi game over thì hum/ai đã +1 rồi
        last_r, last_c, _ = self.move_history[-1]
        winner_sym = self.game.board[last_r][last_c]
        if self.game.check_win(last_r, last_c, self.game.board):
            if winner_sym == self.human_player:
                color, label, sub = (X_COLOR if self.human_player=='X' else O_COLOR), "YOU WIN!", "Congratulations 🎉"
            else:
                color, label, sub = (O_COLOR if self.human_player=='X' else X_COLOR), "AI WINS", "Better luck next time"
        else:
            color, label, sub = TEXT_MUTED, "DRAW", "Well played"
        self._show_endgame_popup(label, sub, color)

    def _highlight_win(self, lx, ly, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        board = self.game.board
        for dx, dy in directions:
            cells = [(lx, ly)]
            for d in [1, -1]:
                nx, ny = lx + d * dx, ly + d * dy
                while 0 <= nx < self.size and 0 <= ny < self.size and board[nx][ny] == player:
                    cells.append((nx, ny))
                    nx += d * dx
                    ny += d * dy
            if len(cells) >= 5:
                self.win_cells = cells
                self._draw_board()
                return

    def _set_status(self, text, color=TEXT_PRIMARY):
        self.status_var.set(text)

    def _update_scores(self):
        self.score_human.config(text=str(self.scores['human']))
        self.score_ai.config(text=str(self.scores['ai']))
        self.score_d.config(text=str(self.scores['Draw']))

    # ──────────────────────────────────────────────────────── CONTROLS ───────
    def _new_game(self):
        # Đóng review bar nếu đang mở
        if hasattr(self, '_review_bar') and self._review_bar.winfo_exists():
            self._review_bar.destroy()
        self._review_mode = False
        self.game      = self.game_factory()
        self.game_over = False
        self.last_move = None
        self.win_cells = []
        self._hover_cell = None
        self.move_history = []
        self.nodes_var.set("—")
        self.time_var.set("—")
        self.thinking_var.set("")

        self.human_player = 'X'
        self.ai_player = 'O'

        self.ai.ai_player = 'O'

        self._set_status("Your turn  ›  X", TEXT_PRIMARY)

        self._draw_board()

    def _undo(self):
        if self.ai_thinking or not hasattr(self.game, 'undo_move'):
            return
        # Undo AI + human moves (2 plies)

        if (self.last_ai):
            r, c = self.last_ai.pop()
            self.game.undo_move(r, c)

        if (self.last_human):
            r, c = self.last_human.pop()
            self.game.undo_move(r, c)

        self.game_over  = False
        self.win_cells  = []
        self.last_move  = None
        self._set_status(f"Your turn  ›  {self.human_player}", TEXT_PRIMARY)
        self._draw_board()

    def _pick_side(self, sym):
        self.human_player = sym
        self.ai_player    = 'O' if sym == 'X' else 'X'
        self._highlight_side_btn(sym)
        human_color = X_COLOR if sym == 'X' else O_COLOR
        ai_color    = O_COLOR if sym == 'X' else X_COLOR
        self.label_human_sym.config(text=sym, fg=human_color)
        self.score_human.config(fg=human_color)
        self.label_ai_sym.config(text=self.ai_player, fg=ai_color)
        self.score_ai.config(fg=ai_color)
        self._new_game()

    def _highlight_side_btn(self, sym):
        for s, b in self._side_btns.items():
            if s == sym:
                b.config(bg=CELL_HOVER,
                         fg=X_COLOR if s == 'X' else O_COLOR)
            else:
                b.config(bg=CELL_NORMAL, fg=TEXT_MUTED)