import cv2
import numpy as np

# 1. 스탬프 이미지 로드 함수
def load_stamp_image(file_path, stamp_size=50):
    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if img.shape[2] == 3:
        b, g, r = cv2.split(img)
        alpha = np.where((b > 220) & (g > 220) & (r > 220), 0, 255).astype(np.uint8)
        img = cv2.merge([b, g, r, alpha])
    return cv2.resize(img, (stamp_size, stamp_size))

dog_img = load_stamp_image('dog.jpg', stamp_size=55)
cat_img = load_stamp_image('cat.jpg', stamp_size=55)

# 2. 카메라 및 추적 설정
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
lower_color = np.array([95, 100, 100])
upper_color = np.array([135, 255, 255])

# 3. 상태 변수
canvas = None
line_prev_point = None
stamp_prev_point = None
eraser_prev_point = None
min_stamp_distance = 45

# 모드 목록에 Eraser 추가
modes = ["Meme Dog Stamp", "Cat Stamp", "Color Line", "Eraser"]
mode_index = 0

pen_colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255)]
color_names = ["Red", "Green", "Blue", "Yellow", "Purple"]
color_index = 0

print("=== Air Canvas Master ===")
print("M 키: 모드 변경 | E 키: 지우개 모드")
print("P 키: 선 색상 변경 | C 키: 전체 초기화 | ESC: 종료")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros_like(frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 10:
            M = cv2.moments(c)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                # 지우개 모드일 때는 포인터 크기를 40px 영역에 맞춰 크게 표시
                pointer_size = 20 if modes[mode_index] == "Eraser" else 6
                pointer_color = (0, 0, 0) if modes[mode_index] == "Eraser" else (255, 255, 0)
                cv2.circle(frame, center, pointer_size, pointer_color, 2)

    current_mode = modes[mode_index]

    if center is not None:
        # A. 스탬프 모드 (Dog / Cat)
        if current_mode in ["Meme Dog Stamp", "Cat Stamp"]:
            target_stamp = dog_img if current_mode == "Meme Dog Stamp" else cat_img
            if target_stamp is not None:
                draw_flag = False
                if stamp_prev_point is None:
                    draw_flag = True
                else:
                    dist = np.linalg.norm(np.array(center) - np.array(stamp_prev_point))
                    if dist > min_stamp_distance:
                        draw_flag = True

                if draw_flag:
                    cx, cy = center
                    s_size = target_stamp.shape[0]
                    half_s = s_size // 2
                    y1, y2 = max(0, cy - half_s), min(h, cy + half_s)
                    x1, x2 = max(0, cx - half_s), min(w, cx + half_s)
                    st_y1, st_y2 = half_s - (cy - y1), half_s + (y2 - cy)
                    st_x1, st_x2 = half_s - (cx - x1), half_s + (x2 - cx)

                    if (y2 > y1) and (x2 > x1):
                        overlay = target_stamp[st_y1:st_y2, st_x1:st_x2]
                        alpha_mask = overlay[:, :, 3] / 255.0
                        for c in range(0, 3):
                            canvas[y1:y2, x1:x2, c] = (
                                alpha_mask * overlay[:, :, c] + (1.0 - alpha_mask) * canvas[y1:y2, x1:x2, c]
                            )
                        stamp_prev_point = center
            line_prev_point = None
            eraser_prev_point = None

        # B. 선 그리기 모드
        elif current_mode == "Color Line":
            if line_prev_point is not None:
                if np.linalg.norm(np.array(center) - np.array(line_prev_point)) < 100:
                    cv2.line(canvas, line_prev_point, center, pen_colors[color_index], 5)
            line_prev_point = center
            stamp_prev_point = None
            eraser_prev_point = None

        # C. 지우개 모드 (40px 두께로 캔버스를 검은색(0)으로 지움)
        elif current_mode == "Eraser":
            if eraser_prev_point is not None:
                if np.linalg.norm(np.array(center) - np.array(eraser_prev_point)) < 100:
                    cv2.line(canvas, eraser_prev_point, center, (0, 0, 0), 40)
            else:
                cv2.circle(canvas, center, 20, (0, 0, 0), -1)  # 첫 터치 시 40px 원 형태로 삭제
            eraser_prev_point = center
            line_prev_point = None
            stamp_prev_point = None
    else:
        line_prev_point = None
        eraser_prev_point = None

    # 화면 합성
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask_inv = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY_INV)
    frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    result = cv2.add(frame_bg, canvas)

    # UI 상단 정보
    cv2.rectangle(result, (10, 10), (380, 60), (0, 0, 0), -1)
    ui_text = f"Mode: {current_mode}"
    if current_mode == "Color Line":
        ui_text += f" ({color_names[color_index]})"

    cv2.putText(result, ui_text, (20, 42), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Air Canvas Master", result)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif key == ord('m') or key == ord('M'):
        mode_index = (mode_index + 1) % len(modes)
        line_prev_point = stamp_prev_point = eraser_prev_point = None
        print(f"[System] 모드 변경: {modes[mode_index]}")
    elif key == ord('e') or key == ord('E'):
        mode_index = modes.index("Eraser")
        line_prev_point = stamp_prev_point = eraser_prev_point = None
        print("[System] 지우개 모드 전환 (40px)")
    elif key == ord('p') or key == ord('P'):
        color_index = (color_index + 1) % len(pen_colors)
        print(f"[System] 선 색상 변경: {color_names[color_index]}")
    elif key == ord('c') or key == ord('C'):
        canvas = np.zeros_like(frame)
        print("[System] 캔버스 초기화")

cap.release()
cv2.destroyAllWindows()