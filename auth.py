import bcrypt
from db_mongo import users

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def verify_password(password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash)

def register_user(email: str, password: str):
    email = email.strip().lower()
    if users.find_one({"email": email}):
        return None, "Ese email ya existe"

    doc = {
        "email": email,
        "password_hash": hash_password(password),
        "created_at": __import__("datetime").datetime.utcnow(),
    }
    result = users.insert_one(doc)
    return str(result.inserted_id), None

def login_user(email: str, password: str):
    email = email.strip().lower()
    u = users.find_one({"email": email})
    if not u:
        return None, "Usuario no encontrado"

    if not verify_password(password, u["password_hash"]):
        return None, "Contraseña incorrecta"

    return str(u["_id"]), None
