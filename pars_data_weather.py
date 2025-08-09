import requests
from datetime import datetime, timedelta
from config import TOKEN_WEATHER, BASE_URL_NOW, BASE_URL_FORECAST

def valid_city(city_name: str):
    params = {
        "q": city_name,
        "appid": TOKEN_WEATHER,
        "units": "metric",
        "lang": "ru"
    }
    response = requests.get(BASE_URL_NOW, params=params)
    if response.status_code != 200:
        return 0
    return 1

def get_weather(city_name: str, day_param: int = 0,notify=False):
    params = {
        "q": city_name,
        "appid": TOKEN_WEATHER,
        "units": "metric",
        "lang": "ru"
    }

    if day_param == 0 and notify!=True:
        response = requests.get(BASE_URL_NOW, params=params)
        if response.status_code != 200:
            return "Oшибка API"
        data = response.json()
        return {
            "город": data["name"],
            "температура": data["main"]["temp"],
            "ощущается как": data["main"]["feels_like"],
            "влажность": data["main"]["humidity"],
            "погода": data["weather"][0]["description"],
            "ветер": data["wind"]["speed"],
        }
    # Прогноз на будущие дни
    response = requests.get(BASE_URL_FORECAST, params=params) # обращаемся к данным прогноза
    if response.status_code != 200:
        print("❌ Forecast error:", response.text)
        return "Ошибка при получении прогноза"

    data = response.json()
    forecasts = data.get("list", [])# список прогнозов на 5 дней через каждые 3 часа
    target_date = (datetime.utcnow() + timedelta(days=day_param)).date() # utcnow считывает дату с utc на сейчашнее время и прибавляем колличество дней(par)

    result = []
    for entry in forecasts:
        entry_time = datetime.utcfromtimestamp(entry["dt"]) #entry["dt"] хранит время в формате utc
        if entry_time.date() == target_date:
            hour = entry_time.hour
            part = None
            if 7 <= hour <= 12:
                part = "утро"
            elif 12 < hour < 18:
                part = "день"
            elif 18 <= hour <= 24:
                part = "вечер"
            elif 0 <= hour <= 6:
                part = "ночь"
            if part:
                result.append({
                    "дата": entry_time.strftime("%d.%m.%Y"),
                    "время суток": part,
                    "температура": entry["main"]["temp"],
                    "ощущается как": entry["main"]["feels_like"],
                    "влажность": entry["main"]["humidity"],
                    "погода": entry["weather"][0]["description"],
                    "ветер": entry["wind"]["speed"]
                })

    if not result:
        return "Нет данных на выбранный день"
    return result

def format_weather_now(data: dict,city_name: str) -> str:
    return (
        f"📍 Город: {city_name.capitalize()}\n"
        f"🌡 Температура: {round(data['температура'])}°C (ощущается как {round(data['ощущается как'])}°C)\n"
        f"💧 Влажность: {data['влажность']}%\n"
        f"💨 Ветер: {data['ветер']} м/с\n"
        f"☀️ Погода: {data['погода'].capitalize()}"
    )

def format_weather_forecast(city_name: str, forecast_list: list, days: int) -> str:
    if not forecast_list or isinstance(forecast_list, str):
        return "⚠️ Данные о погоде не найдены."

    result = f"📍 Погода города {city_name.capitalize()}:\n\n"
    grouped = {}

    for item in forecast_list:
        date = item["дата"]
        time_of_day = item["время суток"]

        if date not in grouped:
            grouped[date] = {"утро": [], "день": [], "вечер": [], "ночь": []}

        if time_of_day == "утро":
            grouped[date]["утро"].append(item)
        elif time_of_day == "день":
            grouped[date]["день"].append(item)
        elif time_of_day == "вечер":
            grouped[date]["вечер"].append(item)
        elif time_of_day == "ночь":
            grouped[date]["ночь"].append(item)

    count = 0
    for date_str, data in grouped.items():
        if count >= days:
            break
        count += 1

        morning_data = data["утро"]
        afternoon_data = data["день"]
        evening_data = data["вечер"]
        night_data = data["ночь"]
        if days>1:
            result += f"📅 {date_str}\n\n"
        else:
            result += f"📅 {date_str}\n"
        
        if morning_data:
            avg_temp_morning = round(sum(d["температура"] for d in morning_data) / len(morning_data))
            avg_hum_morning = round(sum(d["влажность"] for d in morning_data) / len(morning_data))
            description_morning = morning_data[0]["погода"]
            result += f"  ☀️ Утро: {avg_temp_morning}°C, {description_morning.capitalize()}, 💧 {avg_hum_morning}%\n"
        else:
            result += "  ☀️ Утро: нет данных\n"

        if afternoon_data:
            avg_temp_afternoon = round(sum(d["температура"] for d in afternoon_data) / len(afternoon_data))
            avg_hum_afternoon = round(sum(d["влажность"] for d in afternoon_data) / len(afternoon_data))
            description_afternoon = afternoon_data[0]["погода"]
            result += f"  🌻 День: {avg_temp_afternoon}°C, {description_afternoon.capitalize()}, 💧 {avg_hum_afternoon}%\n"
        else:
            result += "  🌻 День: нет данных\n"
        
        if evening_data:
            avg_temp_evening = round(sum(d["температура"] for d in evening_data) / len(evening_data))
            avg_hum_evening = round(sum(d["влажность"] for d in evening_data) / len(evening_data))
            description_evening = evening_data[0]["погода"]
            result += f"  🌃 Вечер: {avg_temp_evening}°C, {description_evening.capitalize()}, 💧 {avg_hum_evening}%\n"
        else:
            result += "  🌃 Вечер: нет данных\n"
            
        if night_data:
            avg_temp_night = round(sum(d["температура"] for d in night_data) / len(night_data))
            avg_hum_night = round(sum(d["влажность"] for d in night_data) / len(night_data))
            description_night = night_data[0]["погода"]
            result += f"  🌙 Ночь: {avg_temp_night}°C, {description_night.capitalize()}, 💧 {avg_hum_night}%\n"
        else:
            result += "  🌙 Ночь: нет данных\n"

        result += "\n"
    return result.strip()
