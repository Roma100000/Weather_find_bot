from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Вспомогательные функции ---

def make_button(text: str) -> KeyboardButton:
    return KeyboardButton(text=text)

def rkb_row(*buttons: KeyboardButton) -> list[KeyboardButton]:
    return list(buttons)

def create_keyboard(rows: list[list[str]], resize: bool = True, one_time: bool = True) -> ReplyKeyboardMarkup:
    keyboard = [rkb_row(*[make_button(text) for text in row]) for row in rows]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize,
        one_time_keyboard=one_time
    )

# --- Главное меню ---

menu_buttons = create_keyboard([
    ["🌤 Получить погоду"],
    ["➕ Добавить город", "❌ Удалить город"],
    ["⏰ Добавить уведомления", "🔔 Мои уведомления"]
])

# --- Ответ с городом ---

reply_w_city_buttons = create_keyboard([
    ["🏠 Меню", "♻️ Ввести название города повторно"]
])

# --- После редактирования ---

choose_after_edit = create_keyboard([
    ["🏠 Меню", "⚙️ Изменить ещё"]
])

# --- После добавления уведомления ---

choose_after_add_notify = create_keyboard([
    ["🏠 Меню", "➕ Добавить ещё"]
])

# --- Простое меню с одной кнопкой ---

menu_btn = create_keyboard([
    ["🏠 Меню"]
])