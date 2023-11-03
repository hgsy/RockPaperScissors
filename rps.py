import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

width, height = 800, 600

root = tk.Tk()
root.title("RPS Machine")
root.geometry(f'{width}x{height}')
root.resizable(False, False)

camera_label = tk.Label(root)
camera_label.pack(side="left")
result_label = tk.Label(root)
result_label.pack(side="right")


def gesture(frame):
    # frame = cv2.resize(frame, (720, 480))
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
    frame: np.ndarray

    rn = cv2.blur(frame, (5, 5))
    # cv.imshow("1. blur", rn)

    hsv = cv2.cvtColor(rn, cv2.COLOR_BGR2HSV)

    # 피부색 범위 정의
    lower = np.array([0, 48, 80], dtype="uint8")
    upper = np.array([20, 255, 255], dtype="uint8")
    skin_region = cv2.inRange(hsv, lower, upper)

    blurred = cv2.medianBlur(skin_region, 5)
    # cv2.imshow("2. medianBlur", blurred)

    # 윤곽선 검출
    contours, hierarchy = cv2.findContours(blurred, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = max(contours, key=lambda x: cv2.contourArea(x))
    cv2.drawContours(frame, [contours], -1, (0, 255, 0), 2)

    # 볼록 껍질, 볼록성 결함 검출.
    hull = cv2.convexHull(contours)
    cv2.drawContours(frame, [hull], -1, (0, 0, 0), 2)
    hull = cv2.convexHull(contours, returnPoints=False)
    defects = cv2.convexityDefects(contours, hull)

    acutes = 0
    for i in range(defects.shape[0]):
        # start, end, far, distance
        s, e, f, d = defects[i][0]
        start = tuple(contours[s][0])
        end = tuple(contours[e][0])
        far = tuple(contours[f][0])

        # a:s--e b:s--f c:e--f
        a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        
        #예각 판별
        angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
        if angle <= np.pi / 2:
            acutes += 1
            # cv2.circle(frame, start, 4, [0, 0, 255], -1)

    fingers = acutes + 1 if acutes > 0 else acutes

    if not fingers:
        motion = "paper"
    elif fingers == 2:
        motion = "rock"
    elif fingers == 5:
        motion = "scissors"
    else:
        motion = None

    return frame, motion


# 카메라
cap = cv2.VideoCapture(0)


# GUI 업데이트
def update():
    ret, frame = cap.read()
    if not ret:
        print("카메라를 열 수 없음.")
        return

    frame_orig = frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (400, height))
    frame = Image.fromarray(frame)
    frame = ImageTk.PhotoImage(frame)

    live_frame, result = gesture(frame_orig)

    # live_frame = cv2.resize(live_frame, (400, height))
    # live_frame = Image.fromarray(live_frame)
    # live_frame = ImageTk.PhotoImage(live_frame)
    #
    # camera_label.configure(image=live_frame)
    # camera_label.image = live_frame

    camera_label.configure(image=frame)
    camera_label.image = frame


    if result != None:
        result_image = Image.open(f"image/{result}.png")
        result_image = ImageTk.PhotoImage(result_image)
        result_label.configure(image=result_image)
        result_label.image = result_image

    # GUI 업데이트 주기
    root.after(100, update)


# 초기 실행
update()
root.mainloop()

cap.release()