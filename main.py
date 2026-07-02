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
# IMPORTS UI
# ==========================================
from Ui.styles import load_global_styles
from Ui.components import render_hero, render_sidebar
from Ui.Pages.diagnostico_page import render_diagnostico_page
from Ui.Pages.auditoria_page import render_auditoria_page
from Ui.Pages.xml_page import render_xml_page

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
# CARGAR ESTILOS Y LAYOUT BASE
# ==========================================
load_global_styles()
render_hero()
opcion = render_sidebar()

# ==========================================
# ROUTING DE PÁGINAS
# ==========================================
if opcion == "Diagnóstico Preliminar de Formatos":
    render_diagnostico_page()

elif opcion == "Comparar Excel Dian vs Novasoft":
    render_auditoria_page()

elif opcion == "Generar XML para la DIAN":
    render_xml_page()