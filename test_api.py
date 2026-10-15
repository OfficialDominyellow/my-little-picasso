import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from pydantic import BaseModel, Field

# 1. .env 파일에서 환경변수 로드
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key or api_key == "your_gemini_api_key_here":
    print("=" * 60)
    print(" [오류] API 키가 설정되지 않았습니다.")
    print(" .env 파일에 GEMINI_API_KEY를 설정해주세요.")
    print(" 발급처: https://aistudio.google.com/app/apikey")
    print("=" * 60)
    sys.exit(1)

# 2. 공식 Google Gen AI SDK 임포트
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[오류] google-genai 패키지가 설치되지 않았습니다. pip install google-genai 를 실행하세요.")
    sys.exit(1)

# 3. Pydantic 스키마 정의
class PictureDiary(BaseModel):
    title: str = Field(description="유치원생이 지은 짧고 귀여운 그림일기 제목")
    sentences: list[str] = Field(description="사진에서 관찰한 사실만을 담은 짧은 3문장 내외의 1인칭 그림일기 본문")

# 4. 샘플 이미지 확인 및 생성 (없을 경우 간단한 테스트용 사과 그림 생성)
sample_image_path = Path("sample_test.png")
if not sample_image_path.exists():
    img = Image.new("RGB", (400, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # 빨간 사과 그리기
    draw.ellipse([100, 120, 300, 320], fill=(220, 50, 50), outline=(150, 0, 0), width=3)
    # 꼭지와 잎사귀
    draw.rectangle([190, 70, 210, 130], fill=(100, 60, 20))
    draw.ellipse([210, 80, 270, 110], fill=(50, 180, 50))
    img.save(sample_image_path)
    print(f"테스트용 샘플 이미지 생성 완료: {sample_image_path.name}")

# 5. Gemini 클라이언트 초기화 (명시적 키 전달)
client = genai.Client(api_key=api_key)
model_name = "gemma-4-26b-a4b-it"

print(f"호출 시작: 모델 '{model_name}'에 샘플 이미지를 입력하여 테스트 중...")

prompt = (
    "이 사진을 보고 유치원생이 쓴 짧은 1인칭 그림일기를 작성해주세요.\n"
    "규칙:\n"
    "1. 유치원생이 쓸 법한 짧고 쉬운 문장으로 작성할 것\n"
    "2. 3문장 내외로 작성할 것\n"
    "3. 사진에서 실제로 눈으로 볼 수 있는 내용만 포함할 것 (없는 사실, 임의의 사건 지어내지 말 것)\n"
    "4. 1인칭 표현('나는', '내가') 사용\n"
)

try:
    image = Image.open(sample_image_path)
    response = client.models.generate_content(
        model=model_name,
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PictureDiary,
            temperature=0.3,
        ),
    )

    result: PictureDiary = response.parsed
    print("\n" + "=" * 60)
    print(" [성공] API 호출 및 응답 검증 성공!")
    print(f" 제목: {result.title}")
    print(" 본문 문장:")
    for i, s in enumerate(result.sentences, 1):
        print(f"   {i}. {s}")
    print("=" * 60)

except Exception as e:
    print("\n" + "=" * 60)
    print(f" [API 호출 실패] {type(e).__name__}: {e}")
    print(" 원인 확인 및 안내:")
    err_str = str(e)
    if "API_KEY_INVALID" in err_str or "400" in err_str or "unauthorized" in err_str.lower():
        print(" - API 키가 유효하지 않거나 인증에 실패했습니다.")
    elif "404" in err_str or "NOT_FOUND" in err_str:
        print(f" - 모델 ID '{model_name}'를 찾을 수 없거나 계정에 해당 모델 권한이 없습니다.")
    elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
        print(" - 요청 한도(Rate Limit)를 초과했습니다. 잠시 후 다시 시도하세요.")
    elif "PERMISSION_DENIED" in err_str:
        print(" - 권한이 거부되었습니다. AI Studio에서 API 키의 활성화 여부나 리전 설정을 확인하세요.")
    else:
        print(f" - 상세 에러: {err_str}")
    print("=" * 60)
    sys.exit(1)

