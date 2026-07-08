import streamlit as st
from Service.auth_service import obtener_usuario_actual, logout_service

def render_hero():
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">Sistema de Automatización de Información Exógena</div>
        <div class="hero-subtitle">
            Diagnóstico preliminar, conciliación de formatos y generación de XML para medios magnéticos DIAN.
        </div>
        <div class="badge-row">
            <div class="badge-pill">📋 Diagnóstico de formatos</div>
            <div class="badge-pill">🔄 Auditoría Novasoft vs DIAN</div>
            <div class="badge-pill">📦 Generación XML</div>
            <div class="badge-pill">🧠 Validación previa de estructura</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        usuario = obtener_usuario_actual()

        st.markdown("## 📊 EXÓGENA DIAN")
        st.caption("Automatización tributaria para medios magnéticos")

        st.divider()

        if usuario:
            st.markdown("### 👤 Sesión activa")
            st.write(f"**{usuario.get('nombre', 'Sin nombre')}**")
            st.caption(f"Rol: {usuario.get('rol', 'usuario')}")

        st.divider()

        st.markdown("### 📂 Módulos")

        if "modulo" not in st.session_state:
            st.session_state.modulo = "Inicio"

        if st.button(
            "🏠 Inicio",
            use_container_width=True,
        ):
            st.session_state.modulo = "Inicio"
            st.rerun()

        if st.button(
            "🔍 Diagnóstico Preliminar",
            use_container_width=True,
        ):
            st.session_state.modulo = "Diagnóstico Preliminar de Formatos"
            st.rerun()

        if st.button(
            "📊 Comparar Excel",
            use_container_width=True,
        ):
            st.session_state.modulo = "Comparar Excel Dian vs Novasoft"
            st.rerun()

        if st.button(
            "📄 Generar XML",
            use_container_width=True,
        ):
            st.session_state.modulo = "Generar XML para la DIAN"
            st.rerun()

        st.divider()

        if st.button(
            "🚪 Cerrar sesión",
            use_container_width=True,
        ):
            logout_service()
            st.rerun()

        st.divider()

        with st.expander("🧭 Acerca de la aplicación"):
            st.caption("""
            • Detecta formatos DIAN en archivos Excel.

            • Evalúa la obligatoriedad preliminar.

            • Compara la estructura Novasoft vs DIAN.

            • Genera XML listos para presentar ante la DIAN.
            """)

        st.caption("Versión 1.0 • Vigencia 2025")

    return st.session_state.modulo


def section_header(title, subtitle):
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, help_text=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-help">{help_text}</div>
    </div>
    """, unsafe_allow_html=True)


def status_box(message, kind="ok"):
    css_class = {
        "ok": "status-ok",
        "warning": "status-warning",
        "error": "status-error"
    }.get(kind, "status-ok")

    st.markdown(f'<div class="{css_class}">{message}</div>', unsafe_allow_html=True)


def step_card(title, desc):
    st.markdown(f"""
    <div class="step-card">
        <div class="step-title">{title}</div>
        <div class="step-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


def soft_divider():
    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)


def detectar_formato_desde_pestana(nombre_pestana):
    for fmt in ["1001", "1003", "1004", "1005", "1006", "1007", "1008", "1009"]:
        if fmt in str(nombre_pestana):
            return fmt
    return None