import cv2
import numpy as np

# 1. 웹캠 연결
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

# 2. 색상 추적용 HSV 범위 설정
lower_color = np.array([95, 100, 100])   # Hue: 파란색 영역, Saturation/Value: 선명한 색상
upper_color = np.array([135, 255, 255])

# 3. 펜 색상 리스트 (P 버튼 누를 때 변경)
pen_colors = [
    (0, 0, 255),    # 빨강 (BGR)
    (0, 255, 0),    # 초록
    (255, 0, 0),    # 파랑
    (0, 255, 255),  # 노랑
    (255, 0, 255)   # 보라
]
color_names = ["Red", "Green", "Blue", "Yellow", "Purple"]
color_index = 0

# 4. 그림을 기록할 투명 캔버스 버퍼 및 좌표 저장소
canvas = None
prev_point = None

print("=== OpenCV Air Canvas 실행 중 ===")
print("C 키: 화면 초기화 | P 키: 펜 색상 변경 | ESC 키: 종료")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    # 좌우 반전 (거울 효과)
    frame = cv2.flip(frame, 1)
    
    # 캔버스 버퍼 최초 생성
    if canvas is None:
        canvas = np.zeros_like(frame)

    # 5. HSV 색상 공간 변환 및 마스크 생성
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    
    # 노이즈 제거 (노이즈 필터링)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # 6. 윤곽선(Contours) 검출을 통한 물체 중심점 추적
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(contours) > 0:
        # 가장 큰 윤곽선 추출
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        
        # 일정 크기 이상의 물체만 추적
        if radius > 10:
            M = cv2.moments(c)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                # 물체 테두리 및 포인터 표시
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, pen_colors[color_index], -1)

    # 7. 이전 좌표와 현재 좌표를 이어선(Line)으로 캔버스에 그리기
    if center is not None:
        if prev_point is not None:
            cv2.line(canvas, prev_point, center, pen_colors[color_index], 5)
        prev_point = center
    else:
        prev_point = None  # 물체를 놓치면 선 연결 끊기

    # 8. 원본 웹캠 영상과 캔버스 합성
    # 캔버스에 그려진 선을 웹캠 프레임 위에 합성
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask_inv = cv2.threshold(gray_canvas, 20, 255, cv2.THRESH_BINARY_INV)
    frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    result = cv2.add(frame_bg, canvas)

    # 9. UI / HUD 상단 정보 표시 (창의적 요소)
    cv2.rectangle(result, (10, 10), (280, 50), (0, 0, 0), -1)
    cv2.putText(result, f"Pen: {color_names[color_index]}", (20, 38), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, pen_colors[color_index], 2)

    # 결과 출력
    cv2.imshow("OpenCV Air Canvas", result)

    # 10. 키보드 입력 처리
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC 키 종료
        break
    elif key == ord('c') or key == ord('C'):  # C 키: 캔버스 지우기
        canvas = np.zeros_like(frame)
        print("[System] 캔버스가 초기화되었습니다.")
    elif key == ord('p') or key == ord('P'):  # P 키: 색상 변경
        color_index = (color_index + 1) % len(pen_colors)
        print(f"[System] 펜 색상 변경: {color_names[color_index]}")

cap.release()
cv2.destroyAllWindows()