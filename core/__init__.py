"""
MangaUz - Mazmunli Manga Tarjima va Lokalizatsiya Tizimi
"""

from core.detector import MangaBubbleDetector, BubbleBox
from core.cleaner import MangaBubbleCleaner
from core.ocr import MangaOCR
from core.translator import MangaTranslator
from core.typesetter import MangaTypesetter
from core.pipeline import MangaPipeline
from core.sfx_dict import SFX_DICTIONARY, translate_sfx

__all__ = [
    "MangaBubbleDetector",
    "BubbleBox",
    "MangaBubbleCleaner",
    "MangaOCR",
    "MangaTranslator",
    "MangaTypesetter",
    "MangaPipeline",
    "SFX_DICTIONARY",
    "translate_sfx",
]
