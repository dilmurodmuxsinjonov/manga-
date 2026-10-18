"""
Manga Pipeline (To'liq Tarjima va Lokalizatsiya Jarayoni).
Manga sahifasini qabul qilishdan tortib, pufakchalarni aniqlash,
tozalash, mazmunli O'zbekcha tarjima qilish va shriftlashgacha
bo'lgan to'liq zanjirni boshqaruvchi markaziy modul.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np
from PIL import Image

from core.detector import MangaBubbleDetector, BubbleBox
from core.cleaner import MangaBubbleCleaner
from core.ocr import MangaOCR
from core.translator import MangaTranslator
from core.typesetter import MangaTypesetter


class MangaPipeline:
    def __init__(
        self,
        translator: Optional[MangaTranslator] = None,
        font_path: Optional[str] = None
    ):
        self.detector = MangaBubbleDetector()
        self.cleaner = MangaBubbleCleaner()
        self.ocr = MangaOCR()
        self.translator = translator or MangaTranslator()
        self.typesetter = MangaTypesetter(font_path=font_path)

    def process_page(
        self,
        image_input: str | np.ndarray | Image.Image,
        genre: str = "Shonen",
        character_hint: str = "",
        custom_bubbles: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Bitta manga sahifasini to'liq qayta ishlaydi.
        :param image_input: Fayl yo'li, numpy massiv (BGR) yoki PIL Image
        :param genre: Manga janri ('Shonen', 'Seinen', 'Komediya', 'Romantika', 'Tarixiy/Murim')
        :param character_hint: Qahramonlar yoki vaziyat haqida qo'shimcha ma'lumot
        :param custom_bubbles: Foydalanuvchi tomonidan qo'lda belgilangan yoki tahrirlangan pufakchalar
        :return: Natija lug'ati (asl tasvir, tozalangan tasvir, tayyor o'zbekcha tasvir, pufakchalar ro'yxati)
        """
        # 1. Tasvirni numpy va PIL formatlariga keltirish
        if isinstance(image_input, str):
            image_bgr = cv2.imread(image_input)
            if image_bgr is None:
                raise ValueError(f"Tasvir yuklanmadi: {image_input}")
        elif isinstance(image_input, Image.Image):
            image_rgb = np.array(image_input)
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_input

        # 2. Pufakchalarni aniqlash
        bubbles: List[BubbleBox] = []
        if custom_bubbles:
            for cb in custom_bubbles:
                bubbles.append(
                    BubbleBox(
                        id=cb.get("id", 1),
                        x=cb["x"],
                        y=cb["y"],
                        w=cb["w"],
                        h=cb["h"],
                        text_raw=cb.get("text_raw", ""),
                        text_uz=cb.get("text_uz", ""),
                        is_sfx=cb.get("is_sfx", False),
                        genre_tone=genre
                    )
                )
        else:
            bubbles = self.detector.detect_bubbles(image_bgr)

        # 3. Har bir pufakchadan matnni o'qish (agar oldindan berilmagan bo'lsa)
        for b in bubbles:
            if not b.text_raw:
                roi = image_bgr[b.y:b.y+b.h, b.x:b.x+b.w]
                b.text_raw = self.ocr.extract_text_from_crop(roi)

        # 4. Pufakchalardagi asl matnni tozalash
        boxes = [(b.x, b.y, b.w, b.h) for b in bubbles]
        cleaned_bgr = self.cleaner.clean_all_bubbles(image_bgr, boxes)

        # 5. Mazmunli O'zbek tiliga tarjima qilish
        raw_texts = [b.text_raw for b in bubbles]
        # Agar text_uz oldindan foydalanuvchi tomonidan berilmagan bo'lsa:
        texts_to_translate = []
        indices_to_translate = []
        for i, b in enumerate(bubbles):
            if not b.text_uz:
                texts_to_translate.append(b.text_raw)
                indices_to_translate.append(i)

        if texts_to_translate:
            translated_uz_list = self.translator.translate_batch(
                texts=texts_to_translate,
                genre=genre,
                character_hint=character_hint
            )
            for idx, uz_text in zip(indices_to_translate, translated_uz_list):
                bubbles[idx].text_uz = uz_text
                bubbles[idx].genre_tone = genre

        # 6. O'zbekcha matnni manga shrifti bilan chizish (Typesetting)
        cleaned_rgb = cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB)
        final_pil = Image.fromarray(cleaned_rgb)

        for b in bubbles:
            if b.text_uz:
                final_pil = self.typesetter.render_bubble_text(
                    image_pil=final_pil,
                    box=(b.x, b.y, b.w, b.h),
                    text=b.text_uz,
                    is_sfx=b.is_sfx
                )

        final_rgb = np.array(final_pil)
        final_bgr = cv2.cvtColor(final_rgb, cv2.COLOR_RGB2BGR)

        return {
            "original_bgr": image_bgr,
            "cleaned_bgr": cleaned_bgr,
            "final_bgr": final_bgr,
            "final_pil": final_pil,
            "bubbles": [b.to_dict() for b in bubbles]
        }

    def process_chapter(
        self,
        input_dir: str,
        output_dir: str,
        genre: str = "Shonen"
    ) -> List[str]:
        """
        Butun bir bob (chapter) papkasidagi barcha sahifalarni tarjima qilib saqlaydi.
        """
        os.makedirs(output_dir, exist_ok=True)
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        files = sorted([
            f for f in os.listdir(input_dir)
            if os.path.splitext(f.lower())[1] in valid_exts
        ])

        output_paths = []
        for f in files:
            in_path = os.path.join(input_dir, f)
            out_path = os.path.join(output_dir, f"uz_{f}")
            res = self.process_page(in_path, genre=genre)
            cv2.imwrite(out_path, res["final_bgr"])
            output_paths.append(out_path)

        return output_paths
