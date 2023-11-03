import tkinter as tk

root = tk.Tk()
root.geometry("800x600")

camera_label = tk.Label(root)   #left
camera_label.pack(side="left")
result_label = tk.Label(root)   #right
result_label.pack(side="right")

# GUI
def update():

    #GUI 업데이트 주기
    root.after(100, update)

# 초기 실행
update()
root.mainloop()