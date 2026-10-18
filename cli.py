"""
MangaUz CLI - Buyruqlar Satri Interfeysi.
Manga sahifalarini yoki butun boblarini avtomatik tarjima qilish.
Misol:
  python cli.py page --input samples/sample_page_1.png --genre Shonen
  python cli.py chapter --input ./chapter1 --output ./chapter1_uz --genre Seinen
"""

import os
import sys
import argparse
import cv2

# Windows konsolida UTF-8 ni to'liq qo'llab-quvvatlash
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.pipeline import MangaPipeline
from core.translator import MangaTranslator


def main():
    parser = argparse.ArgumentParser(
        description="MangaUz - Mazmunli O'zbekcha Manga Tarjima Tizimi"
    )
    subparsers = parser.add_subparsers(dest="command", help="Mavjud buyruqlar")

    # Bitta sahifa uchun buyruq
    page_parser = subparsers.add_parser("page", help="Bitta sahifani tarjima qilish")
    page_parser.add_argument("--input", "-i", required=True, help="Kiruvchi tasvir fayli yo'li")
    page_parser.add_argument("--output", "-o", default=None, help="Chiquvchi fayl yo'li")
    page_parser.add_argument("--genre", "-g", default="Shonen", choices=["Shonen", "Seinen", "Komediya", "Romantika", "Tarixiy/Murim"], help="Manga janri va ohangi")
    page_parser.add_argument("--provider", "-p", default=None, help="LLM provayderi (openrouter, openai, groq, local_heuristic)")

    # Butun bob (chapter) uchun buyruq
    ch_parser = subparsers.add_parser("chapter", help="Butun bob papkasini tarjima qilish")
    ch_parser.add_argument("--input", "-i", required=True, help="Bob tasvirlari papkasi")
    ch_parser.add_argument("--output", "-o", required=True, help="Natijaviy papka")
    ch_parser.add_argument("--genre", "-g", default="Shonen", choices=["Shonen", "Seinen", "Komediya", "Romantika", "Tarixiy/Murim"], help="Manga janri va ohangi")
    ch_parser.add_argument("--provider", "-p", default=None, help="LLM provayderi")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    translator = MangaTranslator(provider=args.provider)
    pipeline = MangaPipeline(translator=translator)

    if args.command == "page":
        print(f"[*] Sahifa qayta ishlanmoqda: {args.input}")
        print(f"[*] Janr va ohang: {args.genre}")
        res = pipeline.process_page(args.input, genre=args.genre)

        out_path = args.output
        if not out_path:
            base, ext = os.path.splitext(args.input)
            out_path = f"{base}_uz{ext}"

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        cv2.imwrite(out_path, res["final_bgr"])
        print(f"[+] Muvaffaqiyatli yakunlandi! Natija: {out_path}")
        print(f"[i] Aniqlangan va tarjima qilingan pufakchalar: {len(res['bubbles'])}")
        for b in res["bubbles"]:
            print(f"    - [{b['id']}] Asl: '{b['text_raw']}' => O'zbekcha: '{b['text_uz']}'")

    elif args.command == "chapter":
        print(f"[*] Bob papkasi qayta ishlanmoqda: {args.input}")
        print(f"[*] Chiqish papkasi: {args.output}")
        out_files = pipeline.process_chapter(args.input, args.output, genre=args.genre)
        print(f"[+] Bob to'liq tarjima qilindi! Jami {len(out_files)} ta sahifa saqlandi.")


if __name__ == "__main__":
    main()
