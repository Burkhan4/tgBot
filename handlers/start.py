from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.supabase_service import supabase

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer(
            "Profilni ulash uchun sayt orqali botga kiring."
        )
        return

    profile_id = parts[1]

    telegram_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    result = (
        supabase
        .table("profiles")
        .update({
            "telegram_id": telegram_id,
            "telegram_chat_id": chat_id,
            "telegram_connected": True,
        })
        .eq("id", profile_id)
        .execute()
    )

    if result.data:
        await message.answer(
            "✅ Telegram muvaffaqiyatli ulandi!"
        )
    else:
        await message.answer(
            "❌ Profil topilmadi."
        )