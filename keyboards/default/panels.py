from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PAGE_SIZE = 5

CATEGORY_LABELS = {
    'ustoz':    '🔍 Ustoz kerak',
    'shogird':  '🎓 Shogird kerak',
    'hodim':    '👔 Hodim kerak',
    'ish_joyi': '💼 Ish joyi kerak',
    'sherik':   '🤝 Sherik kerak',
}


def ads_list_kb(ads, category: str, offset: int, total: int,
                hudud: str = '', texno: str = '') -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for ad in ads:
        active_mark = '' if ad['is_active'] else ' [nofaol]'
        kb.add(InlineKeyboardButton(
            text=f"👤 {ad['fullname']} | 📍 {ad['hudud']}{active_mark}",
            callback_data=f"ad_{ad['id']}"
        ))

    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton(
            text="⬅️ Oldingi",
            callback_data=f"browse_{category}_{offset - PAGE_SIZE}_{hudud}_{texno}"
        ))
    if offset + PAGE_SIZE < total:
        nav.append(InlineKeyboardButton(
            text="Keyingi ➡️",
            callback_data=f"browse_{category}_{offset + PAGE_SIZE}_{hudud}_{texno}"
        ))
    if nav:
        kb.row(*nav)

    kb.add(InlineKeyboardButton(
        text="🔎 Filtr",
        callback_data=f"filter_{category}"
    ))
    return kb


def ad_detail_kb(ad_id: int, contact_info: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(
        text=f"📞 Bog'lanish: {contact_info}",
        callback_data=f"contact_{ad_id}"
    ))
    kb.add(InlineKeyboardButton(
        text="⬅️ Orqaga",
        callback_data=f"back_ad_{ad_id}"
    ))
    return kb


def contact_kb(contact_info: str, username: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    if username:
        kb.add(InlineKeyboardButton(
            text=f"💬 Telegram: @{username}",
            url=f"https://t.me/{username}"
        ))
    kb.add(InlineKeyboardButton(
        text=f"📞 {contact_info}",
        callback_data="noop"
    ))
    return kb


def my_ads_kb(ads) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for ad in ads:
        cat_label = CATEGORY_LABELS.get(ad['category'], ad['category'])
        status = '✅' if ad['is_active'] else '⏸'
        kb.add(InlineKeyboardButton(
            text=f"{status} {cat_label} | {ad['fullname']}",
            callback_data=f"myad_{ad['id']}"
        ))
    return kb


def my_ad_manage_kb(ad_id: int, is_active: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    if is_active:
        kb.add(InlineKeyboardButton(text="⏸ To'xtatish", callback_data=f"myad_off_{ad_id}"))
    else:
        kb.add(InlineKeyboardButton(text="▶️ Faollashtirish", callback_data=f"myad_on_{ad_id}"))
    kb.add(InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"myad_del_{ad_id}"))
    kb.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="myad_back"))
    return kb


def category_select_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for key, label in CATEGORY_LABELS.items():
        kb.add(InlineKeyboardButton(text=label, callback_data=f"newad_{key}"))
    return kb


def admin_users_kb(users) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for u in users[:30]:
        kb.add(InlineKeyboardButton(
            text=f"{'🚫' if u['role']=='blocked' else '👤'} {u['full_name']}",
            callback_data=f"auser_{u['telegram_id']}"
        ))
    return kb


def admin_user_action_kb(telegram_id: int, role: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    if role == 'blocked':
        kb.add(InlineKeyboardButton(text="✅ Blokdan chiqar", callback_data=f"aunblock_{telegram_id}"))
    else:
        kb.add(InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"ablock_{telegram_id}"))
    return kb
