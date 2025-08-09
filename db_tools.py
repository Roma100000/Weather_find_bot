import json

DB_FILE = "db.json"

def load_data():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Возвращает список добавленных городов
def get_user_data(data, user_id: str):
    return data.setdefault(user_id, {}).setdefault("cities", [])