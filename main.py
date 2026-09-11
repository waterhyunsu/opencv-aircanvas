import cv2
import numpy as np

# 1. 강아지 JPG 이미지 로드
dog_img = cv2.imread('dog.jpg')

if dog_img is None:
    print("오류: 'dog.jpg' 파일을 찾을 수 없습니다.")
    exit()

# 2. JPG의 흰색 배경을 투명(BGRA)으로 자동 변환
b, g, r = cv2.split(dog_img)
# 완전히 흰색이거나 밝은 배경(220 이상)인 영역을 알파 0(투명)으로 설정
alpha = np.where((b > 220) & (g > 220) & (r > 220), 0, 255).astype(np.uint8)
dog_img = cv2.merge([b, g, r, alpha])

# 스탬프 크기 조절 (60x60 픽셀)
stamp_size = 60
dog_img = cv2.resize(dog_img, (stamp_size, stamp_size))

# 3. 웹캠 연결
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

# 4. 추적용 파란색 HSV 범위 (텀블러 뚜껑)
lower_color = np.array([95, 100, 100])
upper_color = np.array([135, 255, 255])

# 5. 캔버스 버퍼 초기화
canvas = None

print("=== OpenCV Dog Stamp Air Canvas ===")
print("C 키: 화면 초기화 | ESC 키: 종료")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    if canvas is None:
        canvas = np.zeros_like(frame)

    # 6. HSV 색상 추적
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
                cv2.circle(frame, center, 5, (255, 0, 0), -1)

    # 7. 강아지 스탬프 합성
    if center is not None:
        cx, cy = center
        half_s = stamp_size // 2

        y1, y2 = max(0, cy - half_s), min(h, cy + half_s)
        x1, x2 = max(0, cx - half_s), min(w, cx + half_s)

        dog_y1, dog_y2 = half_s - (cy - y1), half_s + (y2 - cy)
        dog_x1, dog_x2 = half_s - (cx - x1), half_s + (x2 - cx)

        if (y2 > y1) and (x2 > x1):
            overlay = dog_img[dog_y1:dog_y2, dog_x1:dog_x2]

            # Alpha 채널 기반 블렌딩
            alpha_mask = overlay[:, :, 3] / 255.0
            for c in range(0, 3):
                canvas[y1:y2, x1:x2, c] = (
                    alpha_mask * overlay[:, :, c] + (1.0 - alpha_mask) * canvas[y1:y2, x1:x2, c]
                )

    # 8. 원본 영상에 캔버스 합성
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask_inv = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY_INV)
    frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    result = cv2.add(frame_bg, canvas)

    cv2.putText(result, "Mode: Meme Dog Stamp", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Dog Stamp Air Canvas", result)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif key == ord('c') or key == ord('C'):
        canvas = np.zeros_like(frame)

cap.release()
cv2.destroyAllWindows()