# Hello World Chat App - SMP-7 Test Implementation

Simple Streamlit chat application with intentional bugs for AstraSprint pipeline testing.

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
# 아름다운 Hello World 채팅 데모 (SMP-7)
streamlit run demo_hello_world.py

# 기존 골프 스윙 분석기 (백업)
streamlit run demo/src/app.py
```

## 기능

### 1. 간단한 채팅 인터페이스
- 기본적인 텍스트 입력/출력
- 메시지 히스토리 표시
- "hello"와 "bye" 키워드 인식

### 2. 의도적인 버그들 (테스트용)
- 메시지 순서가 잘못 표시됨 (최신 메시지가 위에)
- 일부 입력에 대한 응답 누락
- 채팅 클리어 버튼이 즉시 작동하지 않음
- 메시지 카운트 오류
- 빈 메시지 리스트 처리 오류

### 3. 사이드바 설정
- 채팅 클리어 기능 (버그 있음)
- 메시지 통계 표시 (부정확함)
- 마지막 메시지 미리보기 (오류 발생 가능)

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