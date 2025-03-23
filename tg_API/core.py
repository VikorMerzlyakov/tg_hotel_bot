import re
import requests
import json
from database.core import crud
from config_data.config import URL_DEST, URL_PHOTO, URL_HOTEL, HEADERS, URL_DETAILS
from typing import Dict

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

            #print(f"Получено {len(unique_photo_urls)} уникальных фотографий для отеля с ID {hotel_id}.")
            return unique_photo_urls
        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
            return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

def get_hotel_details(hotel_id, arrival_date, departure_date, adults=1, children_age="0", room_qty=1,
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


def display_hotel_info(city_name, arrival_date, departure_date, price_min, price_max, adults=1, children_age="0", room_qty=1,
                       currency_code="USD", user_tg_id=None):
    """
    Функция для объединения данных из всех функций и сохранения их в список словарей.

    :param city_name: Название города.
    :param arrival_date: Дата заезда.
    :param departure_date: Дата выезда.
    :param adults: Количество взрослых.
    :param children_age: Возраст детей.
    :param room_qty: Количество номеров.
    :param currency_code: Валюта.
    :param user_tg_id: Telegram ID пользователя (необходим для записи в БД).
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
        "price_min": price_min,
        "price_max": price_max,
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

            for hotel in hotels:
                hotel_id = hotel.get("hotel_id")
                hotel_name = hotel.get("property", {}).get("name")
                price = hotel.get("property", {}).get("priceBreakdown", {}).get("grossPrice", {}).get("value")
                coordinates = {
                    "latitude": hotel.get("property", {}).get("latitude"),
                    "longitude": hotel.get("property", {}).get("longitude")
                }

                # Получаем детали отеля
                details = get_hotel_details(hotel_id, arrival_date, departure_date, adults, children_age, room_qty,
                                            currency_code)
                booking_url = find_booking_url(details)
                description = extract_description(details)

                # Получаем фотографии отеля через функцию get_hotel_photos
                photos = get_hotel_photos(hotel_id)[:10]  # Показываем первые 3 фото

                # Создаем словарь с данными об отеле
                hotel_data = {
                    "name": hotel_name,
                    "booking_url": booking_url,
                    "description": description,
                    "price": f"{price} {currency_code}",
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

if __name__ == "__main__":
    city = "Moskow"
    arrival = "2025-05-23"
    departure = "2025-05-30"
    hotels_data = display_hotel_info(city, arrival, departure)

    for hotels in hotels_data:
        print(hotels)
