import streamlit as st
from Service.auth_service import obtener_usuario_actual
from Service.normative_service import obtener_formatos_soportados

def render_dashboard():
    usuario = obtener_usuario_actual()

    nombre = "Usuario"
    rol = "usuario"

    if usuario:
        nombre = usuario.get("nombre", "Usuario")
        rol = usuario.get("rol", "usuario")

    formatos = obtener_formatos_soportados(2025)
    cantidad_formatos = len(formatos)
    cantidad_modulos = 3

    # =========================
    # HERO / ENCABEZADO
    # =========================
    st.markdown("""
    <div style="
        background: linear-gradient(90deg,#0f62fe,#2563eb);
        padding:30px;
        border-radius:18px;
        color:white;
        margin-bottom:25px;
        box-shadow:0 6px 18px rgba(0,0,0,.12);
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
    st.write("Selecciona uno de los módulos para comenzar a trabajar.")

    # =========================
    # ESTILOS DE TARJETAS
    # =========================
    st.markdown("""
    <style>
    .card {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 24px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 12px rgba(0,0,0,.08);
        min-height: 220px;
        margin-bottom: 10px;
    }

    .card-icon {
        font-size: 38px;
        margin-bottom: 8px;
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 10px;
    }

    .card-text {
        color: #475569;
        line-height: 1.6;
        font-size: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # =========================
    # TARJETAS SUPERIORES
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-icon">🔍</div>
            <div class="card-title">Diagnóstico Preliminar</div>
            <div class="card-text">
                Analiza el archivo Excel para detectar automáticamente los formatos
                DIAN presentes y validar la estructura antes del procesamiento.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "🔍 Abrir Diagnóstico",
            key="dashboard_diag",
            use_container_width=True
        ):
            st.session_state.modulo = "Diagnóstico Preliminar de Formatos"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-icon">📊</div>
            <div class="card-title">Comparar Excel</div>
            <div class="card-text">
                Compara la estructura del archivo Novasoft con el formato oficial
                de la DIAN para identificar diferencias e inconsistencias.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "📊 Abrir Comparador",
            key="dashboard_compare",
            use_container_width=True
        ):
            st.session_state.modulo = "Comparar Excel Dian vs Novasoft"
            st.rerun()

    # =========================
    # TARJETA INFERIOR
    # =========================
    st.write("")

    st.markdown("""
    <div class="card">
        <div class="card-icon">📄</div>
        <div class="card-title">Generar XML</div>
        <div class="card-text">
            Convierte automáticamente los datos del Excel en el XML requerido por
            la DIAN, realizando las validaciones necesarias antes de la generación.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "📄 Generar XML",
        key="dashboard_xml",
        use_container_width=True
    ):
        st.session_state.modulo = "Generar XML para la DIAN"
        st.rerun()

    # =========================
    # MÉTRICAS
    # =========================
    st.write("")
    st.divider()

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Versión", "1.0")

    with m2:
        st.metric("Vigencia", "2025")

    with m3:
        st.metric("Estado", "Operativo ✅")

    st.divider()

    st.caption(
        "Bienvenido a Exógena DIAN. Utiliza el menú lateral o las tarjetas de inicio para acceder a los módulos."
    )

    st.write("")
    st.markdown("## 🧾 Resumen del sistema")

    r1, r2 = st.columns(2)

    with r1:
        st.info(
        f"""
        **👤 Usuario activo:** {nombre}  
        **🛡️ Rol:** {rol}  
        **📅 Vigencia base:** 2025  
        **🧩 Módulos disponibles:** {cantidad_modulos}
        """
    )

    with r2:
        formatos_texto = ", ".join(formatos)

    st.success(
        f"""
        **📂 Formatos soportados:** {cantidad_formatos}  
        **🔢 Códigos disponibles:** {formatos_texto}
        """
    )