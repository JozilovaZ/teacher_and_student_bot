import re


def validate_fullname(text: str):
    text = text.strip()
    if len(text) < 5:
        return False, "Ism familiya kamida 5 ta harf bo'lishi kerak."
    if len(text.split()) < 2:
        return False, "Iltimos, ism VA familiyangizni kiriting (ikki so'z)."
    if re.search(r'\d', text):
        return False, "Ism familiyada raqam bo'lmasligi kerak."
    return True, None


def validate_yosh(text: str):
    text = text.strip()
    if not text.isdigit():
        return False, "Yosh faqat raqamdan iborat bo'lishi kerak. Masalan: 25"
    yosh = int(text)
    if yosh < 10 or yosh > 80:
        return False, "Yosh 10 dan 80 gacha bo'lishi kerak."
    return True, None


def validate_texno(text: str):
    text = text.strip()
    if len(text) < 2:
        return False, "Texnologiya nomi kamida 2 ta belgi bo'lishi kerak."
    return True, None


def validate_aloqa(text: str):
    digits = re.sub(r'[\s\-\(\)]', '', text.strip())
    if not re.match(r'^\+?[\d]{9,13}$', digits):
        return False, "Telefon raqam noto'g'ri kiritildi.\nMasalan: +998 90 123 45 67"
    return True, None


def validate_hudud(text: str):
    text = text.strip()
    if len(text) < 3:
        return False, "Hudud nomi kamida 3 ta harf bo'lishi kerak."
    return True, None


def validate_narx(text: str):
    text = text.strip()
    if len(text) < 2:
        return False, "Narx kamida 2 ta belgi bo'lishi kerak."
    return True, None


def validate_kasb(text: str):
    text = text.strip()
    if len(text) < 3:
        return False, "Kasb nomi kamida 3 ta harf bo'lishi kerak."
    return True, None


def validate_vaqt(text: str):
    text = text.strip()
    if len(text) < 3:
        return False, "Vaqt kamida 3 ta belgi bo'lishi kerak. Masalan: 9:00 - 18:00"
    return True, None


def validate_maqsad(text: str):
    text = text.strip()
    if len(text) < 10:
        return False, "Maqsad kamida 10 ta harf bo'lishi kerak. Batafsil yozib bering."
    return True, None


def validate_idora(text: str):
    text = text.strip()
    if len(text) < 3:
        return False, "Idora nomi kamida 3 ta harf bo'lishi kerak."
    return True, None


def validate_murojat(text: str):
    text = text.strip()
    if len(text) < 3:
        return False, "Murojaat vaqti kamida 3 ta belgi bo'lishi kerak."
    return True, None


def validate_maosh(text: str):
    text = text.strip()
    if len(text) < 2:
        return False, "Maosh kamida 2 ta belgi bo'lishi kerak."
    return True, None
