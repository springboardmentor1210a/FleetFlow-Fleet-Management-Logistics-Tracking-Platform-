"""Create the first Administrator account for a new local FleetFlow database."""

from getpass import getpass

from sqlalchemy import select

from .auth import password_hasher
from .database import SessionLocal
from .models import User


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(User.user_id).limit(1)) is not None:
            print("A user account already exists. Ask an Administrator to add users.")
            return

        full_name = input("Administrator full name: ").strip()
        email = input("Administrator email: ").strip().lower()
        password = getpass("Choose a password (at least 12 characters): ")
        confirmation = getpass("Enter the password again: ")
        if not full_name or not email or "@" not in email:
            raise SystemExit("Enter a name and valid email address.")
        if len(password) < 12:
            raise SystemExit("Choose a password with at least 12 characters.")
        if password != confirmation:
            raise SystemExit("The passwords did not match.")

        db.add(
            User(
                full_name=full_name,
                email=email,
                password_hash=password_hasher.hash(password),
                role="administrator",
            )
        )
        db.commit()
    print("Administrator account created. You can now sign in to FleetFlow.")


if __name__ == "__main__":
    main()
