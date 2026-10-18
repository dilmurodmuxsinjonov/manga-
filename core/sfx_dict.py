"""
Manga SFX (Sound Effects / Tovush effektlari) Lug'ati.
Yaponcha, Koreyscha va Inglizcha onomatopeyalarni jonli, tabiiy O'zbekcha ifodalarga o'girish.
"""

SFX_DICTIONARY = {
    # Yaponcha (Katakana/Romaji) -> O'zbekcha ma'noli ifoda
    "ドキドキ": {"romaji": "doki doki", "uzbek": "Gup-gup...", "desc": "Yurak qattiq urishi, hayajon"},
    "ざわざわ": {"romaji": "zawa zawa", "uzbek": "Shivir-shivir...", "desc": "Olomon shovqini, shubha, bezovtalik"},
    "ドカーン": {"romaji": "dokan", "uzbek": "GUMBURR!", "desc": "Katta portlash yoki kuchli zarba"},
    "ドカン": {"romaji": "dokan", "uzbek": "GUM!", "desc": "Portlash"},
    "ゴゴゴゴ": {"romaji": "gogogo", "uzbek": "G'UDURR...", "desc": "Dahshatli aura, bosim, xavf yaqinlashuvi (JoJo uslubi)"},
    "ドドドド": {"romaji": "dododo", "uzbek": "G'OVUR-G'UVUR!", "desc": "Katta tezlikdagi yugurish yoki tebranish"},
    "ガーン": {"romaji": "gaan", "uzbek": "SHOK!", "desc": "Qattiq hafsala pir bo'lishi, kutilmagan zarba"},
    "ニヤリ": {"romaji": "niyari", "uzbek": "*Makkorona kulgi*", "desc": "Rejali tirjayish"},
    "クスッ": {"romaji": "kusu", "uzbek": "Qiqir-qiqir", "desc": "Ovozsiz yoki sekin kulish"},
    "クスクス": {"romaji": "kusu kusu", "uzbek": "Qiqirlash...", "desc": "Pinhona kulish"},
    "バキッ": {"romaji": "baki", "uzbek": "QARS!", "desc": "Suyak sinishi yoki qattiq zarba ovozi"},
    "ドカッ": {"romaji": "doka", "uzbek": "DUK!", "desc": "Zarba tegishi"},
    "ハァハァ": {"romaji": "haa haa", "uzbek": "Hah-hah... (hansirash)", "desc": "Charchoq, nafas yetishmasligi"},
    "ギュッ": {"romaji": "gyu", "uzbek": "*Mahkam quchish*", "desc": "Qattiq quchoqlash yoki ushlab olish"},
    "チラッ": {"romaji": "chira", "uzbek": "*O'g'rincha qarash*", "desc": "Ko'z qiri bilan qarash"},
    "パチパチ": {"romaji": "pachi pachi", "uzbek": "Chapak-chapak!", "desc": "Qarsaklar ovozi"},
    "スッ": {"romaji": "su", "uzbek": "*Shartta*", "desc": "To'satdan tez va silliq harakat"},
    "ピクッ": {"romaji": "piku", "uzbek": "*Seskanish*", "desc": "Kutilmagan xabardan cho'chib tushish"},
    "ドンッ": {"romaji": "don", "uzbek": "G'ARQ! / VAHOMA!", "desc": "Katta hayrat yoki e'lon"},
    "ブルブル": {"romaji": "buru buru", "uzbek": "Tit-tit...", "desc": "Qo'rquvdan yoki sovuqdan qaltirash"},
    "タッタッタ": {"romaji": "tattatta", "uzbek": "Tipir-tipir", "desc": "Shoshilib qadam tashlash"},
    "ジロッ": {"romaji": "jiro", "uzbek": "*Tikilib qarash*", "desc": "G'azab yoki shubha bilan tikilish"},
    "バタン": {"romaji": "batan", "uzbek": "TARS!", "desc": "Eshik qattiq yopilishi yoki yiqilish"},
    "シーン": {"romaji": "shiin", "uzbek": "*Mutlaq sukunat*", "desc": "Noqulay sukunat ovozi"},
    "キラッ": {"romaji": "kira", "uzbek": "*Yalt-yult*", "desc": "Yaltirash, ko'z porlashi"},

    # Inglizcha komiks SFX lari
    "boom": {"romaji": "boom", "uzbek": "GUMBURR!", "desc": "Portlash"},
    "bang": {"romaji": "bang", "uzbek": "QARS!", "desc": "O'q ovozi yoki zarba"},
    "crash": {"romaji": "crash", "uzbek": "JARANG-JURUNG!", "desc": "Sinish, to'qnashuv"},
    "slam": {"romaji": "slam", "uzbek": "TARS!", "desc": "Eshik yopilishi, qattiq zarba"},
    "gasp": {"romaji": "gasp", "uzbek": "*Hushidan ketgudek nafas olish*", "desc": "Hayrat yoki qo'rquv"},
    "sigh": {"romaji": "sigh", "uzbek": "*Chuqur xo'rsinish*", "desc": "Charchoq yoki umidsizlik"},
    "whisper": {"romaji": "whisper", "uzbek": "*Shivir-shivir*", "desc": "Pichirlash"},
    "pant": {"romaji": "pant", "uzbek": "*Hansirash*", "desc": "Hah-hah..."},
    "smirk": {"romaji": "smirk", "uzbek": "*Kekkayib jilmayish*", "desc": "Makkor tabassum"},
    "shiver": {"romaji": "shiver", "uzbek": "*Titrab ketish*", "desc": "Qaltirash"},
    "thump": {"romaji": "thump", "uzbek": "GUP!", "desc": "Yiqilish yoki yurak zarbi"},
    "whoosh": {"romaji": "whoosh", "uzbek": "SHUVV!", "desc": "Shamoldek tez harakat"},
    "clack": {"romaji": "clack", "uzbek": "TIQIR!", "desc": "Qattiq jismlar to'qnashuvi"}
}

def translate_sfx(text: str) -> str | None:
    """SFX matnini topib, mos O'zbekcha mazmunli tovush ifodasini qaytaradi."""
    clean = text.strip()
    if clean in SFX_DICTIONARY:
        return SFX_DICTIONARY[clean]["uzbek"]
    
    clean_lower = clean.lower()
    if clean_lower in SFX_DICTIONARY:
        return SFX_DICTIONARY[clean_lower]["uzbek"]
        
    for k, v in SFX_DICTIONARY.items():
        if k in clean or v["romaji"] == clean_lower:
            return v["uzbek"]
            
    return None
