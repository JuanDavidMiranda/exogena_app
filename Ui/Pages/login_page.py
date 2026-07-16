import streamlit as st
from Service.auth_service import login_service, registrar_usuario_service
from Ui.components import status_box


def render_login_page():
    st.markdown('<div class="login-page-shell">', unsafe_allow_html=True)

    st.markdown("""
    <div class="login-page-header">
        <div class="login-page-badge">🔐 Acceso seguro</div>
        <div class="login-logo-wrap">
            <div class="login-logo-mark">EX</div>
            <div>
                <h1>Plataforma de Información Exógena</h1>
                <p>
                    Inicia sesión o crea una cuenta para acceder al sistema con una experiencia más clara, segura y profesional.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-layout-card">', unsafe_allow_html=True)

    col_info, col_form = st.columns([1.05, 0.95], gap="large")

    # ==========================================================
    # COLUMNA IZQUIERDA - INFO / BRANDING
    # ==========================================================
    with col_info:
        st.markdown("""
            <div class="login-brand-panel">
                <div class="login-brand-title">EXÓGENA APP</div>
                <div class="login-brand-subtitle">
                    Una solución pensada para apoyar la gestión de información exógena
                    con un flujo más claro, organizado y profesional.
                </div>
                <div class="login-brand-highlight">
                    <span>⚡ Automatización</span>
                    <span>🧠 Trazabilidad</span>
                    <span>🔐 Seguridad</span>
                </div>

                <div class="login-feature-box">
                    <strong>📊 Diagnóstico preliminar</strong>
                    <span>Analiza formatos y detecta hojas con información relevante antes de generar el reporte.</span>
                </div>

                <div class="login-feature-box">
                    <strong>🧾 Generación de XML</strong>
                    <span>Centraliza la construcción del XML con validaciones y trazabilidad del proceso.</span>
                </div>

                <div class="login-feature-box">
                    <strong>🔎 Validación y conciliación</strong>
                    <span>Apoya la revisión de inconsistencias, faltantes y diferencias entre archivos.</span>
                </div>

                <div class="login-security-note">
                    <strong>Seguridad de acceso</strong>
                    <span>
                        El ingreso al sistema se realiza mediante autenticación de usuarios,
                        protegiendo el acceso a los módulos del aplicativo.
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ==========================================================
    # COLUMNA DERECHA - FORMULARIO
    # ==========================================================
    with col_form:
        st.markdown("""
            <div class="login-form-panel">
                <div class="login-form-header">
                    <h2>Bienvenido</h2>
                    <p>Ingresa con tus credenciales o crea tu cuenta para continuar</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-form-card">', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Iniciar sesión", "Crear cuenta"])

        # ==========================================
        # TAB LOGIN
        # ==========================================
        with tab1:
            st.markdown("### Iniciar sesión")
            st.markdown('<div class="login-input-group">', unsafe_allow_html=True)
            username_login = st.text_input("Usuario", key="login_user")
            password_login = st.text_input("Contraseña", type="password", key="login_pass")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Ingresar al sistema", key="btn_login", use_container_width=True):
                try:
                    login_service(username_login, password_login)
                    status_box("Inicio de sesión exitoso. Redirigiendo...", kind="ok")
                    st.rerun()
                except Exception as e:
                    status_box(str(e), kind="error")

            st.markdown("""
                <div class="login-mini-help">
                    ¿Aún no tienes cuenta? Puedes crearla desde la pestaña
                    <strong>Crear cuenta</strong>.
                </div>
            """, unsafe_allow_html=True)

        # ==========================================
        # TAB REGISTRO
        # ==========================================
        with tab2:
            st.markdown("### Crear cuenta")
            st.markdown('<div class="login-input-group">', unsafe_allow_html=True)
            nombre = st.text_input("Nombre completo", key="reg_nombre")
            username = st.text_input("Nombre de usuario", key="reg_user")
            password = st.text_input("Contraseña", type="password", key="reg_pass")
            confirm_password = st.text_input("Confirmar contraseña", type="password", key="reg_pass2")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Crear usuario", key="btn_register", use_container_width=True):
                try:
                    registrar_usuario_service(nombre, username, password, confirm_password)
                    status_box(
                        "Usuario creado correctamente. Ahora ya puedes iniciar sesión desde la pestaña anterior.",
                        kind="ok"
                    )
                except Exception as e:
                    status_box(str(e), kind="error")

            st.markdown("""
                <div class="login-mini-help">
                    Usa una contraseña segura y un nombre de usuario fácil de recordar.
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)