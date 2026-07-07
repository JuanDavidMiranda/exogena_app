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

    st.markdown("""
<style>

.card{
    background-color:#ffffff;
    border-radius:15px;
    padding:25px;
    border:1px solid #E5E7EB;
    box-shadow:0 3px 10px rgba(0,0,0,.08);
    height:220px;
    margin-bottom:10px;
}

.card h3{
    margin-top:10px;
    color:#2563eb;
}

.card p{
    color:#555555;
    line-height:1.6;
}

.icon{
    font-size:40px;
}

</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ===========================
# TARJETA DIAGNÓSTICO
# ===========================
with col1:

    st.markdown("""
    <div class="card">
        <div class="icon">🔍</div>
        <h3>Diagnóstico Preliminar</h3>
        <p>
        Analiza el archivo Excel para detectar automáticamente los formatos DIAN
        presentes y verificar su estructura antes del procesamiento.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "🔍 Abrir Diagnóstico",
        key="dashboard_diag",
        use_container_width=True
    ):
        st.session_state.modulo = "Diagnóstico Preliminar de Formatos"
        st.rerun()


# ===========================
# TARJETA COMPARAR
# ===========================
with col2:

    st.markdown("""
    <div class="card">
        <div class="icon">📊</div>
        <h3>Comparar Excel</h3>
        <p>
        Compara la estructura del archivo Novasoft con la plantilla oficial de la
        DIAN para identificar diferencias y posibles inconsistencias.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "📊 Abrir Comparador",
        key="dashboard_compare",
        use_container_width=True
    ):
        st.session_state.modulo = "Comparar Excel Dian vs Novasoft"
        st.rerun()


# ===========================
# TARJETA XML
# ===========================

st.write("")

st.markdown("""
<div class="card">
    <div class="icon">📄</div>
    <h3>Generar XML</h3>
    <p>
    Convierte automáticamente los datos del Excel en el XML requerido por la DIAN,
    realizando las validaciones necesarias antes de la generación.
    </p>
</div>
""", unsafe_allow_html=True)

if st.button(
    "📄 Generar XML",
    key="dashboard_xml",
    use_container_width=True
):
    st.session_state.modulo = "Generar XML para la DIAN"
    st.rerun()


# ===========================
# MÉTRICAS
# ===========================

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