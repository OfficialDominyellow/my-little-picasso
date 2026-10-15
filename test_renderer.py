import os
from PIL import Image
from app.template_renderer import render_diary_template

def main():
    print("그림일기 템플릿 렌더링 테스트 시작...")
    
    # 1. 샘플 사진 로드 (이전에 만든 sample_test.png)
    sample_img_path = "sample_test.png"
    if os.path.exists(sample_img_path):
        photo = Image.open(sample_img_path)
    else:
        photo = None

    # 2. 렌더링 파라미터 준비
    title = "빨간 사과 그리기"
    date_str = "2026년 10월 15일 목요일"
    weather = "맑음 ☀️"
    content = "나는 오늘 빨간 사과를 그렸다.\n사과에 초록색 잎이 있다.\n사과가 아주 동그랗다."

    # 3. 템플릿 렌더링
    rendered_image = render_diary_template(
        title=title,
        date_str=date_str,
        weather=weather,
        content=content,
        photo_image=photo
    )

    output_path = "test_rendered_output.png"
    rendered_image.save(output_path, "PNG")
    print(f"렌더링 성공! 파일 저장됨: {output_path}")
    print(f"해상도: {rendered_image.size}")

if __name__ == "__main__":
    main()

