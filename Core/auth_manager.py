import json
import os
import hashlib
import hmac
import secrets
import base64


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(BASE_DIR, "config", "users.json")


def asegurar_archivo_usuarios():
    """
    Crea el archivo users.json si no existe.
    """
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)


def cargar_usuarios():
    """
    Retorna el diccionario de usuarios registrados.
    """
    asegurar_archivo_usuarios()

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def guardar_usuarios(usuarios):
    """
    Sobrescribe el archivo users.json con el diccionario recibido.
    """
    asegurar_archivo_usuarios()

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)


def existe_usuario(username):
    usuarios = cargar_usuarios()
    return username.strip().lower() in usuarios


# ==========================================================
# FUNCIONES DE HASH SIN DEPENDENCIAS EXTERNAS
# ==========================================================
def hash_password(password: str) -> str:
    """
    Genera un hash seguro con PBKDF2-HMAC-SHA256.
    Guarda el resultado en formato:
    pbkdf2_sha256$iteraciones$salt_base64$hash_base64
    """
    if not isinstance(password, str):
        raise ValueError("La contraseña debe ser texto.")

    salt = secrets.token_bytes(16)
    iterations = 100_000

    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations
    )

    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(pwd_hash).decode("utf-8")

    return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifica una contraseña contra un hash almacenado.
    """
    try:
        algorithm, iterations, salt_b64, hash_b64 = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)
        salt = base64.b64decode(salt_b64.encode("utf-8"))
        original_hash = base64.b64decode(hash_b64.encode("utf-8"))

        test_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations
        )

        return hmac.compare_digest(original_hash, test_hash)

    except Exception:
        return False


# ==========================================================
# CRUD BÁSICO DE USUARIOS
# ==========================================================
def crear_usuario(nombre, username, password, rol="usuario"):
    """
    Crea un usuario nuevo con contraseña hasheada.
    """
    if not nombre or not str(nombre).strip():
        raise ValueError("El nombre es obligatorio.")

    if not username or not str(username).strip():
        raise ValueError("El nombre de usuario es obligatorio.")

    if not password or len(password) < 4:
        raise ValueError("La contraseña debe tener al menos 4 caracteres.")

    username = username.strip().lower()
    nombre = nombre.strip()

    usuarios = cargar_usuarios()

    if username in usuarios:
        raise ValueError("El usuario ya existe. Elige otro nombre de usuario.")

    password_hash = hash_password(password)

    usuarios[username] = {
        "nombre": nombre,
        "username": username,
        "password_hash": password_hash,
        "rol": rol
    }

    guardar_usuarios(usuarios)

    return {
        "nombre": nombre,
        "username": username,
        "rol": rol
    }


def autenticar_usuario(username, password):
    """
    Valida credenciales y retorna datos del usuario si son correctos.
    """
    if not username or not password:
        raise ValueError("Debes ingresar usuario y contraseña.")

    username = username.strip().lower()
    usuarios = cargar_usuarios()

    if username not in usuarios:
        raise ValueError("Usuario no encontrado.")

    usuario = usuarios[username]
    password_hash = usuario.get("password_hash", "")

    if not verify_password(password, password_hash):
        raise ValueError("Contraseña incorrecta.")

    return {
        "nombre": usuario.get("nombre", username),
        "username": usuario.get("username", username),
        "rol": usuario.get("rol", "usuario")
    }