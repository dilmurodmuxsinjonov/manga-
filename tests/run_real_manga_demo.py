"""
Haqiqiy Yaponcha Manga Sahifasini Mazmunli O'zbek Tiliga Lokalizatsiya Qilish Demo Dasturi.
Asl Manga: "佐藤さんは知っていた - 猫麦" (Sato-san knew it - Nekomugi)
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.cleaner import MangaBubbleCleaner
from core.typesetter import MangaTypesetter


def run_demo():
    input_image_path = "samples/japanese_raw_manga.png"
    output_image_path = "outputs/real_manga_uzbek_localized.png"
    os.makedirs("outputs", exist_ok=True)

    print(f"[*] Asl yaponcha manga sahifasi ochilmoqda: {input_image_path}")
    img_bgr = cv2.imread(input_image_path)
    if img_bgr is None:
        raise FileNotFoundError(f"Fayl topilmadi: {input_image_path}")

    h, w = img_bgr.shape[:2]
    print(f"[*] Sahifa o'lchamlari: {w}x{h} piksel")

    # Aniqlangan va tasdiqlangan asosiy pufakchalar koordinatalari va dialoglari
    bubbles = [
        {
            "id": 1,
            "box": (1230, 20, 255, 330),
            "ja": "ねえ、ねえ、めいは坂本のことどう思う？",
            "uz": "Hoy, Mey... o'zi Sakamoto haqida nima deb o'ylaysan?",
            "is_sfx": False
        },
        {
            "id": 4,
            "box": (1100, 170, 168, 210),
            "ja": "坂本くん？",
            "uz": "Sakamotomi?",
            "is_sfx": False
        },
        {
            "id": 2,
            "box": (130, 15, 230, 200),
            "ja": "うーん、そうだなあ… 優しいよね",
            "uz": "Hm... qanday desam ekan... judayam samimiy va ko'ngli ochiq yigit-da.",
            "is_sfx": False
        },
        {
            "id": 6,
            "box": (1275, 410, 212, 320),
            "ja": "じゃあ他には？どんなところ？",
            "uz": "Xo'sh, yana-chi? Qaysi tomonlari yoqadi?",
            "is_sfx": False
        },
        {
            "id": 11,
            "box": (180, 1410, 330, 435),
            "ja": "あ、ええと… こないだね、髪型変えたらすぐに気付いてくれてっ！",
            "uz": "Ha, aytgandek! O'tgan safar soch turmagimni o'zgartirganimda, darrov payqab qoldi-ya!",
            "is_sfx": False
        },
        {
            "id": 10,
            "box": (810, 1435, 220, 415),
            "ja": "店の店員さんとかにも敬語使ってて偉いなとか…",
            "uz": "Keyin, do'kondagi sotuvchilarga ham 'Siz' deb, xushmuomala gaplashadi... judayam odobli yigit.",
            "is_sfx": False
        },
        {
            "id": 9,
            "box": (1360, 1390, 125, 315),
            "ja": "反応がいちいち面白いなとか…",
            "uz": "Har bir gapga reaksiyasiyam qiziq va kulgili-da...",
            "is_sfx": False
        },
        {
            "id": 13,
            "box": (655, 1565, 135, 280),
            "ja": "わあ、いいね！",
            "uz": "Voy, qoyil! Judayam zo'r-ku!",
            "is_sfx": False
        }
    ]

    cleaner = MangaBubbleCleaner(inpaint_radius=4)
    typesetter = MangaTypesetter()

    print("[*] 1-Bosqich: Pufakchalar ichidagi yaponcha matnlarni tozalash (Inpainting)...")
    cleaned_bgr = img_bgr.copy()
    for b in bubbles:
        cleaned_bgr = cleaner.clean_bubble(cleaned_bgr, b["box"], pad_ratio=0.06)

    # Tozalangan holatni oraliq tekshirish uchun saqlash
    cv2.imwrite("outputs/real_manga_cleaned.png", cleaned_bgr)
    print("    -> Tozalangan sahifa saqlandi: outputs/real_manga_cleaned.png")

    print("[*] 2-Bosqich: Mazmunli O'zbekcha tarjimalarni shriftlash (Typesetting)...")
    cleaned_rgb = cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cleaned_rgb)

    for b in bubbles:
        pil_img = typesetter.render_bubble_text(
            image_pil=pil_img,
            box=b["box"],
            text=b["uz"],
            is_sfx=b["is_sfx"],
            stroke_width=3
        )
        print(f"    [Pufakcha #{b['id']}]")
        print(f"      Asl Yaponcha: {b['ja']}")
        print(f"      Mazmunli O'zbekcha: {b['uz']}")

    final_rgb = np.array(pil_img)
    final_bgr = cv2.cvtColor(final_rgb, cv2.COLOR_RGB2BGR)

    cv2.imwrite(output_image_path, final_bgr)
    print(f"\n[+] MUVAFFAQIShLI YAKUNLANDI!")
    print(f"[+] Tayyor O'zbekcha Manga sahifasi: {output_image_path}")


if __name__ == "__main__":
    run_demo()
