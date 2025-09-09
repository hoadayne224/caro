import tkinter as tk
from tkinter import ttk
from game import CaroGame
import os

HISTORY_FILE = "history.txt"

class MenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Caro - Menu")
        self.root.geometry("400x350")

        tk.Label(root, text="CỜ CARO", font=("Arial", 20, "bold")).pack(pady=20)

        tk.Button(root, text="Người vs Người", width=20, height=2,
                  command=lambda: self.start_game("pvp")).pack(pady=10)

        tk.Button(root, text="Người vs Máy (Dễ)", width=20, height=2,
                  command=lambda: self.start_game("easy")).pack(pady=5)

        tk.Button(root, text="Người vs Máy (Trung bình)", width=20, height=2,
                  command=lambda: self.start_game("medium")).pack(pady=5)

        tk.Button(root, text="Người vs Máy (Khó)", width=20, height=2,
                  command=lambda: self.start_game("hard")).pack(pady=5)

        # 👉 Nút xem lịch sử
        tk.Button(root, text="Lịch sử trò chơi", width=20, height=2,
                  command=self.show_history).pack(pady=10)

        tk.Button(root, text="Thoát", width=20, height=2,
                  command=root.quit).pack(pady=10)

    def start_game(self, mode):
        self.root.destroy()
        game_root = tk.Tk()
        game_app = CaroGame(game_root, mode=mode)   # tạo instance
        game_root.mainloop()

    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("Lịch sử trò chơi")
        win.geometry("600x400")

        cols = ("Kết quả", "Chế độ", "Thời gian (s)")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.pack(expand=True, fill=tk.BOTH)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=180)

        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                tree.insert("", "end", values=("Chưa có lịch sử", "-", "-"))
            else:
                for line in lines:
                    # Ví dụ: "Kết quả: Người thắng | Chế độ: easy | Thời gian: 35s"
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        result = parts[0].replace("Kết quả:", "").strip()
                        mode   = parts[1].replace("Chế độ:", "").strip()
                        time   = parts[2].replace("Thời gian:", "").strip()
                        tree.insert("", "end", values=(result, mode, time))
        else:
            tree.insert("", "end", values=("Chưa có lịch sử", "-", "-"))

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuApp(root)
    root.mainloop()
