import os
from dotenv import load_dotenv
import urllib.parse
import base64
import json
import requests

load_dotenv("../.env")

url = f"{os.getenv('APPWRITE_ENDPOINT')}/account/sessions/email"
project_id = os.getenv("APPWRITE_PROJECT_ID")

print(f"Connecting to {url} with project {project_id}")

r = requests.post(
    url,
    json={"email": "test463@test.com", "password": "password123"},
    headers={"X-Appwrite-Project": project_id},
)

print("Status:", r.status_code)
c = r.cookies.get(f"a_session_{project_id}")

if c:
    val = urllib.parse.unquote(c).split("_legacy")[0]
    print("VAL:", val)
    b64_str = val + "=" * (-len(val) % 4)
    decoded = json.loads(base64.b64decode(b64_str).decode("utf-8"))
    print("SECRET:", decoded.get("secret"))
else:
    print("NO COOKIE")
    print("ALL COOKIES:", r.cookies.get_dict())
