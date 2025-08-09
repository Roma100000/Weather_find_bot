from aiogram.fsm.state import State, StatesGroup

class CityForm(StatesGroup):
    waiting_for_city=State()

class NotifyForm(StatesGroup):
    city_notify=State()
    format=State()
    time_notify=State()
    
class NotifyEditForm(StatesGroup):
    city_notify=State()
    format=State()
    time_notify=State()