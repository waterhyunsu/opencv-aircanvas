import cv2
import numpy as np

# ---------------------------------------------------------
# 1. 스탬프 이미지 로드 및 배경 투명화 함수
# ---------------------------------------------------------
def load_stamp_image(file_path, stamp_size=50):
    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    
    # 채널 확인 및 투명화 처리
    if img.shape[2] == 3:  # JPG 등 알파 채널이 없는 경우 (흰색 배경 투명화)
        b, g, r = cv2.split(img)
        alpha = np.where((b > 220) & (g > 220) & (r > 220), 0, 255).astype(np.uint8)
        img = cv2.merge([b, g, r, alpha])
    
    return cv2.resize(img, (stamp_size, stamp_size))

# 이미지 로드 (없을 경우 예외 처리)
dog_img = load_stamp_image('dog.jpg', stamp_size=55)
cat_img = load_stamp_image('cat.jpg', stamp_size=55)

if dog_img is None:
    print("[경고] 'dog.jpg' 파일을 찾을 수 없습니다. 강아지 모드가 건너뛰어질 수 있습니다.")
if cat_img is None:
    print("[경고] 'cat.jpg' 파일을 찾을 수 없습니다. 고양이 모드가 건너뛰어질 수 있습니다.")

# ---------------------------------------------------------
# 2. 카메라 및 추적 설정
# ---------------------------------------------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# 파란색 텀블러 뚜껑 추적용 HSV 범위
lower_color = np.array([95, 100, 100])
upper_color = np.array([135, 255, 255])

# ---------------------------------------------------------
# 3. 상태 변수 및 설정값
# ---------------------------------------------------------
canvas = None
line_prev_point = None
stamp_prev_point = None
min_stamp_distance = 45  # 스탬프 간격 (픽셀)

# 모드 관리
modes = ["Meme Dog Stamp", "Cat Stamp", "Color Line"]
mode_index = 0

# 일반 선 그리기용 색상 목록
pen_colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255)]  # Red, Green, Blue, Yellow, Purple
color_names = ["Red", "Green", "Blue", "Yellow", "Purple"]
color_index = 0

print("=== Air Canvas Multi-Mode ===")
print("M 키: 모드 변경 (Dog -> Cat -> Line)")
print("P 키: 선 색상 변경 (Line 모드 전용)")
print("C 키: 캔버스 초기화 | ESC 키: 종료")

# ---------------------------------------------------------
# 4. 메인 비디오 루프
# ---------------------------------------------------------
while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)  # 좌우 반전
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros_like(frame)

    # HSV 변환 및 색상 마스킹
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
                cv2.circle(frame, center, 6, (255, 255, 0), -1)  # 추적 포인터

    # ---------------------------------------------------------
    # 5. 모드별 그리기 로직
    # ---------------------------------------------------------
    current_mode = modes[mode_index]

    if center is not None:
        # A. 스탬프 모드 (Dog 또는 Cat)
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

            line_prev_point = None  # 선 연결 초기화

        # B. 기본 선 그리기 모드
        elif current_mode == "Color Line":
            if line_prev_point is not None:
                # 좌표가 너무 멀지 않을 때만 선 연결
                if np.linalg.norm(np.array(center) - np.array(line_prev_point)) < 100:
                    cv2.line(canvas, line_prev_point, center, pen_colors[color_index], 5)
            line_prev_point = center
            stamp_prev_point = None  # 스탬프 간격 초기화
    else:
        line_prev_point = None

    # ---------------------------------------------------------
    # 6. 화면 합성 및 가독성 높은 UI 출력
    # ---------------------------------------------------------
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask_inv = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY_INV)
    frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    result = cv2.add(frame_bg, canvas)

    # 좌측 상단 UI 바 (검은색 박스로 가독성 확보)
    cv2.rectangle(result, (10, 10), (360, 60), (0, 0, 0), -1)
    
    ui_text = f"Mode: {current_mode}"
    if current_mode == "Color Line":
        ui_text += f" ({color_names[color_index]})"

    cv2.putText(result, ui_text, (20, 42), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Air Canvas Master", result)

    # ---------------------------------------------------------
    # 7. 키보드 제어
    # ---------------------------------------------------------
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC: 종료
        break
    elif key == ord('m') or key == ord('M'):  # M: 모드 전환
        mode_index = (mode_index + 1) % len(modes)
        line_prev_point = None
        stamp_prev_point = None
        print(f"[System] 모드 변경: {modes[mode_index]}")
    elif key == ord('p') or key == ord('P'):  # P: 펜 색상 변경
        color_index = (color_index + 1) % len(pen_colors)
        print(f"[System] 선 색상 변경: {color_names[color_index]}")
    elif key == ord('c') or key == ord('C'):  # C: 캔버스 비우기
        canvas = np.zeros_like(frame)
        print("[System] 캔버스 초기화")

cap.release()
cv2.destroyAllWindows()