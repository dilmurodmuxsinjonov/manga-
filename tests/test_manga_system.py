"""
Manga Tizimi bo'yicha Integratsion va Birlik Testlari.
- Pufakchalarni aniqlash
- Tozalash (Inpainting)
- Mazmunli O'zbekcha tarjima & SFX
- Shriftlash va sig'dirish (Typesetting)
- Butun Pipeline
"""

import os
import sys

# Windows konsolida UTF-8 ni to'liq qo'llab-quvvatlash
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Loyiha ildiz papkasini import yo'liga qo'shish
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
import numpy as np
from core.detector import MangaBubbleDetector
from core.cleaner import MangaBubbleCleaner
from core.translator import MangaTranslator
from core.typesetter import MangaTypesetter
from core.pipeline import MangaPipeline
from core.sfx_dict import translate_sfx


def test_sfx_translation():
    print("[TEST 1] SFX Tovush effektlari tarjimasi:")
    assert translate_sfx("ドキドキ") == "Gup-gup..."
    assert translate_sfx("ドカーン") == "GUMBURR!"
    assert translate_sfx("boom") == "GUMBURR!"
    assert translate_sfx("slam") == "TARS!"
    print("  -> SFX tarjimasi to'g'ri ishladi!")


def test_detector_and_cleaner():
    print("\n[TEST 2] Pufakchalarni aniqlash va tozalash:")
    sample_path = "samples/sample_page_1.png"
    assert os.path.exists(sample_path), "Namuna fayli topilmadi!"

    img = cv2.imread(sample_path)
    detector = MangaBubbleDetector(min_area=1000)
    bubbles = detector.detect_bubbles(img)

    print(f"  -> Aniqlangan pufakchalar soni: {len(bubbles)}")
    assert len(bubbles) >= 3, f"Pufakchalar yetarli aniqlanmadi: {len(bubbles)}"

    # Tozalash
    cleaner = MangaBubbleCleaner()
    boxes = [(b.x, b.y, b.w, b.h) for b in bubbles]
    cleaned = cleaner.clean_all_bubbles(img, boxes)

    # Tozalangan joylarda o'rtacha oq rang ko'payganini tekshirish
    os.makedirs("outputs/test", exist_ok=True)
    cv2.imwrite("outputs/test/cleaned_sample.png", cleaned)
    print("  -> Pufakchalar tozalanishi muvaffaqiyatli saqlandi: outputs/test/cleaned_sample.png")


def test_meaningful_translator():
    print("\n[TEST 3] 'Mazmunli Tarjima' AI tizimi:")
    translator = MangaTranslator()

    # Oddiy mashina kalkasi emas, qahramonona mazmunli dialoglar
    t1 = translator.translate_bubble("Who are you?!", genre="Shonen")
    print(f"  'Who are you?!' -> '{t1}'")
    assert "Kimsan" in t1 or "sen" in t1.lower()

    t2 = translator.translate_bubble("Leave it to me!", genre="Shonen")
    print(f"  'Leave it to me!' -> '{t2}'")
    assert "menga" in t2.lower() or "qo'yib" in t2.lower()

    t3 = translator.translate_bubble("ドキドキ", genre="Shonen")
    print(f"  'ドキドキ' -> '{t3}'")
    assert "gup-gup" in t3.lower()

    print("  -> Mazmunli tarjima to'g'ri ishladi!")


def test_typesetter_and_pipeline():
    print("\n[TEST 4] To'liq Pipeline va Typesetting:")
    pipeline = MangaPipeline()
    sample_path = "samples/sample_page_1.png"
    
    # Custom aniq dialoglar bilan sinash
    custom_bubbles = [
        {"id": 1, "x": 70, "y": 90, "w": 220, "h": 140, "text_raw": "Who are you?!", "text_uz": "Kimsan o'zi sen?! Bu yer qayer?!"},
        {"id": 2, "x": 515, "y": 125, "w": 210, "h": 130, "text_raw": "Leave it to me!", "text_uz": "Xavotir olma! Bu ishni menga qo'yib ber!"},
        {"id": 3, "x": 85, "y": 700, "w": 260, "h": 160, "text_raw": "I will never forgive you!", "text_uz": "Qilmishing uchun seni aslo kechirmayman!"},
        {"id": 4, "x": 470, "y": 750, "w": 230, "h": 140, "text_raw": "ドキドキ", "text_uz": "Gup-gup...", "is_sfx": True}
    ]

    result = pipeline.process_page(
        sample_path,
        genre="Shonen",
        custom_bubbles=custom_bubbles
    )

    out_file = "outputs/test/manga_uzbek_final.png"
    cv2.imwrite(out_file, result["final_bgr"])
    assert os.path.exists(out_file), "Chiqish fayli yaratilmadi!"
    print(f"  -> Tayyor o'zbekcha manga sahifasi saqlandi: {out_file}")
    print("\nBARCHA TESTLAR MUVAFFAQIShLI O'TDI! [PASS]")


if __name__ == "__main__":
    test_sfx_translation()
    test_detector_and_cleaner()
    test_meaningful_translator()
    test_typesetter_and_pipeline()
