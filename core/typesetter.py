"""
Manga Typesetter (Matnni Joylashtirish va Shriftlash Moduli).
O'zbek tilidagi mazmunli tarjima matnini pufakcha o'lchamiga moslab,
manga uslubidagi qalin va tiniq shriftlar bilan chiroyli joylashtiradi.
"""

import os
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class MangaTypesetter:
    def __init__(self, font_path: Optional[str] = None):
        """
        :param font_path: TTF shrift fayli yo'li. Agar berilmasa, Windows tizimidagi
                          'comicbd.ttf' yoki 'arialbd.ttf' avtomatik olinadi.
        """
        self.font_path = font_path or self._find_best_font()

    def _find_best_font(self) -> str:
        candidates = [
            r"C:\Windows\Fonts\comicbd.ttf",
            r"C:\Windows\Fonts\comic.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\impact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return "arial.ttf"

    def render_bubble_text(
        self,
        image_pil: Image.Image,
        box: Tuple[int, int, int, int],
        text: str,
        is_sfx: bool = False,
        text_color: str = "#000000",
        stroke_color: str = "#FFFFFF",
        stroke_width: int = 2
    ) -> Image.Image:
        """
        Bitta pufakcha ichiga matnni o'lchamini hisoblagan holda markazlashtirib chizadi.
        :param image_pil: PIL Image nusxasi
        :param box: (x, y, w, h) pufakcha chegaralari
        :param text: O'zbekcha tarjima qilingan matn
        :param is_sfx: Agar tovush effekti bo'lsa, yirikroq va qalinroq chiziladi
        """
        if not text or not text.strip():
            return image_pil

        draw = ImageDraw.Draw(image_pil)
        x, y, w, h = box

        # Pufakcha chekkasiga tegib ketmasligi uchun xavfsiz maydon (padding)
        pad_x = int(w * 0.14)
        pad_y = int(h * 0.14)
        avail_w = max(20, w - 2 * pad_x)
        avail_h = max(20, h - 2 * pad_y)

        # Matnni pufakcha o'lchamiga mos keladigan eng yaxshi shrift o'lchamini topish
        font_size, lines = self._fit_text_to_box(text, avail_w, avail_h, is_sfx)

        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except Exception:
            font = ImageFont.load_default()

        # Har bir qatorning balandligi va umumiy blok balandligini hisoblash
        line_heights = []
        line_widths = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            line_widths.append(lw)
            line_heights.append(lh)

        total_text_h = sum(line_heights) + int(len(lines) * font_size * 0.25)
        
        # Vertikal markazlashtirish
        start_y = y + pad_y + max(0, (avail_h - total_text_h) // 2)

        curr_y = start_y
        for idx, line in enumerate(lines):
            lw = line_widths[idx]
            lh = line_heights[idx]
            
            # Gorizontal markazlashtirish
            line_x = x + pad_x + max(0, (avail_w - lw) // 2)

            # Matn atrofidagi oq kontur (Stroke) - harflar ravshan ko'rinishi uchun
            actual_stroke = stroke_width if not is_sfx else stroke_width + 2
            draw.text(
                (line_x, curr_y),
                line,
                font=font,
                fill=text_color,
                stroke_width=actual_stroke,
                stroke_fill=stroke_color
            )
            curr_y += lh + int(font_size * 0.25)

        return image_pil

    def _fit_text_to_box(
        self,
        text: str,
        max_w: int,
        max_h: int,
        is_sfx: bool
    ) -> Tuple[int, List[str]]:
        """
        Matn satrlarini pufakchaga sig'dirish uchun shrift hajmini va
        qatorlarga bo'lishni iterativ optimallashtiradi.
        """
        words = text.split()
        if not words:
            return (14, [text])

        # SFX uchun yirikroq, dialog uchun odatiy oraliq
        min_font_size = 11
        max_font_size = 38 if not is_sfx else 52

        best_font_size = min_font_size
        best_lines = [text]

        # Yuqori o'lchamdan boshlab tekshirib kamaytirib borish
        for font_size in range(max_font_size, min_font_size - 1, -2):
            try:
                font = ImageFont.truetype(self.font_path, font_size)
            except Exception:
                font = ImageFont.load_default()

            lines = self._wrap_words(words, font, max_w)
            
            # Balandlikni tekshirish
            total_h = len(lines) * int(font_size * 1.3)
            if total_h <= max_h:
                # Barcha qatorlar kenglikka to'liq sig'yaptimi?
                fits_all_w = True
                dummy_img = Image.new("RGB", (1, 1))
                draw = ImageDraw.Draw(dummy_img)
                for l in lines:
                    bb = draw.textbbox((0, 0), l, font=font)
                    if (bb[2] - bb[0]) > max_w:
                        fits_all_w = False
                        break

                if fits_all_w:
                    best_font_size = font_size
                    best_lines = lines
                    break

        return (best_font_size, best_lines)

    def _wrap_words(self, words: List[str], font: ImageFont.ImageFont, max_w: int) -> List[str]:
        """So'zlarni berilgan kenglik bo'yicha tabiiy qatorlarga ajratish."""
        dummy_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy_img)

        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bb = draw.textbbox((0, 0), test_line, font=font)
            line_w = bb[2] - bb[0]

            if line_w <= max_w:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # So'zning o'zi bitta qatordan uzun bo'lsa
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        return lines
