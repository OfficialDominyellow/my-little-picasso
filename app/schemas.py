from typing import List, Optional
from pydantic import BaseModel, Field

class PictureDiaryOutput(BaseModel):
    """Gemma 모델이 생성하는 그림일기 구조화된 출력 스키마"""
    title: str = Field(description="유치원생이 지은 짧고 귀여운 그림일기 제목")
    sentences: List[str] = Field(description="사진에서 관찰한 사실만을 담은 짧은 1인칭 그림일기 본문 문장 목록")

class GenerateDiaryResponse(BaseModel):
    """API 클라이언트 반환용 모델"""
    title: str
    sentences: List[str]
    diary_text: str  # 문장들을 결합한 전체 본문 텍스트

class RenderTemplateRequest(BaseModel):
    """그림일기 템플릿 PNG 합성 요청 스키마"""
    title: str = Field(..., description="일기 제목")
    date_str: str = Field(default="", description="날짜 (예: 2026년 10월 15일 목요일)")
    weather: str = Field(default="맑음", description="날씨 (맑음, 구름, 비, 눈 등)")
    content: str = Field(..., description="일기 본문 내용")
    image_base64: Optional[str] = Field(None, description="업로드된 원본 이미지 (Base64 인코딩)")

