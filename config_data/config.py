import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

X_RAPIDAPI_HOST = os.getenv("X-RAPIDAPI-HOST")
URL = os.getenv("URL")
ID = os.getenv("ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ('survey', 'Опрос'),
    ('history', 'История запросов')
)



