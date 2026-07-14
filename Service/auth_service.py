import streamlit as st
import hashlib
import secrets
import base64
import hmac
from Service.transacciones_service import (
    registrar_usuario_si_no_existe,
    obtener_usuario,
    get_connection
)

# ==========================================================
# UTILIDADES DE SEGURIDAD (Migradas de forma interna)
# ==========================================================
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 100_000
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(pwd_hash).decode("utf-8")
    return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, hash_b64 = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations)
        salt = base64.b64decode(salt_b64.encode("utf-8"))
        original_hash = base64.b64decode(hash_b64.encode("utf-8"))
        test_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(original_hash, test_hash)
    except Exception:
        return False

# ==========================================================
# SERVICIOS DE AUTENTICACIÓN DIRECTOS EN SQLITE
# ==========================================================
def inicializar_sesion():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_info" not in st.session_state:
        st.session_state["user_info"] = None

def registrar_usuario_service(nombre, username, password, confirm_password):
    if password != confirm_password:
        raise ValueError("Las contraseñas no coinciden.")
    if not nombre or not username or not password:
        raise ValueError("Todos los campos son obligatorios.")
    if len(password) < 4:
        raise ValueError("La contraseña debe tener al menos 4 caracteres.")

    username_clean = username.strip().lower()
    
    # Validar si ya existe directamente en SQLite
    if obtener_usuario(username_clean) is not None:
        raise ValueError("El usuario ya existe en el sistema. Elige otro.")

    # Hashear contraseña e insertar directamente en la BD
    pwd_encrypted = hash_password(password)
    registrar_usuario_si_no_existe(
        username=username_clean,
        nombre=nombre.strip(),
        password_hash=pwd_encrypted,
        rol="usuario"
    )
    return True

def login_service(username, password):
    if not username or not password:
        raise ValueError("Debes ingresar usuario y contraseña.")

    username_clean = username.strip().lower()
    
    # Consultar datos directo de SQLite
    usuario_db = obtener_usuario(username_clean)
    
    if not usuario_db or not usuario_db.get("password_hash"):
        raise ValueError("Usuario no encontrado.")

    # Verificar credenciales desde la columna de la BD
    if not verify_password(password, usuario_db["password_hash"]):
        raise ValueError("Contraseña incorrecta.")

    # Guardar sesión activa con el rol real de SQLite
    user_info = {
        "username": usuario_db["username"],
        "nombre": usuario_db["nombre"],
        "rol": usuario_db["rol"]
    }

    st.session_state["authenticated"] = True
    st.session_state["user_info"] = user_info
    return user_info

def cerrar_sesion():
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = None
    st.rerun()

def logout_service():
    cerrar_sesion()

def usuario_autenticado():
    return st.session_state.get("authenticated", False)

def obtener_usuario_actual():
    return st.session_state.get("user_info")