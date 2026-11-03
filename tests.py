import requests

BASE = "http://127.0.0.1:5000/api"


# Not logged in
print(requests.get(f"{BASE}/movies").status_code)
