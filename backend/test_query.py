import requests

url = "http://127.0.0.1:8000/api/v1/query"

payload = {
    "question": "Explain the concept of humanoid robotics.",
    "mode": "FULL_BOOK",
    "book_id": None,
    "max_chunks": 5
}

response = requests.post(url, json=payload)
print(response.json())
