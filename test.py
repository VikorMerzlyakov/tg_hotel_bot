import requests

# URL для запроса
url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"

# Параметры запроса
querystring = {
    "dest_id": "-2092174",  # ID города (например, Paris)
    "search_type": "CITY",  # Тип поиска (город)
    "arrival_date": "2025-03-28",  # Дата заезда
    "departure_date": "2025-04-04",  # Дата выезда
    "adults": "1",  # Количество взрослых
    "room_qty": "1",  # Количество номеров
    "categories_filter": "distance::5000",  # Сортировка по удаленности от центра
#    "sort_by": ":1000",  # Фильтр: расстояние до центра < 1 км
    "page_number": "1",  # Номер страницы
    "units": "metric",  # Метрическая система измерения
    "temperature_unit": "c",  # Температура в градусах Цельсия
    "languagecode": "en-us",  # Язык ответа
    "currency_code": "USD"  # Валюта (доллары США)
}

# Заголовки
headers = {
    "x-rapidapi-key": "b793a394eamsh1b1bd341b627933p18a02ejsn20e446d06507",
    "x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

# Выполнение запроса
response = requests.get(url, headers=headers, params=querystring)

# Проверка статуса ответа
if response.status_code == 200:
    data = response.json()
    if data.get("hotels"):
        # Вывод информации о первом отеле (ближайшем к центру)
        closest_hotel = data["hotels"][0]
        print("Ближайший к центру отель:")
        print(f"Название: {closest_hotel['name']}")
        print(f"Расстояние до центра: {closest_hotel['distance']} км")
        print(f"Цена: {closest_hotel['price']} USD")
        print(f"Ссылка: {closest_hotel['booking_url']}")
    else:
        print("Отели не найдены.")
else:
    print(f"Ошибка при выполнении запроса: {response.status_code}")