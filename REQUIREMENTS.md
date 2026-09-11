1. 기능명세서 작성 (REQUIREMENTS.md)구현할 기능, 입력 조건, 출력 결과, 사용할 기술 스택을 미리 정의한다.개발 도중 방향성을 잃지 않고 '무엇을 만들지' 명확히 하는 역할을 한다.

2. 프로젝트 초기 설정 (체크 포인트).gitignore 설정: venv 폴더, 가중치 파일(.weights), 실행 로그, 캐시 파일(__pycache__) 등 Git에 올라가면 안 되는 무거운/불필요한 파일을 거르는 설정을 먼저 해둔다.requirements.txt 생성: 프로젝트에 사용된 라이브러리 목록(opencv-python, numpy 등)을 패키징해둔다 (pip freeze > requirements.txt).

3. 기능 개발 및 Git 커밋명세서에 정리한 기능 단위(기본 기능 $\rightarrow$ C키 초기화 $\rightarrow$ P키 색상 변경 $\rightarrow$ 추가 기능)별로 코드를 작성하고 의미 있는 단위로 커밋을 남긴다.

4. 메인 문서화 (README.md)개발이 끝나면 프로젝트 레포지토리를 방문하는 사람들을 위해 프로젝트 소개, 실행 화면(GIF/사진), 설치 및 실행 방법, 주요 컨트롤러 안내를 작성하여 마무리한다.

5. 추가로 챙기면 좋은 것들
실행 시연 시각자료 (GIF / PNG): README에 실제 동작하는 1~2초짜리 짤(GIF)이나 실행 캡처본을 넣으면 프로젝트 완성도가 급격히 높아 보인다.Troubleshooting (문제 해결 기록): 개발 중 겪었던 오류(예: "PowerShell에서 curl 명령어 에러 해결", "HSV 추적 시 노이즈 제거 모폴로지 적용" 등)를 README 하단이나 별도 블로그/노션에 정리해두면 포트폴리오 면접에서 강점이 된다.





# 프로젝트 요구사항 및 기능 명세서 (Requirements & Specifications)

## 1. 프로젝트 개요 (Project Overview)
- **프로젝트명**: opencv-aircanvas
- **개발 환경**: Python 3.x, OpenCV (cv2), NumPy
- **목적**: OpenCV의 HSV 색상 추적(Color Tracking) 및 영상 합성(Alpha Blending/Masking) 기술을 활용하여 공중에 특정 물체(펜)를 이용해 자유롭게 그림을 그리는 실시간 인터랙티브 Air Canvas 애플리케이션 구현

---

## 2. 요구사항 분석 및 구현 현황 (Functional Requirements)

### [필수 요구사항]
1. **색상 추적 기반 그리기 기능 (Color Tracking & Drawing)**
   - **요구사항**: 지정한 특정 색상 범위의 물체를 실시간 웹캠 프레임에서 검출하고, 해당 물체의 이동 궤적을 따라 화면에 선/점이 연속적으로 그려져야 함.
   - **구현 방식**: `cv2.cvtColor`로 HSV 색상 공간 변환 후 `cv2.inRange` 마스크를 생성, 윤곽선(Contour)의 중심점(Center Point)을 추적하여 `cv2.line`으로 캔버스 버퍼에 그리기 수행.

2. **캔버스 초기화 기능 (Clear Canvas)**
   - **요구사항**: 키보드 `C` 버튼 입력 시 화면에 그려진 모든 그림이 지워져야 함.
   - **구현 방식**: `key == ord('c')` 이벤트 감지 시 캔버스 버퍼 배열(`canvas`)을 `np.zeros_like()`로 재초기화.

3. **펜 색상 변경 기능 (Change Pen Color)**
   - **요구사항**: 키보드 `P` 버튼 입력 시 객체를 따라 그려지는 선의 색상이 순환하며 변경되어야 함.
   - **구현 방식**: `key == ord('p')` 이벤트 감지 시 펜 색상 배열 인덱스(`color_index`)를 순환 증가시켜 BGR 색상값 변경.

---

### [창의적 추가 기능 (Creative Features)]
1. **smooth Line Interpolation (자연스러운 연속선 표현)**
   - 단순 점 찍기가 아닌, 이전 좌표(`prev_point`)와 현재 좌표(`center`)를 이어주는 보정 로직을 추가하여 빠른 움직임에도 선이 끊기지 않도록 처리.
2. **실시간 모드 HUD (Heads-Up Display) 상단 UI**
   - 화면 좌측 상단에 현재 선택된 펜 색상 및 상태를 직관적으로 확인할 수 있는 반투명 오버레이 UI 구현.
3. **거울 모드 (Mirror View)**
   - `cv2.flip(frame, 1)`을 적용하여 사용자 시선 기준 직관적인 공중 그리기 환경 제공.
4. **노이즈 필터링 (Morphology Processing)**
   - 침식(`erode`) 및 팽창(`dilate`) 연산을 통해 주변 조명 반사로 인한 추적 오작동 최소화.

---

## 3. 조작 방법 (Controls)
- **그리기**: 지정된 HSV 색상 오브젝트를 웹캠 앞에 위치시키고 이동
- **C 키**: 캔버스 전체 지우기
- **P 키**: 펜 색상 변경 (Red -> Green -> Blue -> Yellow -> Purple)
- **ESC 키**: 프로그램 종료