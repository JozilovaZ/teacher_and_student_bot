from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = (
        "<b>UstozShogird Bot</b> — IT sohasida ariza berish va topish platformasi.\n\n"
        "<b>Buyruqlar:</b>\n"
        "/start — Botni ishga tushirish\n"
        "/help — Yordam\n\n"
        "<b>Kategoriyalar:</b>\n"
        "🔍 Ustoz kerak — Ustoz izlayotgan shogirdlar\n"
        "🎓 Shogird kerak — Shogird izlayotgan ustozlar\n"
        "👔 Hodim kerak — Hodim izlayotgan kompaniyalar\n"
        "💼 Ish joyi kerak — Ish izlayotganlar\n"
        "🤝 Sherik kerak — Sherik izlayotganlar\n\n"
        "📋 Ariza berish — O'z arizangizni joylashtirish\n"
        "📁 Mening arizalarim — Arizalaringizni boshqarish"
    )
    from keyboards.default.menu import main_menu
    await message.answer(text, reply_markup=main_menu)