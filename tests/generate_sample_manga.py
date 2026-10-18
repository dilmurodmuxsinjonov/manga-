"""
Test va ko'rgazma uchun namunaviy Manga sahifasi generatori.
Haqiqiy manga sahifalariga o'xshash panellar, qahramon chizgilari,
nutq pufakchalari va dialoglarni yaratadi.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_sample_manga_page(output_path: str = "samples/sample_page_1.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 800x1200 o'lchamdagi manga sahifasi (oq fon)
    width, height = 800, 1150
    img = np.ones((height, width, 3), dtype=np.uint8) * 255

    # 1. Panellar chizish (Manga ramkalari)
    # Panel 1: Yuqori panel (0 to 520)
    cv2.rectangle(img, (40, 40), (760, 520), (0, 0, 0), 4)
    # Panel 2: Pastki chap panel (540 to 1100, 40 to 390)
    cv2.rectangle(img, (40, 540), (390, 1100), (0, 0, 0), 4)
    # Panel 3: Pastki o'ng panel (540 to 1100, 410 to 760)
    cv2.rectangle(img, (410, 540), (760, 1100), (0, 0, 0), 4)

    # 2. Anime/Manga chizgilari (fon va harakat chiziqlari)
    # Yuqori panelda harakat (speed lines) chiziqlari
    center_x, center_y = 400, 280
    for angle in range(0, 360, 12):
        rad = np.deg2rad(angle)
        x1 = int(center_x + np.cos(rad) * 120)
        y1 = int(center_y + np.sin(rad) * 90)
        x2 = int(center_x + np.cos(rad) * 450)
        y2 = int(center_y + np.sin(rad) * 350)
        # Faqat panel 1 ichida chizish
        if 40 <= x2 <= 760 and 40 <= y2 <= 520:
            cv2.line(img, (x1, y1), (x2, y2), (210, 210, 210), 1)

    # Qahramon silueti (markazda)
    cv2.circle(img, (400, 280), 65, (40, 40, 40), -1)
    cv2.ellipse(img, (400, 400), (110, 70), 0, 0, 360, (50, 50, 50), -1)

    # 3. Nutq pufakchalari (Speech bubbles)
    # Pufakcha 1: Yuqori chapda (qahramonning hayratlanishi)
    cv2.ellipse(img, (180, 160), (110, 70), 0, 0, 360, (255, 255, 255), -1)
    cv2.ellipse(img, (180, 160), (110, 70), 0, 0, 360, (0, 0, 0), 3)
    # Pufakcha dumchasi (tail)
    pts1 = np.array([[240, 195], [320, 240], [225, 215]], np.int32)
    cv2.fillPoly(img, [pts1], (255, 255, 255))
    cv2.polylines(img, [pts1], False, (0, 0, 0), 3)

    # Pufakcha 2: Yuqori o'ngda (javob dialogi)
    cv2.ellipse(img, (620, 190), (105, 65), 0, 0, 360, (255, 255, 255), -1)
    cv2.ellipse(img, (620, 190), (105, 65), 0, 0, 360, (0, 0, 0), 3)

    # Pufakcha 3: Pastki chap panelda (shijoatli so'zlar)
    cv2.ellipse(img, (215, 780), (130, 80), 0, 0, 360, (255, 255, 255), -1)
    cv2.ellipse(img, (215, 780), (130, 80), 0, 0, 360, (0, 0, 0), 3)

    # Pufakcha 4: Pastki o'ng panelda (SFX yoki reaktsiya)
    cv2.ellipse(img, (585, 820), (115, 70), 0, 0, 360, (255, 255, 255), -1)
    cv2.ellipse(img, (585, 820), (115, 70), 0, 0, 360, (0, 0, 0), 3)

    # PIL orqali pufakchalar ichiga asl matnlarni yozish
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    font_path = r"C:\Windows\Fonts\arialbd.ttf"
    try:
        font = ImageFont.truetype(font_path, 18)
        font_sfx = ImageFont.truetype(font_path, 24)
    except Exception:
        font = ImageFont.load_default()
        font_sfx = font

    # Bubble 1 matni:
    draw.text((120, 140), "Who are you?!", font=font, fill=(0, 0, 0))
    draw.text((105, 165), "What is this place?!", font=font, fill=(0, 0, 0))

    # Bubble 2 matni:
    draw.text((555, 175), "Don't worry.", font=font, fill=(0, 0, 0))
    draw.text((540, 198), "Leave it to me!", font=font, fill=(0, 0, 0))

    # Bubble 3 matni:
    draw.text((125, 760), "I will never forgive", font=font, fill=(0, 0, 0))
    draw.text((140, 785), "what you did!", font=font, fill=(0, 0, 0))

    # Bubble 4 matni (SFX):
    draw.text((545, 805), "ドキドキ", font=font_sfx, fill=(0, 0, 0))

    # Qayta BGR ga o'tkazib saqlash
    final_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, final_cv)
    return output_path


if __name__ == "__main__":
    out = create_sample_manga_page()
    print(f"Sample manga page created at: {out}")
