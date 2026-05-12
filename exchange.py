############## API test

################### exchange
# import requests

# url = "https://open.er-api.com/v6/latest/USD"

# response = requests.get(url)

# data = response.json()

# krw = data["rates"]["KRW"]

# print("1 USD =", krw, "KRW")

##################### get post
# import requests

# url = "https://jsonplaceholder.typicode.com/posts/1"

# response = requests.get(url)

# data = response.json()

# print(data['userId'])

#################### create post
import requests

url = "https://jsonplaceholder.typicode.com/posts"

post_data = {
    "title": "내 첫 API 글",
    "body": "API 테스트 중",
    "userId": 1
}

response = requests.post(url, json=post_data)

print(response.json())
