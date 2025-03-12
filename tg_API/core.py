import os
from dotenv import load_dotenv
import requests

load_dotenv()

url = "https://booking-com15.p.rapidapi.com/api/v1/attraction/getAttractionReviews"

querystring = {"id": "PR6K7ZswbGBs", "page": "1"}


headers = {
    "x-rapidapi-key": os.getenv("SITE_API"),
    "x-rapidapi-host": "booking-com15.p.rapidapi.com"
}


response = requests.get(url, headers=headers, params=querystring)


if response.status_code == 200:
    try:
        # Парсим JSON-ответ
        data = response.json()

        # Извлекаем нужные данные
        reviews = []
        data_list = data.get("data")  # Получаем список данных

        for item in data_list:

            review_id = item.get("id")
            numeric_rating = item.get("numericRating")
            content = item.get("content")
            user_info = item.get("user")

            user_name = user_info.get("name") if isinstance(user_info, dict) else None

            review = {
                "id": review_id,
                "numericRating": numeric_rating,
                "content": content,
                "userName": user_name
            }
            reviews.append(review)


            print("Отзывы:")
            for review in reviews:
                print(f"ID: {review['id']}")
                print(f"Оценка: {review['numericRating']}")
                print(f"Текст: {review['content']}")
                print(f"Пользователь: {review['userName']}")
                print("-" * 40)

    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
else:
    print(f"Ошибка при запросе к API: {response.status_code}")