from aiogram.filters import Command
from aiogram import Router
from aiogram.types import Message

from keyboards.reply import menu_buttons

router=Router()

@router.message(Command('help'))
async def help_bot(message: Message):
    help_text = (
        "Вот несколько нюансов для удобной работы с ботом:\n\n"
        "1️⃣ Сначала добавь город, чтобы получать погоду и уведомления.\n"
        "2️⃣ Для одного города можно настроить уведомления только на одно время.\n"
        "3️⃣ Прогноз на текущий день может не содержать данных по некоторым временным промежуткам, "
        "например, если время уведомления — утром, ночные данные уже недоступны, т.к ночь прошла.\n\n"
    )
    await message.answer(help_text, reply_markup=menu_buttons)