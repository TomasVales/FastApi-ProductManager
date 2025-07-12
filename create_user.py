# create_user.py
from database import SessionLocal, create_tables
from models import User  # Usamos el modelo oficial
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user():
    create_tables()  # Esto usa Base desde models, no local
    db = SessionLocal()
    hashed_password = pwd_context.hash("admin123")
    user = User(username="admin", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.close()
    print("✅ Usuario 'admin' creado con contraseña 'admin123'")


if __name__ == "__main__":
    create_user()
