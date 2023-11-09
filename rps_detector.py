import cv2
import numpy as np

def gesture(frame):

    frame = cv2.resize(frame, None, fx=0.4,fy=0.4)
    frame: np.ndarray

    rn = cv2.blur(frame, (5, 5))
    # cv2.imshow("1. blur", rn)

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
    cv2.drawContours(frame, [contours], -1, (0, 0, 0), 2)

    # 볼록 껍질, 볼록성 결함 검출.
    hull = cv2.convexHull(contours)
    cv2.drawContours(frame, [hull], -1, (0, 0, 255), 2)
    hull = cv2.convexHull(contours, returnPoints=False)
    defects = cv2.convexityDefects(contours, hull)

    acutes = 0
    for i in range(defects.shape[0]):
        # start, end, far, distance
        s, e, f, d = defects[i][0]
        start = tuple(contours[s][0])
        end = tuple(contours[e][0])
        far = tuple(contours[f][0])

        #   a:s--e  b:s--f  c:e--f
        a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        
        angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
        
        #예각 판별
        if angle <= np.pi / 2:
            acutes += 1
            cv2.circle(frame, start, 4, [255, 0, 0], -1)

    fingers = acutes + 1 if acutes > 0 else acutes

    if not fingers:
        motion = "rock"
    elif fingers == 2:
        motion = "scissors"
    elif fingers == 5:
        motion = "paper"
    else:
        motion = None

    return frame, motion


# 카메라
cap = cv2.VideoCapture(0)

# 배경 제거
# fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)  # 배경 빼냄
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("카메라를 열 수 없음.")
        break

    frameOrig = frame

    #배경 제거
    # frame_mask = fgbg.apply(frame)
    # morphed = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, kernel)
    #MORPH_OPEN 침식 - 팽창
    #MORPH_CLOSE 팽창 - 침식

    #try except
    frame, shape = gesture(frame)
    org = (50, 100)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, shape, org, font, 1, (0, 255, 0), 2)

    frame = cv2.resize(frame, None, fx=3.0, fy=3.0)
    cv2.imshow("RPS", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.destroyAllWindows()
cap.release()