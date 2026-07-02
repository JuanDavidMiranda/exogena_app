import json
import os
from werkzeug.security import generate_password_hash, check_password_hash


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

    password_hash = generate_password_hash(password)

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

    if not check_password_hash(password_hash, password):
        raise ValueError("Contraseña incorrecta.")

    return {
        "nombre": usuario.get("nombre", username),
        "username": usuario.get("username", username),
        "rol": usuario.get("rol", "usuario")
    }