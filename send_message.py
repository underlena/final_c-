import requests

url = "http://localhost:8000/notify"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": ""
}
data = {
    "type": "email",
    "recipient": "@mail.ru",
    "message": "Тестовое сообщение",
    "metadata": {
        "subject": "Тестовая тема"
    }
}

response = requests.post(url, json=data, headers=headers)
print(response.json())