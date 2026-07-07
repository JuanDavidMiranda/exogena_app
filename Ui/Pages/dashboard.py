import streamlit as st

from Service.auth_service import obtener_usuario_actual


def render_dashboard():
    usuario = obtener_usuario_actual()

    nombre = "Usuario"
    if usuario:
        nombre = usuario.get("nombre", "Usuario")

    st.markdown("""
    <div style="
        background: linear-gradient(90deg,#0f62fe,#2563eb);
        padding:30px;
        border-radius:15px;
        color:white;
        margin-bottom:25px;
    ">
        <h1 style="margin:0;">📊 EXÓGENA DIAN</h1>
        <p style="font-size:18px;margin-top:8px;">
            Sistema de Automatización de Información Exógena
        </p>
        <p style="margin-top:5px;">
            Vigencia Base 2025
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"# ¡Bienvenido, {nombre}! 👋")

    st.write(
        """
Selecciona uno de los módulos desde el menú lateral para comenzar a trabajar.
"""
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            """
### 🔍 Diagnóstico Preliminar

Detecta automáticamente los formatos presentes en el Excel y verifica si contienen información válida.
"""
        )

    with col2:

        st.info(
            """
### 📊 Comparar Excel

Compara la estructura entre el archivo Novasoft y el formato oficial de la DIAN.
"""
        )

    st.write("")

    st.success(
        """
### 📄 Generación de XML

Convierte automáticamente el archivo de Excel en el XML requerido para la presentación ante la DIAN.
"""
    )

    st.write("")
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Versión",
            "1.0"
        )

    with col2:
        st.metric(
            "Vigencia",
            "2025"
        )

    with col3:
        st.metric(
            "Estado",
            "Operativo ✅"
        )

    st.divider()

    st.caption(
        "Bienvenido a Exógena DIAN. Utiliza el menú lateral para acceder a cada uno de los módulos disponibles."
    )