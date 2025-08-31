# Golf Swing 3D Analyzer

골프 스윙 분석을 위한 FastAPI 기반 백엔드 서비스입니다.

## 프로젝트 구조

```
.
├── demo/               # 데모 파일 디렉토리
├── logs/              # 로그 파일 디렉토리
├── cache/             # 캐시 파일 디렉토리
├── ref/               # 참조 파일 디렉토리
├── requirements.txt   # 의존성 패키지
├── LICENSE           # 라이센스 파일
└── README.md         # 프로젝트 문서
```

## 설치 방법

1. Python 3.8 이상이 필요합니다.

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

## 주요 의존성 패키지

- mediapipe==0.10.21: 포즈 추정을 위한 라이브러리
- opencv-python==4.9.0.80: 이미지/비디오 처리
- numpy==1.26.4: 수치 연산
- streamlit==1.32.2: 웹 인터페이스
- matplotlib==3.8.3: 데이터 시각화
- pillow==10.2.0: 이미지 처리
- python-multipart==0.0.9: 파일 업로드 처리
- python-dotenv==1.0.1: 환경 변수 관리

## 실행 방법

1. 환경 변수 설정:
   - `.env` 파일을 프로젝트 루트에 생성하고 필요한 환경 변수를 설정합니다.

2. 서버 실행:
```bash
# 메인 골프 스윙 분석기
streamlit run demo/src/app.py

# 아름다운 Hello World 데모 (SMP-7)
streamlit run demo_hello_world.py

# SMP-7 최신 구현 (2025-08-31)
./run_smp7.sh
# or
streamlit run smp7_hello_world.py
```

## 기능

### 1. 비디오 업로드
- 골프 스윙 비디오 파일 업로드 (지원 형식: mp4, avi, mov)
- 자동 포맷 검증 및 처리

### 2. 스윙 분석
- 실시간 포즈 추정
- 주요 관절 각도 분석
- 스윙 궤적 시각화
- 프레임별 상세 분석 데이터 제공

### 3. 결과 시각화
- 스윙 궤적 3D 렌더링
- 주요 지표 그래프 표시
- 프레임별 포즈 추정 결과 표시

## 라이센스

이 프로젝트는 LICENSE 파일에 명시된 라이센스 조건에 따라 배포됩니다.

## 문의사항

버그 리포트나 기능 개선 제안은 GitHub Issues를 통해 제출해 주시기 바랍니다.

## 새로운 기능 / New Features

### 🚀 AstraSprint Pipeline Integration
- **Feature**: End-to-end automated pipeline testing
- **Added**: 2025-08-30T02:34:58.813Z
- **Pipeline**: SMP-9 Complete Pipeline Test
- **Components**: PR creation, Jira updates, Confluence documentation

### 📋 Feature Documentation
- **Feature**: Comprehensive feature documentation system
- **Status**: ✅ Active
- **Integration**: GitHub, Jira, Confluence
- **Automation**: Full E2E pipeline support

## 업데이트 기록

**Last Updated**: 2025-08-30T02:34:58.813Z
**Pipeline**: SMP-9 Implementation Complete