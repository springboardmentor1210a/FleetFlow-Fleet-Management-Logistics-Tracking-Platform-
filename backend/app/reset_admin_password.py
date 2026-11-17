"""Reset an Administrator password from the local backend terminal."""

from getpass import getpass

from sqlalchemy import select

from .auth import password_hasher
from .database import SessionLocal
from .models import User


def main() -> None:
    email = input("Administrator email (press Enter to list saved accounts): ").strip().lower()
    with SessionLocal() as db:
        if not email:
            admin_emails = db.scalars(
                select(User.email).where(User.role == "administrator").order_by(User.email)
            ).all()
            if admin_emails:
                print("Administrator email address(es) in this database:")
                for admin_email in admin_emails:
                    print(f"- {admin_email}")
            else:
                print("No Administrator accounts were found in this database.")
            return

        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            admin_emails = db.scalars(
                select(User.email).where(User.role == "administrator").order_by(User.email)
            ).all()
            if admin_emails:
                print("Administrator email address(es) in this database:")
                for admin_email in admin_emails:
                    print(f"- {admin_email}")
            raise SystemExit("No account matches that email. Check the address and try again.")
        if user.role != "administrator":
            raise SystemExit("That account is not an Administrator. No changes were made.")

        new_password = getpass("New password (at least 12 characters): ")
        confirmation = getpass("Enter the new password again: ")
        if len(new_password) < 12:
            raise SystemExit("Choose a password with at least 12 characters.")
        if new_password != confirmation:
            raise SystemExit("The passwords did not match.")
        user.password_hash = password_hasher.hash(new_password)
        db.commit()
    print("Administrator password updated. Sign in with the new password.")


if __name__ == "__main__":
    main()
