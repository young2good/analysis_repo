import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import json
import os

root = tk.Tk()
root.title("출석부")
root.geometry("400x500")

# 축구선수 리스트
players = [
    "Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé",
    "Erling Haaland", "Neymar Jr", "Kevin De Bruyne",
    "Mohamed Salah", "Harry Kane", "Vinícius Jr", "Jude Bellingham", "Son"
]

# --------------------------
# 1페이지 (선택 화면)
# --------------------------
frame_select = tk.Frame(root)
frame_select.pack(fill="both", expand=True)

check_vars = []

tk.Label(frame_select, text="경기 날짜 선택", font=("Arial", 12)).pack(pady=5)

date_entry = DateEntry(
    frame_select,
    width=12,
    background='darkblue',
    foreground='white',
    borderwidth=2,
    date_pattern='yyyy-mm-dd'
)

date_entry.pack(pady=5)

tk.Label(frame_select, text="참석한 선수 선택", font=("Arial", 14)).pack(pady=10)

for player in players:
    var = tk.BooleanVar()
    tk.Checkbutton(frame_select, text=player, variable=var).pack(anchor="w")
    check_vars.append((player, var))


# --------------------------
# 평가 페이지 생성 함수
# --------------------------
frame_rate = None
rating_vars = {}

def create_rate_page(selected_players):
    global frame_rate, rating_vars

    frame_rate = tk.Frame(root)
    rating_vars = {}

    tk.Label(frame_rate, text="선수 평가 (1~5점)", font=("Arial", 14)).pack(pady=10)

    for player in selected_players:
        row = tk.Frame(frame_rate)
        row.pack(anchor="w", pady=5)

        tk.Label(row, text=player, width=18).pack(side="left")

        var = tk.StringVar()
        rating_vars[player] = var

        combo = ttk.Combobox(row, textvariable=var, values=[1, 2, 3, 4, 5], width=5)
        combo.pack(side="left")
        combo.set("3")

    tk.Button(frame_rate, text="제출", command=submit).pack(pady=20)


# --------------------------
# 2페이지 이동
# --------------------------
def go_to_rate():
    selected = [p for p, var in check_vars if var.get()]

    if not selected:
        messagebox.showwarning("경고", "최소 1명 선택하세요")
        return

    frame_select.pack_forget()

    create_rate_page(selected)
    frame_rate.pack(fill="both", expand=True)


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

    # 오늘 날짜 파일명
    selected_date = date_entry.get()


    # 현재 py파일 기준 경로
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # data 폴더 경로
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # data 폴더 생성
    os.makedirs(DATA_DIR, exist_ok=True)

    # 파일 경로
    file_name = os.path.join(DATA_DIR, f"{selected_date}.json")

    # JSON 저장
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    messagebox.showinfo(
        "결과 저장 완료",
        f"{file_name} 저장 완료"
    )

    # 2페이지 종료
    frame_rate.pack_forget()

    # 체크 초기화
    for _, var in check_vars:
        var.set(False)

    # 1페이지 복귀
    frame_select.pack(fill="both", expand=True)


# --------------------------
# 버튼
# --------------------------
tk.Button(frame_select, text="다음", command=go_to_rate).pack(pady=10)

# 실행
root.mainloop()

print(file_name)