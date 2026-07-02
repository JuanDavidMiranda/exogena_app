import streamlit as st
from Core.auth_manager import crear_usuario, autenticar_usuario


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
    """
    if password != confirm_password:
        raise ValueError("Las contraseñas no coinciden.")

    usuario = crear_usuario(nombre, username, password)
    return usuario


def login_service(username, password):
    """
    Autentica al usuario y guarda su sesión.
    """
    usuario = autenticar_usuario(username, password)

    st.session_state["authenticated"] = True
    st.session_state["user_info"] = usuario

    return usuario


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