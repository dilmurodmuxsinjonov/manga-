"""
MangaUz "Mazmunli Tarjima" Sun'iy Intellekt Tizimi (Core Translation Engine).

Biz shunchaki so'zma-so'z tarjima qilmaymiz — har bir qahramonning xarakteri,
vaziyatning dramasi, janr ruhiyati (Shonen, Seinen, Komediya, Romantika) va
O'zbek tilining boy, jonli ifodalarini qo'llagan holda MAZMUNLI lokalizatsiya qilamiz!
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import httpx

from core.sfx_dict import translate_sfx

logger = logging.getLogger("manga_translator")


GENRE_PROMPTS = {
    "Shonen": (
        "Janr: Shonen (Jangari, Shijoatli, Sarguzasht). "
        "Ohang: Qat'iyatli, baquvvat, jo'shqin va qahramonona. "
        "Murojaat: Tengdoshlar va do'stlar bilan 'sen', dushmanlar bilan g'azabli, qari ustozlar bilan 'Siz/Ustoz'. "
        "Misol: 'I won't lose to the likes of you!' -> 'Sen kabilarga yengiladigan ahmoq yo'q!'"
    ),
    "Seinen": (
        "Janr: Seinen (Jiddiy, Psixologik, Falsafiy, Realistik). "
        "Ohang: Og'ir-bosiq, chuqur, kinoyali yoki sovuqqon. "
        "Misol: 'The world is inherently cruel.' -> 'Bu dunyo asli shafqatsizlik ustiga qurilgan.'"
    ),
    "Komediya": (
        "Janr: Komediya va Kundalik Hayot. "
        "Ohang: Qiziqarli, hazilomuz, kulgili kinoyalar va jonli o'zbekcha iboralar. "
        "Misol: 'What on earth are you doing?!' -> 'Hoy, nima hangama qilyapsan bu yerda?!'"
    ),
    "Romantika": (
        "Janr: Shojo / Romantika / Drama. "
        "Ohang: Muloyim, his-tuyg'ularga to'la, samimiy, nozik hislar. "
        "Misol: 'I've always wanted to tell you...' -> 'Senga doim aytmoqchi edim... ammo yuragim dov bermasdi.'"
    ),
    "Tarixiy/Murim": (
        "Janr: Tarixiy, Murim, Fantastika (Xitoy/Koreya/Yaponiya saroy va jang san'ati). "
        "Ohang: Rasmiy, viqorli, qadimiy hikmatlar va oliyjanob so'zlar (Hazratim, Ustoz, Janobi oliylari). "
        "Misol: 'Greetings, Sect Leader!' -> 'Salomlar bo'lsin, Muhtaram Maktab Yetakchisi!'"
    )
}

SYSTEM_INSTRUCTION = """
Siz dunyodagi eng tajribali O'zbek Manga/Manhwa Lokalitizatorisiz.
Sizning vazifangiz shunchaki so'zma-so'z (mashina) tarjimasi qilish EMAS, balki
manganing asl MAZMUNI, emotsiyasi, qahramon xarakteri va kontekstini ochib beruvchi
eng tabiiy, jarangdor va adabiy O'ZBEK tilidagi mazmunli tarjimani yaratishdir!

QOIDALAR:
1. Quruq kalka (Google Translate uslubi) QAT'IYAN TAQIQLANADI! ('Siz buni qilasiz', 'men bo'laman' kabi soxta jumlalar o'rniga jonli dialoglar).
2. Qahramon ohangini saqlang:
   - Shonen qahramon: "Men hech qachon taslim bo'lmayman!"
   - Mag'rur dushman: "Heh, chumolidek kuching bilan menga tenglashmoqchimisan?"
   - Do'stona hazil: "Tentaklikni yig'ishtir-da, yo'lga tush!"
3. Manga tovush effektlari (SFX) kelsa, ularni maxsus O'zbekcha tovushlarga aylantiring (*gup-gup*, *gumburr!*, *shivir-shivir*).
4. Matn uzunligini hisobga oling: Manga pufakchalari cheklangan maydonga ega, shuning uchun tarjima ixcham, jarangdor va lo'nda bo'lishi shart.
5. Chiqish formati: Faqat so'ralgan JSON formatida javob bering.
"""


class MangaTranslator:
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.5
    ):
        """
        :param provider: 'openrouter', 'groq', 'openai' yoki 'local_heuristic'
        """
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.openai_key = os.environ.get("OPENAI_API_KEY", "")
        self.groq_key = os.environ.get("GROQ_API_KEY", "")
        
        # Eng qulay va mavjud provayderni tanlash (OpenRouter birinchi o'rinda)
        if provider:
            self.provider = provider
        elif self.openrouter_key:
            self.provider = "openrouter"
        elif self.openai_key and not self.openai_key.startswith("sk-or-"):
            self.provider = "openai"
        elif self.groq_key and not self.groq_key.startswith("gsk_test"):
            self.provider = "groq"
        else:
            self.provider = "local_heuristic"

        self.model = model
        self.temperature = temperature
        self.glossary: Dict[str, str] = {
            "Senpai": "Senpay (katta kurs/ustoz tengi)",
            "Sensei": "Ustoz",
            "Chakra": "Chakra",
            "Mana": "Mana",
            "Jutsu": "Jutsu (Mahorat)",
            "Dungeon": "Yerosti qo'rg'oni (Dungeon)",
            "Hunter": "Ovchi",
            "Awakened": "Uyg'ongan"
        }

    def add_to_glossary(self, term: str, translation: str):
        """Maxsus manga atamasini lug'atga kiritish."""
        self.glossary[term] = translation

    def translate_bubble(
        self,
        raw_text: str,
        genre: str = "Shonen",
        character_hint: str = "",
        context_history: List[str] = None
    ) -> str:
        """
        Bitta pufakchadagi matnni mazmunli o'zbek tiliga tarjima qilish.
        """
        if not raw_text or not raw_text.strip():
            return ""

        # 1. SFX tekshirish
        sfx_uz = translate_sfx(raw_text)
        if sfx_uz:
            return sfx_uz

        # 2. Agar API provayder mavjud bo'lsa, LLM orqali tarjima qilish
        if self.provider in ["groq", "openrouter", "openai"]:
            try:
                res = self._translate_llm(
                    texts=[raw_text],
                    genre=genre,
                    character_hint=character_hint,
                    context_history=context_history
                )
                if res and len(res) > 0:
                    return res[0]
            except Exception as e:
                logger.warning(f"LLM tarjima xatosi ({self.provider}): {e}, zaxira rejimiga o'tilmoqda.")

        # 3. Zaxira aqlli qoidalar asosidagi tarjima (Offline Heuristic)
        return self._heuristic_meaningful_translation(raw_text, genre)

    def translate_batch(
        self,
        texts: List[str],
        genre: str = "Shonen",
        character_hint: str = "",
        context_history: List[str] = None
    ) -> List[str]:
        """
        Butun sahifadagi barcha dialoglarni kontekstni saqlagan holda
        birlashtirib mazmunli tarjima qiladi.
        """
        if not texts:
            return []

        # SFX larni alohida ajratish
        results = [None] * len(texts)
        texts_to_llm = []
        indices_to_llm = []

        for idx, t in enumerate(texts):
            sfx = translate_sfx(t)
            if sfx:
                results[idx] = sfx
            else:
                texts_to_llm.append(t)
                indices_to_llm.append(idx)

        if texts_to_llm:
            llm_results = []
            if self.provider in ["groq", "openrouter", "openai"]:
                try:
                    llm_results = self._translate_llm(
                        texts=texts_to_llm,
                        genre=genre,
                        character_hint=character_hint,
                        context_history=context_history
                    )
                except Exception as e:
                    logger.warning(f"Batch LLM tarjima xatosi: {e}")

            if not llm_results or len(llm_results) != len(texts_to_llm):
                llm_results = [
                    self._heuristic_meaningful_translation(t, genre)
                    for t in texts_to_llm
                ]

            for orig_idx, uz_text in zip(indices_to_llm, llm_results):
                results[orig_idx] = uz_text

        return [r if r is not None else "" for r in results]

    def _translate_llm(
        self,
        texts: List[str],
        genre: str,
        character_hint: str,
        context_history: List[str] = None
    ) -> List[str]:
        genre_instruction = GENRE_PROMPTS.get(genre, GENRE_PROMPTS["Shonen"])

        user_content = {
            "manga_dialogues": texts,
            "genre_guidance": genre_instruction,
            "character_hint": character_hint or "Kontekstga ko'ra aniqlansin",
            "glossary": self.glossary,
            "previous_context": context_history or [],
            "task": (
                "Har bir dialog uchun faqat eng mazmunli, his-tuyg'uli va tabiiy O'ZBEKCHA "
                "tarjimasini 'translations' massivida bir xil tartibda qaytaring."
            )
        }

        prompt = (
            f"{SYSTEM_INSTRUCTION}\n\n"
            f"Quyidagi ma'lumotlarni qayta ishlang va FAQAT JSON formatda javob bering:\n"
            f"{json.dumps(user_content, ensure_ascii=False, indent=2)}\n\n"
            f"Kutilayotgan JSON formati:\n"
            f'{{"translations": ["O\'zbekcha tarjima 1", "O\'zbekcha tarjima 2", ...]}}'
        )

        headers = {"Content-Type": "application/json"}
        url = ""
        payload = {}

        if self.provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers["Authorization"] = f"Bearer {self.groq_key}"
            payload = {
                "model": self.model or "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": self.temperature
            }
        elif self.provider == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers["Authorization"] = f"Bearer {self.openrouter_key}"
            payload = {
                "model": self.model or "google/gemini-2.0-flash-001",
                "messages": [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": self.temperature
            }
        elif self.provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers["Authorization"] = f"Bearer {self.openai_key}"
            payload = {
                "model": self.model or "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": self.temperature
            }

        try:
            with httpx.Client(timeout=6.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                raw_content = data["choices"][0]["message"]["content"]
                parsed = json.loads(raw_content)
                
                if "translations" in parsed and isinstance(parsed["translations"], list):
                    return [str(item).strip() for item in parsed["translations"]]
        except Exception as e:
            logger.warning(f"LLM so'rovi amalga oshmadi ({e}), zaxira tarjimon ishga tushadi.")
        return []

    def _heuristic_meaningful_translation(self, text: str, genre: str) -> str:
        """
        Tarmoqsiz (offline) rejimda yoki zaxira holatida manga iboralarini
        jonli va mazmunli o'zbek tiliga o'girish qoidalari.
        """
        t = text.strip()
        t_lower = t.lower().rstrip("!?.~")

        # Mashhur yapon va ingliz manga iboralari xaritasi
        common_phrases = {
            # Inglizcha manga skanlari
            "who are you": "Kimsan o'zi sen?!",
            "who are you?": "Kimsan o'zi sen?!",
            "what is this": "Bu nima balo yana?!",
            "what is this?": "Bu nima balo yana?!",
            "i can't believe it": "Aql bovar qilmaydi!",
            "i won't forgive you": "Seni aslo kechirmayman!",
            "i will never forgive you": "Seni aslo kechirmayman!",
            "die": "Yo'qol bu yerdan!",
            "shut up": "Ovozingni o'chir!",
            "get out of my way": "Yo'limdan qoch!",
            "it's impossible": "Buning aslo iloji yo'q!",
            "impossible": "Bo'lishi mumkin emas!",
            "run": "Qochdik!",
            "run away": "Tezroq qochinglar!",
            "help me": "Yordam bering!",
            "don't worry": "Xavotir olma, hammasi joyida.",
            "leave it to me": "Bu ishni menga qo'yib ber!",
            "are you okay": "Yaxshimisan?",
            "are you okay?": "Yaxshimisan?",
            "thank you": "Katta rahmat!",
            "let's go": "Ketdik, olg'a!",
            "wait": "To'xta!",
            "wait for me": "Meni kutib tur!",
            "damn it": "La'nati!",
            "dammit": "La'nat bo'lsin!",
            "what": "Nima?!",
            "why": "Nega axir?!",
            "how could this happen": "Qanday qilib bunday bo'lishi mumkin?!",
            
            # Yaponcha (Romaji)
            "nani": "Nima?!",
            "nani?!": "Nima?!",
            "baka": "Tentak!",
            "bakayarou": "Tentak nodon!",
            "urusai": "Ovozingni o'chir!",
            "kuso": "La'nati!",
            "yamero": "To'xtat buni!",
            "tasukete": "Yordam bering!",
            "matte": "Shoshma!",
            "daijoubu": "Hammasi joyida.",
            "masaka": "Nahotki... bo'lishi mumkin emas!",
            "arigatou": "Rahmat senga!",
            "ikuzo": "Ketdik, olg'a!",
            "shimatta": "E xudo, kechikdik!"
        }

        if t_lower in common_phrases:
            return common_phrases[t_lower]

        # Agar qisman mos kelsa
        for k, v in common_phrases.items():
            if k in t_lower:
                return v

        # O'zbek tiliga mazmunli moslash
        if "!" in t and len(t) < 25:
            return f"Hey, {t.strip('!')}!"
            
        return t
