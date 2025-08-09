import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.states import CityForm
from keyboards.reply import menu_buttons, reply_w_city_buttons
from keyboards.inline import cities_choose_buttons
from pars_data_weather import valid_city
from db_tools import get_user_data,load_data,save_data

router = Router()
logger = logging.getLogger(__name__)

# --- Добавление города ---

@router.message(lambda message: message.text.lower() in ["♻️ ввести название города повторно", "➕ добавить город"])
async def add_city(message: Message, state: FSMContext):
    await message.answer("Введите название города")
    await state.set_state(CityForm.waiting_for_city)

@router.message(CityForm.waiting_for_city)
async def handle_city_input(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    city_name = message.text.strip()
    data = load_data()
    cities = get_user_data(data, user_id)

    if valid_city(city_name) == 0:
        await message.answer(f'Такого города как {city_name} не существует', reply_markup=reply_w_city_buttons)
        await state.clear()
        return

    if city_name.lower() not in [city.lower() for city in cities]:
        cities.append(city_name)
        await message.answer(f'Город {city_name} успешно добавлен', reply_markup=menu_buttons)
    else:
        await message.answer(f'Город {city_name} был добавлен ранее', reply_markup=reply_w_city_buttons)

    save_data(data)
    await state.clear()

# --- Удаление города ---

@router.message(F.text == "❌ Удалить город")
async def choose_city_to_delete(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    cities = get_user_data(data, user_id)

    if not cities:
        await message.answer("Вы ещё не добавили ни одного города")
        return
    await message.answer("Нажмите на город, который хотите <b>удалить</b>",
                         reply_markup=cities_choose_buttons(cities, "del_city"))

@router.callback_query(F.data.startswith("del:city_"))
async def delete_city(callback: CallbackQuery):
    _, city_name= callback.data.split("_")
    user_id=str(callback.from_user.id)
    data = load_data()
    cities = get_user_data(data, user_id)

    if city_name in cities:
        cities.remove(city_name)
        save_data(data)
        await callback.message.edit_text(f"Город <b>{city_name}</b> успешно удалён")
    else:
        await callback.message.edit_text("Город не найден.")

    await callback.answer()
