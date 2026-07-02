import streamlit as st
from Service.auth_service import login_service, registrar_usuario_service
from Ui.components import section_header, status_box


def render_login_page():
    section_header(
        "🔐 Acceso al sistema",
        "Inicia sesión para ingresar al sistema de automatización de información exógena o crea una cuenta nueva."
    )

    tab1, tab2 = st.tabs(["Iniciar sesión", "Crear cuenta"])

    # ==========================================
    # TAB LOGIN
    # ==========================================
    with tab1:
        st.markdown("### Iniciar sesión")

        username_login = st.text_input("Usuario", key="login_user")
        password_login = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar", key="btn_login"):
            try:
                login_service(username_login, password_login)
                status_box("Inicio de sesión exitoso. Redirigiendo...", kind="ok")
                st.rerun()
            except Exception as e:
                status_box(str(e), kind="error")

    # ==========================================
    # TAB REGISTRO
    # ==========================================
    with tab2:
        st.markdown("### Crear cuenta")

        nombre = st.text_input("Nombre completo", key="reg_nombre")
        username = st.text_input("Nombre de usuario", key="reg_user")
        password = st.text_input("Contraseña", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirmar contraseña", type="password", key="reg_pass2")

        if st.button("Crear usuario", key="btn_register"):
            try:
                registrar_usuario_service(nombre, username, password, confirm_password)
                status_box(
                    "Usuario creado correctamente. Ahora ya puedes iniciar sesión desde la pestaña anterior.",
                    kind="ok"
                )
            except Exception as e:
                status_box(str(e), kind="error")