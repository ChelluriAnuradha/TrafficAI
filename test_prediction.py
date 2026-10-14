
import urllib.request
import json

url = "http://127.0.0.1:5000/api/predict"

data = {
    "location": "City Center",
    "date": "2026-10-13",
    "time": "18:00",
    "weather": "Rainy",
    "vehicleCount": 900,
    "speed": 20
}


req = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print(response.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)
