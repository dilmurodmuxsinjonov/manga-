"""
Manga OCR (Matnni Tanish va Ajratib Olish Moduli).
Manga pufakchasidagi yaponcha, inglizcha yoki koreyscha matnni
aniq o'qib olish (Vision AI va lokal modellar orqali).
"""

import os
import json
import base64
import logging
from typing import List, Tuple, Optional
import cv2
import numpy as np
import httpx

logger = logging.getLogger("manga_ocr")


class MangaOCR:
    def __init__(self, use_vision_ai: bool = True):
        self.use_vision_ai = use_vision_ai
        self.groq_key = os.environ.get("GROQ_API_KEY", "")
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.openai_key = os.environ.get("OPENAI_API_KEY", "")

    def extract_text_from_crop(self, roi_bgr: np.ndarray) -> str:
        """
        Pufakchadan qirqib olingan tasvirdan matnni o'qiydi.
        """
        if roi_bgr is None or roi_bgr.size == 0:
            return ""

        # Agar Vision AI mavjud bo'lsa (OpenAI / OpenRouter)
        if self.use_vision_ai and (self.openai_key or self.openrouter_key):
            try:
                text = self._vision_ai_ocr(roi_bgr)
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Vision AI OCR xatosi: {e}")

        # Lokal yoki zaxira tahlil
        return self._fallback_ocr(roi_bgr)

    def _vision_ai_ocr(self, roi_bgr: np.ndarray) -> str:
        """Kichik pufakcha tasvirini Vision modeliga yuborib matnni o'qish."""
        # JPEG ga aylantirish
        success, encoded_img = cv2.imencode(".jpg", roi_bgr)
        if not success:
            return ""
        
        b64_data = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64_data}"

        prompt = (
            "Read and transcribe the exact text written inside this manga/comic speech bubble. "
            "Output ONLY the transcribed text. Do not add explanations, notes, or quotes. "
            "If Japanese or Korean, preserve original characters or romaji."
        )

        headers = {"Content-Type": "application/json"}
        if self.openai_key and not self.openai_key.startswith("sk-or-"):
            url = "https://api.openai.com/v1/chat/completions"
            headers["Authorization"] = f"Bearer {self.openai_key}"
            model = "gpt-4o-mini"
        elif self.openrouter_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers["Authorization"] = f"Bearer {self.openrouter_key}"
            headers["HTTP-Referer"] = "https://github.com/dilmurodmuxsinjonov/manga-"
            model = "nvidia/nemotron-3.5-super-vl:free"
        else:
            return self._fallback_ocr(roi_bgr)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ],
            "max_tokens": 120,
            "temperature": 0.1
        }

        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    def _fallback_ocr(self, roi_bgr: np.ndarray) -> str:
        """
        Zaxira qoidalar: Agar tasvirda matn mavjud bo'lsa,
        test yoki dastlabki tahlil uchun indikator qaytaradi.
        """
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        mean_val = np.mean(gray)
        std_val = np.std(gray)
        
        if std_val < 8:
            return "" # Bo'sh pufakcha
        return "..."
