import streamlit as st


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
        st.markdown("## 📊 EXÓGENA DIAN")
        st.caption("Automatización tributaria para medios magnéticos")

        st.markdown("---")
        opcion = st.selectbox(
            "Módulo de trabajo",
            [
                "Diagnóstico Preliminar de Formatos",
                "Comparar Excel Dian vs Novasoft",
                "Generar XML para la DIAN"
            ]
        )

        st.markdown("---")
        st.markdown("### 🧭 Qué hace esta app")
        st.caption("""
        - Detecta formatos DIAN en libros de Excel  
        - Evalúa obligatoriedad preliminar  
        - Compara estructuras Novasoft vs DIAN  
        - Genera XML por formato con validaciones previas
        """)

        st.markdown("---")
        st.markdown("### ℹ️ Versión")
        st.caption("v1.0 · Vigencia base 2025")

    return opcion


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