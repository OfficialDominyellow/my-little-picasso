import io
import os
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)

def test_endpoints():
    print("=" * 60)
    print("1. 메인 웹 페이지 GET / 테스트")
    res = client.get("/")
    assert res.status_code == 200, f"GET / 실패: {res.status_code}"
    assert "My Little Picasso" in res.text, "페이지 타이틀 누락"
    print("   -> [성공] 메인 페이지 정상 서빙")

    print("\n2. 잘못된 파일 업로드 오류 처리 테스트 (400 Bad Request)")
    dummy_text = io.BytesIO(b"Hello world, this is a text file.")
    res_invalid = client.post(
        "/api/generate-diary",
        files={"file": ("test.txt", dummy_text, "text/plain")},
        data={"language": "ko", "length": "short"}
    )
    assert res_invalid.status_code == 400, f"예상치 못한 상태 코드: {res_invalid.status_code}"
    print(f"   -> [성공] 유효하지 않은 파일 검증 완료 ({res_invalid.json().get('detail')})")

    print("\n2-1. 너무 큰 파일(15MB 초과) 업로드 오류 처리 테스트")
    # 16MB 더미 이미지 데이터
    large_data = io.BytesIO(b"0" * (16 * 1024 * 1024))
    res_large = client.post(
        "/api/generate-diary",
        files={"file": ("large.png", large_data, "image/png")},
        data={"language": "ko", "length": "short"}
    )
    assert res_large.status_code == 400, f"대용량 파일 제한 실패: {res_large.status_code}"
    print(f"   -> [성공] 대용량 파일 검증 완료 ({res_large.json().get('detail')})")

    print("\n3. 실제 사진 업로드 및 AI 그림일기 생성 POST /api/generate-diary 테스트")
    sample_path = Path("sample_test.png")
    if not sample_path.exists():
        raise FileNotFoundError("sample_test.png 파일이 없습니다.")

    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    res_gen = client.post(
        "/api/generate-diary",
        files={"file": ("sample_test.png", file_bytes, "image/png")},
        data={
            "language": "ko",
            "length": "short",
            "notes": "엄마랑 맛있게 먹었다고 써줘"
        }
    )

    assert res_gen.status_code == 200, f"API 실패: {res_gen.status_code} - {res_gen.text}"
    data = res_gen.json()
    print("   -> [성공] 그림일기 생성 완료!")
    print(f"      제목: {data.get('title')}")
    print(f"      본문:\n{data.get('diary_text')}")

    print("\n4. 템플릿 합성 POST /api/render-template 테스트")
    res_render = client.post(
        "/api/render-template",
        files={"file": ("sample_test.png", file_bytes, "image/png")},
        data={
            "title": data.get("title", "맛있는 사과"),
            "date_str": "2026년 10월 15일 목요일",
            "weather": "맑음",
            "content": data.get("diary_text", "나는 오늘 사과를 먹었다.")
        }
    )

    assert res_render.status_code == 200, f"렌더링 실패: {res_render.status_code}"
    assert res_render.headers["content-type"] == "image/png", "MIME 타입 불일치"

    rendered_img = Image.open(io.BytesIO(res_render.content))
    print(f"   -> [성공] PNG 렌더링 완료 (크기: {rendered_img.size}, 포맷: {rendered_img.format})")
    
    # 결과 이미지 저장
    rendered_img.save("test_e2e_output.png")
    print("   -> 최종 E2E 합성 이미지 test_e2e_output.png 저장 완료")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()

