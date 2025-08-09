import textwrap
import re
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.reply import menu_buttons,choose_after_edit
from keyboards.inline import cities_choose_buttons,red_notify,back_data_notify_btn,edit_format_notify
from db_tools import load_data,save_data
from handlers.states import NotifyEditForm

router=Router()

# Функция помощник, выводящая список городов на выбор через callback/message

async def send_notify_city_selection(user_id: str, target, state: FSMContext, is_callback: bool = False):
    data = load_data()

    if user_id not in data or "notify" not in data[user_id] or not data[user_id]["notify"]:
        await target.answer("У вас ещё нету уведомлений")
        return
    await state.set_state(NotifyEditForm.city_notify)
    cities = list(data[user_id]["notify"])

    if is_callback:
        await target.edit_text(
            "Нажмите на город, о котором хотите получить информацию об уведомлении",
            reply_markup=cities_choose_buttons(cities, "notify_edit")
        )
    else:
        await target.answer(
            "Нажмите на город, о котором хотите получить информацию об уведомлении",
            reply_markup=cities_choose_buttons(cities, "notify_edit")
        )
    
# --- Редактирование уведомлений ---

# Выбор города
@router.message(lambda message: message.text.lower() in ["🔔 мои уведомления", "⚙️ изменить ещё"])
async def notify_choose_city(message:Message, state:FSMContext):
    user_id = str(message.from_user.id)
    await send_notify_city_selection(user_id, message, state)
# Просмотр информации по городу
@router.callback_query(F.data.startswith("notify:edit_"))
async def choose_day_for_notify(callback: CallbackQuery, state: FSMContext):
    _, city_name = callback.data.split("_")
    user_id=str(callback.from_user.id)
    
    data=load_data()
    data_now=data[user_id]["notify"][city_name]
    time_notify=data_now["time"]
    format=data_now["format"]
    if format=="0":format="Текущий день" 
    else:format="Ближайшие 3 дня (включая текущий)"

    await state.update_data(city_notify=city_name)
    
    text = textwrap.dedent(f"""
        📍 <b>{city_name}</b>
        🕒 Время: <b>{time_notify}</b>
        📄 Формат: {format}
    """).strip()

    await callback.message.edit_text(text, reply_markup=red_notify(city_name))
    await callback.answer()

# --- Изменение времени ----

@router.callback_query(F.data.startswith("notify:edit:time_"))
async def edit_time(callback: CallbackQuery, state: FSMContext):
    _, name_city = callback.data.split("_")
    
    await callback.message.edit_text("Во сколько присылать погоду? Введите время в формате ЧЧ:ММ (например, 08:30)",
                                     reply_markup=back_data_notify_btn(name_city))
    
    await state.update_data(bot_message_id=callback.message.message_id)
    
    await state.set_state(NotifyEditForm.time_notify)
    await callback.answer()

@router.message(NotifyEditForm.time_notify)
async def time_input(message: Message, state: FSMContext):
    time_text = message.text.strip()
    user_id=str(message.from_user.id)
    data = load_data()

    if not re.match(r"^\d{2}:\d{2}$", time_text):
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, 08:30)")
        return
    try:
        datetime.strptime(time_text, "%H:%M")
    except ValueError:
        await message.answer("Время некорректно. Пример правильного ввода: 07:45")
        return
    
    fsm_data=await state.get_data()
    city=fsm_data["city_notify"]
    data[user_id]["notify"][city]["time"] = time_text
    bot_msg_id = fsm_data.get("bot_message_id")
    
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=bot_msg_id)
    except:
        pass
    
    save_data(data)
    await message.delete()
    
    await message.answer(f"✅ Уведомления для города <b>{city}</b> установлены на {time_text}.",reply_markup=choose_after_edit)
    await state.clear()

# ---- Изменение формата ----

@router.callback_query(F.data.startswith("notify:edit:format_"))
async def edit_time(callback: CallbackQuery, state: FSMContext):
    _, name_city = callback.data.split("_")
    
    await callback.message.edit_text("В каком формате тебе будут приходить обновления",
                                     reply_markup=edit_format_notify(name_city))
    await callback.answer()

@router.callback_query(F.data.startswith("new:format_"))
async def edit_time(callback: CallbackQuery):
    _, format, name_city = callback.data.split("_")
    user_id=str(callback.from_user.id)
    
    data=load_data()
    data[user_id]["notify"][name_city]["format"]=format
    save_data(data)
    
    await callback.message.delete()
    
    await callback.message.answer("✅ Формат успешно изменён",reply_markup=choose_after_edit)
    await callback.answer()

# ---- Удаление уведомления ----
@router.callback_query(F.data.startswith("del:notify_"))
async def edit_time(callback: CallbackQuery):
    _, name_city = callback.data.split("_")
    user_id=str(callback.from_user.id)
    
    data=load_data()
    del data[user_id]["notify"][name_city]
    save_data(data)
    
    await callback.message.delete()
    
    await callback.message.answer("✅ Данные успешно удалены",reply_markup=choose_after_edit)
    await callback.answer()

# ---- Назад к выбору города ----
@router.callback_query(F.data.startswith("back:choose:notify:city"))
async def notify_choose_city(callback: CallbackQuery, state:FSMContext):
    user_id = str(callback.from_user.id)
    await callback.answer() 
    await send_notify_city_selection(user_id, callback.message, state,True)
