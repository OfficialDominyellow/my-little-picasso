import base64
import io
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

from app.diary_service import generate_picture_diary
from app.template_renderer import render_diary_template
from app.schemas import GenerateDiaryResponse, PictureDiaryOutput

app = FastAPI(
    title="My Little Picasso - 마이 리틀 피카소",
    description="사진을 유치원생 눈높이의 귀여운 그림일기로 변환해주는 서비스",
    version="1.0.0",
)

# CORS 설정 (어떤 포트/도메인에서 프론트를 띄워도 fetch 실패 방지)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 허용 이미지 MIME 타입 및 최대 크기 (15MB)
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/heic"}
MAX_FILE_SIZE = 15 * 1024 * 1024


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """메인 페이지 서빙"""
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/generate-diary", response_model=GenerateDiaryResponse)
async def api_generate_diary(
    file: UploadFile = File(..., description="업로드할 사진 파일"),
    language: str = Form("ko", description="일기 작성 언어 (ko, en, ja)"),
    length: str = Form("short", description="글 길이 (short, normal)"),
    notes: Optional[str] = Form(None, description="사용자 추가 메모"),
):
    """
    사진을 분석하여 gemma-4-26b-a4b-it 기반 1인칭 그림일기를 생성합니다.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다 ({file.content_type}). JPG, PNG, WEBP 이미지를 업로드해주세요.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"이미지 크기가 너무 큽니다 (최대 15MB 지원, 현재 {len(image_bytes) // 1024 // 1024}MB).",
        )
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="빈 파일이 업로드되었습니다.")

    try:
        diary_output: PictureDiaryOutput = generate_picture_diary(
            image_bytes=image_bytes,
            language=language,
            length=length,
            notes=notes,
        )

        full_text = "\n".join(diary_output.sentences)

        return GenerateDiaryResponse(
            title=diary_output.title,
            sentences=diary_output.sentences,
            diary_text=full_text,
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


@app.post("/api/render-template")
async def api_render_template(
    title: str = Form("오늘의 일기"),
    date_str: str = Form(""),
    weather: str = Form("맑음"),
    content: str = Form(""),
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
):
    """
    제목, 날짜, 날씨, 본문, 원본 사진을 합성하여 A4 고해상도 그림일기 PNG를 생성합니다.
    """
    photo_image = None

    if file and file.filename:
        try:
            bytes_data = await file.read()
            if bytes_data:
                photo_image = Image.open(io.BytesIO(bytes_data))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"업로드된 사진을 처리할 수 없습니다: {e}")
    elif image_base64:
        try:
            # Data URL 형식 대응 (data:image/png;base64,...)
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]
            raw_data = base64.b64decode(image_base64)
            photo_image = Image.open(io.BytesIO(raw_data))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Base64 이미지를 처리할 수 없습니다: {e}")

    # 사진이 RGBA 모드일 경우 RGB로 변환
    if photo_image and photo_image.mode not in ("RGB", "L"):
        photo_image = photo_image.convert("RGB")

    try:
        result_img = render_diary_template(
            title=title,
            date_str=date_str,
            weather=weather,
            content=content,
            photo_image=photo_image,
        )

        img_byte_arr = io.BytesIO()
        result_img.save(img_byte_arr, format="PNG", quality=95)
        img_bytes = img_byte_arr.getvalue()

        return Response(content=img_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 렌더링 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
