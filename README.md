# My Little Picasso (마이 리틀 피카소) 🎨

사진을 업로드하면 최신 Google Gemma 멀티모달 모델(`gemma-4-26b-a4b-it`)이 사진을 분석하여 유치원생 눈높이의 순수한 1인칭 그림일기를 작성하고, 레트로 원고지 스타일의 A4 그림일기 템플릿에 사진과 글을 합성하여 고해상도 PNG 이미지로 저장할 수 있는 웹 애플리케이션입니다.

---

## ✨ 주요 기능

1. **사진 업로드 및 미리보기**: 드래그 앤 드롭 및 파일 탐색기를 통한 간편한 사진 등록 (JPEG, PNG, WEBP 등 지원)
2. **AI 그림일기 자동 생성**:
   - Google `gemma-4-26b-a4b-it` 멀티모달 MoE 모델 사용
   - 사진에 나타난 실제 시각적 사실만 포착하여 어린이가 쓴 듯한 쉬운 어휘와 1인칭 문장("나는 오늘 ~했다")으로 작성
   - 일기 언어 선택 지원 (한국어 기본값, 영어, 일본어)
   - 글 길이 조절 기능 (짧게: 2~3문장 / 보통: 4~5문장)
   - 사용자 추가 메모 우선 반영 기능
   - Pydantic 스키마 기반 구조화된 JSON 응답 검증
3. **사용자 직접 편집기**:
   - 생성된 일기의 제목, 날짜, 날씨, 본문 문장을 웹 화면에서 직접 자유롭게 수정 가능
   - 원고지 규격(84자) 실시간 글자 수 카운터 제공
4. **A4 그림일기 템플릿 합성 (Pillow)**:
   - 고해상도 인쇄/보관용 규격 (1654 x 2338 px, A4 세로형)
   - 상단 제목 배지, 날짜/날씨 칸, 사진 프레임, 하단 원고지 격자(14칸 x 6줄) 배치
   - 초등학교 저학년 글쓰기장 스타일의 십자 가이드 점선 내장
   - 한국어 원고지 작성 규칙(문장부호 줄 첫 칸 금칙 처리, 첫 칸 공백 방지) 적용
   - 오픈소스 OFL 한글 폰트(`NanumGothic`) 번들링으로 환경에 구애받지 않는 안정적인 텍스트 렌더링
5. **결과 미리보기 및 PNG 다운로드**:
   - 렌더링된 그림일기를 화면에서 즉시 확인하고 고화질 PNG 파일로 다운로드
   - 다시 만들기(초기화) 버튼 지원

---

## 🛠️ 기술 스택

- **Backend**: Python 3.13, FastAPI, Uvicorn, Pydantic v2
- **AI / Multimodal**: Google Gen AI SDK (`google-genai`), Model: `gemma-4-26b-a4b-it`
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML5, CSS3, Modern Vanilla JavaScript (Jinja2 Templates)
- **Fonts**: Nanum Gothic (SIL Open Font License)

---

## 📂 프로젝트 구조

```text
my-little-picasso/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI 애플리케이션 및 API 라우터
│   ├── diary_service.py      # Gemma 4 일기 생성 서비스 (프롬프트 & 규칙)
│   ├── template_renderer.py  # A4 세로형 원고지 그림일기 Pillow 렌더러
│   └── schemas.py            # Pydantic 입출력 스키마
├── assets/
│   └── fonts/
│       ├── NanumGothic-Bold.ttf
│       └── NanumGothic-Regular.ttf
├── static/
│   ├── css/
│   │   └── style.css         # 감성적인 유치원 미술놀이 UI 스타일
│   └── js/
│       └── app.js            # 업로드, 비동기 호출, 편집, 렌더링, 다운로드
├── templates/
│   └── index.html            # 메인 웹 페이지 템플릿
├── requirements.txt          # 프로젝트 의존성 목록
├── .env.example              # 환경변수 템플릿
├── .gitignore                # 보안 파일 및 캐시 제외 설정
├── test_api.py               # 1단계 API 연동 검증 테스트
├── test_renderer.py          # 템플릿 렌더링 검증 테스트
└── test_app.py               # E2E 전체 통합 테스트
```

---

## 🚀 빠른 시작 (Local)

### 1. 가상환경 생성 및 의존성 설치
```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env.example`을 복사하여 `.env`를 생성하고 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료 발급받은 API 키를 설정합니다.
```env
GEMINI_API_KEY=your_actual_api_key_here
```
> **보안 주의**: `.env` 파일은 절대 Git에 커밋하거나 외부에 공유하지 마세요.

### 3. 테스트 실행
```bash
# E2E 통합 테스트 (API 연동, 오류 처리, 템플릿 합성 전과정)
python test_app.py
```

### 4. 웹 서버 실행
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
브라우저에서 `http://localhost:8000`으로 접속하여 서비스를 이용할 수 있습니다.