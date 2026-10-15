import io
import os
import re
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont

# 프로젝트 루트 및 폰트 경로
BASE_DIR = Path(__file__).resolve().parent.parent
FONTS_DIR = BASE_DIR / "assets" / "fonts"

# 기본 폰트 파일 탐색 체인
def get_font_path(bold: bool = False) -> Optional[str]:
    candidate_names = (
        ["NanumGothic-Bold.ttf", "malgunbd.ttf", "NanumSquareRoundB.ttf"]
        if bold
        else ["NanumGothic-Regular.ttf", "malgun.ttf", "NanumSquareRoundR.ttf"]
    )
    # 1. assets/fonts 디렉터리
    for name in candidate_names:
        p = FONTS_DIR / name
        if p.exists():
            return str(p)

    # 2. Windows 시스템 폰트
    win_fonts = Path(r"C:\Windows\Fonts")
    if win_fonts.exists():
        for name in candidate_names:
            p = win_fonts / name
            if p.exists():
                return str(p)

    # 3. Linux 시스템 폰트 (Cloud Run / Debian / Ubuntu)
    linux_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for lp in linux_paths:
        if os.path.exists(lp):
            return lp

    return None


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    font_path = get_font_path(bold=bold)
    if font_path:
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


# A4 캔버스 규격 (200 DPI 기준 고해상도 규격)
CANVAS_WIDTH = 1654
CANVAS_HEIGHT = 2338

# 색상 팔레트 (어린이 그림일기장 감성)
COLOR_BG = (255, 255, 255)            # 종이 흰색
COLOR_OUTLINE = (45, 52, 58)          # 정갈한 차콜 블랙
COLOR_GRID_OUTER = (75, 85, 99)       # 격자 외곽선
COLOR_GRID_CROSS = (220, 226, 235)    # 칸 안쪽 십자 가이드 점선
COLOR_TEXT_MAIN = (25, 30, 36)        # 본문 글씨
COLOR_PHOTO_BG = (248, 250, 252)      # 사진 영역 배경


def draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    start: Tuple[float, float],
    end: Tuple[float, float],
    fill: Tuple[int, int, int],
    dash_length: int = 5,
    space_length: int = 4,
    width: int = 1,
):
    """가이드용 점선 그리기"""
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    dist = (dx**2 + dy**2) ** 0.5
    if dist == 0:
        return

    step = dash_length + space_length
    num_steps = int(dist // step)

    for i in range(num_steps + 1):
        s_dist = i * step
        e_dist = min(s_dist + dash_length, dist)
        if s_dist >= dist:
            break
        sx = x1 + (dx * s_dist / dist)
        sy = y1 + (dy * s_dist / dist)
        ex = x1 + (dx * e_dist / dist)
        ey = y1 + (dy * e_dist / dist)
        draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)


def render_diary_template(
    title: str,
    date_str: str,
    weather: str,
    content: str,
    photo_image: Optional[Image.Image] = None,
) -> Image.Image:
    """
    고정된 A4 세로형 그림일기 템플릿에 원본 사진과 텍스트를 배치하여 Pillow Image로 반환합니다.
    """
    # 1. 기본 흰색 캔버스 생성
    canvas = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=COLOR_BG)
    draw = ImageDraw.Draw(canvas)

    # 폰트 로드
    font_main_title = load_font(size=64, bold=True)
    font_meta = load_font(size=30, bold=False)
    font_meta_bold = load_font(size=32, bold=True)
    font_diary_title = load_font(size=38, bold=True)
    font_char = load_font(size=44, bold=True)

    # 여백 및 영역 정의
    margin_x = 80
    margin_top = 70
    content_width = CANVAS_WIDTH - (margin_x * 2)  # 1494 px

    # 2. 전체 페이지 테두리 (학습지 느낌의 이중선 테두리)
    outer_box = [margin_x // 2, margin_top // 2, CANVAS_WIDTH - (margin_x // 2), CANVAS_HEIGHT - (margin_top // 2)]
    draw.rectangle(outer_box, outline=COLOR_OUTLINE, width=4)
    inner_box = [margin_x // 2 + 8, margin_top // 2 + 8, CANVAS_WIDTH - (margin_x // 2) - 8, CANVAS_HEIGHT - (margin_top // 2) - 8]
    draw.rectangle(inner_box, outline=(200, 205, 215), width=2)

    # 3. 상단 헤더: '오늘의 그림일기'
    header_text = "오늘의 그림일기"
    header_box = [margin_x, 70, margin_x + content_width, 160]
    draw.rounded_rectangle(header_box, radius=18, fill=(245, 247, 250), outline=COLOR_OUTLINE, width=3)

    # 헤더 텍스트 중앙 정렬
    tb = draw.textbbox((0, 0), header_text, font=font_main_title)
    th_w = tb[2] - tb[0]
    th_h = tb[3] - tb[1]
    hx = margin_x + (content_width - th_w) / 2
    hy = 70 + (90 - th_h) / 2 - 4
    draw.text((hx, hy), header_text, fill=COLOR_TEXT_MAIN, font=font_main_title)

    # 4. 날짜 및 날씨 영역
    meta_y = 180
    meta_h = 70
    meta_box = [margin_x, meta_y, margin_x + content_width, meta_y + meta_h]
    draw.rectangle(meta_box, outline=COLOR_OUTLINE, width=2)

    # 날짜 텍스트
    display_date = date_str.strip() if date_str else "2026년 10월 15일"
    draw.text((margin_x + 25, meta_y + 18), "날짜 :", fill=COLOR_OUTLINE, font=font_meta_bold)
    draw.text((margin_x + 110, meta_y + 19), display_date, fill=COLOR_TEXT_MAIN, font=font_meta)

    # 세로 구분선
    split_x = margin_x + int(content_width * 0.7)
    draw.line([(split_x, meta_y), (split_x, meta_y + meta_h)], fill=COLOR_OUTLINE, width=2)

    # 날씨 텍스트 (이모지 등이 폰트에 없을 경우 대비해 텍스트 정제)
    clean_weather = re.sub(r"[^\w\s가-힣a-zA-Z]", "", weather).strip() or "맑음"
    draw.text((split_x + 25, meta_y + 18), "날씨 :", fill=COLOR_OUTLINE, font=font_meta_bold)
    draw.text((split_x + 110, meta_y + 19), clean_weather, fill=COLOR_TEXT_MAIN, font=font_meta)

    # 5. 일기 제목 영역
    title_y = 265
    title_h = 75
    title_box = [margin_x, title_y, margin_x + content_width, title_y + title_h]
    draw.rectangle(title_box, outline=COLOR_OUTLINE, width=2)
    draw.text((margin_x + 25, title_y + 20), "제목 :", fill=COLOR_OUTLINE, font=font_diary_title)

    display_title = title.strip() if title else "즐거운 하루"
    draw.text((margin_x + 130, title_y + 20), display_title, fill=COLOR_TEXT_MAIN, font=font_diary_title)

    # 6. 사진 배치 영역
    photo_y = 355
    photo_h = 1000
    photo_box = [margin_x, photo_y, margin_x + content_width, photo_y + photo_h]
    draw.rectangle(photo_box, fill=COLOR_PHOTO_BG, outline=COLOR_OUTLINE, width=3)

    if photo_image is not None:
        # 비율을 유지하며 photo_box 안에 꽉 채우거나 맞춤 (Letterbox fit)
        avail_w = content_width - 16
        avail_h = photo_h - 16
        p_w, p_h = photo_image.size

        ratio = min(avail_w / p_w, avail_h / p_h)
        new_w = int(p_w * ratio)
        new_h = int(p_h * ratio)

        resized_photo = photo_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        offset_x = margin_x + 8 + (avail_w - new_w) // 2
        offset_y = photo_y + 8 + (avail_h - new_h) // 2
        canvas.paste(resized_photo, (offset_x, offset_y))
    else:
        # 사진이 없을 때 안내 텍스트 표시
        ph_text = "사진이 들어가는 자리입니다"
        tb = draw.textbbox((0, 0), ph_text, font=font_meta)
        pt_w = tb[2] - tb[0]
        pt_h = tb[3] - tb[1]
        draw.text(
            (margin_x + (content_width - pt_w) / 2, photo_y + (photo_h - pt_h) / 2),
            ph_text,
            fill=(160, 170, 185),
            font=font_meta,
        )

    # 7. 하단 원고지 격자 글쓰기 영역
    cols = 14
    rows = 6
    grid_y_start = 1380
    grid_total_w = content_width

    cell_w = grid_total_w / cols  # 1494 / 14 = 106.71 px
    cell_h = 138                 # 한 칸의 높이 (6줄 * 138 = 828 px)

    # 문장부호 금칙 목록 (줄 첫 칸에 단독으로 오지 않도록 함)
    NO_HEAD_PUNCT = {".", ",", "!", "?", ":", ";", ")", "]", "}", "”", "’"}

    raw_lines = [l.strip() for l in content.split("\n") if l.strip()]
    if not raw_lines and content.strip():
        raw_lines = [content.strip()]

    grid_chars: List[List[str]] = [["" for _ in range(cols)] for _ in range(rows)]

    curr_r = 0
    curr_c = 0

    for line in raw_lines:
        if curr_r >= rows:
            break
        i = 0
        chars = list(line)
        while i < len(chars):
            if curr_r >= rows:
                break
            ch = chars[i]

            # 줄의 첫 칸에 공백이 오면 건너뜀 (원고지 첫 칸 공백 방지)
            if curr_c == 0 and ch == " ":
                i += 1
                continue

            # 줄의 첫 칸에 문장부호가 오려고 할 때: 직전 줄 마지막 칸에 병합하거나 직전 칸으로 이동
            if curr_c == 0 and ch in NO_HEAD_PUNCT and curr_r > 0:
                # 이전 줄 마지막 칸에 부호 덧붙임
                grid_chars[curr_r - 1][cols - 1] += ch
                i += 1
                continue

            # 마지막 칸인데 다음 글자가 마침표나 쉼표 등 문장부호인 경우, 현재 칸에 함께 수용
            if curr_c == cols - 1 and (i + 1 < len(chars)) and (chars[i + 1] in NO_HEAD_PUNCT):
                grid_chars[curr_r][curr_c] = ch + chars[i + 1]
                i += 2
                curr_c = 0
                curr_r += 1
                continue

            grid_chars[curr_r][curr_c] = ch
            curr_c += 1
            i += 1
            if curr_c >= cols:
                curr_c = 0
                curr_r += 1

        # 한 문장이 끝나면 다음 줄 첫 칸으로 개행
        if curr_c > 0 and curr_r < rows:
            curr_r += 1
            curr_c = 0

    # 격자 그리기 및 글자 렌더링
    for r in range(rows):
        for c in range(cols):
            x1 = margin_x + (c * cell_w)
            y1 = grid_y_start + (r * cell_h)
            x2 = margin_x + ((c + 1) * cell_w)
            y2 = grid_y_start + ((r + 1) * cell_h)

            # 격자 외곽 테두리
            draw.rectangle([x1, y1, x2, y2], outline=COLOR_GRID_OUTER, width=1)

            # 칸 내부 연한 십자 가이드 점선 (초등 알림장/글쓰기장 느낌)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            draw_dashed_line(draw, (x1 + 4, mid_y), (x2 - 4, mid_y), fill=COLOR_GRID_CROSS, dash_length=4, space_length=4)
            draw_dashed_line(draw, (mid_x, y1 + 4), (mid_x, y2 - 4), fill=COLOR_GRID_CROSS, dash_length=4, space_length=4)

            # 글자 렌더링 (칸 정중앙 배치)
            ch = grid_chars[r][c]
            if ch:
                tb = draw.textbbox((0, 0), ch, font=font_char)
                cw = tb[2] - tb[0]
                ch_h = tb[3] - tb[1]
                cx = x1 + (cell_w - cw) / 2
                # 한글 베이스라인 보정
                cy = y1 + (cell_h - ch_h) / 2 - 3
                draw.text((cx, cy), ch, fill=COLOR_TEXT_MAIN, font=font_char)

    # 전체 격자 바깥 둘레를 도톰한 선으로 마무리
    grid_outer_rect = [margin_x, grid_y_start, margin_x + content_width, grid_y_start + (rows * cell_h)]
    draw.rectangle(grid_outer_rect, outline=COLOR_OUTLINE, width=3)

    return canvas
