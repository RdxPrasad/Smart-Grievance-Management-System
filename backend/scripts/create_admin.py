
from getpass import getpass

from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import User
from app.auth import hash_password


def create_admin():
    print("\n===== ResolveRAG: Initial Admin Setup =====\n")

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()
    password = getpass("Enter admin password: ")
    confirm_password = getpass("Confirm admin password: ")

    # Validate input
    if not name or not email or not password:
        print("Error: All fields are required.")
        return

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    if len(password.encode("utf-8")) > 72:
        print("Error: Password must not exceed 72 bytes.")
        return

    db = SessionLocal()

    try:
        # Check whether this email already exists
        existing_user = db.query(User).filter(
            User.email.ilike(email)
        ).first()

        if existing_user:
            print("Error: This email already exists.")
            print("No existing account has been modified.")
            return

        # Hash the password using the existing auth function
        hashed_password = hash_password(password)

        # Create the administrator
        admin = User(
            name=name,
            email=email,
            role="admin",
            hashed_password=hashed_password,
            department_id=None
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nAdmin account created successfully!")
        print(f"Admin ID: {admin.id}")
        print(f"Name: {admin.name}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")

    except IntegrityError:
        db.rollback()
        print("Error: Database constraint failed. No account was created.")

    except Exception as error:
        db.rollback()
        print(f"An unexpected error occurred: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
