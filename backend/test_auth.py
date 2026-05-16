import os, requests, urllib.parse, base64, json
from dotenv import load_dotenv

load_dotenv("../.env")

url = f"{os.getenv('APPWRITE_ENDPOINT')}/account/sessions/email"
project_id = os.getenv("APPWRITE_PROJECT_ID")

r = requests.post(
    url,
    json={"email": "test463@test.com", "password": "password123"},
    headers={"X-Appwrite-Project": project_id},
)

cookie_val = r.cookies.get(f"a_session_{project_id}")

from appwrite.client import Client
from appwrite.services.account import Account

c = Client()

c.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
c.set_project(project_id)
c.set_session(cookie_val)

a = Account(c)
try:
    print("USER DATA WITH FULL COOKIE:", a.get())
except Exception as e:
    print("ERR FULL COOKIE:", e)

c2 = Client()
c2.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
c2.set_project(project_id)
# Test setting as cookie header instead
c2.add_header("Cookie", f"a_session_{project_id}={cookie_val}")
a2 = Account(c2)
try:
    print("USER DATA WITH COOKIE HEADER:", a2.get())
except Exception as e:
    print("ERR COOKIE HEADER:", e)
