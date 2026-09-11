# OpenCV Air Canvas Master

Python과 OpenCV를 활용하여 웹캠으로 특정 색상의 오브젝트를 추적하고, 공중에서 자유롭게 그림을 그리거나 이미지 스탬프를 찍을 수 있는 **에어 캔버스(Air Canvas)** 프로젝트입니다.

---

## 프로젝트 실행 결과

| 실행 화면 | 터미널 로그 |
| :---: | :---: |
| <img width="643" height="514" alt="demo png" src="https://github.com/user-attachments/assets/f53b34a5-e0ae-4040-9466-f816a6dad813" />
 |<img width="469" height="375" alt="terminal png" src="https://github.com/user-attachments/assets/e6e01a5f-ab57-424b-a8e5-4ff7ddfae7ee" />
|


---

## 핵심 기능

* **HSV 기반 오브젝트 추적**: 파란색 오브젝트(텀블러 뚜껑 등)의 위치를 실시간으로 추적하여 마우스 없이 드로잉 기능 구현
* **다중 드로잉 모드 (M 키)**:
* **Color Line**: 기본 선 그리기 모드
* **Meme Dog Stamp**: 강아지 이미지 스탬프 모드
* **Cat Stamp**: 고양이 이미지 스탬프 모드
* **Eraser (E 키)**: 40px 영역을 지정하여 그렸던 내용을 선택적으로 지우는 지우개 모드


* **펜 색상 변경 (P 키)**: Red, Green, Blue, Yellow, Purple 총 5가지 색상 변경 기능
* **스탬프 밀도 최적화**: 이동 거리를 계산하여 스탬프 겹침(노이즈) 방지
* **캔버스 초기화 (C 키)**: 그려진 선과 스탬프 전체 삭제
* **가독성 높은 UI**: 좌측 상단 검은색 박스 오버레이로 현재 모드 상태 명시

---

## 🛠 기술 스택

* **Language**: Python 3.10+
* **Library**: OpenCV (`opencv-python`), NumPy

---

## 키보드 조작 가이드

| 단축키 | 기능 | 설명 |
| --- | --- | --- |
| **`M`** | 모드 변경 | Dog Stamp ➔ Cat Stamp ➔ Color Line ➔ Eraser 순환 |
| **`E`** | 지우개 모드 | 즉시 40px 지우개 모드로 전환 |
| **`P`** | 색상 변경 | Line 모드에서 펜 색상 전환 (Red, Green, Blue, Yellow, Purple) |
| **`C`** | 화면 초기화 | 캔버스에 그려진 모든 내용 삭제 |
| **`ESC`** | 프로그램 종료 | 에어 캔버스 종료 |

---

## 시작하기

### 1. 가상환경 및 패키지 설치

```bash
python -m venv venv
.\venv\Scripts\activate
pip install opencv-python numpy

```

### 2. 필수 리소스 파일 준비

프로젝트 루트 폴더 내 아래 이미지 파일이 존재해야 스탬프 모드가 정상 작동합니다.

* `dog.jpg`
* `cat.jpg`

### 3. 실행

```bash
python main.py

```
