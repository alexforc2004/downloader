import requests
import json

url = "http://127.0.0.1:8001/register"
data = {
    "username": "alice5",
    "email": "alice5@example.com",
    "password": "password123",
    "full_name": "Alice Wonderland"
}

response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print("Response JSON:")
token_url = "http://127.0.0.1:8001/token"
token_data = {
    "username": "alice5",
    "password": "password123"
}
token_response = requests.post(token_url, data=token_data)
print(f"Token Status Code: {token_response.status_code}")
print("Token Response JSON:")
print(json.dumps(token_response.json(), indent=2))
