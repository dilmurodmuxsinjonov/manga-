"""
FastAPI Server Testi (TestClient orqali).
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_routes():
    print("[TEST SERVER] Bosh sahifa va API yo'llari tekshirilmoqda:")
    # 1. Bosh sahifa
    r = client.get("/")
    assert r.status_code == 200
    assert "MangaUz AI Studio" in r.text
    print("  -> Bosh sahifa (HTML) 200 OK")

    # 2. Namuna API
    r = client.get("/api/sample")
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert "image_base64" in data
    assert len(data["bubbles"]) >= 3
    print(f"  -> Namuna API 200 OK (Pufakchalar: {len(data['bubbles'])})")

    # 3. Tarjima API
    sess_id = data["session_id"]
    r_tr = client.post("/api/translate", json={
        "session_id": sess_id,
        "genre": "Shonen",
        "bubbles": data["bubbles"]
    })
    assert r_tr.status_code == 200
    tr_data = r_tr.json()
    assert "final_image" in tr_data
    print("  -> Tarjima va Typesetting API 200 OK")

    print("\nSERVER TESTLARI MUVAFFAQIShLI O'TDI! [PASS]")

if __name__ == "__main__":
    test_routes()
