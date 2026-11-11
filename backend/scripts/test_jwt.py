# backend/scripts/test_jwt.py
"""
Sanity‑check for the JWT helpers in backend/app/auth.py.
Run with:  python backend/scripts/test_jwt.py
"""

import sys
from pathlib import Path

# Ensure the project root is on PYTHONPATH so the import works
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from backend.app.auth import create_access_token, decode_access_token

def main() -> None:
    # Example claims that mimic what we’ll store after a successful login
    sample_claims = {"sub": 1, "email": "student@example.com", "role": "student"}

    # 1️⃣ Create a token
    token = create_access_token(sample_claims)
    print("\nGenerated JWT:\n", token)

    # 2️⃣ Decode it back
    payload = decode_access_token(token)
    print("\nDecoded payload:\n", payload)

if __name__ == "__main__":
    main()