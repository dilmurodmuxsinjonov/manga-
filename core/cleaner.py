"""
Manga Bubble Cleaner & Inpainter (Matnni Tozalash va Qayta Tiklash Moduli).
Pufakcha ichidagi asl (yaponcha, inglizcha, koreyscha) matnlarni manga fonini buzmasdan
tozalaydi va yangi o'zbekcha matn yozish uchun tayyorlaydi.
"""

from typing import List, Tuple
import cv2
import numpy as np


class MangaBubbleCleaner:
    def __init__(self, inpaint_radius: int = 3):
        self.inpaint_radius = inpaint_radius

    def clean_bubble(self, image: np.ndarray, box: Tuple[int, int, int, int], pad_ratio: float = 0.08) -> np.ndarray:
        """
        Berilgan bitta pufakcha hududidagi matnni tozalaydi.
        :param image: BGR formatidagi manga sahifasi
        :param box: (x, y, w, h) pufakcha koordinatalari
        :param pad_ratio: Chekka ramkalarni saqlab qolish uchun ichki qirqish foizi
        :return: Tozalangan tasvir nusxasi
        """
        img_out = image.copy()
        x, y, w, h = box
        img_h, img_w = image.shape[:2]

        # Chegaralarni xavfsiz kesish
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(img_w, x + w)
        y2 = min(img_h, y + h)

        if x2 <= x1 or y2 <= y1:
            return img_out

        roi = img_out[y1:y2, x1:x2]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Pufakchaning qalin qora chizig'ini (border) o'chirib yubormaslik uchun ichki pad
        pad_x = int(w * pad_ratio)
        pad_y = int(h * pad_ratio)

        # Matn qora/to'q rangda bo'ladi (thresholding)
        # Oq fonga nisbatan qora piksellarni topish
        _, text_mask = cv2.threshold(roi_gray, 185, 255, cv2.THRESH_BINARY_INV)

        # Chegaralarni maskadan olib tashlash (chekka chiziq qoladi)
        if pad_x > 0 and pad_y > 0 and (roi.shape[0] > 2 * pad_y) and (roi.shape[1] > 2 * pad_x):
            border_mask = np.zeros_like(text_mask)
            border_mask[pad_y:-pad_y, pad_x:-pad_x] = 255
            text_mask = cv2.bitwise_and(text_mask, border_mask)

        # Maskani biroz kengaytirish (harf qirralarini to'liq qamrab olish)
        dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        text_mask = cv2.dilate(text_mask, dilate_kernel, iterations=1)

        # Fon rangini aniqlash (pufakchaning fon rangi odatda oq yoki juda och kulrang)
        non_text_pixels = roi[text_mask == 0]
        if len(non_text_pixels) > 0:
            bg_color = np.median(non_text_pixels, axis=0).astype(np.uint8)
        else:
            bg_color = np.array([255, 255, 255], dtype=np.uint8)

        # Agar fon deyarli toza oq bo'lsa (manga pufakchalarining 90% holati)
        if np.mean(bg_color) > 235:
            # To'g'ridan-to'g'ri toza fon bilan to'ldirish (juda silliq va sifatli chiqadi)
            roi[text_mask == 255] = bg_color
            img_out[y1:y2, x1:x2] = roi
        else:
            # Murakkab yoki gradient fonlar uchun Telea Inpainting algoritmi
            cleaned_roi = cv2.inpaint(roi, text_mask, self.inpaint_radius, cv2.INPAINT_TELEA)
            img_out[y1:y2, x1:x2] = cleaned_roi

        return img_out

    def clean_all_bubbles(self, image: np.ndarray, boxes: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """Sahifadagi barcha pufakchalarni tozalaydi."""
        cleaned = image.copy()
        for box in boxes:
            cleaned = self.clean_bubble(cleaned, box)
        return cleaned
