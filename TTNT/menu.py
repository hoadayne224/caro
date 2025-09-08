import tkinter as tk
from game import CaroGame

class MenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Caro - Menu")
        self.root.geometry("400x300")

        tk.Label(root, text="CỜ CARO", font=("Arial", 20, "bold")).pack(pady=20)

        tk.Button(root, text="Người vs Người", width=20, height=2,
                  command=lambda: self.start_game("pvp")).pack(pady=10)

        tk.Button(root, text="Người vs Máy (Dễ)", width=20, height=2,
                  command=lambda: self.start_game("easy")).pack(pady=5)

        tk.Button(root, text="Người vs Máy (Trung bình)", width=20, height=2,
                  command=lambda: self.start_game("medium")).pack(pady=5)

        tk.Button(root, text="Người vs Máy (Khó)", width=20, height=2,
                  command=lambda: self.start_game("hard")).pack(pady=5)

        tk.Button(root, text="Thoát", width=20, height=2,
                  command=root.quit).pack(pady=20)

    def start_game(self, mode):
        self.root.destroy()
        game_root = tk.Tk()
        CaroGame(game_root, mode=mode)
        game_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuApp(root)
    root.mainloop()
