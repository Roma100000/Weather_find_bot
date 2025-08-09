import re
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.reply import menu_buttons,choose_after_add_notify,menu_btn
from keyboards.inline import cities_choose_buttons,variants_weather,back_choose_format_notify_btn
from db_tools import get_user_data,load_data,save_data
from handlers.states import NotifyForm

router=Router()

# --- Добавление уведомлений ---

# Выбор города
@router.message(lambda message: message.text.lower() in ["⏰ добавить уведомления", "➕ добавить ещё"])
async def notify_start(message:Message, state:FSMContext):
    name=message.from_user.first_name
    user_id=str(message.from_user.id)
    data=load_data()

    if user_id not in data or not data[user_id]["cities"]:
        await message.answer(f'Вы ещё не добавили ни одного города',menu_btn)
        return

    user_cities = data[user_id].get("cities", [])
    user_notify_cities = list(data[user_id].get("notify", {}).keys())

    available_cities = [city for city in user_cities if city not in user_notify_cities]

    if not available_cities:
        await message.answer("Ко всем городам уже подключены уведомления",reply_markup=menu_btn)
        return

    await state.set_state(NotifyForm.city_notify)
    await message.answer(f'Привет,{name}! О каком городе вы хотите получать информацию о погоде?', 
                         reply_markup=cities_choose_buttons(available_cities,"notify_add"))

# Выбор формата и обработка города
@router.callback_query(F.data.startswith("notify:add_"))
async def choose_day_for_notify(callback: CallbackQuery, state: FSMContext):
    _, city_name = callback.data.split("_")
    await state.update_data(city_notify=city_name)
    await state.set_state(NotifyForm.format)

    await callback.message.edit_text(
        "Выбери, на какой момент времени ты  ежедневно будешь получать погоду",
        reply_markup=variants_weather(city_name,"notify")
    )
    await callback.answer()

# Обработка формата и ввод времени
@router.callback_query(F.data.startswith("notify:reg_"))
async def reg_city_for_notify(callback: CallbackQuery, state: FSMContext):
    _, par,name_city = callback.data.split("_")
    
    await state.update_data(format=par)
    await callback.message.edit_text("Во сколько присылать погоду? Введите время в формате ЧЧ:ММ (например, 08:30)",
                                     reply_markup=back_choose_format_notify_btn(name_city))
    
    await state.set_state(NotifyForm.time_notify)
    await callback.answer()

# Обработка времени и внесение данных в json
@router.message(NotifyForm.time_notify)
async def time_input(message: Message, state: FSMContext):
    time_text = message.text.strip()
    
    if not re.match(r"^\d{2}:\d{2}$", time_text):
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, 08:30)")
        return
    try:
        datetime.strptime(time_text, "%H:%M")
    except ValueError:
        await message.answer("Время некорректно. Пример правильного ввода: 07:45")
        return

    user_id = str(message.from_user.id)
    data = load_data()
    user_data = data.setdefault(user_id, {})
    notify_data = user_data.setdefault("notify", {})

    fsm_data = await state.get_data()
    city = fsm_data["city_notify"]
    forecast_format = fsm_data["format"]

    notify_data[city] = {
        "time": time_text,
        "format": forecast_format
    }

    save_data(data)
    await message.answer(f"✅ Уведомления для города <b>{city}</b> установлены на {time_text}.",reply_markup=choose_after_add_notify)

    await state.clear()

# --- Обработка кнопок назад ---
@router.callback_query(F.data.startswith("back:choose:cities:notify_"))
async def back_to_city_choose(callback: CallbackQuery):
    await callback.answer()
    
    user_id=str(callback.from_user.id)
    data = load_data()
    cities = get_user_data(data, user_id)

    if not cities:
        await callback.message.edit_text("Вы ещё не добавили ни одного города", reply_markup=menu_buttons)
        return

    await callback.message.edit_text("Выбери, на какой момент времени ты  ежедневно будешь получать погоду",
                                     reply_markup=cities_choose_buttons(cities, "notify_add"))

@router.callback_query(F.data.startswith("back:choose:format:notify_"))
async def back_to_format_choose(callback: CallbackQuery):
    await callback.answer()
    
    user_id=str(callback.from_user.id)
    data = load_data()
    cities = get_user_data(data, user_id)

    if not cities:
        await callback.message.edit_text("Вы ещё не добавили ни одного города", reply_markup=menu_buttons)
        return

    await callback.message.edit_text("Выбери, на какой момент времени ты  ежедневно будешь получать погоду",
                                     reply_markup=cities_choose_buttons(cities,"notify_add"))
