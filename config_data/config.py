import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

X_RAPIDAPI_HOST = os.getenv("X_RAPIDAPI_HOST")
BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
URL_DEST = os.getenv("URL_DEST")
URL_PHOTO = os.getenv("URL_PHOTO")
URL_HOTEL = os.getenv("URL_HOTEL")
URL_DETAILS = os.getenv("URL_DETAILS")
HEADERS = {
    "x-rapidapi-key": RAPID_API_KEY,
    "x-rapidapi-host": X_RAPIDAPI_HOST
}

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ('register', 'Регистрация пользователя'),
    ('survey', 'Опрос о поиске отелей'),
    ('search', 'Поиск'),
    ('history', 'История запросов')
)
