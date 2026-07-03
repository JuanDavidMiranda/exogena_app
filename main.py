import os
import sys
import asyncio
import streamlit as st

# ==========================================
# PARCHE DE RUTA
# ==========================================
ruta_actual = os.path.dirname(os.path.abspath(__file__))
if ruta_actual not in sys.path:
    sys.path.insert(0, ruta_actual)

# ==========================================
# PARCHE WINDOWS / STREAMLIT
# ==========================================
if sys.platform == "win32":
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# ==========================================
# IMPORTS UI Y AUTH
# ==========================================
from Ui.styles import load_global_styles
from Ui.components import render_hero, render_sidebar
from Ui.Pages.login_page import render_login_page
from Ui.Pages.diagnostico_page import render_diagnostico_page
from Ui.Pages.auditoria_page import render_auditoria_page
from Ui.Pages.xml_page import render_xml_page
from Service.auth_service import inicializar_sesion, usuario_autenticado

# ==========================================
# CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(
    page_title="Automatización Exógena DIAN",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS Y SESIÓN
# ==========================================
load_global_styles()
inicializar_sesion()

# ==========================================
# BLOQUEO SI NO HAY LOGIN
# ==========================================
if not usuario_autenticado():
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

    render_login_page()
    st.stop()

# ==========================================
# APP PRINCIPAL
# ==========================================
render_hero()
opcion = render_sidebar()

if opcion == "Diagnóstico Preliminar de Formatos":
    render_diagnostico_page()

elif opcion == "Comparar Excel Dian vs Novasoft":
    render_auditoria_page()

elif opcion == "Generar XML para la DIAN":
    render_xml_page()