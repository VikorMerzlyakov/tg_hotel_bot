from typing import Dict

import requests
from config_data.config import URL_DEST, X_RAPIDAPI_HOST, RAPID_API_KEY, URL_PHOTO, URL_HOTEL, HEADERS, URL_DETAILS

headers = HEADERS
def search_destination(city_name):
    """
    Функция для получения dest_id и search_type по названию города.
    """
    url = URL_DEST

    querystring = {"query": city_name}

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            destinations = data.get("data", [])
            if not destinations:
                print(f"Город '{city_name}' не найден.")
                return None

            # Извлекаем первый найденный город
            dest_id = destinations[0].get("dest_id")
            search_type = destinations[0].get("search_type")
            print(f"Найден город: {city_name}, dest_id: {dest_id}, search_type: {search_type}")
            return {"dest_id": dest_id, "search_type": search_type}
        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


def get_hotel_photos(hotel_id):
    """
    Функция для получения фотографий отеля по hotel_id.

    :param hotel_id: ID отеля.
    :return: Список URL фотографий.
    """
    url = URL_PHOTO

    querystring = {"hotel_id": hotel_id}


    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            photos = data.get("data", [])
            photo_urls = [photo["url"] for photo in photos]
            print(f"Получено {len(photo_urls)} фотографий для отеля с ID {hotel_id}.")
            return photo_urls
        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
            return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


def get_hotel_details(hotel_id, arrival_date, departure_date, adults=1, children_age="0", room_qty=1, currency_code="USD"):
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


def find_booking_url(data: dict) -> str:
    """
    Рекурсивная функция для поиска ключа 'url' в ответе API.

    :param data: Ответ API в формате словаря.
    :return: Значение ключа 'url', если найдено, или пустая строка.
    """
    if isinstance(data, dict):  # Если данные — словарь
        for key, value in data.items():
            if key == "url":  # Если найден ключ 'url'
                return value
            result = find_booking_url(value)  # Рекурсивный вызов для значения
            if result:  # Если результат найден
                return result
    elif isinstance(data, list):  # Если данные — список
        for item in data:
            result = find_booking_url(item)  # Рекурсивный вызов для каждого элемента
            if result:  # Если результат найден
                return result
    return ""  # Если ключ 'url' не найден


from typing import Dict, List

def extract_description(data: Dict) -> str:
    """
    Рекурсивная функция для поиска ключа 'top_ufi_benefits' и извлечения значений ключей "translated_name".

    :param data: Ответ API в формате словаря.
    :return: Описание отеля, где значения ключей "translated_name" объединены в строку через запятую.
    """
    description = []

    def find_translated_names(data):
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
                    find_translated_names(value)  # Рекурсивный вызов для значения
        elif isinstance(data, list):  # Если данные — список
            for item in data:
                find_translated_names(item)  # Рекурсивный вызов для каждого элемента

    find_translated_names(data)  # Запускаем рекурсивный поиск
    return ", ".join(description)  # Объединяем найденные значения в строку через запятую

def display_hotel_info(city_name, arrival_date, departure_date, adults=1, children_age="0", room_qty=1, currency_code="USD"):
    """
    Функция для объединения данных из всех функций и сохранения их в список словарей.

    :param city_name: Название города.
    :param arrival_date: Дата заезда.
    :param departure_date: Дата выезда.
    :param adults: Количество взрослых.
    :param children_age: Возраст детей.
    :param room_qty: Количество номеров.
    :param currency_code: Валюта.
    :return: Список словарей с данными об отелях.
    """
    # Получаем dest_id и search_type для города
    destination = search_destination(city_name)
    if not destination:
        print("Не удалось найти информацию о городе.")
        return []

    dest_id = destination["dest_id"]
    search_type = destination["search_type"]

    url = URL_HOTEL

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

            print(f"Найдено {len(hotels)} отелей в городе {city_name}:")
            for hotel in hotels:
                hotel_id = hotel.get("hotel_id")
                hotel_name = hotel.get("property", {}).get("name")
                price = hotel.get("property", {}).get("priceBreakdown", {}).get("grossPrice", {}).get("value")
                photos = hotel.get("property", {}).get("photoUrls", [])
                coordinates = {
                    "latitude": hotel.get("property", {}).get("latitude"),
                    "longitude": hotel.get("property", {}).get("longitude")
                }

                # Получаем детали отеля
                details = get_hotel_details(hotel_id, arrival_date, departure_date, adults, children_age, room_qty, currency_code)
                booking_url = find_booking_url(details)
                description = extract_description(details)

                # Создаем словарь с данными об отеле
                hotel_data = {
                    "name": hotel_name,
                    "booking_url": booking_url,
                    "description": description,
                    "price": f"{price} {currency_code}",
                    "dates": f"{arrival_date} - {departure_date}",
                    "photos": photos[:3],  # Показываем первые 3 фото
                    "coordinates": coordinates
                }

                # Добавляем словарь в список
                hotels_list.append(hotel_data)

                # Выводим данные об отеле на консоль
                print(f"Название: {hotel_name}")
                print(f"Ссылка на бронирование: {booking_url}")
                print(f"Описание: {description}")
                print(f"Цена: {price} {currency_code}")
                print(f"Выбранные даты: {arrival_date} - {departure_date}")
                print(f"Фотографии: {', '.join(photos[:3])}")  # Показываем первые 3 фото
                print(f"Координаты: {coordinates}")
                print("-" * 40)

            # Возвращаем список словарей
            return hotels_list

        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
            return []

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


if __name__ == "__main__":
    city = "Paris"
    arrival = "2025-03-22"
    departure = "2025-03-28"
    hotels_data = display_hotel_info(city, arrival, departure)

    for hotel in hotels_data:
        print(hotel)