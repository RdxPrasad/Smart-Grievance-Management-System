# backend/scripts/test_jwt.py
"""
Sanity‑check for the JWT helpers in backend/app/auth.py.
Run with:  python backend/scripts/test_jwt.py
"""

import os
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# 1️⃣ Load .env ---------------------------------------------------------
# ----------------------------------------------------------------------
# python‑dotenv reads the .env file located in the current working directory
# (the project root). If you don't have python‑dotenv installed, run:
#   pip install python-dotenv
from dotenv import load_dotenv

# Ensure we are running from the project root so load_dotenv can find .env
project_root = Path(__file__).resolve().parents[2]   # points to <repo_root>
os.chdir(project_root)                               # change cwd to repo root
load_dotenv()                                        # now JWT_SECRET_KEY is in os.environ

# ----------------------------------------------------------------------
# 2️⃣ Make the repo importable -----------------------------------------
# ----------------------------------------------------------------------
# Add the repo root to PYTHONPATH so ``backend.app`` can be imported.
sys.path.append(str(project_root))

# ----------------------------------------------------------------------
# 3️⃣ Import the JWT helpers -------------------------------------------
# ----------------------------------------------------------------------
from backend.app.auth import create_access_token, decode_access_token


def main() -> None:

    sample_claims = {
        "sub": "1",
        "email": "student@example.com",
        "role": "student",
    }

    print("Original claims:", sample_claims)
    print("Subject type:", type(sample_claims["sub"]))

    token = create_access_token(sample_claims)

    print("\nGenerated JWT:\n", token)

    payload = decode_access_token(token)

    print("\nDecoded payload:\n", payload)


if __name__ == "__main__":
    main()
