import os
import sys
import traceback

# Parche estricto para forzar la visibilidad del módulo 'core'
ruta_actual = os.path.dirname(os.path.abspath(__file__))
if ruta_actual not in sys.path:
    sys.path.insert(0, ruta_actual)

# Ahora sí, el resto de tus imports respirarán tranquilos
import asyncio
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import io

from Service.diagnostic_service import ejecutar_diagnostico_service
from Service.audit_service import ejecutar_auditoria_service
from Service.xml_service import (
    obtener_pestanas_validas_service,
    generar_xml_service
)
# ==========================================
# PARCHE SEGURO PARA WINDOWS (COMPATIBLE PYTHON 3.14+)
# ==========================================
if sys.platform == "win32":
    try:
        # Usamos un bloque try-except amigable para evitar advertencias de deprecación
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass


st.set_page_config(page_title="Automatización Exógena DIAN", page_icon="📊", layout="wide")
st.title("📊 Sistema de Automatización de Información Exógena")
st.write("Carga tus archivos de Novasoft / Excel para procesar las validaciones o generar los XML oficiales.")

opcion = st.sidebar.selectbox("Seleccione una opción de visualización:", [
    "Diagnóstico Preliminar de Formatos", 
    "Comparar Excel Dian vs Novasoft", 
    "Generar XML para la DIAN"
])

# --- MÓDULO 1: DIAGNÓSTICO ---
if opcion == "Diagnóstico Preliminar de Formatos":
    st.header("📋 Diagnóstico Inteligente de Medios Magnéticos")
    archivo_maestro = st.file_uploader("Sube el libro de Excel con los formatos", type=["xlsx"])

    if archivo_maestro is not None:
        try:
            resultado = ejecutar_diagnostico_service(archivo_maestro)

            if resultado["resultados"]:
                st.dataframe(resultado["resultados"], use_container_width=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("Formatos analizados", resultado["total_formatos"])
                c2.metric("Con datos", resultado["formatos_con_datos"])
                c3.metric("Vacíos", resultado["formatos_vacios"])

                st.markdown("### 💡 Plan de Acción Sugerido:")
                for f in resultado["resultados"]:
                    if "🟢" in f["Dictamen"]:
                        st.success(
                            f"**{f['Formato DIAN']} ({f['Nombre de la Pestaña']}):** "
                            f"Acción requerida. Se detectaron **{f['Terceros Detectados']}** registros."
                        )
                    else:
                        st.error(
                            f"**{f['Formato DIAN']} ({f['Nombre de la Pestaña']}):** "
                            f"Omitir. Hoja vacía."
                        )
            else:
                st.warning("⚠️ No se identificaron pestañas válidas.")

        except Exception as e:
            st.error(f"❌ Error en el diagnóstico: {e}")

# --- MÓDULO 2: CONCILIACIÓN ---
elif opcion == "Comparar Excel Dian vs Novasoft":
    st.header("🔄 Auditoría de Datos: Novasoft vs Formatos DIAN")

    col1, col2 = st.columns(2)
    with col1:
        archivo_novasoft = st.file_uploader("Sube el reporte de NOVASOFT", type=["xlsx", "xls", "csv"])
    with col2:
        archivo_dian = st.file_uploader("Sube el borrador de formato DIAN", type=["xlsx", "csv"])

    if archivo_novasoft and archivo_dian:
        try:
            resultado = ejecutar_auditoria_service(archivo_novasoft, archivo_dian)

            st.success("✅ Cruce completado con éxito.")

            c1, c2, c3 = st.columns(3)
            c1.metric("Diferencias en Montos", resultado["resumen"]["diferencias_montos"])
            c2.metric("Solo en DIAN", resultado["resumen"]["solo_dian"])
            c3.metric("Solo en Novasoft", resultado["resumen"]["solo_novasoft"])

            dif_montos = resultado["dif_montos"]
            solo_dian = resultado["solo_dian"]
            solo_novasoft = resultado["solo_novasoft"]

            import io
            import pandas as pd

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                dif_montos.to_excel(writer, sheet_name='Diferencias_Montos', index=False)
                solo_dian.to_excel(writer, sheet_name='Solo_en_DIAN', index=False)
                solo_novasoft.to_excel(writer, sheet_name='Solo_en_Novasoft', index=False)

            buffer.seek(0)

            st.download_button(
                label="📥 Descargar Conciliación Final (.xlsx)",
                data=buffer,
                file_name="conciliacion_final_exogena.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Error al procesar estructuras: {e}")

# --- MÓDULO 3: XML GENERATOR ---
if opcion == "Generar XML para la DIAN":
    st.header("📦 Generador Dinámico de Archivos XML (Medios Magnéticos)")
    st.write("Sube el archivo Excel de Actualícese. El sistema detectará automáticamente el formato según el nombre de la pestaña elegida.")

    col1, col2, col3 = st.columns(3)
    with col1:
        ano = st.number_input("Año Gravable:", min_value=2020, max_value=2030, value=2025)
    with col2:
        envio = st.number_input("Número de Envío:", min_value=1, max_value=9999, value=1)
    with col3:
        st.info("ℹ️ Las versiones del XML se configuran automáticamente.")

    archivo_excel = st.file_uploader("Carga el archivo de Excel oficial (.xlsx):", type=["xlsx"])

    if archivo_excel is not None:
        try:
            pestanas_formatos = obtener_pestanas_validas_service(archivo_excel)
            pestana_seleccionada = st.selectbox(
                "Selecciona la pestaña del formato a procesar:",
                pestanas_formatos
            )

            if st.button("🚀 Generar XML"):
                with st.spinner(f"Procesando la pestaña '{pestana_seleccionada}'..."):
                    resultado = generar_xml_service(
                        archivo_excel=archivo_excel,
                        pestana_seleccionada=pestana_seleccionada,
                        ano=ano,
                        envio=envio
                    )

                    st.success(
                        f"✅ ¡XML del Formato {resultado['formato_detectado']} generado exitosamente!"
                    )

                    c1, c2 = st.columns(2)
                    c1.metric("Cantidad de Terceros Reportados", f"{resultado['total_registros']:,}")
                    c2.metric("Suma Total de Cuantías", f"${resultado['total_cuantias']:,.0f}")

                    st.download_button(
                        label="💾 Descargar Archivo XML Oficial",
                        data=resultado["xml_bytes"],
                        file_name=resultado["nombre_archivo"],
                        mime="text/xml"
                    )

        except Exception as e:
            st.error(f"❌ Error durante el procesamiento: {e}")