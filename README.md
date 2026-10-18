# 漫 MangaUz AI Studio - Mazmunli Manga Tarjima va Lokalizatsiya Tizimi

> **"Biz shunchaki so'zma-so'z tarjima qilmaymiz, biz mazmunli va jonli lokalizatsiya qilamiz!"**

MangaUz AI Studio — bu yapon, koreys (manhwa) va xitoy (manhua) komikslarini o'zbek tiliga yuqori adabiy sifatda, qahramonlarning xarakteri, emotsiyasi va madaniy nozikliklarini inobatga olgan holda **mazmunli** o'giruvchi zamonaviy sun'iy intellekt tizimi va interaktiv studiyasidir.

---

## 🌟 Asosiy Xususiyatlar va Falsafamiz

### 1. 🎯 Shunchaki tarjima emas — MAZMUNLI LOKALIZATSIYA!
Quruq mashina tarjimasi (Google Translate uslubidagi kalka dialoglar) o'quvchining asardan oladigan lazzatini o'ldiradi. Bizning AI quyidagilarni ta'minlaydi:
- **Janrga xos ohang**:
  - **Shonen**: Jo'shqin, qahramonona, g'ayratga to'la dialoglar (*"Men aslo taslim bo'lmayman!"*).
  - **Seinen**: Falsafiy, jiddiy, chuqur va realistik iboralar (*"Bu dunyo asli shafqatsizlik ustiga qurilgan"*).
  - **Komediya**: Jonli o'zbekona hazil, kinoya va ko'cha jargonlari (*"Nima hangama qilyapsan bu yerda?!"*).
  - **Romantika / Shojo**: Samimiy, nozik, hissiyotga boy jumlalar.
  - **Tarixiy / Murim**: Oliyjanob, rasmiy va viqorli murojaatlar (*"Salomlar bo'lsin, Muhtaram Maktab Yetakchisi!"*).
- **Murojaat va Hurmat shakllari**: Senpai, Sensei, -san, -kun, Hyung, Oppa kabi atamalarni o'zbek tiliga tabiiy va manga atmosferasini saqlagan holda moslash.

### 2. 💥 Manga SFX (Tovush Effektlari / Onomatopoeia)
Manga tovushlarini o'zbek tilidagi jonli analoglariga aylantirish:
- ドキドキ (*Doki-doki*) ➡️ **Gup-gup...** (Yurak urishi)
- ドカーン (*Dokan*) ➡️ **GUMBURR!** (Katta portlash)
- ざわざわ (*Zawa-zawa*) ➡️ **Shivir-shivir...** (Shubha, shovqin)
- ゴゴゴゴ (*Gogogo*) ➡️ **G'UDURR...** (Dahshatli bosim / JoJo aurasi)
- バキッ (*Baki*) ➡️ **QARS!** (Suyak yoki jism sinishi)

### 3. 🫧 Avtomatik Pufakchalarni Aniqlash va Tozalash (Inpainting)
- OpenCV orqali nutq pufakchalarining chegaralarini aniq topish.
- Asl matnlarni fon va ramkalarni buzmagan holda silliq tozalash.

### 4. ✍️ Professional Shriftlash (Typesetting)
- Manga shriftlari bilan pufakcha o'lchamiga mos avtomatik moslashuv (Auto-fitting).
- Kontur (stroke) va markazlashtirilgan matn joylashuvi.

### 5. 🎨 Zamonaviy Veb Studiya va CLI
- Brauzer orqali sahifalarni ochish, har bir pufakchani interaktiv bosib tahrirlash.
- Asl nusxa, tozalangan holat va o'zbekcha yakuniy natijani taqqoslash.
- Bitta buyruq bilan butun boshli boblarni (chapters) tarjima qilish.

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.10+ (tizimda Python 3.12 tavsiya etiladi)
- Git

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Interaktiv Veb Studiyani ishga tushirish
```bash
python server.py
```
Brauzerda oching: **`http://localhost:8080`**

### 4. Buyruqlar Satri (CLI) orqali ishlatish

**Bitta sahifani tarjima qilish:**
```bash
python cli.py page --input samples/sample_page_1.png --genre Shonen
```

**Butun bobni tarjima qilish:**
```bash
python cli.py chapter --input ./manga_ch1 --output ./manga_ch1_uz --genre Seinen
```

---

## 📁 Loyiha Tuzilmasi

```
manga-/
├── core/
│   ├── detector.py          # Pufakchalarni aniqlash (OpenCV)
│   ├── cleaner.py           # Matnni tozalash va tiklash (Inpainting)
│   ├── ocr.py               # Vision AI & OCR moduli
│   ├── translator.py        # "Mazmunli Tarjima" AI Engine
│   ├── typesetter.py        # Shriftlash va sig'dirish
│   ├── pipeline.py          # To'liq avtomatik jarayon
│   └── sfx_dict.py          # Manga SFX tovushlar bazasi
├── web/
│   ├── static/              # CSS va JS interfeys
│   └── templates/           # Veb Studiya HTML shabloni
├── tests/
│   ├── test_manga_system.py # Barcha asosiy modullar testi
│   ├── test_server.py       # API va server testlari
│   └── generate_sample_manga.py # Test manga sahifasi
├── samples/                 # Namunaviy manga sahifalari
├── cli.py                   # Konsol vositasi
├── server.py                # FastAPI Veb Studiyasi
├── requirements.txt         # Kerakli paketlar
└── README.md
```

---

## 🧪 Testlarni Ishga Tushirish

Barcha funksional va integratsion testlarni tekshirish uchun:
```bash
python tests/test_manga_system.py
python tests/test_server.py
```

---

## 🤝 Hissa Qo'shish (Contributing)

Loyiha Git va GitHub standartlariga qat'iy amal qiladi:
1. Ishni doim yangi `feature/<nomi>` tarmog'ida olib boring.
2. Har bir o'zgarish uchun semantik Conventional Commit (`feat: ...`, `fix: ...`) qiling.
3. Asosiy `main` tarmog'iga Pull Request (PR) orqali birlashtiring.
