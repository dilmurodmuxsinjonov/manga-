"""
MangaUz Studio - Veb Server va API (FastAPI).
Interaktiv Veb Studiya orqali manga sahifalarini yuklash,
pufakchalarni tahrirlash, janr va ohangni tanlash,
hamda tayyor O'zbekcha sahifalarni yuklab olish.
"""

import os
import sys
import uuid
import base64
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

# Windows konsolida UTF-8 ni to'liq qo'llab-quvvatlash
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core.pipeline import MangaPipeline
from core.translator import MangaTranslator, GENRE_PROMPTS
from core.sfx_dict import SFX_DICTIONARY

app = FastAPI(title="MangaUz Studio", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")
UPLOAD_DIR = os.path.join(BASE_DIR, "outputs", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Global pipeline instance
pipeline = MangaPipeline()

# Cache for active sessions: {session_id: {"original_bgr": ..., "cleaned_bgr": ..., "bubbles": ...}}
active_sessions: Dict[str, Dict[str, Any]] = {}


def img_to_base64(img_bgr: np.ndarray) -> str:
    success, buffer = cv2.imencode(".png", img_bgr)
    if not success:
        return ""
    b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


class BubbleUpdate(BaseModel):
    id: int
    x: int
    y: int
    w: int
    h: int
    text_raw: str = ""
    text_uz: str = ""
    is_sfx: bool = False
    genre_tone: str = "Shonen"


class ProcessRequest(BaseModel):
    session_id: str
    genre: str = "Shonen"
    character_hint: str = ""
    bubbles: Optional[List[BubbleUpdate]] = None


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "genres": list(GENRE_PROMPTS.keys()),
            "sfx_count": len(SFX_DICTIONARY)
        }
    )


@app.get("/api/sample")
async def load_sample():
    sample_file = os.path.join(BASE_DIR, "samples", "sample_page_1.png")
    if not os.path.exists(sample_file):
        raise HTTPException(status_code=404, detail="Namuna fayli topilmadi")

    img_bgr = cv2.imread(sample_file)
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "original_bgr": img_bgr,
        "cleaned_bgr": None,
        "final_bgr": None,
        "bubbles": []
    }

    # Boshlang'ich pufakchalarni aniqlash
    detected = pipeline.detector.detect_bubbles(img_bgr)
    
    # Namuna uchun oldindan tayyorlangan aniq matnlar (yuqori sifatli ko'rinish uchun)
    sample_texts = [
        {"raw": "Who are you?! What is this place?!", "uz": "Kimsan o'zi sen?! Bu yer qayer o'zi?!"},
        {"raw": "Don't worry. Leave it to me!", "uz": "Xavotir olma! Bu yog'ini menga qo'yib ber!"},
        {"raw": "I will never forgive what you did!", "uz": "Qilmishing uchun seni aslo kechirmayman!"},
        {"raw": "ドキドキ", "uz": "Gup-gup...", "is_sfx": True}
    ]

    bubbles_data = []
    for i, b in enumerate(detected):
        if i < len(sample_texts):
            b.text_raw = sample_texts[i]["raw"]
            b.text_uz = sample_texts[i]["uz"]
            b.is_sfx = sample_texts[i].get("is_sfx", False)
        bubbles_data.append(b.to_dict())

    active_sessions[session_id]["bubbles"] = bubbles_data

    return {
        "session_id": session_id,
        "image_base64": img_to_base64(img_bgr),
        "width": img_bgr.shape[1],
        "height": img_bgr.shape[0],
        "bubbles": bubbles_data
    }


@app.post("/api/upload")
async def upload_page(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Tasvir faylini o'qib bo'lmadi")

    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "original_bgr": img_bgr,
        "cleaned_bgr": None,
        "final_bgr": None,
        "bubbles": []
    }

    # Avtomatik pufakchalarni aniqlash
    detected = pipeline.detector.detect_bubbles(img_bgr)
    bubbles_data = [b.to_dict() for b in detected]
    active_sessions[session_id]["bubbles"] = bubbles_data

    return {
        "session_id": session_id,
        "image_base64": img_to_base64(img_bgr),
        "width": img_bgr.shape[1],
        "height": img_bgr.shape[0],
        "bubbles": bubbles_data
    }


@app.post("/api/translate")
async def translate_page(req: ProcessRequest):
    if req.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Sessiya topilmadi")

    sess = active_sessions[req.session_id]
    img_bgr = sess["original_bgr"]

    # Agar foydalanuvchi pufakchalarni yuborgan bo'lsa
    custom_bubbles = []
    if req.bubbles:
        for b in req.bubbles:
            custom_bubbles.append({
                "id": b.id,
                "x": b.x,
                "y": b.y,
                "w": b.w,
                "h": b.h,
                "text_raw": b.text_raw,
                "text_uz": b.text_uz,
                "is_sfx": b.is_sfx,
                "genre_tone": req.genre
            })

    result = pipeline.process_page(
        image_input=img_bgr,
        genre=req.genre,
        character_hint=req.character_hint,
        custom_bubbles=custom_bubbles if custom_bubbles else None
    )

    sess["cleaned_bgr"] = result["cleaned_bgr"]
    sess["final_bgr"] = result["final_bgr"]
    sess["bubbles"] = result["bubbles"]

    return {
        "session_id": req.session_id,
        "final_image": img_to_base64(result["final_bgr"]),
        "cleaned_image": img_to_base64(result["cleaned_bgr"]),
        "bubbles": result["bubbles"]
    }


@app.post("/api/re-render")
async def rerender_page(req: ProcessRequest):
    """Faqat o'zbekcha matnni qayta chizish (tozalashni qaytadan bajarmasdan tezkor chizish)."""
    if req.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Sessiya topilmadi")

    sess = active_sessions[req.session_id]
    cleaned_bgr = sess.get("cleaned_bgr")
    if cleaned_bgr is None:
        # Agar hali tozalangan rasm bo'lmasa, to'liq jarayonni chaqirish
        return await translate_page(req)

    cleaned_rgb = cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cleaned_rgb)

    bubbles = req.bubbles or []
    for b in bubbles:
        if b.text_uz:
            pil_img = pipeline.typesetter.render_bubble_text(
                image_pil=pil_img,
                box=(b.x, b.y, b.w, b.h),
                text=b.text_uz,
                is_sfx=b.is_sfx
            )

    final_rgb = np.array(pil_img)
    final_bgr = cv2.cvtColor(final_rgb, cv2.COLOR_RGB2BGR)
    sess["final_bgr"] = final_bgr

    return {
        "session_id": req.session_id,
        "final_image": img_to_base64(final_bgr)
    }


@app.get("/api/download/{session_id}")
async def download_translated(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Sessiya topilmadi")

    sess = active_sessions[session_id]
    final_bgr = sess.get("final_bgr")
    if final_bgr is None:
        raise HTTPException(status_code=400, detail="Tarjima hali tayyor emas")

    file_path = os.path.join(UPLOAD_DIR, f"manga_uz_{session_id}.png")
    cv2.imwrite(file_path, final_bgr)
    return FileResponse(file_path, filename="manga_uzbek_localized.png", media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    print("\n=======================================================")
    print("   MangaUz Studio - Mazmunli Manga Tarjima Tizimi     ")
    print("   Veb interfeys: http://localhost:8080               ")
    print("=======================================================\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
