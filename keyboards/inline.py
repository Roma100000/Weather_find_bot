from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Вспомогательные функции ---

def make_button(text: str, cb: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=cb)

def ikb_row(*buttons: InlineKeyboardButton) -> list[InlineKeyboardButton]:
    return list(buttons)

def create_inline_keyboard(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    keyboard = [ikb_row(*[make_button(text, cb) for text, cb in row]) for row in rows]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- Выбор города (для погоды, удаления, уведомлений) ---

def cities_choose_buttons(cities: list[str], par: str) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(0, len(cities), 2):
        row = []
        for j in range(i, min(i + 2, len(cities))):
            city_name = cities[j]
            if par == "find_weather":
                cb = f'coll:days_{city_name}'
            elif par == "del_city":
                cb = f'del:city_{city_name}'
            elif par == "notify_add":
                cb = f'notify:add_{city_name}'
            elif par == "notify_edit":
                cb = f'notify:edit_{city_name}'
            row.append(make_button(city_name, cb))
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- Выбор формата прогноза погоды или уведомления ---

def variants_weather(name_city: str, par: str) -> InlineKeyboardMarkup:
    if par == "find":
        return create_inline_keyboard([
            [("Сейчас", f'day_0_{name_city}')],
            [("⬅️ Назад", "back:choose:find"),
             ("Завтра", f'day_1_{name_city}'),
             ("На 3 дня", f'day_3_{name_city}')]
        ])
    else:
        return create_inline_keyboard([
            [("⬅️ Назад", "back:choose:cities:notify"),
             ("Текущий день", f'notify:reg_0_{name_city}'),
             ("На 3 дня", f'notify:reg_3_{name_city}')]
        ])

# --- Управление уведомлениями (редактирование, удаление) ---

def red_notify(name_city: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([
        [("🛠️ Изменить время", f'notify:edit:time_{name_city}'),
         ("🔄 Изменить формат", f'notify:edit:format_{name_city}')],
        [("⬅️ Назад", "back:choose:notify:city"),
         ("🗑️ Удалить", f'del:notify_{name_city}')]
    ])

def edit_format_notify(name_city: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([
        [("Текущий день", f'new:format_0_{name_city}'),
         ("На 3 дня", f'new:format_3_{name_city}')],
        [("⬅️ Назад", f'notify:edit_{name_city}')]
    ])

# --- Кнопки "назад" для разных экранов ---

def back_choose_day_btn(name_city: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([
        [("⬅️ Назад", f'coll:days_{name_city}')]
    ])

def back_choose_format_notify_btn(name_city: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([
        [("⬅️ Назад", f'notify:add_{name_city}')]
    ])

def back_data_notify_btn(name_city: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([
        [("⬅️ Назад", f'notify:edit_{name_city}')]
    ])
