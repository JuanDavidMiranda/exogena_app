import streamlit as st

from Service.transacciones_service import (
    registrar_usuario_si_no_existe,
    obtener_rol_usuario
)

# ==========================================================
# USUARIOS DE ACCESO / ORIGEN DE AUTENTICACIÓN
# ==========================================================
# Aquí dejas los usuarios válidos para iniciar sesión.
# Luego, SQLite se encarga de persistirlos y guardar su rol.
USUARIOS_APP = {
    "prueba": {
        "password": "12345",
        "nombre": "Usuario Prueba"
    },
    "juan": {
        "password": "12345",
        "nombre": "juan david miranda"
    }
}


# ==========================================================
# SESIÓN
# ==========================================================
def inicializar_sesion():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if "username" not in st.session_state:
        st.session_state.username = None

    if "nombre" not in st.session_state:
        st.session_state.nombre = None

    if "rol" not in st.session_state:
        st.session_state.rol = None

    if "user_info" not in st.session_state:
        st.session_state.user_info = None


def usuario_autenticado():
    return st.session_state.get("autenticado", False)


def es_admin():
    return st.session_state.get("rol") == "admin"


def cerrar_sesion():
    st.session_state.autenticado = False
    st.session_state.username = None
    st.session_state.nombre = None
    st.session_state.rol = None
    st.session_state.user_info = None
    st.rerun()


# ==========================================================
# AUTENTICACIÓN
# ==========================================================
def autenticar_usuario(username: str, password: str):
    """
    Valida el usuario contra la fuente actual de autenticación
    y luego sincroniza/recupera su rol desde SQLite.
    """
    username = (username or "").strip().lower()
    password = (password or "").strip()

    if not username or not password:
        return False, "Debes ingresar usuario y contraseña."

    usuario = USUARIOS_APP.get(username)

    if not usuario:
        return False, "Usuario no encontrado."

    if usuario["password"] != password:
        return False, "Contraseña incorrecta."

    nombre = usuario.get("nombre", username)

    # ======================================================
    # 1) Registrar el usuario en SQLite si no existe
    #    Siempre entra como 'usuario' la primera vez.
    # ======================================================
    registrar_usuario_si_no_existe(
        username=username,
        nombre=nombre,
        rol="usuario"
    )

    # ======================================================
    # 2) Recuperar el rol real desde SQLite
    #    Si ya fue ascendido a admin, aquí se conserva.
    # ======================================================
    rol_real = obtener_rol_usuario(username)

    # Fallback de seguridad
    if not rol_real:
        rol_real = "usuario"

    # ======================================================
    # 3) Guardar sesión
    # ======================================================
    st.session_state.autenticado = True
    st.session_state.username = username
    st.session_state.nombre = nombre
    st.session_state.rol = rol_real
    st.session_state.user_info = {
        "username": username,
        "nombre": nombre,
        "rol": rol_real
    }

    return True, "Inicio de sesión exitoso."


# ==========================================================
# HELPERS DE USUARIO EN SESIÓN
# ==========================================================
def obtener_usuario_actual():
    if not usuario_autenticado():
        return None

    return {
        "username": st.session_state.get("username"),
        "nombre": st.session_state.get("nombre"),
        "rol": st.session_state.get("rol")
    }