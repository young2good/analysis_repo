import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk

import json
import os

# ==========================
# 기본 설정
# ==========================
root = tk.Tk()
root.title("출석부")
root.geometry("700x850")

# 선수 목록
players = [
    "Lionel Messi",
    "Cristiano Ronaldo",
    "Kylian Mbappé",
    "Erling Haaland",
    "Neymar Jr",
    "Kevin De Bruyne",
    "Mohamed Salah",
    "Harry Kane",
    "Vinícius Jr",
    "Jude Bellingham",
    "Son",
    "JaeYoon"
]

# ==========================
# 현재 파일 기준 경로
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ==========================
# 1페이지
# ==========================
frame_select = tk.Frame(root)
frame_select.pack(fill="both", expand=True)

check_vars = []

# 날짜
tk.Label(
    frame_select,
    text="경기 날짜 선택",
    font=("Arial", 12)
).pack(pady=5)

date_entry = DateEntry(
    frame_select,
    width=15,
    background="darkblue",
    foreground="white",
    borderwidth=2,
    date_pattern="yyyy-mm-dd"
)

date_entry.pack(pady=5)

# 시간
tk.Label(
    frame_select,
    text="경기 시간",
    font=("Arial", 12)
).pack(pady=5)

time_entry = tk.Entry(frame_select, width=20)
time_entry.pack(pady=5)
time_entry.insert(0, "19:00")

# 상대팀
tk.Label(
    frame_select,
    text="상대팀",
    font=("Arial", 12)
).pack(pady=5)

opponent_entry = tk.Entry(frame_select, width=30)
opponent_entry.pack(pady=5)

# 장소
tk.Label(
    frame_select,
    text="경기 장소",
    font=("Arial", 12)
).pack(pady=5)

location_entry = tk.Entry(frame_select, width=30)
location_entry.pack(pady=5)

# 선수 선택
tk.Label(
    frame_select,
    text="참석한 선수 선택",
    font=("Arial", 14)
).pack(pady=10)

for player in players:

    var = tk.BooleanVar()

    tk.Checkbutton(
        frame_select,
        text=player,
        variable=var
    ).pack(anchor="w")

    check_vars.append((player, var))

# ==========================
# 2페이지 변수
# ==========================
frame_rate = None
rating_vars = {}

# ==========================
# 포지션 페이지 생성
# ==========================
def create_rate_page(selected_players):

    global frame_rate
    global rating_vars

    frame_rate = tk.Frame(root)
    rating_vars = {}

    # ----------------------
    # 제목
    # ----------------------
    tk.Label(
        frame_rate,
        text="선수 포지션 선택",
        font=("Arial", 16)
    ).pack(pady=10)

    # ----------------------
    # 포메이션 이미지
    # ----------------------
    image_path = os.path.join(BASE_DIR, "formation.png")

    if os.path.exists(image_path):

        image = Image.open(image_path)
        image = image.resize((320, 250))


        photo = ImageTk.PhotoImage(image)

        image_label = tk.Label(
            frame_rate,
            image=photo
        )

        image_label.image = photo
        image_label.pack(pady=10)

    # ----------------------
    # 스크롤 컨테이너
    # ----------------------
    list_container = tk.Frame(frame_rate)
    list_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(list_container)

    scrollbar = ttk.Scrollbar(
        list_container,
        orient="vertical",
        command=canvas.yview
    )

    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window(
        (0, 0),
        window=scrollable_frame,
        anchor="nw"
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # ----------------------
    # 선수 목록
    # ----------------------
    for player in selected_players:

        row = tk.Frame(scrollable_frame)
        row.pack(fill="x", pady=5, padx=10)

        # 선수 이름
        tk.Label(
            row,
            text=player,
            width=18,
            anchor="w"
        ).pack(side="left")

        # 1Q
        tk.Label(
            row,
            text="1Q"
        ).pack(side="left")

        quarter1_var = tk.StringVar(value="MF")

        quarter1_combo = ttk.Combobox(
            row,
            textvariable=quarter1_var,
            values=["FW", "MF", "DF", "GK", "Sub"],
            width=6,
            state="readonly"
        )

        quarter1_combo.pack(side="left", padx=5)

        # 2Q
        tk.Label(
            row,
            text="2Q"
        ).pack(side="left")

        quarter2_var = tk.StringVar(value="Sub")

        quarter2_combo = ttk.Combobox(
            row,
            textvariable=quarter2_var,
            values=["FW", "MF", "DF", "GK", "Sub"],
            width=6,
            state="readonly"
        )

        quarter2_combo.pack(side="left", padx=5)

        # 저장
        rating_vars[player] = {
            "quarter_1": quarter1_var,
            "quarter_2": quarter2_var
        }

    # ----------------------
    # 제출 버튼
    # ----------------------
    tk.Button(
        frame_rate,
        text="제출",
        command=submit,
        height=2,
        bg="#4CAF50",
        fg="white"
    ).pack(
        fill="x",
        pady=10,
        padx=10
    )

# ==========================
# 페이지 이동
# ==========================
def go_to_rate():

    selected = [
        p for p, var in check_vars
        if var.get()
    ]

    if not selected:
        messagebox.showwarning(
            "경고",
            "최소 1명 선택하세요"
        )
        return

    frame_select.pack_forget()

    create_rate_page(selected)

    frame_rate.pack(
        fill="both",
        expand=True
    )

# ==========================
# 제출
# ==========================
def submit():

    results = {}

    for player, positions in rating_vars.items():

        results[player] = {
            "quarter_1": positions["quarter_1"].get(),
            "quarter_2": positions["quarter_2"].get()
        }

    # 경기 정보
    selected_date = date_entry.get()
    match_time = time_entry.get()
    opponent = opponent_entry.get()
    location = location_entry.get()

    # 최종 JSON
    final_data = {
        "match_info": {
            "date": selected_date,
            "time": match_time,
            "opponent": opponent,
            "location": location
        },
        "players": results
    }

    # 파일명
    safe_opponent = opponent.replace(" ", "_")

    file_name = os.path.join(
        DATA_DIR,
        f"{selected_date}_{safe_opponent}.json"
    )

    # 저장
    with open(file_name, "w", encoding="utf-8") as f:

        json.dump(
            final_data,
            f,
            ensure_ascii=False,
            indent=4
        )

    messagebox.showinfo(
        "저장 완료",
        f"{file_name} 저장 완료"
    )

    # 초기화
    frame_rate.pack_forget()

    for _, var in check_vars:
        var.set(False)

    frame_select.pack(
        fill="both",
        expand=True
    )

# ==========================
# 다음 버튼
# ==========================
tk.Button(
    frame_select,
    text="다음",
    command=go_to_rate
).pack(pady=10)

# ==========================
# 실행
# ==========================
root.mainloop()