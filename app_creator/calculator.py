import tkinter as tk

# 버튼 클릭 시 실행 함수
def click(value):
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(tk.END, current + str(value))

# 결과 계산
def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Error")

# 초기화
def clear():
    entry.delete(0, tk.END)

# 메인 창
root = tk.Tk()
root.title("계산기")
root.geometry("300x400")

# 입력창
entry = tk.Entry(root, font=("Arial", 20), bd=5, relief=tk.RIDGE, justify="right")
entry.pack(fill="both", ipadx=8, ipady=15, padx=10, pady=10)

# 버튼 프레임
frame = tk.Frame(root)
frame.pack()

# 버튼 목록
buttons = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['0', 'C', '=', '+']
]

# 버튼 생성
for row in buttons:
    row_frame = tk.Frame(frame)
    row_frame.pack(expand=True, fill="both")
    for btn in row:
        if btn == '=':
            action = calculate
        elif btn == 'C':
            action = clear
        else:
            action = lambda x=btn: click(x)

        b = tk.Button(row_frame, text=btn, font=("Arial", 16), command=action)
        b.pack(side="left", expand=True, fill="both")

# 실행
root.mainloop()