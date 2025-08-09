import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.reply import menu_buttons
from keyboards.inline import cities_choose_buttons, variants_weather, back_choose_day_btn
from pars_data_weather import get_weather, format_weather_now, format_weather_forecast
from db_tools import get_user_data,load_data

router = Router()
logger = logging.getLogger(__name__)

# ---- Получение погоды ----

# Обработка города погоды
@router.message(F.text == "🌤 Получить погоду")
async def choose_city_for_weather(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    cities = get_user_data(data, user_id)

    if not cities:
        await message.answer("Вы ещё не добавили ни одного города")
        return
    await message.answer("Нажмите на город, в котором хотите узнать погоду",
                         reply_markup=cities_choose_buttons(cities, "find_weather"))

# Обработка формата погоды
@router.callback_query(F.data.startswith("coll:days_"))
async def choose_day_for_weather(callback: CallbackQuery):
    _, city_name = callback.data.split("_")
    await callback.message.edit_text(
        "Выбери, на какой момент времени хочешь узнать погоду",
        reply_markup=variants_weather(city_name,"find")
    )
    await callback.answer()

# Подключение к API и вывод данных
@router.callback_query(F.data.startswith("day_"))
async def show_weather(callback: CallbackQuery):
    await callback.answer("Загружаю погоду...")
    try:
        _, par, city_name = callback.data.split("_")
        par = int(par)

        if par == 0:
            weather_data = get_weather(city_name, day_param=0)
            text = format_weather_now(weather_data, city_name)
        elif par == 1:
            forecast_data = get_weather(city_name, day_param=1)
            text = format_weather_forecast(city_name, forecast_data, 1)
        elif par == 3:
            result_data = []
            for i in range(1, 4):
                daily = get_weather(city_name, day_param=i)
                if isinstance(daily, list):
                    result_data.extend(daily)
            text = format_weather_forecast(city_name, result_data, 3)
        else:
            text = "Неверный параметр прогноза."

        await callback.message.edit_text(text, reply_markup=back_choose_day_btn(city_name))

    except Exception as e:
        logger.error("Ошибка в обработке погоды: %s", e)
        await callback.message.edit_text("Произошла ошибка при получении погоды.")

# ---- Назад к выбору города ----

@router.callback_query(F.data.startswith("back:choose:find"))
async def back_to_city_choose(callback: CallbackQuery):
    await callback.answer()
    user_id=str(callback.from_user.id)
    data = load_data()
    cities = get_user_data(data, user_id)

    if not cities:
        await callback.message.edit_text("Вы ещё не добавили ни одного города", reply_markup=menu_buttons)
        return

    await callback.message.edit_text("Нажмите на город, в котором хотите узнать погоду",
                                     reply_markup=cities_choose_buttons(cities, "find_weather"))
