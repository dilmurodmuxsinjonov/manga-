"""
Manga & Webtoon Downloader.
"My Love Interferer" (My Meddler in Love / 나의 연애 참견자) 1-bobini to'liq yuklab olish.
"""

import os
import sys
import time
import httpx
from bs4 import BeautifulSoup
import zipfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def download_my_love_interferer_ch1(output_dir: str = "downloads/my_love_interferer/chapter_1"):
    os.makedirs(output_dir, exist_ok=True)
    
    url = "https://www.webtoons.com/en/romance/my-meddler-in-love/episode-1/viewer?title_no=9859&episode_no=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.webtoons.com/"
    }

    print(f"[*] Epizod sahifasi tahlil qilinmoqda: {url}")
    with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        viewer = soup.find("div", id="_imageList")
        if not viewer:
            raise ValueError("Manga tasvirlari konteyneri (_imageList) topilmadi")

        img_tags = viewer.find_all("img")
        img_urls = [img.get("data-url") or img.get("src") for img in img_tags]
        img_urls = [u for u in img_urls if u and u.startswith("http")]

        total = len(img_urls)
        print(f"[+] 1-bobda jami {total} ta tasvir paneli topildi.")

        downloaded_files = []
        for idx, img_url in enumerate(img_urls, start=1):
            file_name = f"page_{idx:03d}.jpg"
            file_path = os.path.join(output_dir, file_name)

            # Agar fayl allaqachon yuklangan bo'lsa, o'tkazib yuborish
            if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
                downloaded_files.append(file_path)
                continue

            try:
                img_resp = client.get(img_url)
                img_resp.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(img_resp.content)
                downloaded_files.append(file_path)
                print(f"    [{idx}/{total}] Yuklandi: {file_name} ({len(img_resp.content) // 1024} KB)")
                time.sleep(0.05)
            except Exception as e:
                print(f"    [!] Xatolik {idx}-panelda: {e}")

        print(f"\n[+] Barcha {len(downloaded_files)} ta panel muvaffaqiyatli saqlandi: {output_dir}")

        # CBZ (Comic Book Zip) arxivini yaratish
        cbz_path = os.path.join(os.path.dirname(output_dir), "My_Love_Interferer_Ch1.cbz")
        with zipfile.ZipFile(cbz_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in downloaded_files:
                zipf.write(f, os.path.basename(f))
        print(f"[+] O'qish uchun qulay CBZ komiks arxivi tayyor: {cbz_path}")
        return output_dir, cbz_path


if __name__ == "__main__":
    download_my_love_interferer_ch1()
