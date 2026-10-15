import io
import os
from typing import Optional
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.schemas import PictureDiaryOutput

# .env 로드
load_dotenv()

MODEL_NAME = "gemma-4-26b-a4b-it"


def get_genai_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일에 API 키를 등록해주세요."
        )
    return genai.Client(api_key=api_key)


def build_diary_prompt(
    language: str = "ko",
    length: str = "short",
    notes: Optional[str] = None,
) -> str:
    # 1. 문장 수 지시
    if length == "short":
        length_instruction = "본문 문장은 2~3문장의 짧은 분량으로 작성해주세요."
    else:
        length_instruction = "본문 문장은 4~5문장 분량으로 작성해주세요."

    # 2. 언어 지시
    if language == "en":
        lang_instruction = "Write the title and all sentences in natural English suitable for a kindergarten child."
    elif language == "ja":
        lang_instruction = "幼稚園児が書いたような易しい日本語でタイトルと日記本文を作成してください。"
    else:
        lang_instruction = "한국어로 유치원생이 말하듯 귀엽고 쉬운 어휘로 작성해주세요 (~했다, ~다)."

    # 3. 사용자 메모 반영 여부
    notes_instruction = ""
    if notes and notes.strip():
        notes_instruction = (
            f"\n[사용자 메모]: \"{notes.strip()}\"\n"
            "- 사용자가 입력한 위 메모 내용을 최우선으로 일기에 반영해주세요. "
            "단, 사진의 실제 분위기와 어울리게 자연스럽게 녹여내세요.\n"
        )

    prompt = f"""당신은 유치원생(5~7세) 어린이입니다. 첨부된 사진을 보고 직접 오늘의 그림일기를 작성해주세요.

[필수 규칙]
1. 관찰 사실만 서술: 사진 속에서 실제로 볼 수 있는 사물, 색상, 모습, 동물, 음식 등 명확한 사실만을 바탕으로 씁니다.
2. 상상 및 허구 금지: 사진에 찍히지 않은 가상의 인물, 일어나지 않은 사건, 확실치 않은 장소나 감정을 임의로 지어내지 마세요. 확실하지 않은 내용은 과감히 생략하세요.
3. 1인칭 시점: 유치원생 어린이가 직접 겪은 것처럼 1인칭('나는', '내가') 표현을 자연스럽게 사용하세요.
4. 어휘 수준: 유치원생이 쓰는 아주 쉽고 순수한 어휘와 짧은 문장 구조를 사용하세요.
5. 분량 규칙: {length_instruction}
6. 언어: {lang_instruction}
{notes_instruction}
출력은 지정된 스키마에 맞춰 제목(title)과 문장 목록(sentences)으로 구분된 JSON으로 반환하세요.
"""
    return prompt


def generate_picture_diary(
    image_bytes: bytes,
    language: str = "ko",
    length: str = "short",
    notes: Optional[str] = None,
) -> PictureDiaryOutput:
    """
    이미지 바이트와 옵션을 입력받아 gemma-4-26b-a4b-it 모델로 일기를 생성합니다.
    """
    client = get_genai_client()

    # PIL 이미지 로드 및 검증
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # RGBA나 P 모드일 경우 RGB로 변환 (JPEG/PNG 일관성)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
    except Exception as e:
        raise ValueError(f"유효한 이미지 파일이 아닙니다: {e}")

    # 이미지 크기가 지나치게 클 경우 축소 (네트워크 비용 및 지연 감소)
    max_dimension = 2048
    if max(image.size) > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

    prompt = build_diary_prompt(language=language, length=length, notes=notes)

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PictureDiaryOutput,
                temperature=0.3,  # 사실에 충실하게 낮은 온도로 생성
            ),
        )

        result: PictureDiaryOutput = response.parsed
        if not result or not result.sentences:
            raise ValueError("모델이 일기 내용을 생성하지 못했습니다.")

        return result

    except APIError as api_err:
        raise RuntimeError(f"Google Gen AI API 오류: {api_err.message} (코드: {api_err.code})")
    except Exception as err:
        raise RuntimeError(f"일기 생성 중 오류 발생: {str(err)}")

