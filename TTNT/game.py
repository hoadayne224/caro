import tkinter as tk
from tkinter import messagebox
import math
import random
import time
import os
from typing import List, Tuple, Optional

# ================== CẤU HÌNH ==================
BOARD_SIZE  = 60     # số ô bàn cờ
CELL_SIZE   = 30     # kích thước 1 ô

SEARCH_DEPTH = 2
BEAM_WIDTH   = 8
NEAR_RADIUS  = 2

PLAYER_HUMAN = "X"
PLAYER_AI    = "O"

INF = 10**12
HISTORY_FILE = "history.txt"


class CaroGame:
    def __init__(self, root, mode="pvp"):
        self.root = root
        self.mode = mode
        self.root.title("Cờ Caro")

        # ================== MENU ==================
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chế độ", menu=game_menu)
        game_menu.add_command(label="Người vs Người", command=lambda: self.new_game("pvp"))
        game_menu.add_command(label="Người vs Máy – Dễ", command=lambda: self.new_game("easy"))
        game_menu.add_command(label="Người vs Máy – Trung bình", command=lambda: self.new_game("medium"))
        game_menu.add_command(label="Người vs Máy – Khó", command=lambda: self.new_game("hard"))
        game_menu.add_separator()
        game_menu.add_command(label="Thoát", command=self.exit_to_menu)

        # ================== NÚT & ĐỒNG HỒ ==================
        top = tk.Frame(root)
        top.pack(side=tk.TOP, pady=6)
        tk.Button(top, text="Ván mới", width=10, bg="#c8f7c5",
                  command=lambda: self.new_game(self.mode)).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Thoát", width=10, bg="#f7c5c5",
                  command=self.exit_to_menu).pack(side=tk.LEFT, padx=4)

        self.time_label = tk.Label(top, text="⏱ 00:00", font=("Arial", 12), fg="blue")
        self.time_label.pack(side=tk.LEFT, padx=20)

        # ================== BÀN CỜ ==================
        self.canvas = tk.Canvas(root,
                                width=BOARD_SIZE*CELL_SIZE,
                                height=BOARD_SIZE*CELL_SIZE,
                                bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        # ================== TRẠNG THÁI ==================
        self.board: List[List[str]] = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_HUMAN

        # Đồng hồ
        self.start_time = None
        self.timer_running = False

        self.draw_grid()
        self.start_timer()

    # ================== UI ==================
    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(BOARD_SIZE):
            x = i * CELL_SIZE
            self.canvas.create_line(x, 0, x, BOARD_SIZE*CELL_SIZE)
            self.canvas.create_line(0, x, BOARD_SIZE*CELL_SIZE, x)

    def draw_mark(self, r: int, c: int, player: str):
        x1, y1 = c*CELL_SIZE, r*CELL_SIZE
        x2, y2 = (c+1)*CELL_SIZE, (r+1)*CELL_SIZE
        color = "blue" if player == PLAYER_HUMAN else "red"
        self.canvas.create_text((x1+x2)//2, (y1+y2)//2,
                                text=player, font=("Arial", 20, "bold"), fill=color)

    def new_game(self, mode="pvp"):
        self.board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_HUMAN
        self.mode = mode
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.handle_click)

        # reset thời gian
        self.start_timer()

        # cập nhật tiêu đề
        mode_name = {
            "pvp": "Người vs Người",
            "easy": "Người vs Máy – Dễ",
            "medium": "Người vs Máy – Trung bình",
            "hard": "Người vs Máy – Khó"
        }
        self.root.title(f"Cờ Caro ({mode_name.get(self.mode, 'Chế độ ?')})")

    def disable_board(self):
        self.canvas.unbind("<Button-1>")

    # ================== TIMER ==================
    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def stop_timer(self):
        self.timer_running = False

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.time_label.config(text=f"⏱ {minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    # ================== LỊCH SỬ ==================
    def save_history(self, result: str):
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"Kết quả: {result} | Chế độ: {self.mode} | Thời gian: {elapsed}s\n")

    # ================== XỬ LÝ CLICK ==================
    def handle_click(self, event):
        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE
        if not self.in_bounds(r, c) or self.board[r][c] != "" or self.game_over():
            return

        self.place(r, c, self.current_player)
        self.draw_mark(r, c, self.current_player)

        if self.check_win(r, c):
            messagebox.showinfo("Kết quả", f"🎉 Người chơi {self.current_player} thắng!")
            self.save_history(f"Người chơi {self.current_player} thắng")
            self.disable_board()
            self.stop_timer()
            return

        if self.mode == "pvp":
            self.current_player = PLAYER_AI if self.current_player == PLAYER_HUMAN else PLAYER_HUMAN
        else:
            self.current_player = PLAYER_AI
            self.root.after(200, self.ai_move)

    # ================== LOGIC CỜ ==================
    @staticmethod
    def in_bounds(r, c) -> bool:
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def place(self, r, c, player):
        self.board[r][c] = player

    def undo(self, r, c):
        self.board[r][c] = ""

    def opponent(self, player: str) -> str:
        return PLAYER_AI if player == PLAYER_HUMAN else PLAYER_HUMAN

    def game_over(self) -> bool:
        return all(self.board[r][c] != "" for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

    def check_win(self, r: int, c: int) -> bool:
        player = self.board[r][c]
        if not player:
            return False
        for dr, dc in [(1,0), (0,1), (1,1), (1,-1)]:
            cnt = 1
            rr, cc = r+dr, c+dc
            while self.in_bounds(rr, cc) and self.board[rr][cc] == player:
                cnt += 1; rr += dr; cc += dc
            rr, cc = r-dr, c-dc
            while self.in_bounds(rr, cc) and self.board[rr][cc] == player:
                cnt += 1; rr -= dr; cc -= dc
            if cnt >= 5:
                return True
        return False

    # ================== AI ==================
    def ai_move(self):
        if self.mode == "easy":
            self.ai_easy()
        elif self.mode == "medium":
            self.ai_medium()
        elif self.mode == "hard":
            self.ai_best_first()

    def ai_easy(self):
        # 1. Nước thắng ngay cho AI → đánh luôn
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == "":
                    self.place(r, c, PLAYER_AI)
                    if self.check_win(r, c):
                        self.draw_mark(r, c, PLAYER_AI)
                        messagebox.showinfo("Kết quả", "🤖 Máy thắng!")
                        self.disable_board()
                        self.stop_timer()
                        return
                    self.undo(r, c)

        # 2. Chặn thắng ngay cho người chơi
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == "":
                    self.place(r, c, PLAYER_HUMAN)
                    if self.check_win(r, c):
                        self.undo(r, c)
                        self.place(r, c, PLAYER_AI)
                        self.draw_mark(r, c, PLAYER_AI)
                        self.current_player = PLAYER_HUMAN
                        return
                    self.undo(r, c)

        # 3. Ưu tiên đánh gần quân người chơi (đu bám)
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == "":
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            rr, cc = r+dr, c+dc
                            if self.in_bounds(rr, cc) and self.board[rr][cc] == PLAYER_HUMAN:
                                moves.append((r, c))
                                break
        if moves:
            r, c = random.choice(moves)
        else:
            # 4. fallback random
            empties = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board[r][c] == ""]
            r, c = random.choice(empties)

        # Đặt cờ
        self.place(r, c, PLAYER_AI)
        self.draw_mark(r, c, PLAYER_AI)
        if self.check_win(r, c):
            messagebox.showinfo("Kết quả", "🤖 Máy thắng!")
            self.disable_board()
            self.stop_timer()
        else:
            self.current_player = PLAYER_HUMAN

    def ai_medium(self):
        best_score = -1
        best_move = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == "":
                    score = self.evaluate_move(r, c)
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        if best_move:
            r,c = best_move
            self.place(r,c,PLAYER_AI)
            self.draw_mark(r,c,PLAYER_AI)
            if self.check_win(r,c):
                messagebox.showinfo("Kết quả", "🤖 Máy thắng!")
                self.save_history("🤖 Máy thắng")
                self.disable_board()
                self.stop_timer()
                return
        self.current_player = PLAYER_HUMAN

    def ai_best_first(self):
        r,c = self.find_best_move_best_first()
        if r is None:
            self.ai_easy()
            return
        self.place(r,c,PLAYER_AI)
        self.draw_mark(r,c,PLAYER_AI)
        if self.check_win(r,c):
            messagebox.showinfo("Kết quả", "🤖 Máy thắng!")
            self.save_history("🤖 Máy thắng")
            self.disable_board()
            self.stop_timer()
            return
        self.current_player = PLAYER_HUMAN

    def evaluate_move(self, r, c) -> int:
        score = 0
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr==0 and dc==0: continue
                rr,cc = r+dr, c+dc
                if self.in_bounds(rr,cc) and self.board[rr][cc] != "":
                    score += 1
        return score

    # ================== BEST FIRST SEARCH ==================
    def find_best_move_best_first(self) -> Tuple[Optional[int], Optional[int]]:
        moves = self.generate_moves()
        if not moves:
            center = BOARD_SIZE // 2
            return center, center
        scored = []
        for (r, c) in moves:
            self.place(r, c, PLAYER_AI)
            if self.check_win(r, c):
                self.undo(r, c)
                return r, c
            val = self.evaluate_board(PLAYER_AI)
            scored.append((val, (r, c)))
            self.undo(r, c)
        scored.sort(reverse=True)
        scored = scored[:BEAM_WIDTH]
        best_val = -INF
        best_move = None
        for _, (r, c) in scored:
            self.place(r, c, PLAYER_AI)
            val = self.minimax_beam(depth=SEARCH_DEPTH-1,
                                    player=self.opponent(PLAYER_AI),
                                    alpha=-INF, beta=INF)
            self.undo(r, c)
            if val > best_val:
                best_val = val
                best_move = (r, c)
        return best_move if best_move else (None, None)

    def minimax_beam(self, depth: int, player: str, alpha: float, beta: float) -> float:
        if depth == 0:
            return self.evaluate_board(PLAYER_AI)
        moves = self.generate_moves()
        if not moves:
            return self.evaluate_board(PLAYER_AI)
        scored = []
        for (r, c) in moves:
            self.place(r, c, player)
            val = None
            if self.check_immediate(r, c, player):
                val = INF if player == PLAYER_AI else -INF
            else:
                val = self.evaluate_board(PLAYER_AI)
            scored.append((val, (r, c)))
            self.undo(r, c)
        scored.sort(reverse=(player == PLAYER_AI))
        scored = scored[:BEAM_WIDTH]
        if player == PLAYER_AI:
            value = -INF
            for _, (r, c) in scored:
                self.place(r, c, player)
                if self.check_immediate(r, c, player):
                    child_val = INF
                else:
                    child_val = self.minimax_beam(depth-1, self.opponent(player), alpha, beta)
                self.undo(r, c)
                value = max(value, child_val)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = INF
            for _, (r, c) in scored:
                self.place(r, c, player)
                if self.check_immediate(r, c, player):
                    child_val = -INF
                else:
                    child_val = self.minimax_beam(depth-1, self.opponent(player), alpha, beta)
                self.undo(r, c)
                value = min(value, child_val)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def check_immediate(self, r: int, c: int, player: str) -> bool:
        return self.check_win(r, c)

    def generate_moves(self) -> List[Tuple[int, int]]:
        occupied = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board[r][c] != ""]
        if not occupied:
            return [(BOARD_SIZE//2, BOARD_SIZE//2)]
        cand = set()
        for (r, c) in occupied:
            for dr in range(-NEAR_RADIUS, NEAR_RADIUS+1):
                for dc in range(-NEAR_RADIUS, NEAR_RADIUS+1):
                    rr, cc = r+dr, c+dc
                    if self.in_bounds(rr, cc) and self.board[rr][cc] == "":
                        cand.add((rr, cc))
        return list(cand) if cand else [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board[r][c] == ""]

    # ================== ĐÁNH GIÁ ==================
    def evaluate_board(self, perspective: str) -> int:
        return self.score_side(perspective) - self.score_side(self.opponent(perspective))

    def score_side(self, player: str) -> int:
        score = 0
        dirs = [(1,0), (0,1), (1,1), (1,-1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != player:
                    continue
                for dr, dc in dirs:
                    pr, pc = r - dr, c - dc
                    if self.in_bounds(pr, pc) and self.board[pr][pc] == player:
                        continue
                    length, open_ends = self.count_run_and_open(r, c, dr, dc, player)
                    if length >= 5:
                        score += 1000000000
                    elif length == 4:
                        if open_ends == 2: score += 100000
                        elif open_ends == 1: score += 12000
                    elif length == 3:
                        if open_ends == 2: score += 2000
                        elif open_ends == 1: score += 300
                    elif length == 2:
                        if open_ends == 2: score += 120
                        elif open_ends == 1: score += 20
                    elif length == 1:
                        if open_ends == 2: score += 2
                        elif open_ends == 1: score += 1
        return score

    def count_run_and_open(self, r: int, c: int, dr: int, dc: int, player: str) -> Tuple[int, int]:
        length = 0
        rr, cc = r, c
        while self.in_bounds(rr, cc) and self.board[rr][cc] == player:
            length += 1
            rr += dr; cc += dc
        open1 = 1 if (self.in_bounds(rr, cc) and self.board[rr][cc] == "") else 0
        rr2, cc2 = r - dr, c - dc
        while self.in_bounds(rr2, cc2) and self.board[rr2][cc2] == player:
            length += 1
            rr2 -= dr; cc2 -= dc
        open2 = 1 if (self.in_bounds(rr2, cc2) and self.board[rr2][cc2] == "") else 0
        return length, (open1 + open2)

    # ================== THOÁT VỀ MENU ==================
    def exit_to_menu(self):
        self.root.destroy()
        import menu
        new_root = tk.Tk()
        menu.MenuApp(new_root)
        new_root.mainloop()


# ================== CHẠY ==================
if __name__ == "__main__":
    root = tk.Tk()
    app = CaroGame(root)
    root.mainloop()
