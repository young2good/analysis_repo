import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

root = tk.Tk()
root.title("축구선수 평가 프로그램")
root.geometry("400x500")

# 축구선수 리스트
players = [
    "Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé",
    "Erling Haaland", "Neymar Jr", "Kevin De Bruyne",
    "Mohamed Salah", "Harry Kane", "Vinícius Jr", "Jude Bellingham", "Son"
]

# --------------------------
# 1페이지: 선택 화면
# --------------------------
frame_select = tk.Frame(root)
frame_select.pack(fill="both", expand=True)

check_vars = []

tk.Label(frame_select, text="평가할 선수 선택", font=("Arial", 14)).pack(pady=10)

for player in players:
    var = tk.BooleanVar()
    tk.Checkbutton(frame_select, text=player, variable=var).pack(anchor="w")
    check_vars.append((player, var))

# --------------------------
# 2페이지: 평가 화면
# --------------------------
frame_rate = tk.Frame(root)

rating_vars = {}

def go_to_rate():
    selected = [p for p, var in check_vars if var.get()]
    
    if not selected:
        messagebox.showwarning("경고", "최소 1명 선택하세요")
        return
    
    # 화면 전환
    frame_select.pack_forget()
    frame_rate.pack(fill="both", expand=True)

    tk.Label(frame_rate, text="선수 평가 (1~5점)", font=("Arial", 14)).pack(pady=10)

    for player in selected:
        frame = tk.Frame(frame_rate)
        frame.pack(anchor="w", pady=5)

        tk.Label(frame, text=player, width=18).pack(side="left")

        var = tk.StringVar()
        rating_vars[player] = var

        combo = ttk.Combobox(frame, textvariable=var, values=[1, 2, 3, 4, 5], width=5)
        combo.pack(side="left")
        combo.set("선택")

# --------------------------
# 제출
# --------------------------
def submit():
    results = {}

    for player, var in rating_vars.items():
        value = var.get()
        if value not in ["1", "2", "3", "4", "5"]:
            messagebox.showwarning("경고", f"{player} 점수 선택 안됨")
            return
        results[player] = int(value)

    result_text = "\n".join([f"{p}: {s}점" for p, s in results.items()])
    messagebox.showinfo("결과", result_text)

# 버튼
tk.Button(frame_select, text="다음", command=go_to_rate).pack(pady=10)
tk.Button(frame_rate, text="제출", command=submit).pack(pady=20)

root.mainloop()