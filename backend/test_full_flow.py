import os, sys, uuid
from pathlib import Path

# Ensure repository root is in PYTHONPATH
repo_root = Path(__file__).resolve().parents[1]
os.chdir(repo_root)
sys.path.append(str(repo_root))

# Load environment (needed for DB and JWT secret)
from dotenv import load_dotenv
load_dotenv()

# Import FastAPI app
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def run():
    # 1️⃣ Health check
    r = client.get('/')
    print('Health:', r.status_code, r.json())

    # 2️⃣ Register a random student
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "Test User",
        "email": email,
        "password": "TestPass123!",
        "role": "student",
        "department_id": None,
    }
    r = client.post('/auth/register', json=payload)
    print('Register:', r.status_code, r.json())
    if r.status_code != 201:
        return

    # 3️⃣ Login with the same credentials
    login_payload = {"email": email, "password": "TestPass123!"}
    r = client.post('/auth/login', json=login_payload)
    print('Login:', r.status_code, r.json())
    if r.status_code != 200:
        return
    token = r.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}

    # 4️⃣ Try a protected endpoint (list users) using token
    r = client.get('/users/', headers=headers)
    print('Users list with token:', r.status_code, r.json()[:2])  # show first two entries only

if __name__ == '__main__':
    run()

