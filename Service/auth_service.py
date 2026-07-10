import streamlit as st
from Core.auth_manager import crear_usuario, autenticar_usuario
from Service.transacciones_service import (
    registrar_usuario_si_no_existe,
    obtener_usuario
)


def inicializar_sesion():
    """
    Asegura que existan las variables base de sesión.
    """
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "user_info" not in st.session_state:
        st.session_state["user_info"] = None


def registrar_usuario_service(nombre, username, password, confirm_password):
    """
    Registra un nuevo usuario validando confirmación de contraseña.
    Además lo sincroniza con SQLite para manejo de roles.
    """
    if password != confirm_password:
        raise ValueError("Las contraseñas no coinciden.")

    if not nombre or not username or not password:
        raise ValueError("Todos los campos son obligatorios.")

    # 1) Registrar en tu sistema actual de autenticación
    usuario = crear_usuario(nombre, username, password)

    # 2) Registrar también en SQLite con rol por defecto = usuario
    registrar_usuario_si_no_existe(
        username=username,
        nombre=nombre,
        rol="usuario"
    )

    return usuario


def login_service(username, password):
    """
    Autentica al usuario, lo sincroniza con SQLite y guarda la sesión.
    """
    # 1) Autenticación contra tu sistema actual
    usuario = autenticar_usuario(username, password)

    # ==========================================================
    # Normalizar datos del usuario autenticado
    # ==========================================================
    # Soporta si auth_manager devuelve dict u objeto
    if isinstance(usuario, dict):
        username_real = (
            usuario.get("username")
            or usuario.get("usuario")
            or username
        )
        nombre_real = (
            usuario.get("nombre")
            or usuario.get("name")
            or username_real
        )
    else:
        username_real = getattr(usuario, "username", username)
        nombre_real = getattr(usuario, "nombre", username_real)

    # 2) Si no existe en SQLite, se crea como usuario normal
    registrar_usuario_si_no_existe(
        username=username_real,
        nombre=nombre_real,
        rol="usuario"
    )

    # 3) Consultar rol real desde SQLite
    usuario_db = obtener_usuario(username_real)

    rol_real = "usuario"
    if usuario_db and usuario_db.get("rol"):
        rol_real = usuario_db["rol"]

    # 4) Guardar sesión enriquecida
    user_info = {
        "username": username_real,
        "nombre": nombre_real,
        "rol": rol_real
    }

    st.session_state["authenticated"] = True
    st.session_state["user_info"] = user_info

    return user_info


def logout_service():
    """
    Cierra la sesión actual.
    """
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = None


def usuario_autenticado():
    return st.session_state.get("authenticated", False)


def obtener_usuario_actual():
    return st.session_state.get("user_info")