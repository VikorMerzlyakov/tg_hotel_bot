import requests

from settings import SiteSetting

url = "https://booking-com15.p.rapidapi.com/api/v1/attraction/getAttractionReviews"

querystring = {"id":"PR6K7ZswbGBs","page":"1"}

headers = {
	"x-rapidapi-key": "2cdea864d3msh2f2d1b647f2ba0ap15b054jsne3e9370ebbad",
	"x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.text)