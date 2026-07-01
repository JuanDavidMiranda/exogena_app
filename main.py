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

from Core.diagnostics import analizar_obligatoriedad
from Core.auditors import ejecutar_conciliacion_posicional
from Core.xml_generators import procesar_dinamico_xml

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
        formatos_analizados = analizar_obligatoriedad(archivo_maestro)
        if formatos_analizados:
            st.dataframe(pd.DataFrame(formatos_analizados), use_container_width=True)
            st.markdown("### 💡 Plan de Acción Sugerido:")
            for f in formatos_analizados:
                if "🟢" in f["Dictamen"]:
                    st.success(f"**{f['Formato DIAN']} ({f['Nombre de la Pestaña']}):** Acción requerida. Se detectaron **{f['Terceros Detectados']}** registros.")
                else:
                    st.error(f"**{f['Formato DIAN']} ({f['Nombre de la Pestaña']}):** Omitir. Hoja vacía.")
        else:
            st.warning("⚠️ No se identificaron pestañas válidas.")

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
            dif_montos, solo_dian, solo_novasoft = ejecutar_conciliacion_posicional(archivo_novasoft, archivo_dian)
            
            st.success("✅ Cruce completado con éxito.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Diferencias en Montos", len(dif_montos))
            c2.metric("Solo en DIAN", len(solo_dian))
            c3.metric("Solo en Novasoft", len(solo_novasoft))

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
        st.info("ℹ️ Las versiones del XML se configuran automáticamente (1001 v10, 1003 v7, 1005 v9, 1006 v8, 1007 v9).")

    archivo_excel = st.file_uploader("Carga el archivo de Excel oficial (.xlsx):", type=["xlsx"])

    if archivo_excel is not None:
        try:
            xls = pd.ExcelFile(archivo_excel)
            pestanas_disponibles = xls.sheet_names
            
            # Filtrar solo pestañas asociadas a formatos válidos
            pestanas_formatos = [p for p in pestanas_disponibles if any(f in p for f in ["1001", "1003", "1004", "1005", "1006", "1007"])]
            
            if not pestanas_formatos:
                pestanas_formatos = pestanas_disponibles

            pestana_seleccionada = st.selectbox("Selecciona la pestaña del formato a procesar:", pestanas_formatos)
            
            # Extraer el número de formato
            formato_detectado = "".join(filter(str.isdigit, pestana_seleccionada))
            if not formato_detectado:
                formato_detectado = "1001"

            # Tabla de mapeo de versiones oficiales DIAN
            versiones_formatos = {"1001": 10, "1003": 7, "1004": 8, "1005": 9, "1006": 8, "1007": 9}
            version_oficial = versiones_formatos.get(str(formato_detectado), 9)

            if st.button(f"🚀 Generar XML del Formato {formato_detectado}"):
                with st.spinner(f"Procesando filas de la pestaña '{pestana_seleccionada}'..."):
                    
                    # Llamar al motor unificado y dinámico de core.xml_generators
                    xml_bytes, total_registros, total_cuantias = procesar_dinamico_xml(
                        archivo_xml_insumo=archivo_excel,
                        pestana_seleccionada=pestana_seleccionada,
                        año_gravable=ano,
                        version_xml=version_oficial,
                        num_envio=envio,
                        formato_detectado=str(formato_detectado)
                    )
                    
                    nombre_archivo_xml = f"Dmuisca_01{str(formato_detectado).zfill(4)}{str(version_oficial).zfill(2)}{ano}{str(envio).zfill(8)}.xml"
                    
                    st.success(f"✅ ¡XML del Formato {formato_detectado} generado exitosamente!")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Cantidad de Terceros Reportados", f"{total_registros:,}")
                    c2.metric("Suma Total de Cuantías", f"${total_cuantias:,.0f}")
                    
                    st.download_button(
                        label="💾 Descargar Archivo XML Oficial",
                        data=xml_bytes,
                        file_name=nombre_archivo_xml,
                        mime="text/xml"
                    )
                    
        except Exception as e:
             st.error("❌ Error durante el procesamiento")
             st.code(traceback.format_exc())