"""
Manga Bubble & Text Detector (Nutq Pufakchalarini Aniqlash Moduli).
Manga sahifasidagi nutq pufakchalari (speech bubbles), ramkalar va matn joylashgan
hududlarni OpenCV yordamida aniqlaydi va chegaralarini (bounding box) ajratadi.
"""

from dataclasses import dataclass
from typing import List, Tuple
import cv2
import numpy as np


@dataclass
class BubbleBox:
    id: int
    x: int
    y: int
    w: int
    h: int
    confidence: float = 1.0
    text_raw: str = ""
    text_uz: str = ""
    speaker: str = "Noma'lum"
    genre_tone: str = "Shonen"
    is_sfx: bool = False

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "confidence": round(self.confidence, 2),
            "text_raw": self.text_raw,
            "text_uz": self.text_uz,
            "speaker": self.speaker,
            "genre_tone": self.genre_tone,
            "is_sfx": self.is_sfx,
        }


class MangaBubbleDetector:
    def __init__(self, min_area: int = 1200, max_area_ratio: float = 0.45):
        """
        :param min_area: Pufakcha deb hisoblanadigan minimal maydon (pikselda)
        :param max_area_ratio: Sahifa umumiy maydoniga nisbatan maksimal pufakcha o'lchami
        """
        self.min_area = min_area
        self.max_area_ratio = max_area_ratio

    def detect_bubbles(self, image_np: np.ndarray) -> List[BubbleBox]:
        """
        Manga tasviridan nutq pufakchalarini avtomatik ajratib oladi.
        """
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np

        img_h, img_w = gray.shape[:2]
        total_area = img_h * img_w
        max_area = total_area * self.max_area_ratio

        # 1. Oq / och rangli pufakchalarni ajratish (Thresholding)
        _, thresh = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY)

        # 2. Morfologik operatsiyalar - matn bo'shliqlarini to'ldirish va konturni mustahkamlash
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))

        # 3. Konturlarni topish (RETR_TREE orqali ichki pufakchalarni ham aniqlash)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bubbles: List[BubbleBox] = []
        bubble_id = 1

        # Har bir konturni tekshirish
        candidates = []
        # Manga sahifasidagi odatiy pufakcha maydoni: 1500 dan 90000 px gacha
        max_bubble_area = min(max_area, total_area * 0.18)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area or area > max_bubble_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / max(h, 1)

            # Manga pufakchalari odatda elliptik yoki yumaloq to'rtburchak (0.35 dan 3.2 gacha)
            if 0.35 < aspect_ratio < 3.2:
                # Kontur ichida matn (qora piksellar / kontrast) borligini tekshirish
                roi_gray = gray[y:y+h, x:x+w]
                if roi_gray.size == 0:
                    continue

                mean_val = np.mean(roi_gray)
                std_val = np.std(roi_gray)

                # Pufakcha ichidagi fon och rangda (mean > 170) va matn bor (std > 8)
                if mean_val > 170 and std_val > 8:
                    candidates.append((x, y, w, h, area))

        # 4. Yapon manga o'qish tartibi bo'yicha saralash:
        # Manga an'anaviy ravishda o'ngdan chapga, yuqoridan pastga o'qiladi!
        # X koordinatasi teskari (img_w - x), Y koordinatasi to'g'ri tartibda
        candidates.sort(key=lambda b: (b[1] // 80, -b[0]))

        # 5. Qoplanuvchi (ichma-ich) to'rtburchaklarni birlashtirish / filtrlash
        filtered = self._non_max_suppression(candidates)

        for x, y, w, h, _ in filtered:
            bubbles.append(
                BubbleBox(
                    id=bubble_id,
                    x=int(x),
                    y=int(y),
                    w=int(w),
                    h=int(h),
                    confidence=0.92
                )
            )
            bubble_id += 1

        return bubbles

    def _non_max_suppression(self, boxes: List[Tuple[int, int, int, int, float]], iou_thresh: float = 0.3):
        """Ichma-ich yoki qisman qoplagan qutilarni tozalaydi."""
        if not boxes:
            return []

        clean_boxes = []
        for b in boxes:
            x1, y1, w1, h1, a1 = b
            keep = True
            for cb in clean_boxes:
                x2, y2, w2, h2, a2 = cb
                # Kesishtirish maydoni
                ix1 = max(x1, x2)
                iy1 = max(y1, y2)
                ix2 = min(x1 + w1, x2 + w2)
                iy2 = min(y1 + h1, y2 + h2)

                iw = max(0, ix2 - ix1)
                ih = max(0, iy2 - iy1)
                inter_area = iw * ih

                if inter_area > 0:
                    min_area = min(a1, a2)
                    if inter_area / min_area > 0.65:
                        keep = False
                        break
            if keep:
                clean_boxes.append(b)
        return clean_boxes
