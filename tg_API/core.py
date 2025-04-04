import logging
import requests
from config_data.config import URL_DEST, URL_PHOTO, URL_HOTEL, HEADERS, URL_DETAILS
from typing import Dict

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
    handlers=[logging.StreamHandler()]  # Вывод логов в консоль
)
headers = HEADERS


def getDestinations(city_name: str) -> list:
    """
    Отправляет запрос к API для получения списка dest_id и их типов для указанного города.

    :param city_name: Название города.
    :return: Список уникальных типов локаций (search_type).
    """
    url = URL_DEST

    querystring = {"query": city_name}

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        unique_types = set()  # Используем множество для хранения уникальных значений

        # Обрабатываем массив данных
        for item in data.get("data", []):
            search_type = item.get("search_type")  # Получаем значение типа локации
            if search_type:  # Проверяем, что значение существует
                unique_types.add(search_type)

        return list(unique_types)  # Преобразуем множество обратно в список
    else:
        raise Exception(f"Ошибка при запросе к API: {response.status_code}")


def searchDestinationId(city_name: str, local: str):
    """
    Функция для получения dest_id по названию города и типу локации (dest_type).

    :param city_name: Название города.
    :param local: Тип локации (например, "city", "district").
    :return: Словарь с ключами "dest_id" и "search_type", если найден соответствующий dest_type, иначе None.
    """
    url = URL_DEST  # URL для запроса к API
    querystring = {"query": city_name}

    try:
        logging.info(f"Отправка запроса к API для города '{city_name}'")
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            logging.debug("Получен ответ от API со статусом 200")
            data = response.json()
            destinations = data.get("data", [])

            if not destinations:
                logging.warning(f"Город '{city_name}' не найден.")
                return None

            logging.debug(f"Найдено {len(destinations)} локаций для города '{city_name}'")

            # Ищем dest_id, где dest_type совпадает с local
            for destination in destinations:
                dest_type = destination.get("dest_type")
                if local == dest_type:
                    dest_id = destination.get("dest_id")
                    logging.info(f"Найдена локация: {local}, dest_id: {dest_id}")
                    return {"dest_id": dest_id, "search_type": dest_type}  # Возвращаем словарь

            # Если не найдено совпадений
            logging.warning(f"Локация '{local}' для города '{city_name}' не найдена.")
            return None
        else:
            logging.error(f"Ошибка при запросе к API: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return None


def getHotelPhotos(hotel_id):
    """
    Функция для получения фотографий отеля по hotel_id.

    :param hotel_id: ID отеля.
    :return: Список уникальных URL фотографий.
    """
    url = URL_PHOTO  # Замените на реальный URL API

    querystring = {"hotel_id": hotel_id}

    try:
        # Отправляем GET-запрос к API
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            # Преобразуем ответ в JSON
            data = response.json()

            # Извлекаем все URL из JSON
            photo_urls = []
            for item in data.get("data", []):  # Предполагаем, что "data" — это список
                photo_url = item.get("url")
                if photo_url:
                    photo_urls.append(photo_url)

            # Убираем дубликаты, если они есть
            unique_photo_urls = list(set(photo_urls))

            # print(f"Получено {len(unique_photo_urls)} уникальных фотографий для отеля с ID {hotel_id}.")
            return unique_photo_urls
        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
            return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


def getHotelDetails(hotel_id, arrival_date, departure_date, adults=1, children_age="0", room_qty=1,
                    currency_code="USD"):
    """
    Функция для получения деталей отеля, включая ссылку на бронирование и описание.

    :param hotel_id: ID отеля.
    :param arrival_date: Дата заезда.
    :param departure_date: Дата выезда.
    :param adults: Количество взрослых.
    :param children_age: Возраст детей.
    :param room_qty: Количество номеров.
    :param currency_code: Валюта.
    :return: Словарь с данными об отеле.
    """
    url = URL_DETAILS

    querystring = {
        "hotel_id": hotel_id,
        "arrival_date": arrival_date,
        "departure_date": departure_date,
        "adults": str(adults),
        "children_age": children_age,
        "room_qty": str(room_qty),
        "units": "metric",
        "temperature_unit": "c",
        "languagecode": "en-us",
        "currency_code": currency_code
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return {}


def findBookingUrl(data: dict) -> str:
    """
    Рекурсивная функция для поиска ключа 'url' в ответе API.

    :param data: Ответ API в формате словаря.
    :return: Значение ключа 'url', если найдено, или пустая строка.
    """
    if isinstance(data, dict):  # Если данные — словарь
        for key, value in data.items():
            if key == "url":  # Если найден ключ 'url'
                return value
            result = findBookingUrl(value)  # Рекурсивный вызов для значения
            if result:  # Если результат найден
                return result
    elif isinstance(data, list):  # Если данные — список
        for item in data:
            result = findBookingUrl(item)  # Рекурсивный вызов для каждого элемента
            if result:  # Если результат найден
                return result
    return ""  # Если ключ 'url' не найден


def extractDescription(data: Dict) -> str:
    """
    Рекурсивная функция для поиска ключа 'top_ufi_benefits' и извлечения значений ключей "translated_name".

    :param data: Ответ API в формате словаря.
    :return: Описание отеля, где значения ключей "translated_name" объединены в строку через запятую.
    """
    description = []

    def findTranslatedNames(data):
        """
        Вспомогательная рекурсивная функция для поиска ключей "translated_name".
        """
        if isinstance(data, dict):  # Если данные — словарь
            for key, value in data.items():
                if key == "top_ufi_benefits" and isinstance(value, list):  # Найден ключ 'top_ufi_benefits'
                    for benefit in value:
                        if isinstance(benefit, dict) and "translated_name" in benefit:  # Ищем "translated_name"
                            description.append(benefit["translated_name"])
                else:
                    findTranslatedNames(value)  # Рекурсивный вызов для значения
        elif isinstance(data, list):  # Если данные — список
            for item in data:
                findTranslatedNames(item)  # Рекурсивный вызов для каждого элемента

    findTranslatedNames(data)  # Запускаем рекурсивный поиск
    return ", ".join(description)  # Объединяем найденные значения в строку через запятую


def displayHotelInfo(city_name, local, arrival_date, departure_date, adults=1, children_age="0", room_qty=1,
                     currency_code="USD", user_tg_id=None, categories_filter=None, sort_by=None, price_min=None,
                     price_max=None):
    """
    Функция для объединения данных из всех функций и сохранения их в список словарей.
    Добавлены необязательные параметры sort_by и цены (price_min, price_max).

    :param city_name: Название города.
    :param local: Тип локации (например, "city", "district").
    :param arrival_date: Дата заезда.
    :param departure_date: Дата выезда.
    :param adults: Количество взрослых.
    :param children_age: Возраст детей.
    :param room_qty: Количество номеров.
    :param currency_code: Валюта.
    :param user_tg_id: Telegram ID пользователя (необходим для записи в БД).
    :param categories_filter: Фильтр для категорий (например, "reviewscorebuckets::80").
    :param sort_by: Параметр сортировки (например, "price").
    :param price_min: Минимальная цена (необязательно).
    :param price_max: Максимальная цена (необязательно).
    :return: Список словарей с данными об отелях.
    """
    # Получаем dest_id и search_type для города
    destination = searchDestinationId(city_name, local)
    if not destination:
        print("Не удалось найти информацию о городе.")
        return []

    dest_id = destination["dest_id"]
    search_type = destination["search_type"]

    url = URL_HOTEL

    # Формируем параметры запроса
    querystring = {
        "dest_id": dest_id,
        "search_type": search_type,
        "arrival_date": arrival_date,
        "departure_date": departure_date,
        "adults": str(adults),
        "children_age": children_age,
        "room_qty": str(room_qty),
        "page_number": "1",
        "units": "metric",
        "temperature_unit": "c",
        "languagecode": "en-us",
        "currency_code": currency_code
    }

    # Добавляем фильтр по минимальной и максимальной цене, если они указаны
    if price_min is not None:
        querystring["price_min"] = price_min
    if price_max is not None:
        querystring["price_max"] = price_max

    # Добавляем фильтр по категориям, если он указан
    if categories_filter:
        querystring["categories_filter"] = categories_filter

    # Добавляем параметр сортировки, если он указан
    if sort_by:
        querystring["sort_by"] = sort_by

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            hotels = data.get("data", {}).get("hotels", [])
            if not hotels:
                print("Отели не найдены.")
                return []

            # Создаем список для хранения данных об отелях
            hotels_list = []

            for hotel in hotels:
                hotel_id = hotel.get("hotel_id")
                hotel_name = hotel.get("property", {}).get("name")
                price = hotel.get("property", {}).get("priceBreakdown", {}).get("grossPrice", {}).get("value")
                coordinates = {
                    "latitude": hotel.get("property", {}).get("latitude"),
                    "longitude": hotel.get("property", {}).get("longitude")
                }

                # Получаем детали отеля
                details = getHotelDetails(hotel_id, arrival_date, departure_date, adults, children_age, room_qty,
                                          currency_code)
                booking_url = findBookingUrl(details)
                description = extractDescription(details)

                # Получаем фотографии отеля через функцию get_hotel_photos
                photos = getHotelPhotos(hotel_id)[:10]  # Показываем первые 10 фото

                # Создаем словарь с данными об отеле
                hotel_data = {
                    "name": hotel_name,
                    "booking_url": booking_url,
                    "description": description,
                    "price": f"{price} {currency_code}" if price else "Цена не указана",
                    "dates": f"{arrival_date} - {departure_date}",
                    "photos": photos,  # Добавляем фото
                    "coordinates": coordinates  # Добавляем координаты
                }

                # Добавляем словарь в список
                hotels_list.append(hotel_data)

            # Возвращаем список словарей
            return hotels_list

        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
            return []

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []
