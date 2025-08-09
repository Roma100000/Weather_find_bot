from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from db_tools import load_data
from pars_data_weather import get_weather, format_weather_now, format_weather_forecast 
from aiogram import Bot

scheduler = AsyncIOScheduler()

def start_scheduler(bot: Bot):
    async def send_weather_notifications():
        data = load_data()
        now = datetime.now().strftime("%H:%M")

        for user_id, user_data in data.items():
            notify = user_data.get("notify", {})
            for city, options in notify.items():
                if options["time"] != now:
                    continue

                day_param = int(options["format"])
                try:
                    if day_param == 0:
                        weather = get_weather(city, day_param,notify=True)
                        text = format_weather_forecast(city,weather,1)
                    else:
                        result_data = []
                        for i in range(0, 3):
                            daily = get_weather(city, day_param=i,notify=True)
                            if isinstance(daily, list):
                                result_data.extend(daily)
                        text = format_weather_forecast(city, result_data, 3)
                    await bot.send_message(chat_id=user_id, text=f"{text}")
                except Exception as e:
                    print(f"[Ошибка уведомления] {user_id=} {city=} — {e}")

    # Выполняем каждую минуту (можно позже заменить на минутный триггер)
    scheduler.add_job(send_weather_notifications, CronTrigger(minute="*"))
    scheduler.start()