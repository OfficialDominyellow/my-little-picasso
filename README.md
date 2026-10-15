# My Little Picasso (마이 리틀 피카소)

사진을 입력하면 AI가 유치원생 수준의 짧은 그림일기 글을 작성하고, 사진과 글을 고정된 그림일기 템플릿에 배치해 PNG 이미지로 저장할 수 있게 하는 웹 애플리케이션입니다.

## 주요 기능
- **AI 그림일기 작성**: Google의 `gemma-4-26b-a4b-it` 멀티모달 모델을 사용하여 어린이가 쓴 듯한 귀엽고 쉬운 1인칭 그림일기를 생성
- **사용자 편집**: 생성된 제목과 문장을 사용자가 직접 수정 가능
- **그림일기 템플릿 합성**: A4 규격의 레트로 격자 원고지 스타일 그림일기 템플릿에 사진과 글을 배치하여 고품질 PNG로 다운로드

## 기술 스택
- **Language**: Python 3.13
- **Framework**: FastAPI, Uvicorn
- **AI SDK**: Google Gen AI SDK (`google-genai`)
- **AI Model**: `gemma-4-26b-a4b-it` (Google AI Studio)
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML5, CSS3, Modern Vanilla JavaScript

## 시작하기

### 1. 가상환경 및 의존성 설치
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env.example`을 복사하여 `.env`를 생성하고 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받은 API 키를 입력합니다.
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. API 동작 테스트
```bash
python test_api.py
```