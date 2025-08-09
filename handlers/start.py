from aiogram.filters import Command
from aiogram import Router
from aiogram.types import Message

from keyboards.reply import menu_buttons

router=Router()

@router.message(lambda message: message.text.lower() in ["/start", "🏠 меню"])
async def start_bot(message: Message):
    name = message.from_user.first_name or "друг"
    text = message.text.lower()
    if text == "🏠 меню":
        await message.answer('Что ещё хочешь сделать?', reply_markup=menu_buttons)
    else:
        await message.answer(
            f'Привет, {name}! Я помогу тебе узнать погоду в твоём городе и настроить уведомления о ней.\n\n'
            f'Если хочешь узнать подробности о том, как пользоваться ботом, напиши /help.',
            reply_markup=menu_buttons
        )