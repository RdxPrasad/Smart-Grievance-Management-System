import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

email = input("Email: ")
password = input("Password: ")

response = httpx.post(
    f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
    headers={
        "apikey": SUPABASE_PUBLISHABLE_KEY,
        "Content-Type": "application/json"
    },
    json={
        "email": email,
        "password": password
    }
)

print("Status:", response.status_code)
print(response.json())